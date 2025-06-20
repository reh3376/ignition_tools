"""Repository Analyzer for Pydantic AI.

This module provides comprehensive analysis of the Pydantic AI repository,
parsing its structure, dependencies, and code to create a detailed graph
representation for LLM agent context.
"""

import ast
import hashlib
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from sentence_transformers import SentenceTransformer

from .repository_schema import (
    RepositorySchema,
)

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Analyzes repositories and creates graph representations."""

    def __init__(self, graph_client, embedder: SentenceTransformer | None = None):
        """Initialize the repository analyzer."""
        self.client = graph_client
        self.embedder = embedder or SentenceTransformer("all-MiniLM-L6-v2")
        self.schema = RepositorySchema(graph_client)

        # Initialize schema
        self.schema.create_repository_schema()

    def analyze_repository(self, repo_url: str, branch: str = "main") -> bool:
        """Analyze a repository and store results in Neo4j."""
        try:
            logger.info(f"Starting analysis of repository: {repo_url}")

            # Clone repository
            repo_path = self._clone_repository(repo_url, branch)
            if not repo_path:
                return False

            try:
                # Get repository metadata
                repo_info = self._get_repository_info(repo_url, repo_path)
                repo_info["local_path"] = repo_path

                # Create repository node
                self._create_repository_node(repo_info)

                # Analyze directory structure
                self._analyze_directory_structure(repo_path, repo_info["name"])

                # Analyze Python files
                self._analyze_python_files(repo_path, repo_info["name"])

                # Analyze dependencies
                self._analyze_dependencies(repo_path, repo_info["name"])

                # Analyze Pydantic AI specific components
                self._analyze_pydantic_ai_components(repo_path, repo_info["name"])

                logger.info(f"Repository analysis completed: {repo_url}")
                return True

            finally:
                # Clean up cloned repository
                self._cleanup_repository(repo_path)

        except Exception as e:
            logger.error(f"Failed to analyze repository {repo_url}: {e}")
            return False

    def _clone_repository(self, repo_url: str, branch: str) -> Path | None:
        """Clone repository to temporary directory."""
        try:
            temp_dir = tempfile.mkdtemp(prefix="repo_analysis_")
            repo_path = Path(temp_dir) / "repository"

            cmd = [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                branch,
                repo_url,
                str(repo_path),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                logger.info(f"Repository cloned to: {repo_path}")
                return repo_path
            else:
                logger.error(f"Failed to clone repository: {result.stderr}")
                return None

        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return None

    def _get_repository_info(self, repo_url: str, repo_path: Path) -> dict[str, Any]:
        """Extract repository metadata."""
        # Parse GitHub URL for API call
        if "github.com" in repo_url:
            parts = repo_url.replace("https://github.com/", "").replace(".git", "").split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]

                try:
                    # Get GitHub API data
                    api_url = f"https://api.github.com/repos/{owner}/{repo}"
                    response = requests.get(api_url, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        return {
                            "name": data.get("name", repo),
                            "url": repo_url,
                            "description": data.get("description", ""),
                            "language": data.get("language", "Python"),
                            "stars": data.get("stargazers_count", 0),
                            "forks": data.get("forks_count", 0),
                            "size_kb": data.get("size", 0),
                            "created_at": datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                            "updated_at": datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                            "license": (data.get("license", {}).get("name") if data.get("license") else None),
                            "topics": data.get("topics", []),
                        }
                except Exception as e:
                    logger.warning(f"Failed to get GitHub API data: {e}")

        # Fallback to basic info
        return {
            "name": repo_url.split("/")[-1].replace(".git", ""),
            "url": repo_url,
            "description": "Repository analysis",
            "language": "Python",
            "stars": 0,
            "forks": 0,
            "size_kb": 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "license": None,
            "topics": [],
        }

    def _create_repository_node(self, repo_info: dict[str, Any]) -> None:
        """Create repository node in Neo4j."""
        # Get README content
        readme_content = None
        readme_files = ["README.md", "README.rst", "README.txt", "readme.md"]

        for readme_file in readme_files:
            readme_path = repo_info.get("local_path", Path()) / readme_file
            if readme_path.exists():
                try:
                    readme_content = readme_path.read_text(encoding="utf-8")[:5000]  # Limit size
                    break
                except Exception:
                    continue

        # Create embedding
        embedding = None
        if readme_content:
            embedding = self.embedder.encode(readme_content).tolist()

        # Create repository node
        cypher = """
        MERGE (r:Repository {url: $url})
        SET r.name = $name,
            r.description = $description,
            r.language = $language,
            r.stars = $stars,
            r.forks = $forks,
            r.size_kb = $size_kb,
            r.created_at = datetime($created_at),
            r.updated_at = datetime($updated_at),
            r.license = $license,
            r.topics = $topics,
            r.readme_content = $readme_content,
            r.embedding = $embedding
        """

        self.client.execute_query(
            cypher,
            {
                "url": repo_info["url"],
                "name": repo_info["name"],
                "description": repo_info["description"],
                "language": repo_info["language"],
                "stars": repo_info["stars"],
                "forks": repo_info["forks"],
                "size_kb": repo_info["size_kb"],
                "created_at": repo_info["created_at"].isoformat(),
                "updated_at": repo_info["updated_at"].isoformat(),
                "license": repo_info["license"],
                "topics": repo_info["topics"],
                "readme_content": readme_content,
                "embedding": embedding,
            },
        )

    def _analyze_directory_structure(self, repo_path: Path, repo_name: str) -> None:
        """Analyze and store directory structure."""
        for root, dirs, files in os.walk(repo_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(repo_path)

            # Skip hidden directories and common ignore patterns
            if any(part.startswith(".") for part in relative_path.parts):
                continue
            if any(ignore in str(relative_path) for ignore in ["__pycache__", ".git", "node_modules"]):
                continue

            # Count files and subdirectories
            file_count = len([f for f in files if not f.startswith(".")])
            subdirs = [d for d in dirs if not d.startswith(".")]

            # Calculate total lines
            total_lines = 0
            for file in files:
                if file.endswith((".py", ".md", ".txt", ".yml", ".yaml", ".toml")):
                    try:
                        file_path = root_path / file
                        with open(file_path, encoding="utf-8") as f:
                            total_lines += len(f.readlines())
                    except Exception:
                        continue

            # Create directory node
            self._create_directory_node(
                name=relative_path.name or repo_name,
                path=str(relative_path),
                repository=repo_name,
                file_count=file_count,
                subdirectory_count=len(subdirs),
                total_lines=total_lines,
                root_path=root_path,
            )

    def _create_directory_node(
        self,
        name: str,
        path: str,
        repository: str,
        file_count: int,
        subdirectory_count: int,
        total_lines: int,
        root_path: Path,
    ) -> None:
        """Create directory node in Neo4j."""
        # Check for README in directory
        readme_content = None
        for readme_file in ["README.md", "README.rst", "index.md"]:
            readme_path = root_path / readme_file
            if readme_path.exists():
                try:
                    readme_content = readme_path.read_text(encoding="utf-8")[:2000]
                    break
                except Exception:
                    continue

        # Create embedding
        embedding = None
        if readme_content:
            embedding = self.embedder.encode(readme_content).tolist()

        cypher = """
        MERGE (d:Directory {path: $path, repository: $repository})
        SET d.name = $name,
            d.file_count = $file_count,
            d.subdirectory_count = $subdirectory_count,
            d.total_lines = $total_lines,
            d.readme_content = $readme_content,
            d.embedding = $embedding
        """

        self.client.execute_query(
            cypher,
            {
                "name": name,
                "path": path,
                "repository": repository,
                "file_count": file_count,
                "subdirectory_count": subdirectory_count,
                "total_lines": total_lines,
                "readme_content": readme_content,
                "embedding": embedding,
            },
        )

        # Create relationship to repository
        if path != "":  # Not root directory
            cypher_rel = """
            MATCH (r:Repository {name: $repository})
            MATCH (d:Directory {path: $path, repository: $repository})
            MERGE (r)-[:CONTAINS]->(d)
            """
            self.client.execute_query(
                cypher_rel,
                {
                    "repository": repository,
                    "path": path,
                },
            )

    def _analyze_python_files(self, repo_path: Path, repo_name: str) -> None:
        """Analyze Python files and extract code structure."""
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and ignored directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", ".git"]]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(repo_path)

                    try:
                        self._analyze_python_file(file_path, relative_path, repo_name)
                    except Exception as e:
                        logger.warning(f"Failed to analyze {relative_path}: {e}")

    def _analyze_python_file(self, file_path: Path, relative_path: Path, repo_name: str) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Calculate basic metrics
            lines = len(content.splitlines())
            size_bytes = len(content.encode("utf-8"))
            content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

            # Determine file type
            file_type = self._determine_file_type(relative_path, content)

            # Extract docstring
            docstring = ast.get_docstring(tree)

            # Create file node
            self._create_file_node(
                name=file_path.name,
                path=str(relative_path),
                repository=repo_name,
                directory=str(relative_path.parent),
                extension=file_path.suffix,
                size_bytes=size_bytes,
                lines=lines,
                language="python",
                file_type=file_type,
                content_hash=content_hash,
                docstring=docstring,
                content=content,
            )

            # Analyze classes and functions
            self._analyze_ast_nodes(tree, str(relative_path), repo_name)

        except Exception as e:
            logger.error(f"Failed to analyze Python file {relative_path}: {e}")

    def _determine_file_type(self, path: Path, content: str) -> str:
        """Determine the type of Python file."""
        path_str = str(path).lower()

        if "test" in path_str or path_str.startswith("tests/"):
            return "test"
        elif path_str.endswith("example.py") or "example" in path_str:
            return "example"
        elif path_str.endswith("config.py") or "config" in path_str:
            return "config"
        elif "__init__.py" in path_str:
            return "package_init"
        elif "setup.py" in path_str or "conftest.py" in path_str:
            return "config"
        else:
            return "source"

    def _create_file_node(
        self,
        name: str,
        path: str,
        repository: str,
        directory: str,
        extension: str,
        size_bytes: int,
        lines: int,
        language: str,
        file_type: str,
        content_hash: str,
        docstring: str | None,
        content: str,
    ) -> None:
        """Create file node in Neo4j."""
        # Create embedding from docstring or first few lines
        text_for_embedding = docstring or content[:1000]
        embedding = self.embedder.encode(text_for_embedding).tolist() if text_for_embedding else None

        cypher = """
        MERGE (f:File {path: $path, repository: $repository})
        SET f.name = $name,
            f.directory = $directory,
            f.extension = $extension,
            f.size_bytes = $size_bytes,
            f.lines = $lines,
            f.language = $language,
            f.file_type = $file_type,
            f.content_hash = $content_hash,
            f.docstring = $docstring,
            f.embedding = $embedding,
            f.last_modified = datetime()
        """

        self.client.execute_query(
            cypher,
            {
                "name": name,
                "path": path,
                "repository": repository,
                "directory": directory,
                "extension": extension,
                "size_bytes": size_bytes,
                "lines": lines,
                "language": language,
                "file_type": file_type,
                "content_hash": content_hash,
                "docstring": docstring,
                "embedding": embedding,
            },
        )

    def _analyze_ast_nodes(self, tree: ast.AST, file_path: str, repo_name: str) -> None:
        """Analyze AST nodes to extract classes and functions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._create_class_node(node, file_path, repo_name)
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                self._create_function_node(node, file_path, repo_name)

    def _create_class_node(self, node: ast.ClassDef, file_path: str, repo_name: str) -> None:
        """Create class node from AST."""
        docstring = ast.get_docstring(node)
        base_classes = [self._get_node_name(base) for base in node.bases]

        # Count methods and properties
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]
        properties = [
            n for n in methods if any(d.id == "property" for d in n.decorator_list if isinstance(d, ast.Name))
        ]

        # Check for decorators
        decorators = [self._get_node_name(d) for d in node.decorator_list]
        is_dataclass = "dataclass" in decorators
        is_pydantic_model = any("BaseModel" in base for base in base_classes)

        # Create embedding
        embedding = self.embedder.encode(docstring).tolist() if docstring else None

        cypher = """
        MERGE (c:Class {name: $name, module: $module, repository: $repository, start_line: $start_line})
        SET c.docstring = $docstring,
            c.end_line = $end_line,
            c.base_classes = $base_classes,
            c.method_count = $method_count,
            c.property_count = $property_count,
            c.is_dataclass = $is_dataclass,
            c.is_pydantic_model = $is_pydantic_model,
            c.decorators = $decorators,
            c.embedding = $embedding
        """

        self.client.execute_query(
            cypher,
            {
                "name": node.name,
                "module": file_path,
                "repository": repo_name,
                "start_line": node.lineno,
                "docstring": docstring,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "base_classes": base_classes,
                "method_count": len(methods),
                "property_count": len(properties),
                "is_dataclass": is_dataclass,
                "is_pydantic_model": is_pydantic_model,
                "decorators": decorators,
                "embedding": embedding,
            },
        )

    def _create_function_node(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: str,
        repo_name: str,
    ) -> None:
        """Create function node from AST."""
        docstring = ast.get_docstring(node)
        parameters = [arg.arg for arg in node.args.args]

        # Get return type annotation
        return_type = self._get_node_name(node.returns) if node.returns else None

        # Check function properties
        is_async = isinstance(node, ast.AsyncFunctionDef)
        is_generator = any(isinstance(n, ast.Yield) for n in ast.walk(node))
        decorators = [self._get_node_name(d) for d in node.decorator_list]
        is_property = "property" in decorators

        # Create function signature
        signature = f"{node.name}({', '.join(parameters)})"
        if return_type:
            signature += f" -> {return_type}"

        # Create embedding
        embedding = self.embedder.encode(docstring).tolist() if docstring else None

        cypher = """
        MERGE (f:Function {name: $name, module: $module, repository: $repository, start_line: $start_line})
        SET f.signature = $signature,
            f.docstring = $docstring,
            f.end_line = $end_line,
            f.parameters = $parameters,
            f.return_type = $return_type,
            f.is_async = $is_async,
            f.is_generator = $is_generator,
            f.is_property = $is_property,
            f.decorators = $decorators,
            f.embedding = $embedding
        """

        self.client.execute_query(
            cypher,
            {
                "name": node.name,
                "module": file_path,
                "repository": repo_name,
                "start_line": node.lineno,
                "signature": signature,
                "docstring": docstring,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "parameters": parameters,
                "return_type": return_type,
                "is_async": is_async,
                "is_generator": is_generator,
                "is_property": is_property,
                "decorators": decorators,
                "embedding": embedding,
            },
        )

    def _get_node_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return "Unknown"

    def _analyze_dependencies(self, repo_path: Path, repo_name: str) -> None:
        """Analyze project dependencies."""
        # Check pyproject.toml
        pyproject_path = repo_path / "pyproject.toml"
        if pyproject_path.exists():
            self._parse_pyproject_dependencies(pyproject_path, repo_name)

        # Check requirements.txt files
        for req_file in repo_path.glob("*requirements*.txt"):
            self._parse_requirements_file(req_file, repo_name)

    def _parse_pyproject_dependencies(self, pyproject_path: Path, repo_name: str) -> None:
        """Parse dependencies from pyproject.toml."""
        try:
            import tomli

            with open(pyproject_path, "rb") as f:
                data = tomli.load(f)

            # Parse different dependency types
            project = data.get("project", {})
            dependencies = project.get("dependencies", [])
            optional_deps = project.get("optional-dependencies", {})

            # Process main dependencies
            for dep in dependencies:
                self._create_dependency_node(dep, repo_name, "runtime", "pyproject.toml")

            # Process optional dependencies
            for group, deps in optional_deps.items():
                for dep in deps:
                    self._create_dependency_node(dep, repo_name, f"optional-{group}", "pyproject.toml")

        except Exception as e:
            logger.warning(f"Failed to parse pyproject.toml: {e}")

    def _parse_requirements_file(self, req_file: Path, repo_name: str) -> None:
        """Parse dependencies from requirements file."""
        try:
            with open(req_file, encoding="utf-8") as f:
                lines = f.readlines()

            dep_type = "dev" if "dev" in req_file.name else "runtime"

            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    self._create_dependency_node(line, repo_name, dep_type, req_file.name)

        except Exception as e:
            logger.warning(f"Failed to parse {req_file}: {e}")

    def _create_dependency_node(self, dep_spec: str, repo_name: str, dep_type: str, source: str) -> None:
        """Create dependency node from dependency specification."""
        # Parse dependency specification
        dep_name = (
            dep_spec.split("==")[0].split(">=")[0].split("<=")[0].split(">")[0].split("<")[0].split("~=")[0].strip()
        )
        version = None

        if "==" in dep_spec:
            version = dep_spec.split("==")[1].strip()

        cypher = """
        MERGE (d:Dependency {name: $name, repository: $repository})
        SET d.version = $version,
            d.dependency_type = $dependency_type,
            d.source = $source
        """

        self.client.execute_query(
            cypher,
            {
                "name": dep_name,
                "repository": repo_name,
                "version": version,
                "dependency_type": dep_type,
                "source": source,
            },
        )

    def _analyze_pydantic_ai_components(self, repo_path: Path, repo_name: str) -> None:
        """Analyze Pydantic AI specific components like agents and tools."""
        # Look for agent definitions
        for py_file in repo_path.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse for Pydantic AI patterns
                tree = ast.parse(content)
                relative_path = py_file.relative_to(repo_path)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check if it's an Agent class
                        if "Agent" in node.name or any("Agent" in self._get_node_name(base) for base in node.bases):
                            self._create_agent_node(node, str(relative_path), repo_name, content)

                    elif isinstance(node, ast.FunctionDef):
                        # Check if it's a tool function (decorated with @tool or similar)
                        decorators = [self._get_node_name(d) for d in node.decorator_list]
                        if any("tool" in dec.lower() for dec in decorators):
                            self._create_tool_node(node, str(relative_path), repo_name)

            except Exception as e:
                logger.warning(f"Failed to analyze Pydantic AI components in {py_file}: {e}")

    def _create_agent_node(self, node: ast.ClassDef, file_path: str, repo_name: str, content: str) -> None:
        """Create agent node for Pydantic AI agents."""
        docstring = ast.get_docstring(node)

        # Extract agent capabilities from docstring and code
        capabilities = []
        model_support = []

        # Simple pattern matching for common AI model providers
        if "openai" in content.lower():
            model_support.append("openai")
        if "anthropic" in content.lower():
            model_support.append("anthropic")
        if "gemini" in content.lower():
            model_support.append("gemini")

        # Determine agent type
        agent_type = "simple"
        if "stream" in node.name.lower() or "streaming" in (docstring or "").lower():
            agent_type = "streaming"
        elif "structured" in node.name.lower():
            agent_type = "structured"

        embedding = self.embedder.encode(docstring).tolist() if docstring else None

        cypher = """
        MERGE (a:Agent {name: $name, module: $module, repository: $repository})
        SET a.agent_type = $agent_type,
            a.model_support = $model_support,
            a.capabilities = $capabilities,
            a.docstring = $docstring,
            a.embedding = $embedding
        """

        self.client.execute_query(
            cypher,
            {
                "name": node.name,
                "module": file_path,
                "repository": repo_name,
                "agent_type": agent_type,
                "model_support": model_support,
                "capabilities": capabilities,
                "docstring": docstring,
                "embedding": embedding,
            },
        )

    def _create_tool_node(self, node: ast.FunctionDef, file_path: str, repo_name: str) -> None:
        """Create tool node for Pydantic AI tools."""
        docstring = ast.get_docstring(node)
        parameters = [arg.arg for arg in node.args.args]
        return_type = self._get_node_name(node.returns) if node.returns else None

        embedding = self.embedder.encode(docstring).tolist() if docstring else None

        cypher = """
        MERGE (t:Tool {name: $name, module: $module, repository: $repository})
        SET t.tool_type = $tool_type,
            t.parameters = $parameters,
            t.return_type = $return_type,
            t.docstring = $docstring,
            t.embedding = $embedding
        """

        self.client.execute_query(
            cypher,
            {
                "name": node.name,
                "module": file_path,
                "repository": repo_name,
                "tool_type": "function",
                "parameters": parameters,
                "return_type": return_type,
                "docstring": docstring,
                "embedding": embedding,
            },
        )

    def _cleanup_repository(self, repo_path: Path) -> None:
        """Clean up cloned repository."""
        try:
            import shutil

            shutil.rmtree(repo_path.parent)
            logger.debug(f"Cleaned up repository: {repo_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup repository: {e}")
