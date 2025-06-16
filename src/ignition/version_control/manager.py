"""Version Control Manager for coordinating all version control intelligence operations."""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class VersionControlConfig:
    """Configuration for version control intelligence operations."""

    repository_path: Path
    git_enabled: bool = True
    auto_track_changes: bool = True
    conflict_prediction_enabled: bool = True
    impact_analysis_enabled: bool = True
    release_planning_enabled: bool = True
    risk_threshold: float = 0.7
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour


class VersionControlManager:
    """Central coordinator for all version control intelligence operations.

    This class manages the coordination between different analysis modules,
    handles version control state and history, and provides a unified API
    for CLI and UI integration.
    """

    def __init__(
        self,
        config: VersionControlConfig,
        graph_client: Any | None = None,
        gateway_client: Any | None = None,
    ):
        """Initialize the Version Control Manager.

        Args:
            config: Version control configuration
            graph_client: Optional graph database client for intelligence storage
            gateway_client: Optional gateway client for resource analysis
        """
        self.config = config
        self.graph_client = graph_client
        self.gateway_client = gateway_client

        # Initialize components (lazy loading)
        self._change_tracker = None
        self._dependency_analyzer = None
        self._impact_analyzer = None
        self._conflict_predictor = None
        self._release_planner = None

        # State management
        self._initialized = False
        self._cache = {}

        logger.info(
            f"VersionControlManager initialized for repository: {config.repository_path}"
        )

    def initialize(self) -> bool:
        """Initialize the version control manager and all components.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Validate repository path
            if not self.config.repository_path.exists():
                logger.error(
                    f"Repository path does not exist: {self.config.repository_path}"
                )
                return False

            # Check if it's a git repository
            if self.config.git_enabled:
                git_dir = self.config.repository_path / ".git"
                if not git_dir.exists():
                    logger.warning(
                        f"Git repository not found at {self.config.repository_path}"
                    )
                    self.config.git_enabled = False

            # Initialize graph database schema if available
            if (
                self.graph_client
                and hasattr(self.graph_client, "is_connected")
                and self.graph_client.is_connected
            ):
                self._initialize_graph_schema()

            # Set up file system monitoring if enabled
            if self.config.auto_track_changes:
                self._setup_change_monitoring()

            self._initialized = True
            logger.info("VersionControlManager initialization completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize VersionControlManager: {e}")
            return False

    @property
    def change_tracker(self):
        """Get the change tracker instance (lazy loading)."""
        if self._change_tracker is None:
            from .change_tracker import ChangeTracker

            self._change_tracker = ChangeTracker(
                repository_path=self.config.repository_path,
                graph_client=self.graph_client,
            )
        return self._change_tracker

    @property
    def dependency_analyzer(self):
        """Get the dependency analyzer instance (lazy loading)."""
        if self._dependency_analyzer is None:
            from .dependency_analyzer import DependencyAnalyzer

            self._dependency_analyzer = DependencyAnalyzer(
                repository_path=self.config.repository_path,
                graph_client=self.graph_client,
                gateway_client=self.gateway_client,
            )
        return self._dependency_analyzer

    @property
    def impact_analyzer(self):
        """Get the impact analyzer instance (lazy loading)."""
        if self._impact_analyzer is None:
            from .impact_analyzer import CommitImpactAnalyzer

            self._impact_analyzer = CommitImpactAnalyzer(
                change_tracker=self.change_tracker,
                dependency_analyzer=self.dependency_analyzer,
                graph_client=self.graph_client,
            )
        return self._impact_analyzer

    @property
    def conflict_predictor(self):
        """Get the conflict predictor instance (lazy loading)."""
        if self._conflict_predictor is None:
            from .conflict_predictor import MergeConflictPredictor

            self._conflict_predictor = MergeConflictPredictor(
                change_tracker=self.change_tracker,
                dependency_analyzer=self.dependency_analyzer,
                graph_client=self.graph_client,
            )
        return self._conflict_predictor

    @property
    def release_planner(self):
        """Get the release planner instance (lazy loading)."""
        if self._release_planner is None:
            from .release_planner import ReleasePlanner

            self._release_planner = ReleasePlanner(
                impact_analyzer=self.impact_analyzer,
                conflict_predictor=self.conflict_predictor,
                graph_client=self.graph_client,
            )
        return self._release_planner

    def analyze_commit_impact(
        self,
        commit_hash: str | None = None,
        files: list[str] | None = None,
        detailed: bool = False,
    ) -> dict[str, Any]:
        """Analyze the impact of a commit or set of files.

        Args:
            commit_hash: Git commit hash to analyze (if None, analyzes current changes)
            files: Specific files to analyze (if None, analyzes all changed files)
            detailed: Whether to include detailed analysis

        Returns:
            Impact analysis results
        """
        if not self.config.impact_analysis_enabled:
            return {"error": "Impact analysis is disabled"}

        try:
            return self.impact_analyzer.analyze_impact(
                commit_hash=commit_hash, files=files, detailed=detailed
            )
        except Exception as e:
            logger.error(f"Failed to analyze commit impact: {e}")
            return {"error": str(e)}

    def predict_merge_conflicts(
        self, source_branch: str, target_branch: str = "main", detailed: bool = False
    ) -> dict[str, Any]:
        """Predict merge conflicts between branches.

        Args:
            source_branch: Source branch to merge from
            target_branch: Target branch to merge to
            detailed: Whether to include detailed predictions

        Returns:
            Conflict prediction results
        """
        if not self.config.conflict_prediction_enabled:
            return {"error": "Conflict prediction is disabled"}

        try:
            return self.conflict_predictor.predict_conflicts(
                source_branch=source_branch,
                target_branch=target_branch,
                detailed=detailed,
            )
        except Exception as e:
            logger.error(f"Failed to predict merge conflicts: {e}")
            return {"error": str(e)}

    def plan_release(
        self,
        version: str,
        strategy: str = "incremental",
        include_changes: list[str] | None = None,
        exclude_changes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Plan a release with intelligent recommendations.

        Args:
            version: Release version identifier
            strategy: Release strategy (incremental, big_bang, feature_flag, etc.)
            include_changes: Specific changes to include
            exclude_changes: Specific changes to exclude

        Returns:
            Release planning results
        """
        if not self.config.release_planning_enabled:
            return {"error": "Release planning is disabled"}

        try:
            return self.release_planner.plan_release(
                version=version,
                strategy=strategy,
                include_changes=include_changes,
                exclude_changes=exclude_changes,
            )
        except Exception as e:
            logger.error(f"Failed to plan release: {e}")
            return {"error": str(e)}

    def get_repository_status(self) -> dict[str, Any]:
        """Get comprehensive repository status and health metrics.

        Returns:
            Repository status information
        """
        try:
            status = {
                "repository_path": str(self.config.repository_path),
                "git_enabled": self.config.git_enabled,
                "initialized": self._initialized,
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "change_tracker": self._change_tracker is not None,
                    "dependency_analyzer": self._dependency_analyzer is not None,
                    "impact_analyzer": self._impact_analyzer is not None,
                    "conflict_predictor": self._conflict_predictor is not None,
                    "release_planner": self._release_planner is not None,
                },
                "capabilities": {
                    "impact_analysis": self.config.impact_analysis_enabled,
                    "conflict_prediction": self.config.conflict_prediction_enabled,
                    "release_planning": self.config.release_planning_enabled,
                    "auto_tracking": self.config.auto_track_changes,
                },
                "connections": {
                    "graph_database": (
                        self.graph_client is not None
                        and hasattr(self.graph_client, "is_connected")
                        and self.graph_client.is_connected()
                        if self.graph_client
                        else False
                    ),
                    "gateway": self.gateway_client is not None,
                },
            }

            # Add git status if available
            if self.config.git_enabled:
                status["git"] = self._get_git_status()

            return status

        except Exception as e:
            logger.error(f"Failed to get repository status: {e}")
            return {"error": str(e)}

    def generate_report(
        self,
        report_type: str = "comprehensive",
        format: str = "json",
        output_path: Path | None = None,
    ) -> dict[str, Any]:
        """Generate a comprehensive version control intelligence report.

        Args:
            report_type: Type of report (comprehensive, summary, conflicts, releases)
            format: Output format (json, html, markdown)
            output_path: Optional path to save the report

        Returns:
            Report data and metadata
        """
        try:
            report_data = {
                "metadata": {
                    "report_type": report_type,
                    "format": format,
                    "generated_at": datetime.now().isoformat(),
                    "repository": str(self.config.repository_path),
                },
                "status": self.get_repository_status(),
            }

            # Add report-specific sections
            if report_type in ["comprehensive", "summary"]:
                report_data["recent_commits"] = self._get_recent_commits()
                report_data["risk_metrics"] = self._get_risk_metrics()

            if report_type in ["comprehensive", "conflicts"]:
                report_data["predicted_conflicts"] = self._get_predicted_conflicts()
                report_data["conflict_history"] = self._get_conflict_history()

            if report_type in ["comprehensive", "releases"]:
                report_data["planned_releases"] = self._get_planned_releases()
                report_data["release_history"] = self._get_release_history()

            # Save report if output path specified
            if output_path:
                self._save_report(report_data, output_path, format)
                report_data["metadata"]["saved_to"] = str(output_path)

            return report_data

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return {"error": str(e)}

    def _initialize_graph_schema(self) -> None:
        """Initialize the graph database schema for version control intelligence."""
        try:
            # Add version control specific node types and relationships
            # This will be implemented when we extend the graph schema
            logger.info("Graph database schema initialized for version control")
        except Exception as e:
            logger.error(f"Failed to initialize graph schema: {e}")

    def _setup_change_monitoring(self) -> None:
        """Set up file system monitoring for automatic change tracking."""
        try:
            # This will be implemented with the ChangeTracker
            logger.info("Change monitoring setup completed")
        except Exception as e:
            logger.error(f"Failed to setup change monitoring: {e}")

    def _get_git_status(self) -> dict[str, Any]:
        """Get current git repository status."""
        try:
            import subprocess

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.config.repository_path,
                capture_output=True,
                text=True,
            )
            current_branch = (
                result.stdout.strip() if result.returncode == 0 else "unknown"
            )

            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.config.repository_path,
                capture_output=True,
                text=True,
            )

            changes = []
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        status = line[:2]
                        file_path = line[3:]
                        changes.append({"status": status, "file": file_path})

            return {
                "current_branch": current_branch,
                "changes": changes,
                "clean": len(changes) == 0,
            }

        except Exception as e:
            logger.error(f"Failed to get git status: {e}")
            return {"error": str(e)}

    def _get_recent_activity(self) -> dict[str, Any]:
        """Get recent version control activity from graph database."""
        # This will be implemented when we have the graph schema
        return {"commits": [], "conflicts": [], "releases": []}

    def _get_recent_commits(self) -> list[dict[str, Any]]:
        """Get recent commits information."""
        # This will be implemented with git integration
        return []

    def _get_risk_metrics(self) -> dict[str, Any]:
        """Get current risk metrics."""
        # This will be implemented with the impact analyzer
        return {"overall_risk": 0.0, "high_risk_changes": 0}

    def _get_predicted_conflicts(self) -> list[dict[str, Any]]:
        """Get currently predicted conflicts."""
        # This will be implemented with the conflict predictor
        return []

    def _get_conflict_history(self) -> list[dict[str, Any]]:
        """Get historical conflict data."""
        # This will be implemented with graph database queries
        return []

    def _get_planned_releases(self) -> list[dict[str, Any]]:
        """Get planned releases."""
        # This will be implemented with the release planner
        return []

    def _get_release_history(self) -> list[dict[str, Any]]:
        """Get release history."""
        # This will be implemented with graph database queries
        return []

    def _save_report(
        self, data: dict[str, Any], output_path: Path, format: str
    ) -> None:
        """Save report to file in specified format."""
        try:
            if format == "json":
                import json

                with open(output_path, "w") as f:
                    json.dump(data, f, indent=2)
            elif format == "html":
                # HTML report generation will be implemented later
                raise NotImplementedError("HTML format not yet implemented")
            elif format == "markdown":
                # Markdown report generation will be implemented later
                raise NotImplementedError("Markdown format not yet implemented")
            else:
                raise ValueError(f"Unsupported format: {format}")

        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            raise
