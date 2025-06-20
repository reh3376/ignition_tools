"""Knowledge Validator for AI Assistant Module

Adapted from docs/crawl test/knowledge_graph/knowledge_graph_validator.py
Validates AI-generated code against Neo4j knowledge graph containing repository information.
Checks imports, methods, attributes, and parameters.
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .code_analyzer import (
    AnalysisResult,
    AttributeAccess,
    ClassInstantiation,
    FunctionCall,
    ImportInfo,
    MethodCall,
)

from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNCERTAIN = "UNCERTAIN"
    NOT_FOUND = "NOT_FOUND"


@dataclass
class ValidationResult:
    """Result of validating a single element"""
    status: ValidationStatus
    confidence: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ImportValidation:
    """Validation result for an import"""
    import_info: ImportInfo
    validation: ValidationResult
    available_classes: List[str] = field(default_factory=list)
    available_functions: List[str] = field(default_factory=list)


@dataclass
class MethodValidation:
    """Validation result for a method call"""
    method_call: MethodCall
    validation: ValidationResult
    expected_params: List[str] = field(default_factory=list)
    actual_params: List[str] = field(default_factory=list)
    parameter_validation: Optional[ValidationResult] = None


@dataclass
class AttributeValidation:
    """Validation result for attribute access"""
    attribute_access: AttributeAccess
    validation: ValidationResult
    expected_type: Optional[str] = None


@dataclass
class FunctionValidation:
    """Validation result for function call"""
    function_call: FunctionCall
    validation: ValidationResult
    expected_params: List[str] = field(default_factory=list)
    actual_params: List[str] = field(default_factory=list)
    parameter_validation: Optional[ValidationResult] = None


@dataclass
class ClassValidation:
    """Validation result for class instantiation"""
    class_instantiation: ClassInstantiation
    validation: ValidationResult
    constructor_params: List[str] = field(default_factory=list)
    parameter_validation: Optional[ValidationResult] = None


@dataclass
class ScriptValidationResult:
    """Complete validation results for a script"""
    script_path: str
    analysis_result: AnalysisResult
    import_validations: List[ImportValidation] = field(default_factory=list)
    class_validations: List[ClassValidation] = field(default_factory=list)
    method_validations: List[MethodValidation] = field(default_factory=list)
    attribute_validations: List[AttributeValidation] = field(default_factory=list)
    function_validations: List[FunctionValidation] = field(default_factory=list)
    overall_confidence: float = 0.0
    hallucinations_detected: List[Dict[str, Any]] = field(default_factory=list)


class KnowledgeValidator:
    """Validates code against Neo4j knowledge graph"""

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ):
        self.neo4j_uri = neo4j_uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = neo4j_user or os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = neo4j_password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None

        # Cache for performance
        self.module_cache: Dict[str, List[str]] = {}
        self.class_cache: Dict[str, Dict[str, Any]] = {}
        self.method_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.repo_cache: Dict[str, str] = {}  # module_name -> repo_name
        self.knowledge_graph_modules: set[str] = set()  # Track modules in knowledge graph

    async def initialize(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password)
            )
            logger.info("Knowledge graph validator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection: {e}")
            raise

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()

    async def validate_script(self, analysis_result: AnalysisResult) -> ScriptValidationResult:
        """Validate entire script analysis against knowledge graph"""
        result = ScriptValidationResult(
            script_path=analysis_result.file_path, analysis_result=analysis_result
        )

        try:
            # Validate imports first (builds context for other validations)
            result.import_validations = await self._validate_imports(analysis_result.imports)

            # Validate class instantiations
            result.class_validations = await self._validate_class_instantiations(
                analysis_result.class_instantiations
            )

            # Validate method calls
            result.method_validations = await self._validate_method_calls(
                analysis_result.method_calls
            )

            # Validate attribute accesses
            result.attribute_validations = await self._validate_attribute_accesses(
                analysis_result.attribute_accesses
            )

            # Validate function calls
            result.function_validations = await self._validate_function_calls(
                analysis_result.function_calls
            )

            # Calculate overall confidence and detect hallucinations
            result.overall_confidence = self._calculate_overall_confidence(result)
            result.hallucinations_detected = self._detect_hallucinations(result)

        except Exception as e:
            logger.error(f"Error during script validation: {e}")
            result.overall_confidence = 0.0
            result.hallucinations_detected.append({
                "type": "validation_error",
                "message": f"Validation failed: {str(e)}",
                "confidence": 0.0
            })

        return result

    async def _validate_imports(self, imports: List[ImportInfo]) -> List[ImportValidation]:
        """Validate all imports against knowledge graph"""
        validations = []
        for import_info in imports:
            validation = await self._validate_single_import(import_info)
            validations.append(validation)
        return validations

    async def _validate_single_import(self, import_info: ImportInfo) -> ImportValidation:
        """Validate a single import"""
        search_module = import_info.module if import_info.is_from_import else import_info.name

        # Check cache first
        if search_module in self.module_cache:
            available_items = self.module_cache[search_module]
        else:
            available_items = await self._find_modules(search_module)
            self.module_cache[search_module] = available_items

        if available_items:
            validation = ValidationResult(
                status=ValidationStatus.VALID,
                confidence=0.9,
                message=f"Module '{search_module}' found in knowledge graph",
                details={"available_items": available_items}
            )
        else:
            # Try to find similar modules
            similar_modules = await self._find_similar_modules(search_module)
            validation = ValidationResult(
                status=ValidationStatus.NOT_FOUND,
                confidence=0.1,
                message=f"Module '{search_module}' not found in knowledge graph",
                suggestions=[f"Did you mean '{mod}'?" for mod in similar_modules[:3]]
            )

        return ImportValidation(
            import_info=import_info,
            validation=validation,
            available_classes=available_items if available_items else [],
            available_functions=[]
        )

    async def _validate_class_instantiations(
        self, instantiations: List[ClassInstantiation]
    ) -> List[ClassValidation]:
        """Validate all class instantiations"""
        validations = []
        for instantiation in instantiations:
            validation = await self._validate_single_class_instantiation(instantiation)
            validations.append(validation)
        return validations

    async def _validate_single_class_instantiation(
        self, instantiation: ClassInstantiation
    ) -> ClassValidation:
        """Validate a single class instantiation"""
        class_info = await self._find_class(instantiation.class_name)

        if class_info:
            validation = ValidationResult(
                status=ValidationStatus.VALID,
                confidence=0.9,
                message=f"Class '{instantiation.class_name}' found",
                details=class_info
            )
            # Get constructor parameters if available
            constructor_params = class_info.get("constructor_params", [])
        else:
            validation = ValidationResult(
                status=ValidationStatus.NOT_FOUND,
                confidence=0.1,
                message=f"Class '{instantiation.class_name}' not found in knowledge graph"
            )
            constructor_params = []

        return ClassValidation(
            class_instantiation=instantiation,
            validation=validation,
            constructor_params=constructor_params
        )

    async def _validate_method_calls(self, method_calls: List[MethodCall]) -> List[MethodValidation]:
        """Validate all method calls"""
        validations = []
        for method_call in method_calls:
            validation = await self._validate_single_method_call(method_call)
            validations.append(validation)
        return validations

    async def _validate_single_method_call(self, method_call: MethodCall) -> MethodValidation:
        """Validate a single method call"""
        # Try to find the method in the knowledge graph
        method_info = None
        if method_call.object_type:
            method_info = await self._find_method(method_call.object_type, method_call.method_name)

        if method_info:
            validation = ValidationResult(
                status=ValidationStatus.VALID,
                confidence=0.8,
                message=f"Method '{method_call.method_name}' found for class '{method_call.object_type}'",
                details=method_info
            )
            expected_params = method_info.get("parameters", [])
        else:
            # Try to find similar methods
            similar_methods = []
            if method_call.object_type:
                similar_methods = await self._find_similar_methods(
                    method_call.object_type, method_call.method_name
                )

            validation = ValidationResult(
                status=ValidationStatus.NOT_FOUND,
                confidence=0.2,
                message=f"Method '{method_call.method_name}' not found",
                suggestions=[f"Did you mean '{method}'?" for method in similar_methods[:3]]
            )
            expected_params = []

        return MethodValidation(
            method_call=method_call,
            validation=validation,
            expected_params=expected_params,
            actual_params=method_call.args
        )

    async def _validate_attribute_accesses(
        self, attribute_accesses: List[AttributeAccess]
    ) -> List[AttributeValidation]:
        """Validate all attribute accesses"""
        validations = []
        for attr_access in attribute_accesses:
            validation = await self._validate_single_attribute_access(attr_access)
            validations.append(validation)
        return validations

    async def _validate_single_attribute_access(
        self, attr_access: AttributeAccess
    ) -> AttributeValidation:
        """Validate a single attribute access"""
        attr_info = None
        if attr_access.object_type:
            attr_info = await self._find_attribute(attr_access.object_type, attr_access.attribute_name)

        if attr_info:
            validation = ValidationResult(
                status=ValidationStatus.VALID,
                confidence=0.8,
                message=f"Attribute '{attr_access.attribute_name}' found",
                details=attr_info
            )
        else:
            validation = ValidationResult(
                status=ValidationStatus.NOT_FOUND,
                confidence=0.2,
                message=f"Attribute '{attr_access.attribute_name}' not found"
            )

        return AttributeValidation(
            attribute_access=attr_access,
            validation=validation,
            expected_type=attr_info.get("type") if attr_info else None
        )

    async def _validate_function_calls(self, function_calls: List[FunctionCall]) -> List[FunctionValidation]:
        """Validate all function calls"""
        validations = []
        for func_call in function_calls:
            validation = await self._validate_single_function_call(func_call)
            validations.append(validation)
        return validations

    async def _validate_single_function_call(self, func_call: FunctionCall) -> FunctionValidation:
        """Validate a single function call"""
        func_info = await self._find_function(func_call.function_name)

        if func_info:
            validation = ValidationResult(
                status=ValidationStatus.VALID,
                confidence=0.8,
                message=f"Function '{func_call.function_name}' found",
                details=func_info
            )
            expected_params = func_info.get("parameters", [])
        else:
            validation = ValidationResult(
                status=ValidationStatus.NOT_FOUND,
                confidence=0.2,
                message=f"Function '{func_call.function_name}' not found"
            )
            expected_params = []

        return FunctionValidation(
            function_call=func_call,
            validation=validation,
            expected_params=expected_params,
            actual_params=func_call.args
        )

    # Neo4j query methods (simplified versions)
    async def _find_modules(self, module_name: str) -> List[str]:
        """Find modules in the knowledge graph"""
        if not self.driver:
            return []

        query = """
        MATCH (m:Module {name: $module_name})
        OPTIONAL MATCH (m)-[:CONTAINS]->(c:Class)
        OPTIONAL MATCH (m)-[:CONTAINS]->(f:Function)
        RETURN collect(DISTINCT c.name) as classes, collect(DISTINCT f.name) as functions
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, module_name=module_name)
                record = await result.single()
                if record:
                    classes = record.get("classes", [])
                    functions = record.get("functions", [])
                    return classes + functions
        except Exception as e:
            logger.warning(f"Failed to query modules: {e}")

        return []

    async def _find_class(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Find class information in the knowledge graph"""
        if not self.driver:
            return None

        query = """
        MATCH (c:Class {name: $class_name})
        OPTIONAL MATCH (c)-[:HAS_METHOD]->(m:Method)
        RETURN c.name as name, c.docstring as docstring, 
               collect(m.name) as methods
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, class_name=class_name)
                record = await result.single()
                if record:
                    return {
                        "name": record.get("name"),
                        "docstring": record.get("docstring"),
                        "methods": record.get("methods", [])
                    }
        except Exception as e:
            logger.warning(f"Failed to query class: {e}")

        return None

    async def _find_method(self, class_name: str, method_name: str) -> Optional[Dict[str, Any]]:
        """Find method information in the knowledge graph"""
        if not self.driver:
            return None

        query = """
        MATCH (c:Class {name: $class_name})-[:HAS_METHOD]->(m:Method {name: $method_name})
        RETURN m.name as name, m.docstring as docstring, m.parameters as parameters
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, class_name=class_name, method_name=method_name)
                record = await result.single()
                if record:
                    return {
                        "name": record.get("name"),
                        "docstring": record.get("docstring"),
                        "parameters": record.get("parameters", [])
                    }
        except Exception as e:
            logger.warning(f"Failed to query method: {e}")

        return None

    async def _find_attribute(self, class_name: str, attr_name: str) -> Optional[Dict[str, Any]]:
        """Find attribute information in the knowledge graph"""
        if not self.driver:
            return None

        query = """
        MATCH (c:Class {name: $class_name})-[:HAS_ATTRIBUTE]->(a:Attribute {name: $attr_name})
        RETURN a.name as name, a.type as type, a.docstring as docstring
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, class_name=class_name, attr_name=attr_name)
                record = await result.single()
                if record:
                    return {
                        "name": record.get("name"),
                        "type": record.get("type"),
                        "docstring": record.get("docstring")
                    }
        except Exception as e:
            logger.warning(f"Failed to query attribute: {e}")

        return None

    async def _find_function(self, func_name: str) -> Optional[Dict[str, Any]]:
        """Find function information in the knowledge graph"""
        if not self.driver:
            return None

        query = """
        MATCH (f:Function {name: $func_name})
        RETURN f.name as name, f.docstring as docstring, f.parameters as parameters
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, func_name=func_name)
                record = await result.single()
                if record:
                    return {
                        "name": record.get("name"),
                        "docstring": record.get("docstring"),
                        "parameters": record.get("parameters", [])
                    }
        except Exception as e:
            logger.warning(f"Failed to query function: {e}")

        return None

    async def _find_similar_modules(self, module_name: str) -> List[str]:
        """Find similar module names using fuzzy matching"""
        if not self.driver:
            return []

        query = """
        MATCH (m:Module)
        WHERE m.name CONTAINS $partial_name OR $partial_name CONTAINS m.name
        RETURN m.name as name
        LIMIT 5
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, partial_name=module_name.lower())
                records = await result.data()
                return [record["name"] for record in records]
        except Exception as e:
            logger.warning(f"Failed to find similar modules: {e}")

        return []

    async def _find_similar_methods(self, class_name: str, method_name: str) -> List[str]:
        """Find similar method names using fuzzy matching"""
        if not self.driver:
            return []

        query = """
        MATCH (c:Class {name: $class_name})-[:HAS_METHOD]->(m:Method)
        WHERE m.name CONTAINS $partial_name OR $partial_name CONTAINS m.name
        RETURN m.name as name
        LIMIT 5
        """

        try:
            async with self.driver.session() as session:
                result = await session.run(query, class_name=class_name, partial_name=method_name.lower())
                records = await result.data()
                return [record["name"] for record in records]
        except Exception as e:
            logger.warning(f"Failed to find similar methods: {e}")

        return []

    def _calculate_overall_confidence(self, result: ScriptValidationResult) -> float:
        """Calculate overall confidence score for the validation"""
        all_validations = []
        all_validations.extend([v.validation for v in result.import_validations])
        all_validations.extend([v.validation for v in result.class_validations])
        all_validations.extend([v.validation for v in result.method_validations])
        all_validations.extend([v.validation for v in result.attribute_validations])
        all_validations.extend([v.validation for v in result.function_validations])

        if not all_validations:
            return 1.0  # No validations means no issues

        total_confidence = sum(v.confidence for v in all_validations)
        return total_confidence / len(all_validations)

    def _detect_hallucinations(self, result: ScriptValidationResult) -> List[Dict[str, Any]]:
        """Detect potential hallucinations in the validation results"""
        hallucinations = []

        # Check for low-confidence validations
        all_validations = []
        all_validations.extend([(v.validation, f"import {v.import_info.name}") for v in result.import_validations])
        all_validations.extend([(v.validation, f"class {v.class_instantiation.class_name}") for v in result.class_validations])
        all_validations.extend([(v.validation, f"method {v.method_call.method_name}") for v in result.method_validations])
        all_validations.extend([(v.validation, f"attribute {v.attribute_access.attribute_name}") for v in result.attribute_validations])
        all_validations.extend([(v.validation, f"function {v.function_call.function_name}") for v in result.function_validations])

        for validation, description in all_validations:
            if validation.confidence < 0.5:
                hallucinations.append({
                    "type": "low_confidence",
                    "description": description,
                    "confidence": validation.confidence,
                    "message": validation.message,
                    "suggestions": validation.suggestions
                })

        return hallucinations 