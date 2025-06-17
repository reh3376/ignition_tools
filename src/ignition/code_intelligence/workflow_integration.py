"""Development Workflow Integration for Code Intelligence

This module provides integration with development workflows including:
- Git hooks for automatic code analysis
- Pre-commit code intelligence checks
- Code review assistance tools
- Automated code quality gates
"""

import json
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .analytics_dashboard import CodeIntelligenceDashboard
from .ai_assistant_enhancement import AIAssistantEnhancement, ChangeImpactAnalysis
from .manager import CodeIntelligenceManager


@dataclass
class QualityGateResult:
    """Result of a quality gate check."""
    
    gate_name: str
    passed: bool
    score: float
    threshold: float
    message: str
    details: Dict[str, Any]
    recommendations: List[str]


@dataclass
class CodeReviewInsight:
    """Insights for code review assistance."""
    
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    impact_score: float
    complexity_change: float
    debt_impact: float
    suggestions: List[str]
    related_files: List[str]
    test_recommendations: List[str]


@dataclass
class WorkflowIntegrationConfig:
    """Configuration for workflow integration."""
    
    enable_git_hooks: bool = True
    enable_pre_commit: bool = True
    enable_quality_gates: bool = True
    complexity_threshold: float = 50.0
    debt_threshold: float = 0.6
    coverage_threshold: float = 80.0
    file_size_threshold: int = 1000
    enable_auto_analysis: bool = True
    enable_review_assistance: bool = True


