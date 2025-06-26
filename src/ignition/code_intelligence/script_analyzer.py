"""AI Script Analyzer for IGN Scripts.

This module provides AI-powered script analysis using local open source models,
adapted from ai_script_analyzer.py and following crawl_mcp.py methodology.

Core Features:
- Environment validation with comprehensive checks
- Local model integration (Qwen2.5-Coder, CodeLlama)
- AST-based pattern detection
- Code understanding and context analysis
- Confidence scoring without external API dependencies
"""

import ast
import json
import os
import time
from typing import Any

from pydantic import BaseModel, Field, ValidationError

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class AnalysisRequest(BaseModel):
    """Input validation model for script analysis requests."""

    script_path: str = Field(..., description="Path to Python script to analyze")
    analysis_type: str = Field(
        default="comprehensive",
        description="Type of analysis: pattern, context, structure, comprehensive",
    )
    model_preference: str = Field(default="qwen", description="Preferred model: qwen, codellama, auto")
    include_suggestions: bool = Field(default=True, description="Whether to include improvement suggestions")
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Confidence threshold for insights")


class CodePattern(BaseModel):
    """Model for detected code patterns."""

    pattern_type: str = Field(..., description="Type of pattern detected")
    pattern_name: str = Field(..., description="Name of the pattern")
    line_number: int = Field(..., description="Line number where pattern occurs")
    confidence: float = Field(..., description="Confidence score for pattern detection")
    description: str = Field(..., description="Description of the pattern")
    suggestion: str | None = Field(default=None, description="Improvement suggestion")


class AnalysisResult(BaseModel):
    """Output model for script analysis results."""

    success: bool = Field(..., description="Whether analysis completed successfully")
    script_path: str = Field(..., description="Path to analyzed script")
    analysis_type: str = Field(..., description="Type of analysis performed")

    # Code Structure Analysis
    total_lines: int = Field(default=0, description="Total lines of code")
    total_functions: int = Field(default=0, description="Total number of functions")
    total_classes: int = Field(default=0, description="Total number of classes")
    complexity_score: float = Field(default=0.0, description="Code complexity score")

    # Pattern Detection Results
    patterns_detected: list[CodePattern] = Field(default_factory=list, description="Detected code patterns")
    antipatterns_detected: list[CodePattern] = Field(default_factory=list, description="Detected antipatterns")

    # AI Analysis Results
    context_understanding: dict[str, Any] = Field(default_factory=dict, description="AI understanding of code context")
    code_quality_score: float = Field(default=0.0, description="Overall code quality score")
    maintainability_score: float = Field(default=0.0, description="Code maintainability score")

    # Processing Information
    processing_time: float = Field(default=0.0, description="Total processing time in seconds")
    models_used: list[str] = Field(default_factory=list, description="Models used for analysis")

    # Improvement Suggestions
    suggestions: list[dict[str, str]] = Field(default_factory=list, description="Code improvement suggestions")

    # Confidence Metrics
    confidence_scores: dict[str, float] = Field(
        default_factory=dict, description="Confidence scores for various checks"
    )


