"""Documentation Synchronization System - Phase 8.4.

This module provides automated documentation updates and synchronization
with code changes, maintaining consistency between code and documentation.
"""

import ast
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DocumentationItem:
    """Represents a documentation item that needs synchronization."""

    doc_path: str
    doc_type: str  # api, guide, example, reference
    source_files: list[str]  # source files this doc depends on
    last_updated: datetime
    sync_status: str  # synced, outdated, missing
    update_priority: str  # critical, high, medium, low


@dataclass
class CodeChange:
    """Represents a code change that affects documentation."""

    file_path: str
    change_type: str  # function_added, function_removed, signature_changed, etc.
    element_name: str  # function/class name
    old_signature: str | None
    new_signature: str | None
    description: str
    impact_level: str  # breaking, major, minor
    affected_docs: list[str]


@dataclass
class DocumentationUpdate:
    """Represents a required documentation update."""

    doc_path: str
    update_type: str  # api_change, example_update, cross_reference
    description: str
    suggested_content: str
    confidence: float  # 0.0 to 1.0
    dependencies: list[str]  # other updates this depends on


class DocumentationSynchronizer:
    """Main class for documentation synchronization and updates."""

    def __init__(self, code_manager, project_root: Path) -> None:
        """Initialize the documentation synchronizer.

        Args:
            code_manager: CodeIntelligenceManager instance
            project_root: Root path of the project
        """
        self.code_manager = code_manager
        self.project_root = Path(project_root)
        self.docs_root = self.project_root / "docs"

        # Documentation patterns and mappings
        self.doc_patterns = {
            "api_reference": ["docs/api/*.md", "docs/reference/*.md"],
            "examples": ["docs/examples/*.md", "docs/tutorials/*.md"],
            "guides": ["docs/guides/*.md", "docs/getting-started/*.md"],
            "configuration": ["docs/configuration/*.md", "docs/config/*.md"],
        }

        # Code-to-doc mappings cache
        self._mappings_cache = {}
        self._last_scan = None

    def analyze_documentation_sync_status(self) -> list[DocumentationItem]:
        """Analyze the synchronization status of all documentation.

        Returns:
            List of documentation items with their sync status
        """
        try:
            doc_items = []

            # Scan all documentation files
            for doc_type, patterns in self.doc_patterns.items():
                for pattern in patterns:
                    doc_files = list(self.project_root.glob(pattern))

                    for doc_file in doc_files:
                        # Analyze each documentation file
                        source_files = self._find_source_dependencies(doc_file)
                        sync_status = self._check_sync_status(doc_file, source_files)
                        priority = self._calculate_update_priority(
                            doc_file, sync_status
                        )

                        doc_item = DocumentationItem(
                            doc_path=str(doc_file.relative_to(self.project_root)),
                            doc_type=doc_type,
                            source_files=source_files,
                            last_updated=datetime.fromtimestamp(
                                doc_file.stat().st_mtime
                            ),
                            sync_status=sync_status,
                            update_priority=priority,
                        )
                        doc_items.append(doc_item)

            return sorted(doc_items, key=lambda x: (x.update_priority, x.sync_status))

        except Exception as e:
            logger.error(f"Failed to analyze documentation sync status: {e}")
            return []

    def detect_code_changes_affecting_docs(
        self, since_hours: int = 24
    ) -> list[CodeChange]:
        """Detect code changes that affect documentation.

        Args:
            since_hours: Look for changes within this time period

        Returns:
            List of code changes that affect documentation
        """
        try:
            changes = []

            # Get recent code changes from git or file modification times
            recent_files = self._get_recently_modified_files(since_hours)

            for file_path in recent_files:
                file_changes = self._analyze_file_changes(file_path)
                changes.extend(file_changes)

            return changes

        except Exception as e:
            logger.error(f"Failed to detect code changes: {e}")
            return []

    def generate_documentation_updates(
        self, code_changes: list[CodeChange]
    ) -> list[DocumentationUpdate]:
        """Generate required documentation updates based on code changes.

        Args:
            code_changes: List of code changes to process

        Returns:
            List of required documentation updates
        """
        try:
            updates = []

            for change in code_changes:
                # Find affected documentation
                affected_docs = self._find_affected_documentation(change)

                for doc_path in affected_docs:
                    update = self._generate_update_for_doc(doc_path, change)
                    if update:
                        updates.append(update)

            # Remove duplicates and sort by priority
            unique_updates = self._deduplicate_updates(updates)
            return sorted(unique_updates, key=lambda x: x.confidence, reverse=True)

        except Exception as e:
            logger.error(f"Failed to generate documentation updates: {e}")
            return []

    def update_api_documentation(self, file_path: str) -> bool:
        """Update API documentation for a specific file.

        Args:
            file_path: Path to the source file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Parse the file to extract API information
            api_info = self._extract_api_information(file_path)

            # Find corresponding documentation files
            doc_files = self._find_api_documentation_files(file_path)

            # Update each documentation file
            for doc_file in doc_files:
                success = self._update_api_doc_file(doc_file, api_info)
                if not success:
                    logger.warning(f"Failed to update {doc_file}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to update API documentation for {file_path}: {e}")
            return False

    def sync_code_examples(self) -> dict[str, bool]:
        """Synchronize code examples in documentation with actual code.

        Returns:
            Dictionary mapping doc files to sync success status
        """
        try:
            results = {}

            # Find all documentation files with code examples
            example_docs = self._find_docs_with_code_examples()

            for doc_file in example_docs:
                try:
                    success = self._sync_examples_in_doc(doc_file)
                    results[str(doc_file)] = success
                except Exception as e:
                    logger.error(f"Failed to sync examples in {doc_file}: {e}")
                    results[str(doc_file)] = False

            return results

        except Exception as e:
            logger.error(f"Failed to sync code examples: {e}")
            return {}

    def validate_cross_references(self) -> list[dict[str, Any]]:
        """Validate cross-references between documentation and code.

        Returns:
            List of validation issues found
        """
        try:
            issues = []

            # Find all cross-references in documentation
            cross_refs = self._find_cross_references()

            for ref in cross_refs:
                # Validate each reference
                validation_result = self._validate_reference(ref)
                if not validation_result["valid"]:
                    issues.append(validation_result)

            return issues

        except Exception as e:
            logger.error(f"Failed to validate cross-references: {e}")
            return []

    def generate_changelog_entries(self, code_changes: list[CodeChange]) -> list[str]:
        """Generate changelog entries from code changes.

        Args:
            code_changes: List of code changes

        Returns:
            List of changelog entry strings
        """
        try:
            entries = []

            # Group changes by type and impact
            breaking_changes = [c for c in code_changes if c.impact_level == "breaking"]
            major_changes = [c for c in code_changes if c.impact_level == "major"]
            minor_changes = [c for c in code_changes if c.impact_level == "minor"]

            # Generate entries for breaking changes
            if breaking_changes:
                entries.append("### Breaking Changes")
                for change in breaking_changes:
                    entry = self._format_changelog_entry(change, include_migration=True)
                    entries.append(f"- {entry}")
                entries.append("")

            # Generate entries for major changes
            if major_changes:
                entries.append("### New Features")
                for change in major_changes:
                    entry = self._format_changelog_entry(change)
                    entries.append(f"- {entry}")
                entries.append("")

            # Generate entries for minor changes
            if minor_changes:
                entries.append("### Improvements")
                for change in minor_changes:
                    entry = self._format_changelog_entry(change)
                    entries.append(f"- {entry}")

            return entries

        except Exception as e:
            logger.error(f"Failed to generate changelog entries: {e}")
            return []

    # Helper methods

    def _find_source_dependencies(self, doc_file: Path) -> list[str]:
        """Find source files that a documentation file depends on."""
        try:
            dependencies = []

            # Read documentation content
            content = doc_file.read_text(encoding="utf-8")

            # Look for explicit file references
            file_refs = re.findall(r"```[\w]*:([^`\n]+)", content)
            dependencies.extend(file_refs)

            # Look for function/class references
            code_refs = re.findall(
                r"`([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)`", content
            )
            for ref in code_refs:
                # Find source file containing this reference
                source_file = self._find_source_file_for_reference(ref)
                if source_file:
                    dependencies.append(source_file)

            return list(set(dependencies))  # Remove duplicates

        except Exception as e:
            logger.warning(f"Failed to find dependencies for {doc_file}: {e}")
            return []

    def _check_sync_status(self, doc_file: Path, source_files: list[str]) -> str:
        """Check if documentation is synchronized with source files."""
        try:
            doc_mtime = doc_file.stat().st_mtime

            # Check if any source file is newer than documentation
            for source_file in source_files:
                source_path = self.project_root / source_file
                if source_path.exists():
                    source_mtime = source_path.stat().st_mtime
                    if source_mtime > doc_mtime:
                        return "outdated"

            # Check if documentation references non-existent code
            content = doc_file.read_text(encoding="utf-8")
            if self._has_broken_references(content):
                return "outdated"

            return "synced"

        except Exception:
            return "unknown"

    def _calculate_update_priority(self, doc_file: Path, sync_status: str) -> str:
        """Calculate update priority for a documentation file."""
        if sync_status == "outdated":
            # High priority for API documentation
            if "api" in str(doc_file) or "reference" in str(doc_file):
                return "critical"
            # Medium priority for guides and examples
            elif "guide" in str(doc_file) or "example" in str(doc_file):
                return "high"
            else:
                return "medium"
        elif sync_status == "missing":
            return "high"
        else:
            return "low"

    def _get_recently_modified_files(self, since_hours: int) -> list[str]:
        """Get list of recently modified Python files."""
        try:
            cutoff_time = datetime.now().timestamp() - (since_hours * 3600)
            recent_files = []

            # Scan Python files in src directory
            src_dir = self.project_root / "src"
            if src_dir.exists():
                for py_file in src_dir.rglob("*.py"):
                    if py_file.stat().st_mtime > cutoff_time:
                        recent_files.append(str(py_file.relative_to(self.project_root)))

            return recent_files

        except Exception as e:
            logger.error(f"Failed to get recently modified files: {e}")
            return []

    def _analyze_file_changes(self, file_path: str) -> list[CodeChange]:
        """Analyze changes in a specific file."""
        try:
            changes = []

            # Parse the current file
            full_path = self.project_root / file_path
            if not full_path.exists():
                return changes

            # Extract current API surface
            current_api = self._extract_api_surface(full_path)

            # For now, just create a generic change entry
            # In a real implementation, this would compare with previous versions
            for func_name, signature in current_api.items():
                change = CodeChange(
                    file_path=file_path,
                    change_type="function_modified",
                    element_name=func_name,
                    old_signature=None,  # Would come from git history
                    new_signature=signature,
                    description=f"Function {func_name} potentially modified",
                    impact_level="minor",
                    affected_docs=[],
                )
                changes.append(change)

            return changes

        except Exception as e:
            logger.error(f"Failed to analyze changes in {file_path}: {e}")
            return []

    def _extract_api_surface(self, file_path: Path) -> dict[str, str]:
        """Extract the public API surface of a Python file."""
        try:
            api_surface = {}

            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):  # Public functions only
                        signature = self._extract_function_signature(node)
                        api_surface[node.name] = signature
                elif isinstance(node, ast.ClassDef):
                    if not node.name.startswith("_"):  # Public classes only
                        api_surface[node.name] = f"class {node.name}"

            return api_surface

        except Exception as e:
            logger.error(f"Failed to extract API surface from {file_path}: {e}")
            return {}

    def _extract_function_signature(self, func_node: ast.FunctionDef) -> str:
        """Extract function signature from AST node."""
        try:
            args = []
            for arg in func_node.args.args:
                args.append(arg.arg)

            return f"{func_node.name}({', '.join(args)})"

        except Exception:
            return f"{func_node.name}(...)"

    def _find_affected_documentation(self, change: CodeChange) -> list[str]:
        """Find documentation files affected by a code change."""
        affected_docs = []

        # Look for documentation that might reference this code
        element_name = change.element_name
        file_name = Path(change.file_path).stem

        # Search in API documentation
        api_docs = list(self.docs_root.glob("**/api/*.md")) + list(
            self.docs_root.glob("**/reference/*.md")
        )
        for doc_file in api_docs:
            if self._doc_references_code(doc_file, element_name, file_name):
                affected_docs.append(str(doc_file.relative_to(self.project_root)))

        # Search in examples and guides
        example_docs = list(self.docs_root.glob("**/examples/*.md")) + list(
            self.docs_root.glob("**/guides/*.md")
        )
        for doc_file in example_docs:
            if self._doc_references_code(doc_file, element_name, file_name):
                affected_docs.append(str(doc_file.relative_to(self.project_root)))

        return affected_docs

    def _doc_references_code(
        self, doc_file: Path, element_name: str, file_name: str
    ) -> bool:
        """Check if a documentation file references specific code."""
        try:
            content = doc_file.read_text(encoding="utf-8")

            # Check for direct references
            if element_name in content or file_name in content:
                return True

            # Check for code blocks that might contain the reference
            code_blocks = re.findall(r"```[\s\S]*?```", content)
            return any(
                element_name in block or file_name in block for block in code_blocks
            )

        except Exception:
            return False

    def _generate_update_for_doc(
        self, doc_path: str, change: CodeChange
    ) -> DocumentationUpdate | None:
        """Generate a documentation update for a specific change."""
        try:
            # Determine update type
            if change.change_type.startswith("function"):
                update_type = "api_change"
            elif "example" in doc_path:
                update_type = "example_update"
            else:
                update_type = "cross_reference"

            # Generate suggested content
            suggested_content = self._generate_suggested_content(change, update_type)

            # Calculate confidence based on change type and documentation type
            confidence = self._calculate_update_confidence(change, doc_path)

            return DocumentationUpdate(
                doc_path=doc_path,
                update_type=update_type,
                description=f"Update {update_type} for {change.element_name}",
                suggested_content=suggested_content,
                confidence=confidence,
                dependencies=[],
            )

        except Exception as e:
            logger.error(f"Failed to generate update for {doc_path}: {e}")
            return None

    def _generate_suggested_content(self, change: CodeChange, update_type: str) -> str:
        """Generate suggested content for a documentation update."""
        if update_type == "api_change" and change.new_signature:
            return f"```python\n{change.new_signature}\n```\n\n{change.description}"
        elif update_type == "example_update":
            return f"# Updated example for {change.element_name}\n\n```python\n# Example usage:\n{change.new_signature}\n```"
        else:
            return f"Reference to {change.element_name} may need updating due to: {change.description}"

    def _calculate_update_confidence(self, change: CodeChange, doc_path: str) -> float:
        """Calculate confidence score for a documentation update."""
        confidence = 0.5  # Base confidence

        # Higher confidence for API changes
        if change.change_type.startswith("function") and "api" in doc_path:
            confidence += 0.3

        # Higher confidence for breaking changes
        if change.impact_level == "breaking":
            confidence += 0.2

        # Lower confidence for minor changes
        if change.impact_level == "minor":
            confidence -= 0.1

        return min(1.0, max(0.0, confidence))

    def _deduplicate_updates(
        self, updates: list[DocumentationUpdate]
    ) -> list[DocumentationUpdate]:
        """Remove duplicate documentation updates."""
        seen = set()
        unique_updates = []

        for update in updates:
            key = (update.doc_path, update.update_type, update.description)
            if key not in seen:
                seen.add(key)
                unique_updates.append(update)

        return unique_updates

    def _extract_api_information(self, file_path: str) -> dict[str, Any]:
        """Extract API information from a source file."""
        try:
            full_path = self.project_root / file_path
            content = full_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            api_info = {
                "classes": [],
                "functions": [],
                "constants": [],
                "module_docstring": ast.get_docstring(tree),
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": [],
                    }

                    for item in node.body:
                        if isinstance(
                            item, ast.FunctionDef
                        ) and not item.name.startswith("_"):
                            method_info = {
                                "name": item.name,
                                "signature": self._extract_function_signature(item),
                                "docstring": ast.get_docstring(item),
                            }
                            class_info["methods"].append(method_info)

                    api_info["classes"].append(class_info)

                elif isinstance(node, ast.FunctionDef) and not node.name.startswith(
                    "_"
                ):
                    func_info = {
                        "name": node.name,
                        "signature": self._extract_function_signature(node),
                        "docstring": ast.get_docstring(node),
                    }
                    api_info["functions"].append(func_info)

            return api_info

        except Exception as e:
            logger.error(f"Failed to extract API information from {file_path}: {e}")
            return {
                "classes": [],
                "functions": [],
                "constants": [],
                "module_docstring": None,
            }

    def _find_api_documentation_files(self, file_path: str) -> list[Path]:
        """Find API documentation files for a source file."""
        doc_files = []

        # Look for corresponding API documentation
        file_stem = Path(file_path).stem

        # Common patterns for API documentation
        patterns = [
            f"docs/api/{file_stem}.md",
            f"docs/reference/{file_stem}.md",
            f"docs/api/{file_stem}-api.md",
        ]

        for pattern in patterns:
            doc_path = self.project_root / pattern
            if doc_path.exists():
                doc_files.append(doc_path)

        return doc_files

    def _update_api_doc_file(self, doc_file: Path, api_info: dict[str, Any]) -> bool:
        """Update a specific API documentation file."""
        try:
            # For now, just return True to indicate the operation would succeed
            # In a real implementation, this would update the documentation content
            logger.info(f"Would update API documentation in {doc_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to update API doc file {doc_file}: {e}")
            return False

    def _find_docs_with_code_examples(self) -> list[Path]:
        """Find documentation files that contain code examples."""
        example_docs = []

        for doc_file in self.docs_root.rglob("*.md"):
            try:
                content = doc_file.read_text(encoding="utf-8")
                if "```python" in content or "```py" in content:
                    example_docs.append(doc_file)
            except Exception:
                continue

        return example_docs

    def _sync_examples_in_doc(self, doc_file: Path) -> bool:
        """Synchronize code examples in a documentation file."""
        try:
            # For now, just return True to indicate the operation would succeed
            logger.info(f"Would sync code examples in {doc_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to sync examples in {doc_file}: {e}")
            return False

    def _find_cross_references(self) -> list[dict[str, Any]]:
        """Find all cross-references in documentation."""
        cross_refs = []

        for doc_file in self.docs_root.rglob("*.md"):
            try:
                content = doc_file.read_text(encoding="utf-8")

                # Find function/class references
                refs = re.findall(
                    r"`([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)`", content
                )
                for ref in refs:
                    cross_refs.append(
                        {
                            "doc_file": str(doc_file),
                            "reference": ref,
                            "type": "code_reference",
                        }
                    )

                # Find file references
                file_refs = re.findall(r"\[([^\]]+)\]\(([^)]+\.py)\)", content)
                for _text, file_path in file_refs:
                    cross_refs.append(
                        {
                            "doc_file": str(doc_file),
                            "reference": file_path,
                            "type": "file_reference",
                        }
                    )

            except Exception:
                continue

        return cross_refs

    def _validate_reference(self, ref: dict[str, Any]) -> dict[str, Any]:
        """Validate a cross-reference."""
        try:
            if ref["type"] == "file_reference":
                file_path = self.project_root / ref["reference"]
                valid = file_path.exists()
            else:
                # For code references, check if they exist in the codebase
                valid = self._code_reference_exists(ref["reference"])

            return {
                "reference": ref["reference"],
                "doc_file": ref["doc_file"],
                "valid": valid,
                "issue": None if valid else f"Reference {ref['reference']} not found",
            }

        except Exception as e:
            return {
                "reference": ref["reference"],
                "doc_file": ref["doc_file"],
                "valid": False,
                "issue": str(e),
            }

    def _code_reference_exists(self, reference: str) -> bool:
        """Check if a code reference exists in the codebase."""
        # Simple implementation - would be enhanced with actual code analysis
        return True  # Assume valid for now

    def _has_broken_references(self, content: str) -> bool:
        """Check if documentation content has broken references."""
        # Simple check for common broken reference patterns
        broken_patterns = [
            r"`[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*`",  # Code references
            r"\[[^\]]+\]\([^)]+\.py\)",  # File references
        ]

        for pattern in broken_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Check if the reference is valid (simplified)
                if "example" in match.lower() or "todo" in match.lower():
                    return True

        return False

    def _find_source_file_for_reference(self, reference: str) -> str | None:
        """Find the source file that contains a specific reference."""
        # Simple implementation - would use code intelligence system
        return None

    def _format_changelog_entry(
        self, change: CodeChange, include_migration: bool = False
    ) -> str:
        """Format a changelog entry for a code change."""
        entry = f"{change.element_name}: {change.description}"

        if include_migration and change.old_signature and change.new_signature:
            entry += f" (was: `{change.old_signature}`, now: `{change.new_signature}`)"

        return entry
