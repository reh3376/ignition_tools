"""Dependency Analyzer - Phase 8.4

This module analyzes and creates proper dependency relationships between CodeFile nodes
for accurate dependency graph visualization and analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DependencyRelationship:
    """Represents a dependency relationship between two files."""

    source_file: str
    target_file: str
    relationship_type: str  # imports, calls, inherits
    strength: float  # 0.0 to 1.0 based on usage frequency
    import_details: list[str]  # specific imports


class DependencyAnalyzer:
    """Analyzes and creates dependency relationships between code files."""

    def __init__(self, graph_client):
        """Initialize the dependency analyzer.

        Args:
            graph_client: IgnitionGraphClient instance
        """
        self.client = graph_client

    def analyze_and_create_dependencies(self) -> int:
        """Analyze imports and create CodeFile-to-CodeFile dependency relationships.

        Returns:
            Number of dependency relationships created
        """
        try:
            logger.info("Starting dependency analysis...")

            # Get all CodeFile nodes and their imports
            file_imports = self._get_file_imports()

            # Create a mapping of module paths to CodeFile paths
            module_to_file_mapping = self._create_module_mapping()

            # Analyze dependencies and create relationships
            dependencies = self._analyze_dependencies(
                file_imports, module_to_file_mapping
            )

            # Create the relationships in the graph
            relationships_created = self._create_dependency_relationships(dependencies)

            logger.info(f"Created {relationships_created} dependency relationships")
            return relationships_created

        except Exception as e:
            logger.error(f"Failed to analyze dependencies: {e}")
            return 0

    def get_dependency_metrics(self) -> dict[str, any]:
        """Get metrics about the dependency structure.

        Returns:
            Dictionary with dependency metrics
        """
        try:
            metrics = {}

            # Count total dependencies
            dep_count_query = """
            MATCH (a:CodeFile)-[:DEPENDS_ON]->(b:CodeFile)
            RETURN count(*) as total_dependencies
            """
            result = self.client.execute_query(dep_count_query)
            metrics["total_dependencies"] = (
                result[0]["total_dependencies"] if result else 0
            )

            # Get files with highest in-degree (most depended upon)
            high_in_degree_query = """
            MATCH (f:CodeFile)
            OPTIONAL MATCH (dependent:CodeFile)-[:DEPENDS_ON]->(f)
            WITH f, count(dependent) as in_degree
            WHERE in_degree > 0
            RETURN f.path as file_path, in_degree
            ORDER BY in_degree DESC
            LIMIT 10
            """
            result = self.client.execute_query(high_in_degree_query)
            metrics["most_depended_upon"] = result

            # Get files with highest out-degree (most dependencies)
            high_out_degree_query = """
            MATCH (f:CodeFile)
            OPTIONAL MATCH (f)-[:DEPENDS_ON]->(dependency:CodeFile)
            WITH f, count(dependency) as out_degree
            WHERE out_degree > 0
            RETURN f.path as file_path, out_degree
            ORDER BY out_degree DESC
            LIMIT 10
            """
            result = self.client.execute_query(high_out_degree_query)
            metrics["most_dependencies"] = result

            # Detect circular dependencies
            circular_deps = self._detect_circular_dependencies()
            metrics["circular_dependencies"] = circular_deps

            return metrics

        except Exception as e:
            logger.error(f"Failed to get dependency metrics: {e}")
            return {}

    def _get_file_imports(self) -> dict[str, list[dict[str, str]]]:
        """Get all imports for each CodeFile.

        Returns:
            Dictionary mapping file paths to their imports
        """
        query = """
        MATCH (f:CodeFile)-[:IMPORTS]->(i:Import)
        RETURN f.path as file_path,
               i.module as module,
               i.name as name
        ORDER BY f.path, i.module, i.name
        """

        result = self.client.execute_query(query)

        file_imports = {}
        for row in result:
            file_path = row["file_path"]
            if file_path not in file_imports:
                file_imports[file_path] = []

            file_imports[file_path].append(
                {"module": row["module"], "name": row["name"]}
            )

        return file_imports

    def _create_module_mapping(self) -> dict[str, str]:
        """Create a mapping from module names to CodeFile paths.

        Returns:
            Dictionary mapping module names to file paths
        """
        # Get all CodeFile paths
        query = """
        MATCH (f:CodeFile)
        RETURN f.path as file_path
        """

        result = self.client.execute_query(query)

        module_mapping = {}
        for row in result:
            file_path = row["file_path"]

            # Convert file path to potential module names
            path_obj = Path(file_path)

            # Remove src/ prefix and .py suffix, convert to module notation
            if file_path.startswith("src/"):
                module_path = file_path[4:]  # Remove 'src/'
            else:
                module_path = file_path

            if module_path.endswith(".py"):
                module_path = module_path[:-3]  # Remove '.py'

            # Convert path separators to dots
            module_name = module_path.replace("/", ".")
            module_mapping[module_name] = file_path

            # Also map the filename without path
            filename = path_obj.stem
            if filename not in module_mapping:
                module_mapping[filename] = file_path

            # Map the full path as well
            module_mapping[file_path] = file_path

        return module_mapping

    def _analyze_dependencies(
        self,
        file_imports: dict[str, list[dict[str, str]]],
        module_mapping: dict[str, str],
    ) -> list[DependencyRelationship]:
        """Analyze imports and determine file-to-file dependencies.

        Args:
            file_imports: Dictionary of file imports
            module_mapping: Mapping of module names to file paths

        Returns:
            List of dependency relationships
        """
        dependencies = []

        for source_file, imports in file_imports.items():
            for import_info in imports:
                module = import_info["module"]
                name = import_info["name"]

                # Try to find the target file for this import
                target_file = None

                # Focus on internal project imports (those that might map to our CodeFiles)
                # Skip standard library and external imports
                if module in [
                    "datetime",
                    "typing",
                    "pathlib",
                    "logging",
                    "json",
                    "ast",
                    "re",
                    "os",
                    "sys",
                ]:
                    continue

                # Try different variations of the module name for internal imports
                potential_modules = [
                    module,
                    f"src.{module}",
                    f"src/{module.replace('.', '/')}",
                    module.replace(".", "/"),
                    f"src/ignition/{module.replace('.', '/')}",
                    f"src/ignition/code_intelligence/{module}",
                ]

                # Also try treating the module as a file name
                if "." not in module:
                    potential_modules.extend(
                        [
                            f"src/ignition/code_intelligence/{module}.py",
                            f"src/core/{module}.py",
                            f"src/{module}.py",
                        ]
                    )

                for potential_module in potential_modules:
                    if potential_module in module_mapping:
                        target_file = module_mapping[potential_module]
                        break

                # If we found a target file and it's different from source
                if target_file and target_file != source_file:
                    # Calculate relationship strength (simple: 1.0 for now)
                    strength = 1.0

                    # Check if we already have this relationship
                    existing = next(
                        (
                            d
                            for d in dependencies
                            if d.source_file == source_file
                            and d.target_file == target_file
                        ),
                        None,
                    )

                    if existing:
                        # Add to existing relationship
                        existing.import_details.append(
                            f"{module}.{name}" if name else module
                        )
                        existing.strength = min(
                            existing.strength + 0.1, 1.0
                        )  # Increase strength
                    else:
                        # Create new relationship
                        dependency = DependencyRelationship(
                            source_file=source_file,
                            target_file=target_file,
                            relationship_type="imports",
                            strength=strength,
                            import_details=[f"{module}.{name}" if name else module],
                        )
                        dependencies.append(dependency)

        return dependencies

    def _create_dependency_relationships(
        self, dependencies: list[DependencyRelationship]
    ) -> int:
        """Create DEPENDS_ON relationships in the graph.

        Args:
            dependencies: List of dependency relationships to create

        Returns:
            Number of relationships created
        """
        if not dependencies:
            return 0

        # First, remove existing DEPENDS_ON relationships to avoid duplicates
        cleanup_query = """
        MATCH (a:CodeFile)-[r:DEPENDS_ON]->(b:CodeFile)
        DELETE r
        """
        self.client.execute_query(cleanup_query)

        # Create new relationships
        created_count = 0
        for dependency in dependencies:
            try:
                create_query = """
                MATCH (source:CodeFile {path: $source_path})
                MATCH (target:CodeFile {path: $target_path})
                CREATE (source)-[:DEPENDS_ON {
                    relationship_type: $rel_type,
                    strength: $strength,
                    import_details: $import_details,
                    created_at: datetime()
                }]->(target)
                """

                self.client.execute_query(
                    create_query,
                    {
                        "source_path": dependency.source_file,
                        "target_path": dependency.target_file,
                        "rel_type": dependency.relationship_type,
                        "strength": dependency.strength,
                        "import_details": dependency.import_details,
                    },
                )

                created_count += 1

            except Exception as e:
                logger.warning(
                    f"Failed to create dependency {dependency.source_file} -> {dependency.target_file}: {e}"
                )

        return created_count

    def _detect_circular_dependencies(self) -> list[list[str]]:
        """Detect circular dependencies in the codebase.

        Returns:
            List of circular dependency chains
        """
        try:
            # Find cycles using Neo4j's path finding
            cycle_query = """
            MATCH path = (start:CodeFile)-[:DEPENDS_ON*2..10]->(start)
            WHERE length(path) >= 2
            RETURN [node in nodes(path) | node.path] as cycle_path
            LIMIT 10
            """

            result = self.client.execute_query(cycle_query)
            cycles = [row["cycle_path"] for row in result]

            # Remove duplicates (same cycle in different order)
            unique_cycles = []
            for cycle in cycles:
                # Normalize cycle by starting with the lexicographically smallest file
                min_index = cycle.index(min(cycle))
                normalized_cycle = cycle[min_index:] + cycle[:min_index]

                if normalized_cycle not in unique_cycles:
                    unique_cycles.append(normalized_cycle)

            return unique_cycles

        except Exception as e:
            logger.error(f"Failed to detect circular dependencies: {e}")
            return []

    def refresh_dependencies(self) -> bool:
        """Refresh all dependency relationships.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Refreshing dependency relationships...")

            # Analyze and create dependencies
            relationships_created = self.analyze_and_create_dependencies()

            logger.info(
                f"Dependency refresh complete. Created {relationships_created} relationships."
            )
            return True

        except Exception as e:
            logger.error(f"Failed to refresh dependencies: {e}")
            return False