class DevelopmentWorkflowIntegrator:
    """Integrates code intelligence with development workflows."""
    
    def __init__(self, 
                 manager: CodeIntelligenceManager,
                 dashboard: CodeIntelligenceDashboard,
                 ai_assistant: AIAssistantEnhancement,
                 config: Optional[WorkflowIntegrationConfig] = None):
        self.manager = manager
        self.dashboard = dashboard
        self.ai_assistant = ai_assistant
        self.config = config or WorkflowIntegrationConfig()
        self.project_root = Path.cwd()
        
    def setup_git_hooks(self) -> bool:
        """Set up git hooks for automatic code analysis."""
        if not self.config.enable_git_hooks:
            return False
            
        hooks_dir = self.project_root / ".git" / "hooks"
        if not hooks_dir.exists():
            print("❌ Git repository not found")
            return False
            
        # Create pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        pre_commit_script = self._create_pre_commit_script()
        
        try:
            with open(pre_commit_hook, 'w') as f:
                f.write(pre_commit_script)
            pre_commit_hook.chmod(0o755)
            
            # Create post-commit hook for analysis
            post_commit_hook = hooks_dir / "post-commit"
            post_commit_script = self._create_post_commit_script()
            
            with open(post_commit_hook, 'w') as f:
                f.write(post_commit_script)
            post_commit_hook.chmod(0o755)
            
            print("✅ Git hooks installed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install git hooks: {e}")
            return False
    
    def _create_pre_commit_script(self) -> str:
        """Create the pre-commit hook script."""
        return f"""#!/bin/bash
# IGN Scripts Code Intelligence Pre-commit Hook

echo "🧠 Running code intelligence checks..."

# Get list of staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\\.py$')

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No Python files to check"
    exit 0
fi

# Run quality gates on staged files
python -c "
import sys
sys.path.append('{self.project_root}')
from src.ignition.code_intelligence.workflow_integration import DevelopmentWorkflowIntegrator
from src.ignition.code_intelligence.manager import CodeIntelligenceManager
from src.ignition.code_intelligence.analytics_dashboard import CodeIntelligenceDashboard
from src.ignition.code_intelligence.ai_assistant_enhancement import AIAssistantEnhancement
from src.ignition.graph.client import IgnitionGraphClient

# Initialize systems
client = IgnitionGraphClient()
if client.connect():
    manager = CodeIntelligenceManager(client)
    dashboard = CodeIntelligenceDashboard(client)
    ai_assistant = AIAssistantEnhancement(manager)
    integrator = DevelopmentWorkflowIntegrator(manager, dashboard, ai_assistant)
    
    # Get staged files
    import subprocess
    result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'], 
                          capture_output=True, text=True)
    staged_files = [f for f in result.stdout.strip().split('\\n') if f.endswith('.py')]
    
    # Run pre-commit checks
    if not integrator.run_pre_commit_checks(staged_files):
        print('❌ Pre-commit checks failed')
        sys.exit(1)
    else:
        print('✅ Pre-commit checks passed')
else:
    print('⚠️  Code intelligence not available, skipping checks')
"

echo "✅ Code intelligence checks completed"
"""

    def _create_post_commit_script(self) -> str:
        """Create the post-commit hook script."""
        return f"""#!/bin/bash
# IGN Scripts Code Intelligence Post-commit Hook

echo "🔄 Updating code intelligence database..."

# Run analysis on changed files in background
python -c "
import sys
sys.path.append('{self.project_root}')
from src.ignition.code_intelligence.workflow_integration import DevelopmentWorkflowIntegrator
from src.ignition.code_intelligence.manager import CodeIntelligenceManager
from src.ignition.code_intelligence.analytics_dashboard import CodeIntelligenceDashboard
from src.ignition.code_intelligence.ai_assistant_enhancement import AIAssistantEnhancement
from src.ignition.graph.client import IgnitionGraphClient

# Initialize systems
client = IgnitionGraphClient()
if client.connect():
    manager = CodeIntelligenceManager(client)
    dashboard = CodeIntelligenceDashboard(client)
    ai_assistant = AIAssistantEnhancement(manager)
    integrator = DevelopmentWorkflowIntegrator(manager, dashboard, ai_assistant)
    
    # Get changed files from last commit
    import subprocess
    result = subprocess.run(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'], 
                          capture_output=True, text=True)
    changed_files = [f for f in result.stdout.strip().split('\\n') if f.endswith('.py')]
    
    # Run post-commit analysis
    integrator.run_post_commit_analysis(changed_files)
    print('✅ Code intelligence database updated')
else:
    print('⚠️  Code intelligence not available')
" &

echo "✅ Post-commit analysis started"
"""

    def run_pre_commit_checks(self, staged_files: List[str]) -> bool:
        """Run pre-commit code intelligence checks."""
        if not self.config.enable_pre_commit:
            return True
            
        print("🔍 Running pre-commit code intelligence checks...")
        
        all_passed = True
        for file_path in staged_files:
            if not Path(file_path).exists():
                continue
                
            # Run quality gates for this file
            gate_results = self.run_quality_gates(file_path)
            
            # Check if any critical gates failed
            for result in gate_results:
                if not result.passed and result.gate_name in ['complexity', 'file_size', 'debt_score']:
                    print(f"❌ {result.gate_name} check failed for {file_path}: {result.message}")
                    all_passed = False
                elif not result.passed:
                    print(f"⚠️  {result.gate_name} warning for {file_path}: {result.message}")
        
        return all_passed
    
    def run_post_commit_analysis(self, changed_files: List[str]) -> None:
        """Run post-commit analysis on changed files."""
        if not self.config.enable_auto_analysis:
            return
            
        for file_path in changed_files:
            if Path(file_path).exists() and file_path.endswith('.py'):
                try:
                    # Update code intelligence database
                    self.manager.analyze_and_store_file(Path(file_path))
                except Exception as e:
                    print(f"⚠️  Failed to analyze {file_path}: {e}")
    
    def run_quality_gates(self, file_path: str) -> List[QualityGateResult]:
        """Run quality gates on a file."""
        results = []
        
        try:
            # Get file context from manager
            file_context = self.manager.get_file_context(file_path)
            if not file_context or not file_context.get("file"):
                # Try to analyze the file first
                try:
                    self.manager.analyze_and_store_file(Path(file_path))
                    file_context = self.manager.get_file_context(file_path)
                except Exception:
                    pass
            
            if not file_context or not file_context.get("file"):
                return results
            
            file_info = file_context["file"]
            
            # Gate 1: File size check
            if self.config.file_size_threshold > 0:
                lines = file_info.get("lines", 0)
                passed = lines <= self.config.file_size_threshold
                results.append(QualityGateResult(
                    gate_name="file_size",
                    passed=passed,
                    score=min(1.0, self.config.file_size_threshold / max(lines, 1)),
                    threshold=self.config.file_size_threshold,
                    message=f"File has {lines} lines (threshold: {self.config.file_size_threshold})",
                    details={"lines": lines},
                    recommendations=["Consider refactoring large files"] if not passed else []
                ))
            
            # Gate 2: Complexity check
            if self.config.complexity_threshold > 0:
                complexity = file_info.get("complexity", 0)
                passed = complexity <= self.config.complexity_threshold
                results.append(QualityGateResult(
                    gate_name="complexity",
                    passed=passed,
                    score=max(0.0, 1.0 - (complexity / 100.0)),
                    threshold=self.config.complexity_threshold,
                    message=f"Complexity score: {complexity:.1f} (threshold: {self.config.complexity_threshold})",
                    details={"complexity": complexity},
                    recommendations=["Reduce cyclomatic complexity"] if not passed else []
                ))
            
            # Gate 3: Technical debt check (simplified calculation)
            if self.config.debt_threshold > 0:
                # Calculate a simple debt score based on complexity and maintainability
                complexity_factor = min(complexity / 50.0, 2.0)
                maintainability = file_info.get("maintainability_index", 100)
                maintainability_factor = max(0, (100 - maintainability) / 100.0)
                debt_score = (complexity_factor + maintainability_factor) / 2.0
                
                passed = debt_score <= self.config.debt_threshold
                results.append(QualityGateResult(
                    gate_name="debt_score",
                    passed=passed,
                    score=max(0.0, 1.0 - debt_score),
                    threshold=self.config.debt_threshold,
                    message=f"Technical debt score: {debt_score:.2f} (threshold: {self.config.debt_threshold})",
                    details={"debt_score": debt_score},
                    recommendations=["Address technical debt issues"] if not passed else []
                ))
            
            # Gate 4: Maintainability check
            maintainability = file_info.get("maintainability_index", 100)
            passed = maintainability >= 20  # Minimum maintainability threshold
            results.append(QualityGateResult(
                gate_name="maintainability",
                passed=passed,
                score=maintainability / 100.0,
                threshold=20.0,
                message=f"Maintainability index: {maintainability:.1f}",
                details={"maintainability": maintainability},
                recommendations=["Improve code maintainability"] if not passed else []
            ))
            
        except Exception as e:
            results.append(QualityGateResult(
                gate_name="analysis_error",
                passed=False,
                score=0.0,
                threshold=1.0,
                message=f"Failed to analyze file: {e}",
                details={"error": str(e)},
                recommendations=["Check file syntax and structure"]
            ))
        
        return results
    
    def generate_code_review_insights(self, changed_files: List[str]) -> List[CodeReviewInsight]:
        """Generate insights for code review assistance."""
        if not self.config.enable_review_assistance:
            return []
            
        insights = []
        
        for file_path in changed_files:
            try:
                # Get change type
                change_type = self._get_change_type(file_path)
                
                # Analyze impact
                impact_analysis = self.ai_assistant.analyze_change_impact(file_path)
                
                # Calculate risk level
                risk_level = self._calculate_risk_level(impact_analysis)
                
                # Get related files
                related_files = impact_analysis.affected_files[:5]  # Top 5
                
                # Generate suggestions
                suggestions = self._generate_review_suggestions(file_path, impact_analysis)
                
                # Generate test recommendations
                test_recommendations = self._generate_test_recommendations(file_path, impact_analysis)
                
                insight = CodeReviewInsight(
                    file_path=file_path,
                    change_type=change_type,
                    risk_level=risk_level,
                    impact_score=len(impact_analysis.affected_files) / 10.0,  # Normalized impact
                    complexity_change=0.0,  # Would need before/after analysis
                    debt_impact=0.0,  # Would need before/after analysis
                    suggestions=suggestions,
                    related_files=related_files,
                    test_recommendations=test_recommendations
                )
                
                insights.append(insight)
                
            except Exception as e:
                print(f"⚠️  Failed to generate insights for {file_path}: {e}")
        
        return insights
    
    def _get_change_type(self, file_path: str) -> str:
        """Determine the type of change for a file."""
        try:
            # Check if file exists
            if not Path(file_path).exists():
                return "deleted"
            
            # Check git status
            result = subprocess.run(
                ['git', 'status', '--porcelain', file_path],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.stdout.strip():
                status = result.stdout.strip()[:2]
                if status.startswith('A'):
                    return "added"
                elif status.startswith('M'):
                    return "modified"
                elif status.startswith('D'):
                    return "deleted"
                elif status.startswith('R'):
                    return "renamed"
            
            return "modified"  # Default
            
        except Exception:
            return "unknown"
    
    def _calculate_risk_level(self, impact_analysis: ChangeImpactAnalysis) -> str:
        """Calculate risk level based on impact analysis."""
        return impact_analysis.risk_level
    
    def _generate_review_suggestions(self, file_path: str, impact_analysis: ChangeImpactAnalysis) -> List[str]:
        """Generate code review suggestions."""
        suggestions = []
        
        # High impact suggestions
        if len(impact_analysis.affected_files) > 5:
            suggestions.append("High-impact change - review dependencies carefully")
        
        # Breaking changes suggestions
        if impact_analysis.breaking_changes:
            suggestions.append("Potential breaking changes detected - review API compatibility")
        
        # Test coverage suggestions
        if impact_analysis.test_coverage_gaps:
            suggestions.append("Test coverage gaps identified - consider adding tests")
        
        # File size suggestions
        try:
            with open(file_path, 'r') as f:
                lines = len(f.readlines())
            if lines > 1000:
                suggestions.append("Consider refactoring large file")
        except Exception:
            pass
        
        return suggestions
    
    def _generate_test_recommendations(self, file_path: str, impact_analysis: ChangeImpactAnalysis) -> List[str]:
        """Generate test recommendations."""
        recommendations = []
        
        # Impact-based recommendations
        if len(impact_analysis.affected_files) > 3:
            recommendations.append("Add integration tests for high-impact changes")
        
        # Dependency-based recommendations
        if impact_analysis.affected_files:
            recommendations.append(f"Test interactions with {len(impact_analysis.affected_files)} dependent files")
        
        # Breaking changes recommendations
        if impact_analysis.breaking_changes:
            recommendations.append("Add regression tests for breaking changes")
        
        return recommendations
    
    def create_workflow_report(self, changed_files: List[str]) -> Dict[str, Any]:
        """Create a comprehensive workflow report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "files_analyzed": len(changed_files),
            "quality_gates": {},
            "review_insights": [],
            "overall_health": {},
            "recommendations": []
        }
        
        # Run quality gates
        all_gate_results = []
        for file_path in changed_files:
            if Path(file_path).exists():
                gate_results = self.run_quality_gates(file_path)
                all_gate_results.extend(gate_results)
                report["quality_gates"][file_path] = [
                    {
                        "gate": result.gate_name,
                        "passed": result.passed,
                        "score": result.score,
                        "message": result.message
                    }
                    for result in gate_results
                ]
        
        # Generate review insights
        insights = self.generate_code_review_insights(changed_files)
        report["review_insights"] = [
            {
                "file": insight.file_path,
                "risk_level": insight.risk_level,
                "impact_score": insight.impact_score,
                "suggestions": insight.suggestions,
                "test_recommendations": insight.test_recommendations
            }
            for insight in insights
        ]
        
        # Overall health
        if all_gate_results:
            passed_gates = sum(1 for result in all_gate_results if result.passed)
            total_gates = len(all_gate_results)
            report["overall_health"] = {
                "gates_passed": passed_gates,
                "total_gates": total_gates,
                "pass_rate": passed_gates / total_gates if total_gates > 0 else 0.0
            }
        
        # Global recommendations
        if insights:
            high_risk_files = [i for i in insights if i.risk_level in ['high', 'critical']]
            if high_risk_files:
                report["recommendations"].append(
                    f"Review {len(high_risk_files)} high-risk files carefully"
                )
            
            avg_impact = sum(i.impact_score for i in insights) / len(insights)
            if avg_impact > 0.5:
                report["recommendations"].append("Consider staging deployment due to high impact")
        
        return report
    
    def export_workflow_config(self, config_path: str) -> bool:
        """Export workflow configuration to file."""
        try:
            config_data = {
                "enable_git_hooks": self.config.enable_git_hooks,
                "enable_pre_commit": self.config.enable_pre_commit,
                "enable_quality_gates": self.config.enable_quality_gates,
                "complexity_threshold": self.config.complexity_threshold,
                "debt_threshold": self.config.debt_threshold,
                "coverage_threshold": self.config.coverage_threshold,
                "file_size_threshold": self.config.file_size_threshold,
                "enable_auto_analysis": self.config.enable_auto_analysis,
                "enable_review_assistance": self.config.enable_review_assistance
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Failed to export config: {e}")
            return False
    
    def import_workflow_config(self, config_path: str) -> bool:
        """Import workflow configuration from file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            self.config = WorkflowIntegrationConfig(**config_data)
            return True
        except Exception as e:
            print(f"❌ Failed to import config: {e}")
            return False 