def validate_analyzer_environment() -> dict[str, Any]:
    """Validate environment for script analysis following crawl_mcp.py patterns."""
    validation_result: dict[str, Any] = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "available_components": {
            "ollama_available": False,
            "local_models_enabled": False,
            "ast_parser_available": True,  # Built-in Python AST
            "requests_available": REQUESTS_AVAILABLE,
        },
    }

    try:
        # Check Ollama availability
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        if REQUESTS_AVAILABLE:
            try:
                response = requests.get(f"{ollama_host}/api/tags", timeout=5)
                if response.status_code == 200:
                    validation_result["available_components"]["ollama_available"] = True
                    tags_data = response.json()
                    available_models = [model["name"] for model in tags_data.get("models", [])]
                    validation_result["available_models"] = available_models

                    # Check for preferred models
                    preferred_models = [
                        "qwen2.5-coder:7b",
                        "codellama:7b-instruct",
                        "codellama:13b-instruct",
                    ]
                    validation_result["preferred_models_available"] = [
                        model for model in preferred_models if any(model in available for available in available_models)
                    ]
                else:
                    validation_result["warnings"].append(f"Ollama not responding at {ollama_host}")
            except Exception:
                validation_result["warnings"].append(f"Cannot connect to Ollama at {ollama_host}")
        else:
            validation_result["warnings"].append("Requests library not available for Ollama communication")

        # Check local models configuration
        use_local_models = os.getenv("USE_LOCAL_MODELS", "false").lower() == "true"
        validation_result["available_components"]["local_models_enabled"] = use_local_models

        if not use_local_models:
            validation_result["warnings"].append("Local models disabled. AI analysis will be limited.")

    except Exception as e:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Environment validation failed: {e!s}")

    return validation_result


def format_analyzer_error(error: Exception) -> str:
    """Format analyzer errors for user-friendly messages following crawl_mcp.py patterns."""
    error_str = str(error).lower()

    if "syntax" in error_str:
        return f"Python syntax error in script: {error!s}"
    elif "file not found" in error_str or "no such file" in error_str:
        return f"Script file not found: {error!s}"
    elif "permission" in error_str:
        return f"Permission denied accessing script: {error!s}"
    elif "encoding" in error_str:
        return f"File encoding error: {error!s}"
    elif "model" in error_str:
        return f"Model analysis error: {error!s}"
    else:
        return f"Analysis error: {error!s}"


