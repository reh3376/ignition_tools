#!/usr/bin/env python3
"""
Import IGN Scripts Codebase to Neo4j Knowledge Graph

Following crawl_mcp.py methodology for systematic codebase import:
1. Environment validation first
2. Input validation and sanitization  
3. Comprehensive error handling
4. Modular testing integration
5. Progressive complexity
6. Resource management

Based on: docs/crawl test/knowledge_graph/parse_repo_into_neo4j.py
"""

import asyncio
import ast
import logging
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class LocalCodebaseImporter:
    """Import local codebase to Neo4j following crawl_mcp.py methodology."""

    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        """Initialize with Neo4j credentials."""
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None
        
        # External modules to ignore (from DirectNeo4jExtractor)
        self.external_modules = {
            "asyncio", "json", "os", "sys", "pathlib", "typing", "dataclasses",
            "datetime", "enum", "logging", "re", "collections", "itertools",
            "functools", "operator", "copy", "pickle", "sqlite3", "csv",
            "xml", "html", "http", "urllib", "socket", "threading", "multiprocessing",
            "subprocess", "shutil", "tempfile", "glob", "fnmatch", "linecache",
            "pprint", "textwrap", "string", "io", "base64", "binascii", "struct",
            "codecs", "unicodedata", "locale", "gettext", "calendar", "time",
            "zoneinfo", "math", "cmath", "decimal", "fractions", "random",
            "statistics", "hashlib", "hmac", "secrets", "uuid", "ipaddress",
            "argparse", "configparser", "fileinput", "platform", "ctypes",
            "mmap", "winreg", "msvcrt", "posix", "pwd", "grp", "termios",
            "tty", "pty", "fcntl", "resource", "syslog", "signal", "msilib",
            "winsound", "tkinter", "turtle", "email", "mailbox", "mimetypes",
            "quopri", "uu", "encodings", "locale", "gettext", "doctest",
            "unittest", "test", "pdb", "profile", "pstats", "timeit", "trace",
            "gc", "inspect", "site", "fpectl", "distutils", "ensurepip",
            "venv", "zipapp", "ast", "symtable", "token", "keyword", "tokenize",
            "tabnanny", "pyclbr", "py_compile", "compileall", "dis", "pickletools",
            "warnings", "contextlib", "abc", "atexit", "traceback", "future_builtins",
            "importlib", "imp", "zipimport", "pkgutil", "modulefinder", "runpy",
            "parser", "weakref", "types", "builtins", "__future__", "__main__"
        }

    async def validate_environment(self) -> bool:
        """Step 1: Environment validation (crawl_mcp.py methodology)."""
        try:
            logger.info("🔍 Validating environment...")
            
            # Check Neo4j connection
            if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
                logger.error("❌ Neo4j credentials not configured")
                return False
            
            # Test Neo4j connection
            try:
                self.driver = AsyncGraphDatabase.driver(
                    self.neo4j_uri, 
                    auth=(self.neo4j_user, self.neo4j_password)
                )
                async with self.driver.session() as session:
                    await session.run("RETURN 1")
                logger.info("✅ Neo4j connection successful")
            except Exception as e:
                logger.error(f"❌ Neo4j connection failed: {e}")
                return False
            
            # Check project root exists
            if not project_root.exists():
                logger.error(f"❌ Project root not found: {project_root}")
                return False
            
            logger.info(f"✅ Project root validated: {project_root}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            return False

    def validate_inputs(self, repo_path: Path) -> dict[str, Any]:
        """Step 2: Input validation and sanitization (crawl_mcp.py methodology)."""
        try:
            logger.info("🔍 Validating inputs...")
            
            if not repo_path.exists():
                raise ValueError(f"Repository path does not exist: {repo_path}")
            
            if not repo_path.is_dir():
                raise ValueError(f"Repository path is not a directory: {repo_path}")
            
            # Get Python files
            python_files = list(repo_path.rglob("*.py"))
            if not python_files:
                raise ValueError(f"No Python files found in: {repo_path}")
            
            # Filter out common non-source directories
            excluded_dirs = {
                "__pycache__", ".git", ".pytest_cache", "node_modules", 
                ".venv", "venv", "env", ".env", "build", "dist", ".tox"
            }
            
            filtered_files = []
            for file_path in python_files:
                # Check if any parent directory is in excluded_dirs
                if not any(part in excluded_dirs for part in file_path.parts):
                    filtered_files.append(file_path)
            
            logger.info(f"✅ Found {len(filtered_files)} Python files to analyze")
            
            return {
                "repo_path": repo_path,
                "python_files": filtered_files,
                "repo_name": repo_path.name,
                "total_files": len(filtered_files)
            }
            
        except Exception as e:
            logger.error(f"❌ Input validation failed: {e}")
            raise

    async def analyze_repository(self, repo_path: Path) -> bool:
        """Step 3: Main analysis with comprehensive error handling."""
        try:
            # Step 1: Environment validation
            if not await self.validate_environment():
                return False
            
            # Step 2: Input validation
            validated_inputs = self.validate_inputs(repo_path)
            repo_name = validated_inputs["repo_name"]
            python_files = validated_inputs["python_files"]
            
            logger.info(f"🚀 Starting analysis of repository: {repo_name}")
            
            # Step 3: Clear existing repository data
            await self._clear_repository_data(repo_name)
            
            # Step 4: Identify project modules
            logger.info("🔍 Identifying project modules...")
            project_modules = set()
            for file_path in python_files:
                relative_path = str(file_path.relative_to(repo_path))
                module_parts = relative_path.replace("/", ".").replace(".py", "").split(".")
                if len(module_parts) > 0 and not module_parts[0].startswith("."):
                    project_modules.add(module_parts[0])
            
            logger.info(f"✅ Identified project modules: {sorted(project_modules)}")
            
            # Step 5: Analyze files progressively
            logger.info("📊 Analyzing Python files...")
            modules_data = []
            for i, file_path in enumerate(python_files):
                if i % 20 == 0:
                    logger.info(f"📝 Analyzing file {i + 1}/{len(python_files)}: {file_path.name}")
                
                try:
                    analysis = self._analyze_python_file(file_path, repo_path, project_modules)
                    if analysis:
                        modules_data.append(analysis)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to analyze {file_path}: {e}")
                    continue
            
            logger.info(f"✅ Analyzed {len(modules_data)} files successfully")
            
            # Step 6: Create graph with resource management
            logger.info("🔗 Creating Neo4j graph...")
            await self._create_graph(repo_name, modules_data)
            
            # Step 7: Print summary
            total_classes = sum(len(mod["classes"]) for mod in modules_data)
            total_methods = sum(len(cls["methods"]) for mod in modules_data for cls in mod["classes"])
            total_functions = sum(len(mod["functions"]) for mod in modules_data)
            total_imports = sum(len(mod["imports"]) for mod in modules_data)
            
            logger.info("🎉 Repository import completed successfully!")
            print(f"\n=== IGN Scripts Codebase Import Summary ===")
            print(f"Repository: {repo_name}")
            print(f"Files processed: {len(modules_data)}")
            print(f"Classes created: {total_classes}")
            print(f"Methods created: {total_methods}")
            print(f"Functions created: {total_functions}")
            print(f"Import relationships: {total_imports}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Repository analysis failed: {e}")
            return False

    async def _clear_repository_data(self, repo_name: str):
        """Clear existing repository data with proper error handling."""
        logger.info(f"🧹 Clearing existing data for repository: {repo_name}")
        
        try:
            async with self.driver.session() as session:
                # Delete in specific order to avoid constraint issues
                queries = [
                    # Delete methods and attributes
                    """
                    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)-[:HAS_METHOD]->(m:Method)
                    DETACH DELETE m
                    """,
                    """
                    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)-[:HAS_ATTRIBUTE]->(a:Attribute)
                    DETACH DELETE a
                    """,
                    # Delete functions
                    """
                    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(func:Function)
                    DETACH DELETE func
                    """,
                    # Delete classes
                    """
                    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)-[:DEFINES]->(c:Class)
                    DETACH DELETE c
                    """,
                    # Delete files
                    """
                    MATCH (r:Repository {name: $repo_name})-[:CONTAINS]->(f:File)
                    DETACH DELETE f
                    """,
                    # Delete repository
                    """
                    MATCH (r:Repository {name: $repo_name})
                    DETACH DELETE r
                    """
                ]
                
                for query in queries:
                    await session.run(query, repo_name=repo_name)
                
                logger.info("✅ Repository data cleared successfully")
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to clear repository data: {e}")

    def _analyze_python_file(self, file_path: Path, repo_root: Path, project_modules: set[str]) -> dict[str, Any] | None:
        """Analyze Python file for structure extraction."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = str(file_path.relative_to(repo_root))
            module_name = self._get_importable_module_name(file_path, repo_root, relative_path)
            
            # Extract structure
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Extract class with methods and attributes
                    methods = []
                    attributes = []
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Extract method parameters
                            params = self._extract_function_parameters(item)
                            methods.append({
                                "name": item.name,
                                "params": params,
                                "return_type": self._get_name(item.returns) if item.returns else "Any",
                                "args": [arg.arg for arg in item.args.args]
                            })
                        elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            # Type annotated attributes
                            if not item.target.id.startswith("_"):
                                attributes.append({
                                    "name": item.target.id,
                                    "type": self._get_name(item.annotation) if item.annotation else "Any"
                                })
                    
                    classes.append({
                        "name": node.name,
                        "full_name": f"{module_name}.{node.name}",
                        "methods": methods,
                        "attributes": attributes
                    })
                
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    # Top-level function
                    params = self._extract_function_parameters(node)
                    functions.append({
                        "name": node.name,
                        "full_name": f"{module_name}.{node.name}",
                        "params": params,
                        "return_type": self._get_name(node.returns) if node.returns else "Any",
                        "args": [arg.arg for arg in node.args.args]
                    })
                
                elif isinstance(node, ast.Import | ast.ImportFrom):
                    # Track internal imports only
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if self._is_likely_internal(alias.name, project_modules):
                                imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        if node.module.startswith(".") or self._is_likely_internal(node.module, project_modules):
                            imports.append(node.module)
            
            return {
                "module_name": module_name,
                "file_path": relative_path,
                "classes": classes,
                "functions": functions,
                "imports": list(set(imports)),  # Remove duplicates
                "line_count": len(content.splitlines())
            }
            
        except Exception as e:
            logger.warning(f"Could not analyze {file_path}: {e}")
            return None

    def _get_importable_module_name(self, file_path: Path, repo_root: Path, relative_path: str) -> str:
        """Determine the actual importable module name for a Python file."""
        # Convert file path to module path
        default_module = relative_path.replace("/", ".").replace("\\", ".").replace(".py", "")
        
        # Look for common package indicators
        path_parts = Path(relative_path).parts
        package_roots = []
        
        # Check each directory level for __init__.py
        current_path = repo_root
        for i, part in enumerate(path_parts[:-1]):
            current_path = current_path / part
            if (current_path / "__init__.py").exists():
                package_roots.append(i)
        
        if package_roots:
            # Use the first package as the root
            package_start = package_roots[0]
            module_parts = path_parts[package_start:]
            module_name = ".".join(module_parts).replace(".py", "")
            return module_name
        
        # Skip common non-package directories
        skip_dirs = {"src", "lib", "source", "python", "pkg", "packages"}
        filtered_parts = []
        for part in path_parts:
            if part.lower() not in skip_dirs or filtered_parts:
                filtered_parts.append(part)
        
        if filtered_parts:
            module_name = ".".join(filtered_parts).replace(".py", "")
            return module_name
        
        return default_module

    def _extract_function_parameters(self, func_node):
        """Extract function parameters with type information."""
        params = []
        for arg in func_node.args.args:
            param_info = {
                "name": arg.arg,
                "type": self._get_name(arg.annotation) if arg.annotation else "Any"
            }
            params.append(param_info)
        return params

    def _get_name(self, node):
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return "Any"

    def _is_likely_internal(self, import_name: str, project_modules: set[str]) -> bool:
        """Check if import is likely internal to the project."""
        if not import_name:
            return False
        
        # Check if it's in external modules
        if import_name.split(".")[0] in self.external_modules:
            return False
        
        # Check if it starts with project modules
        for module in project_modules:
            if import_name.startswith(module):
                return True
        
        # Check for relative imports
        if import_name.startswith("."):
            return True
        
        return False

    async def _create_graph(self, repo_name: str, modules_data: list[dict]):
        """Create all nodes and relationships in Neo4j."""
        async with self.driver.session() as session:
            # Create Repository node
            await session.run(
                "CREATE (r:Repository {name: $repo_name, created_at: datetime()})",
                repo_name=repo_name
            )
            
            nodes_created = 0
            relationships_created = 0
            
            for i, mod in enumerate(modules_data):
                # 1. Create File node
                await session.run(
                    """
                    CREATE (f:File {
                        name: $name,
                        path: $path,
                        module_name: $module_name,
                        line_count: $line_count,
                        created_at: datetime()
                    })
                    """,
                    name=mod["file_path"].split("/")[-1],
                    path=mod["file_path"],
                    module_name=mod["module_name"],
                    line_count=mod["line_count"]
                )
                nodes_created += 1
                
                # 2. Connect File to Repository
                await session.run(
                    """
                    MATCH (r:Repository {name: $repo_name})
                    MATCH (f:File {path: $file_path})
                    CREATE (r)-[:CONTAINS]->(f)
                    """,
                    repo_name=repo_name,
                    file_path=mod["file_path"]
                )
                relationships_created += 1
                
                # 3. Create Class nodes
                for cls in mod["classes"]:
                    await session.run(
                        """
                        CREATE (c:Class {
                            name: $name,
                            full_name: $full_name,
                            created_at: datetime()
                        })
                        """,
                        name=cls["name"],
                        full_name=cls["full_name"]
                    )
                    nodes_created += 1
                    
                    # Connect File to Class
                    await session.run(
                        """
                        MATCH (f:File {path: $file_path})
                        MATCH (c:Class {full_name: $class_full_name})
                        CREATE (f)-[:DEFINES]->(c)
                        """,
                        file_path=mod["file_path"],
                        class_full_name=cls["full_name"]
                    )
                    relationships_created += 1
                    
                    # 4. Create Method nodes
                    for method in cls["methods"]:
                        method_id = f"{cls['full_name']}::{method['name']}"
                        await session.run(
                            """
                            CREATE (m:Method {
                                name: $name,
                                method_id: $method_id,
                                full_name: $full_name,
                                args: $args,
                                return_type: $return_type,
                                created_at: datetime()
                            })
                            """,
                            name=method["name"],
                            method_id=method_id,
                            full_name=f"{cls['full_name']}.{method['name']}",
                            args=method["args"],
                            return_type=method["return_type"]
                        )
                        nodes_created += 1
                        
                        # Connect Class to Method
                        await session.run(
                            """
                            MATCH (c:Class {full_name: $class_full_name})
                            MATCH (m:Method {method_id: $method_id})
                            CREATE (c)-[:HAS_METHOD]->(m)
                            """,
                            class_full_name=cls["full_name"],
                            method_id=method_id
                        )
                        relationships_created += 1
                    
                    # 5. Create Attribute nodes
                    for attr in cls["attributes"]:
                        attr_id = f"{cls['full_name']}::{attr['name']}"
                        await session.run(
                            """
                            CREATE (a:Attribute {
                                name: $name,
                                attr_id: $attr_id,
                                full_name: $full_name,
                                type: $type,
                                created_at: datetime()
                            })
                            """,
                            name=attr["name"],
                            attr_id=attr_id,
                            full_name=f"{cls['full_name']}.{attr['name']}",
                            type=attr["type"]
                        )
                        nodes_created += 1
                        
                        # Connect Class to Attribute
                        await session.run(
                            """
                            MATCH (c:Class {full_name: $class_full_name})
                            MATCH (a:Attribute {attr_id: $attr_id})
                            CREATE (c)-[:HAS_ATTRIBUTE]->(a)
                            """,
                            class_full_name=cls["full_name"],
                            attr_id=attr_id
                        )
                        relationships_created += 1
                
                # 6. Create Function nodes (top-level)
                for func in mod["functions"]:
                    func_id = f"{mod['file_path']}::{func['name']}"
                    await session.run(
                        """
                        CREATE (f:Function {
                            name: $name,
                            func_id: $func_id,
                            full_name: $full_name,
                            args: $args,
                            return_type: $return_type,
                            created_at: datetime()
                        })
                        """,
                        name=func["name"],
                        func_id=func_id,
                        full_name=func["full_name"],
                        args=func["args"],
                        return_type=func["return_type"]
                    )
                    nodes_created += 1
                    
                    # Connect File to Function
                    await session.run(
                        """
                        MATCH (file:File {path: $file_path})
                        MATCH (func:Function {func_id: $func_id})
                        CREATE (file)-[:DEFINES]->(func)
                        """,
                        file_path=mod["file_path"],
                        func_id=func_id
                    )
                    relationships_created += 1
                
                # 7. Create Import relationships
                for import_name in mod["imports"]:
                    await session.run(
                        """
                        MATCH (source:File {path: $source_path})
                        OPTIONAL MATCH (target:File)
                        WHERE target.module_name = $import_name OR target.module_name STARTS WITH $import_name
                        WITH source, target
                        WHERE target IS NOT NULL
                        MERGE (source)-[:IMPORTS]->(target)
                        """,
                        source_path=mod["file_path"],
                        import_name=import_name
                    )
                    relationships_created += 1
                
                if (i + 1) % 10 == 0:
                    logger.info(f"📝 Processed {i + 1}/{len(modules_data)} files...")
            
            logger.info(f"✅ Created {nodes_created} nodes and {relationships_created} relationships")

    async def close(self):
        """Step 6: Resource management and cleanup."""
        if self.driver:
            await self.driver.close()
            logger.info("✅ Neo4j connection closed")


async def main():
    """Main function following crawl_mcp.py methodology."""
    # Step 1: Environment validation
    load_dotenv()
    
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "ignition-graph")
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        logger.error("❌ Neo4j environment variables not configured")
        logger.info("💡 Required: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
        return False
    
    # Step 2: Initialize importer
    importer = LocalCodebaseImporter(neo4j_uri, neo4j_user, neo4j_password)
    
    try:
        # Step 3: Import current codebase
        repo_path = project_root
        logger.info(f"🚀 Starting IGN Scripts codebase import from: {repo_path}")
        
        success = await importer.analyze_repository(repo_path)
        
        if success:
            logger.info("🎉 Codebase import completed successfully!")
            return True
        else:
            logger.error("❌ Codebase import failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    finally:
        # Step 6: Resource cleanup
        await importer.close()


if __name__ == "__main__":
    asyncio.run(main()) 