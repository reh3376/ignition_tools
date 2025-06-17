"""Code Intelligence Manager - Main coordinator for code intelligence system."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CodeIntelligenceManager:
    """Main manager for code intelligence system."""

    def __init__(self, graph_client, embedder=None):
        """Initialize the code intelligence manager.
        
        Args:
            graph_client: Neo4j graph client
            embedder: Optional sentence transformer for embeddings
        """
        self.client = graph_client
        self.embedder = embedder

        # Import here to avoid circular imports
        from .analyzer import CodeAnalyzer
        from .schema import CodeSchema

        self.schema = CodeSchema(graph_client)
        self.analyzer = CodeAnalyzer()

        # Initialize schema
        self._initialize_schema()

    def _initialize_schema(self):
        """Initialize the Neo4j schema for code intelligence."""
        try:
            self.schema.create_schema()
            logger.info("Code intelligence schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")

    def analyze_and_store_file(self, file_path: Path) -> bool:
        """Analyze a file and store results in Neo4j."""
        try:
            # Analyze the file
            analysis = self.analyzer.analyze_file(file_path)
            if not analysis:
                return False

            # Store in Neo4j
            return self._store_analysis(analysis)

        except Exception as e:
            logger.error(f"Failed to analyze and store file {file_path}: {e}")
            return False

    def analyze_and_store_directory(self, directory_path: Path, recursive: bool = True) -> dict[str, Any]:
        """Analyze all files in a directory and store results."""
        results = {
            "files_processed": 0,
            "files_successful": 0,
            "files_failed": 0,
            "errors": []
        }

        try:
            # Analyze directory
            analyses = self.analyzer.analyze_directory(directory_path, recursive)
            results["files_processed"] = len(analyses)

            # Store each analysis
            for analysis in analyses:
                try:
                    if self._store_analysis(analysis):
                        results["files_successful"] += 1
                    else:
                        results["files_failed"] += 1
                except Exception as e:
                    results["files_failed"] += 1
                    results["errors"].append(str(e))

            logger.info(f"Processed {results['files_processed']} files, "
                       f"{results['files_successful']} successful, "
                       f"{results['files_failed']} failed")

        except Exception as e:
            logger.error(f"Failed to analyze directory {directory_path}: {e}")
            results["errors"].append(str(e))

        return results

    def _store_analysis(self, analysis: dict[str, Any]) -> bool:
        """Store analysis results in Neo4j."""
        try:
            # Store file node
            file_info = analysis["file"]
            self._store_file_node(file_info)

            # Store classes
            for class_info in analysis["classes"]:
                self._store_class_node(class_info)

            # Store methods
            for method_info in analysis["methods"]:
                self._store_method_node(method_info)

            # Store imports
            for import_info in analysis["imports"]:
                self._store_import_node(import_info)

            # Create relationships
            self._create_relationships(analysis)

            return True

        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")
            return False

    def _store_file_node(self, file_info):
        """Store a file node in Neo4j."""
        cypher = """
        MERGE (f:CodeFile {path: $path})
        SET f.lines = $lines,
            f.complexity = $complexity,
            f.maintainability_index = $maintainability_index,
            f.last_modified = $last_modified,
            f.content_hash = $content_hash,
            f.language = $language,
            f.size_bytes = $size_bytes,
            f.updated_at = datetime()
        """

        params = {
            "path": file_info.path,
            "lines": file_info.lines,
            "complexity": file_info.complexity,
            "maintainability_index": file_info.maintainability_index,
            "last_modified": file_info.last_modified.isoformat(),
            "content_hash": file_info.content_hash,
            "language": file_info.language,
            "size_bytes": file_info.size_bytes
        }

        self.client.execute_query(cypher, params)

    def _store_class_node(self, class_info):
        """Store a class node in Neo4j."""
        cypher = """
        MERGE (c:Class {name: $name, file_path: $file_path})
        SET c.start_line = $start_line,
            c.end_line = $end_line,
            c.methods_count = $methods_count,
            c.complexity = $complexity,
            c.docstring = $docstring,
            c.inheritance = $inheritance,
            c.updated_at = datetime()
        """

        params = {
            "name": class_info.name,
            "file_path": class_info.file_path,
            "start_line": class_info.start_line,
            "end_line": class_info.end_line,
            "methods_count": class_info.methods_count,
            "complexity": class_info.complexity,
            "docstring": class_info.docstring,
            "inheritance": class_info.inheritance
        }

        self.client.execute_query(cypher, params)

    def _store_method_node(self, method_info):
        """Store a method node in Neo4j."""
        cypher = """
        MERGE (m:Method {name: $name, file_path: $file_path, start_line: $start_line})
        SET m.class_name = $class_name,
            m.end_line = $end_line,
            m.parameters = $parameters,
            m.complexity = $complexity,
            m.return_type = $return_type,
            m.docstring = $docstring,
            m.is_async = $is_async,
            m.updated_at = datetime()
        """

        params = {
            "name": method_info.name,
            "class_name": method_info.class_name,
            "file_path": method_info.file_path,
            "start_line": method_info.start_line,
            "end_line": method_info.end_line,
            "parameters": method_info.parameters,
            "complexity": method_info.complexity,
            "return_type": method_info.return_type,
            "docstring": method_info.docstring,
            "is_async": method_info.is_async
        }

        self.client.execute_query(cypher, params)

    def _store_import_node(self, import_info):
        """Store an import node in Neo4j."""
        cypher = """
        MERGE (i:Import {module: $module, file_path: $file_path, line_number: $line_number})
        SET i.alias = $alias,
            i.from_module = $from_module,
            i.is_local = $is_local,
            i.updated_at = datetime()
        """

        params = {
            "module": import_info.module,
            "alias": import_info.alias,
            "from_module": import_info.from_module,
            "file_path": import_info.file_path,
            "line_number": import_info.line_number,
            "is_local": import_info.is_local
        }

        self.client.execute_query(cypher, params)

    def _create_relationships(self, analysis: dict[str, Any]):
        """Create relationships between nodes."""
        file_path = analysis["file"].path

        # File CONTAINS Class relationships
        for class_info in analysis["classes"]:
            cypher = """
            MATCH (f:CodeFile {path: $file_path})
            MATCH (c:Class {name: $class_name, file_path: $file_path})
            MERGE (f)-[:CONTAINS]->(c)
            """
            self.client.execute_query(cypher, {
                "file_path": file_path,
                "class_name": class_info.name
            })

        # Class HAS_METHOD Method relationships
        for method_info in analysis["methods"]:
            if method_info.class_name:
                cypher = """
                MATCH (c:Class {name: $class_name, file_path: $file_path})
                MATCH (m:Method {name: $method_name, file_path: $file_path, start_line: $start_line})
                MERGE (c)-[:HAS_METHOD]->(m)
                """
                self.client.execute_query(cypher, {
                    "class_name": method_info.class_name,
                    "method_name": method_info.name,
                    "file_path": file_path,
                    "start_line": method_info.start_line
                })
            else:
                # File-level function
                cypher = """
                MATCH (f:CodeFile {path: $file_path})
                MATCH (m:Method {name: $method_name, file_path: $file_path, start_line: $start_line})
                MERGE (f)-[:CONTAINS]->(m)
                """
                self.client.execute_query(cypher, {
                    "file_path": file_path,
                    "method_name": method_info.name,
                    "start_line": method_info.start_line
                })

        # File IMPORTS relationships
        for import_info in analysis["imports"]:
            cypher = """
            MATCH (f:CodeFile {path: $file_path})
            MATCH (i:Import {module: $module, file_path: $file_path, line_number: $line_number})
            MERGE (f)-[:IMPORTS]->(i)
            """
            self.client.execute_query(cypher, {
                "file_path": file_path,
                "module": import_info.module,
                "line_number": import_info.line_number
            })

    def get_file_context(self, file_path: str) -> dict[str, Any]:
        """Get comprehensive context for a file."""
        cypher = """
        MATCH (f:CodeFile {path: $path})
        OPTIONAL MATCH (f)-[:CONTAINS]->(c:Class)
        OPTIONAL MATCH (c)-[:HAS_METHOD]->(cm:Method)
        OPTIONAL MATCH (f)-[:CONTAINS]->(fm:Method) WHERE fm.class_name IS NULL
        OPTIONAL MATCH (f)-[:IMPORTS]->(i:Import)
        OPTIONAL MATCH (dep:CodeFile)-[:IMPORTS]->(di:Import) WHERE di.from_module CONTAINS replace($path, '.py', '') OR di.module CONTAINS replace($path, '.py', '')
        RETURN f,
               collect(DISTINCT c) as classes,
               collect(DISTINCT cm) as class_methods,
               collect(DISTINCT fm) as file_methods,
               collect(DISTINCT i) as imports,
               collect(DISTINCT dep.path) as dependents
        """

        result = self.client.execute_query(cypher, {"path": file_path})

        if not result:
            return {}

        data = result[0]
        return {
            "file": dict(data["f"]) if data["f"] else None,
            "classes": [dict(c) for c in data["classes"] if c],
            "class_methods": [dict(m) for m in data["class_methods"] if m],
            "file_methods": [dict(m) for m in data["file_methods"] if m],
            "imports": [dict(i) for i in data["imports"] if i],
            "dependents": [path for path in data["dependents"] if path]
        }

    def find_similar_files(self, file_path: str, limit: int = 10) -> list[dict[str, Any]]:
        """Find files similar to the given file based on structure."""
        # Get the target file's characteristics
        context = self.get_file_context(file_path)
        if not context or not context["file"]:
            return []

        target_complexity = context["file"]["complexity"]
        target_classes = len(context["classes"])
        target_methods = len(context["class_methods"]) + len(context["file_methods"])

        cypher = """
        MATCH (f:CodeFile)
        WHERE f.path <> $path
        OPTIONAL MATCH (f)-[:CONTAINS]->(c:Class)
        OPTIONAL MATCH (f)-[:CONTAINS]->(m:Method)
        WITH f, count(DISTINCT c) as class_count, count(DISTINCT m) as method_count
        WITH f, class_count, method_count,
             abs(f.complexity - $target_complexity) as complexity_diff,
             abs(class_count - $target_classes) as class_diff,
             abs(method_count - $target_methods) as method_diff
        WITH f, class_count, method_count,
             (complexity_diff + class_diff + method_diff) as similarity_score
        ORDER BY similarity_score ASC
        LIMIT $limit
        RETURN f.path as path,
               f.complexity as complexity,
               f.maintainability_index as maintainability,
               class_count,
               method_count,
               similarity_score
        """

        params = {
            "path": file_path,
            "target_complexity": target_complexity,
            "target_classes": target_classes,
            "target_methods": target_methods,
            "limit": limit
        }

        return self.client.execute_query(cypher, params)

    def get_code_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics about the codebase."""
        stats = {}

        # Basic counts
        counts_cypher = """
        MATCH (f:CodeFile) 
        OPTIONAL MATCH (f)-[:CONTAINS]->(c:Class)
        OPTIONAL MATCH (f)-[:CONTAINS]->(m:Method)
        OPTIONAL MATCH (f)-[:IMPORTS]->(i:Import)
        RETURN count(DISTINCT f) as files,
               count(DISTINCT c) as classes,
               count(DISTINCT m) as methods,
               count(DISTINCT i) as imports
        """

        counts = self.client.execute_query(counts_cypher)[0]
        stats.update(counts)

        # Complexity statistics
        complexity_cypher = """
        MATCH (f:CodeFile)
        RETURN avg(f.complexity) as avg_complexity,
               max(f.complexity) as max_complexity,
               min(f.complexity) as min_complexity,
               avg(f.maintainability_index) as avg_maintainability,
               sum(f.lines) as total_lines
        """

        complexity = self.client.execute_query(complexity_cypher)[0]
        stats.update(complexity)

        # Top complex files
        top_complex_cypher = """
        MATCH (f:CodeFile)
        RETURN f.path as path, f.complexity as complexity, f.lines as lines
        ORDER BY f.complexity DESC
        LIMIT 10
        """

        stats["most_complex_files"] = self.client.execute_query(top_complex_cypher)

        # Language distribution
        lang_cypher = """
        MATCH (f:CodeFile)
        RETURN f.language as language, count(*) as count
        ORDER BY count DESC
        """

        stats["language_distribution"] = self.client.execute_query(lang_cypher)

        return stats

    def search_code(self, query: str, search_type: str = "all") -> list[dict[str, Any]]:
        """Search for code elements by name or content."""
        results = []

        if search_type in ["all", "files"]:
            # Search files
            file_cypher = """
            MATCH (f:CodeFile)
            WHERE f.path CONTAINS $query
            RETURN 'file' as type, f.path as name, f.path as file_path,
                   f.complexity as complexity, f.lines as lines
            """
            results.extend(self.client.execute_query(file_cypher, {"query": query}))

        if search_type in ["all", "classes"]:
            # Search classes
            class_cypher = """
            MATCH (c:Class)
            WHERE c.name CONTAINS $query OR c.docstring CONTAINS $query
            RETURN 'class' as type, c.name as name, c.file_path as file_path,
                   c.complexity as complexity, c.start_line as start_line
            """
            results.extend(self.client.execute_query(class_cypher, {"query": query}))

        if search_type in ["all", "methods"]:
            # Search methods
            method_cypher = """
            MATCH (m:Method)
            WHERE m.name CONTAINS $query OR m.docstring CONTAINS $query
            RETURN 'method' as type, m.name as name, m.file_path as file_path,
                   m.complexity as complexity, m.start_line as start_line,
                   m.class_name as class_name
            """
            results.extend(self.client.execute_query(method_cypher, {"query": query}))

        return results

    def get_dependency_graph(self, file_path: str, depth: int = 2) -> dict[str, Any]:
        """Get dependency graph for a file."""
        cypher = """
        MATCH path = (f:CodeFile {path: $path})-[:IMPORTS*1..$depth]-(related:CodeFile)
        RETURN f.path as source,
               related.path as target,
               length(path) as distance,
               relationships(path) as relationships
        """

        dependencies = self.client.execute_query(cypher, {
            "path": file_path,
            "depth": depth
        })

        return {
            "center_file": file_path,
            "dependencies": dependencies,
            "depth": depth
        }