class AIScriptAnalyzer:
    """AI-powered script analyzer using local open source models."""

    def __init__(self) -> None:
        """Initialize the AI script analyzer."""
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.initialized = False
        self.available_models = []

    async def initialize(self) -> bool:
        """Initialize analyzer components with environment validation."""
        try:
            # Validate environment first
            env_validation = validate_analyzer_environment()
            if not env_validation["valid"]:
                print(f"Environment validation failed: {env_validation['errors']}")
                return False

            # Store available models
            self.available_models = env_validation.get("available_models", [])

            if env_validation["available_components"]["ollama_available"]:
                print("✓ Ollama models available for analysis")
            else:
                print("⚠️  Ollama not available - analysis will be limited to AST-based patterns")

            self.initialized = True
            return True

        except Exception as e:
            print(f"Initialization failed: {format_analyzer_error(e)}")
            return False

    async def analyze_script(
        self,
        script_path: str,
        analysis_type: str = "comprehensive",
        model_preference: str = "qwen",
        include_suggestions: bool = True,
        confidence_threshold: float = 0.6,
    ) -> AnalysisResult:
        """Analyze a Python script with AI-powered analysis.

        Following crawl_mcp.py methodology for systematic analysis.
        """
        start_time = time.time()

        # Step 1: Input validation and sanitization
        try:
            AnalysisRequest(
                script_path=script_path,
                analysis_type=analysis_type,
                model_preference=model_preference,
                include_suggestions=include_suggestions,
                confidence_threshold=confidence_threshold,
            )
        except ValidationError as e:
            return AnalysisResult(
                success=False,
                script_path=script_path,
                analysis_type=analysis_type,
                processing_time=time.time() - start_time,
                suggestions=[{"type": "error", "suggestion": f"Input validation failed: {e}"}],
            )

        # Step 2: Environment validation
        if not self.initialized:
            await self.initialize()

        # Step 3: Create result object
        result = AnalysisResult(success=True, script_path=script_path, analysis_type=analysis_type)

        try:
            # Step 4: Basic AST Analysis
            result = await self._analyze_ast_structure(result, script_path)

            # Step 5: Pattern Detection
            if analysis_type in ["pattern", "comprehensive"]:
                result = await self._detect_code_patterns(result, script_path)

            # Step 6: AI Context Understanding
            if analysis_type in ["context", "comprehensive"]:
                result = await self._analyze_code_context(result, script_path, model_preference, confidence_threshold)

            # Step 7: Generate Suggestions
            if include_suggestions:
                result = await self._generate_improvement_suggestions(result, script_path, model_preference)

        except Exception as e:
            result.success = False
            result.suggestions.append({"type": "error", "suggestion": format_analyzer_error(e)})

        result.processing_time = time.time() - start_time
        return result

    async def _analyze_ast_structure(self, result: AnalysisResult, script_path: str) -> AnalysisResult:
        """Analyze basic script structure using AST."""
        try:
            with open(script_path, encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code, filename=script_path)

            # Count structural elements
            structure_analyzer = StructureAnalyzer()
            structure_analyzer.visit(tree)

            result.total_lines = len(source_code.splitlines())
            result.total_functions = len(structure_analyzer.functions)
            result.total_classes = len(structure_analyzer.classes)
            result.complexity_score = structure_analyzer.calculate_complexity()

            result.confidence_scores["structure_analysis"] = 1.0

        except SyntaxError as e:
            result.success = False
            result.suggestions.append(
                {
                    "type": "syntax_error",
                    "suggestion": f"Fix syntax error at line {e.lineno}: {e.msg}",
                }
            )
            result.confidence_scores["structure_analysis"] = 0.0
        except Exception as e:
            result.success = False
            result.suggestions.append({"type": "structure_error", "suggestion": format_analyzer_error(e)})
            result.confidence_scores["structure_analysis"] = 0.0

        return result

    async def _detect_code_patterns(self, result: AnalysisResult, script_path: str) -> AnalysisResult:
        """Detect code patterns and antipatterns using AST analysis."""
        try:
            with open(script_path, encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # Pattern detection
            pattern_detector = CodePatternDetector()
            pattern_detector.visit(tree)

            # Convert detected patterns to CodePattern objects
            for pattern_info in pattern_detector.patterns:
                pattern = CodePattern(
                    pattern_type=pattern_info["type"],
                    pattern_name=pattern_info["name"],
                    line_number=pattern_info["line"],
                    confidence=pattern_info["confidence"],
                    description=pattern_info["description"],
                    suggestion=pattern_info.get("suggestion"),
                )

                if pattern_info["is_antipattern"]:
                    result.antipatterns_detected.append(pattern)
                else:
                    result.patterns_detected.append(pattern)

            result.confidence_scores["pattern_detection"] = 0.9

        except Exception as e:
            result.suggestions.append(
                {
                    "type": "pattern_error",
                    "suggestion": f"Pattern detection error: {format_analyzer_error(e)}",
                }
            )
            result.confidence_scores["pattern_detection"] = 0.0

        return result

    async def _analyze_code_context(
        self,
        result: AnalysisResult,
        script_path: str,
        model_preference: str,
        confidence_threshold: float,
    ) -> AnalysisResult:
        """Analyze code context using local AI models."""
        try:
            pass  # TODO: Add try block content
        except Exception:
            pass  # TODO: Handle exception
            if not REQUESTS_AVAILABLE:
                result.suggestions.append(
                    {
                        "type": "model_unavailable",
                        "suggestion": "Requests library not available for AI analysis",
                    }
                )
                return result

            # Check if Ollama is available
            try:
                response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
                if response.status_code != 200:
                    result.suggestions.append(
                        {
                            "type": "model_unavailable",
                            "suggestion": "Ollama not available for AI context analysis",
                        }
                    )
                    return result
            except Exception:
                result.suggestions.append(
                    {
                        "type": "model_unavailable",
                        "suggestion": "Cannot connect to Ollama for AI analysis",
                    }
                )
                return result

            # Read script content
            with open(script_path, encoding="utf-8") as f:
                source_code = f.read()

            # Select model based on preference
            model_name = "qwen2.5-coder:7b" if model_preference == "qwen" else "codellama:7b-instruct"

            # Check if preferred model is available
            if not any(model_name in available for available in self.available_models):
                # Fallback to any available code model
                code_models = [m for m in self.available_models if "code" in m.lower() or "llama" in m.lower()]
                if code_models:
                    model_name = code_models[0]
                else:
                    result.suggestions.append(
                        {
                            "type": "model_unavailable",
                            "suggestion": "No suitable code analysis models available",
                        }
                    )
                    return result

            prompt = f"""Analyze the following Python code and provide insights about its context, purpose, and quality:

{source_code}

Please analyze:
1. What is the main purpose of this code?
2. What patterns or architectural approaches does it use?
3. What is the overall code quality (scale 1-10)?
4. What is the maintainability score (scale 1-10)?
5. Are there any specific Ignition/SCADA related patterns?

Respond with JSON format:
{{
    "purpose": "string description",
    "patterns": ["pattern1", "pattern2"],
    "quality_score": float,
    "maintainability_score": float,
    "ignition_patterns": ["pattern1", "pattern2"],
    "insights": ["insight1", "insight2"]
}}"""

            payload = {"model": model_name, "prompt": prompt, "stream": False}

            response = requests.post(f"{self.ollama_host}/api/generate", json=payload, timeout=120)

            if response.status_code == 200:
                ollama_response = response.json()
                response_text = ollama_response.get("response", "")

                try:
                    # Parse JSON response
                    analysis = json.loads(response_text)

                    result.context_understanding = analysis
                    result.code_quality_score = float(analysis.get("quality_score", 0.0))
                    result.maintainability_score = float(analysis.get("maintainability_score", 0.0))

                    result.confidence_scores["context_analysis"] = 0.8
                    result.models_used.append(model_name)

                except json.JSONDecodeError:
                    result.suggestions.append(
                        {
                            "type": "analysis_error",
                            "suggestion": "Failed to parse AI model response for context analysis",
                        }
                    )
                    result.confidence_scores["context_analysis"] = 0.3
            else:
                result.suggestions.append(
                    {
                        "type": "model_error",
                        "suggestion": f"AI model request failed with status {response.status_code}",
                    }
                )
                result.confidence_scores["context_analysis"] = 0.0

        except Exception as e:
            result.suggestions.append({"type": "context_error", "suggestion": format_analyzer_error(e)})
            result.confidence_scores["context_analysis"] = 0.0

        return result

    async def _generate_improvement_suggestions(
        self, result: AnalysisResult, script_path: str, model_preference: str
    ) -> AnalysisResult:
        """Generate improvement suggestions based on analysis results."""
        try:
            suggestions = []

            # Structure-based suggestions
            if result.total_functions > 20:
                suggestions.append(
                    {
                        "type": "structure",
                        "suggestion": f"Consider splitting script with {result.total_functions} functions into modules",
                    }
                )

            if result.complexity_score > 7.0:
                suggestions.append(
                    {
                        "type": "complexity",
                        "suggestion": f"High complexity score ({result.complexity_score:.1f}) - consider refactoring",
                    }
                )

            # Pattern-based suggestions
            if result.antipatterns_detected:
                suggestions.append(
                    {
                        "type": "antipatterns",
                        "suggestion": f"Found {len(result.antipatterns_detected)} antipatterns - review and refactor",
                    }
                )

            # Quality-based suggestions
            if result.code_quality_score < 6.0:
                suggestions.append(
                    {
                        "type": "quality",
                        "suggestion": f"Low quality score ({result.code_quality_score:.1f}) - improve code structure and documentation",  # noqa: E501
                    }
                )

            if result.maintainability_score < 6.0:
                suggestions.append(
                    {
                        "type": "maintainability",
                        "suggestion": f"Low maintainability score ({result.maintainability_score:.1f}) - add comments and simplify logic",  # noqa: E501
                    }
                )

            # Add existing suggestions
            result.suggestions.extend(suggestions)

        except Exception as e:
            print(f"Error generating suggestions: {format_analyzer_error(e)}")

        return result


class StructureAnalyzer(ast.NodeVisitor):
    """AST analyzer for basic script structure."""

    def __init__(self) -> Any:
        self.functions = []
        self.classes = []
        self.complexity = 0
        self.current_function_complexity = 0

    def visit_FunctionDef(self, node) -> Any:
        """Visit function definitions."""
        self.functions.append({"name": node.name, "line": node.lineno, "args_count": len(node.args.args)})

        # Calculate complexity for this function
        old_complexity = self.current_function_complexity
        self.current_function_complexity = 0
        self.generic_visit(node)
        function_complexity = self.current_function_complexity
        self.current_function_complexity = old_complexity

        self.complexity += function_complexity

    def visit_ClassDef(self, node) -> Any:
        """Visit class definitions."""
        self.classes.append({"name": node.name, "line": node.lineno})
        self.generic_visit(node)

    def visit_If(self, node) -> Any:
        """Visit if statements - increases complexity."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node) -> Any:
        """Visit for loops - increases complexity."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node) -> Any:
        """Visit while loops - increases complexity."""
        self.current_function_complexity += 1
        self.generic_visit(node)

    def calculate_complexity(self) -> float:
        """Calculate overall complexity score."""
        if not self.functions:
            return 0.0
        return min(10.0, self.complexity / len(self.functions))


class CodePatternDetector(ast.NodeVisitor):
    """Detect common code patterns and antipatterns."""

    def __init__(self) -> None:
        self.patterns = []

    def visit_FunctionDef(self, node) -> None:
        """Visit function definitions to detect patterns."""
        # Check for too many parameters (antipattern)
        if len(node.args.args) > 8:
            self.patterns.append(
                {
                    "type": "function",
                    "name": "too_many_parameters",
                    "line": node.lineno,
                    "confidence": 0.9,
                    "description": f"Function '{node.name}' has {len(node.args.args)} parameters",
                    "suggestion": "Consider using a configuration object or breaking into smaller functions",
                    "is_antipattern": True,
                }
            )

        # Check for very long functions
        if hasattr(node, "end_lineno") and node.end_lineno:
            function_length = node.end_lineno - node.lineno
            if function_length > 50:
                self.patterns.append(
                    {
                        "type": "function",
                        "name": "long_function",
                        "line": node.lineno,
                        "confidence": 0.8,
                        "description": f"Function '{node.name}' is {function_length} lines long",
                        "suggestion": "Consider breaking into smaller, focused functions",
                        "is_antipattern": True,
                    }
                )

        # Check for Ignition-specific patterns
        if any(ignition_keyword in node.name.lower() for ignition_keyword in ["system", "tag", "opc", "plc"]):
            self.patterns.append(
                {
                    "type": "ignition",
                    "name": "ignition_function",
                    "line": node.lineno,
                    "confidence": 0.7,
                    "description": f"Function '{node.name}' appears to be Ignition-related",
                    "suggestion": None,
                    "is_antipattern": False,
                }
            )

        self.generic_visit(node)

    def visit_Import(self, node) -> None:
        """Visit import statements to detect Ignition imports."""
        for alias in node.names:
            if any(ignition_module in alias.name for ignition_module in ["system", "shared"]):
                self.patterns.append(
                    {
                        "type": "import",
                        "name": "ignition_import",
                        "line": node.lineno,
                        "confidence": 0.8,
                        "description": f"Ignition module import: {alias.name}",
                        "suggestion": None,
                        "is_antipattern": False,
                    }
                )

        self.generic_visit(node)


__all__ = [
    "AIScriptAnalyzer",
    "AnalysisRequest",
    "AnalysisResult",
    "CodePattern",
    "format_analyzer_error",
    "validate_analyzer_environment",
]
