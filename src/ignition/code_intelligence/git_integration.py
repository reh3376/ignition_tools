"""
Git Integration for Code Intelligence System

This module provides comprehensive git integration for tracking code evolution,
linking code changes to commits and branches, and monitoring complexity trends.
"""

import logging
import subprocess
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

logger = logging.getLogger(__name__)


@dataclass
class GitCommit:
    """Represents a git commit with code analysis data."""
    
    hash: str
    short_hash: str
    author: str
    email: str
    date: datetime
    message: str
    branch: str
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    complexity_delta: float = 0.0
    maintainability_delta: float = 0.0


@dataclass
class CodeEvolution:
    """Tracks the evolution of a file over time."""
    
    file_path: str
    commits: List[GitCommit]
    size_history: List[Tuple[datetime, int]]  # (date, lines)
    complexity_history: List[Tuple[datetime, float]]  # (date, complexity)
    maintainability_history: List[Tuple[datetime, float]]  # (date, maintainability)
    growth_rate: float  # lines per day
    complexity_trend: str  # "increasing", "decreasing", "stable"


@dataclass
class BranchAnalysis:
    """Analysis of code changes across branches."""
    
    branch_name: str
    base_branch: str
    commits_ahead: int
    commits_behind: int
    files_modified: List[str]
    total_complexity_change: float
    risk_assessment: str  # "low", "medium", "high"
    merge_conflicts_predicted: List[str]


class GitIntegration:
    """Provides git integration for code intelligence tracking."""
    
    def __init__(self, repository_path: Path, graph_client=None):
        self.repository_path = repository_path
        self.graph_client = graph_client
        self._git_available = self._check_git_availability()
        
    def _check_git_availability(self) -> bool:
        """Check if git is available and repository is valid."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(f"Git not available or not a git repository: {self.repository_path}")
            return False
    
    def get_commit_history(self, file_path: Optional[str] = None, limit: int = 100) -> List[GitCommit]:
        """Get commit history for a file or entire repository."""
        if not self._git_available:
            return []
        
        try:
            # Build git log command
            cmd = [
                "git", "log", 
                f"--max-count={limit}",
                "--pretty=format:%H|%h|%an|%ae|%ai|%s",
                "--numstat"
            ]
            
            if file_path:
                cmd.append("--")
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return self._parse_git_log_output(result.stdout)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get git history: {e}")
            return []
    
    def _parse_git_log_output(self, output: str) -> List[GitCommit]:
        """Parse git log output into GitCommit objects."""
        commits = []
        lines = output.strip().split('\n')
        i = 0
        
        while i < len(lines):
            if '|' in lines[i]:
                # Parse commit info line
                parts = lines[i].split('|')
                if len(parts) >= 6:
                    hash_full = parts[0]
                    hash_short = parts[1]
                    author = parts[2]
                    email = parts[3]
                    date_str = parts[4]
                    message = parts[5]
                    
                    # Parse date
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except ValueError:
                        date = datetime.now()
                    
                    # Get current branch for this commit
                    branch = self._get_commit_branch(hash_full)
                    
                    # Parse file changes (next lines until empty line or next commit)
                    i += 1
                    files_changed = []
                    lines_added = 0
                    lines_deleted = 0
                    
                    while i < len(lines) and lines[i] and '|' not in lines[i]:
                        if '\t' in lines[i]:
                            parts = lines[i].split('\t')
                            if len(parts) >= 3:
                                added = parts[0] if parts[0] != '-' else '0'
                                deleted = parts[1] if parts[1] != '-' else '0'
                                filename = parts[2]
                                
                                try:
                                    lines_added += int(added)
                                    lines_deleted += int(deleted)
                                    files_changed.append(filename)
                                except ValueError:
                                    pass
                        i += 1
                    
                    commit = GitCommit(
                        hash=hash_full,
                        short_hash=hash_short,
                        author=author,
                        email=email,
                        date=date,
                        message=message,
                        branch=branch,
                        files_changed=files_changed,
                        lines_added=lines_added,
                        lines_deleted=lines_deleted
                    )
                    commits.append(commit)
                    continue
            i += 1
        
        return commits
    
    def _get_commit_branch(self, commit_hash: str) -> str:
        """Get the branch name for a specific commit."""
        try:
            result = subprocess.run(
                ["git", "branch", "--contains", commit_hash],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = result.stdout.strip().split('\n')
            for branch in branches:
                branch = branch.strip()
                if branch.startswith('* '):
                    return branch[2:]
                elif branch and not branch.startswith('('):
                    return branch
            
            return "unknown"
            
        except subprocess.CalledProcessError:
            return "unknown"
    
    def track_file_evolution(self, file_path: str) -> Optional[CodeEvolution]:
        """Track the evolution of a specific file over time."""
        if not self._git_available:
            return None
        
        try:
            # Get commit history for the file
            commits = self.get_commit_history(file_path, limit=50)
            
            if not commits:
                return None
            
            # Build evolution data
            size_history = []
            complexity_history = []
            maintainability_history = []
            
            # Get file metrics at different points in time
            for commit in commits[:10]:  # Limit to last 10 commits for performance
                try:
                    # Get file content at this commit
                    file_content = self._get_file_at_commit(file_path, commit.hash)
                    if file_content:
                        lines = len(file_content.splitlines())
                        size_history.append((commit.date, lines))
                        
                        # Calculate complexity if we have the analyzer
                        if hasattr(self, 'analyzer'):
                            # This would require code analysis at each commit
                            # For now, we'll estimate based on file size
                            estimated_complexity = lines * 0.1  # Rough estimate
                            complexity_history.append((commit.date, estimated_complexity))
                            
                            # Estimate maintainability
                            estimated_maintainability = max(0, 100 - lines * 0.05)
                            maintainability_history.append((commit.date, estimated_maintainability))
                
                except Exception as e:
                    logger.debug(f"Could not analyze commit {commit.short_hash}: {e}")
                    continue
            
            # Calculate growth rate
            growth_rate = self._calculate_growth_rate(size_history)
            
            # Determine complexity trend
            complexity_trend = self._determine_trend(complexity_history)
            
            return CodeEvolution(
                file_path=file_path,
                commits=commits,
                size_history=size_history,
                complexity_history=complexity_history,
                maintainability_history=maintainability_history,
                growth_rate=growth_rate,
                complexity_trend=complexity_trend
            )
            
        except Exception as e:
            logger.error(f"Failed to track file evolution for {file_path}: {e}")
            return None
    
    def _get_file_at_commit(self, file_path: str, commit_hash: str) -> Optional[str]:
        """Get file content at a specific commit."""
        try:
            result = subprocess.run(
                ["git", "show", f"{commit_hash}:{file_path}"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return None
    
    def _calculate_growth_rate(self, size_history: List[Tuple[datetime, int]]) -> float:
        """Calculate the growth rate in lines per day."""
        if len(size_history) < 2:
            return 0.0
        
        # Sort by date
        size_history.sort(key=lambda x: x[0])
        
        # Calculate rate between first and last
        first_date, first_size = size_history[0]
        last_date, last_size = size_history[-1]
        
        days_diff = (last_date - first_date).days
        if days_diff == 0:
            return 0.0
        
        size_diff = last_size - first_size
        return size_diff / days_diff
    
    def _determine_trend(self, history: List[Tuple[datetime, float]]) -> str:
        """Determine if a metric is increasing, decreasing, or stable."""
        if len(history) < 3:
            return "stable"
        
        # Sort by date
        history.sort(key=lambda x: x[0])
        
        # Calculate trend using simple linear regression
        values = [h[1] for h in history]
        n = len(values)
        
        # Calculate slope
        x_mean = (n - 1) / 2  # 0, 1, 2, ... n-1
        y_mean = sum(values) / n
        
        numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return "stable"
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def analyze_branch_differences(self, source_branch: str, target_branch: str = "main") -> Optional[BranchAnalysis]:
        """Analyze differences between branches."""
        if not self._git_available:
            return None
        
        try:
            # Get commits ahead/behind
            ahead_result = subprocess.run(
                ["git", "rev-list", "--count", f"{target_branch}..{source_branch}"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            commits_ahead = int(ahead_result.stdout.strip())
            
            behind_result = subprocess.run(
                ["git", "rev-list", "--count", f"{source_branch}..{target_branch}"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            commits_behind = int(behind_result.stdout.strip())
            
            # Get modified files
            diff_result = subprocess.run(
                ["git", "diff", "--name-only", f"{target_branch}...{source_branch}"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            files_modified = [f.strip() for f in diff_result.stdout.strip().split('\n') if f.strip()]
            
            # Assess risk based on number of files and commits
            risk_score = commits_ahead * 0.1 + len(files_modified) * 0.2
            if risk_score > 5:
                risk_assessment = "high"
            elif risk_score > 2:
                risk_assessment = "medium"
            else:
                risk_assessment = "low"
            
            # Predict potential merge conflicts (simplified)
            merge_conflicts_predicted = self._predict_merge_conflicts(source_branch, target_branch)
            
            return BranchAnalysis(
                branch_name=source_branch,
                base_branch=target_branch,
                commits_ahead=commits_ahead,
                commits_behind=commits_behind,
                files_modified=files_modified,
                total_complexity_change=0.0,  # Would need detailed analysis
                risk_assessment=risk_assessment,
                merge_conflicts_predicted=merge_conflicts_predicted
            )
            
        except (subprocess.CalledProcessError, ValueError) as e:
            logger.error(f"Failed to analyze branch differences: {e}")
            return None
    
    def _predict_merge_conflicts(self, source_branch: str, target_branch: str) -> List[str]:
        """Predict potential merge conflicts between branches."""
        try:
            # Get files modified in both branches
            source_files = set(self._get_modified_files_in_branch(source_branch, target_branch))
            target_files = set(self._get_modified_files_in_branch(target_branch, source_branch))
            
            # Files modified in both branches are potential conflicts
            potential_conflicts = list(source_files.intersection(target_files))
            
            return potential_conflicts
            
        except Exception as e:
            logger.error(f"Failed to predict merge conflicts: {e}")
            return []
    
    def _get_modified_files_in_branch(self, branch: str, base_branch: str) -> List[str]:
        """Get files modified in a branch compared to base."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_branch}...{branch}"],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def store_evolution_in_graph(self, evolution: CodeEvolution) -> bool:
        """Store code evolution data in Neo4j graph database."""
        if not self.graph_client:
            logger.warning("No graph client available for storing evolution data")
            return False
        
        try:
            # Create or update CodeEvolution node
            cypher = """
            MERGE (ce:CodeEvolution {file_path: $file_path})
            SET ce.growth_rate = $growth_rate,
                ce.complexity_trend = $complexity_trend,
                ce.last_updated = datetime(),
                ce.commit_count = $commit_count
            RETURN ce
            """
            
            result = self.graph_client.execute_query(cypher, {
                "file_path": evolution.file_path,
                "growth_rate": evolution.growth_rate,
                "complexity_trend": evolution.complexity_trend,
                "commit_count": len(evolution.commits)
            })
            
            # Store commits
            for commit in evolution.commits[:5]:  # Store last 5 commits
                self._store_commit_in_graph(commit, evolution.file_path)
            
            # Store size history
            for date, size in evolution.size_history:
                self._store_size_history_in_graph(evolution.file_path, date, size)
            
            logger.info(f"Stored evolution data for {evolution.file_path} in graph database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store evolution in graph: {e}")
            return False
    
    def _store_commit_in_graph(self, commit: GitCommit, file_path: str) -> None:
        """Store a commit in the graph database."""
        cypher = """
        MERGE (c:GitCommit {hash: $hash})
        SET c.short_hash = $short_hash,
            c.author = $author,
            c.email = $email,
            c.date = datetime($date),
            c.message = $message,
            c.branch = $branch,
            c.lines_added = $lines_added,
            c.lines_deleted = $lines_deleted,
            c.complexity_delta = $complexity_delta
        
        MERGE (ce:CodeEvolution {file_path: $file_path})
        MERGE (c)-[:MODIFIES]->(ce)
        """
        
        self.graph_client.execute_query(cypher, {
            "hash": commit.hash,
            "short_hash": commit.short_hash,
            "author": commit.author,
            "email": commit.email,
            "date": commit.date.isoformat(),
            "message": commit.message,
            "branch": commit.branch,
            "lines_added": commit.lines_added,
            "lines_deleted": commit.lines_deleted,
            "complexity_delta": commit.complexity_delta,
            "file_path": file_path
        })
    
    def _store_size_history_in_graph(self, file_path: str, date: datetime, size: int) -> None:
        """Store size history point in graph database."""
        cypher = """
        MERGE (ce:CodeEvolution {file_path: $file_path})
        MERGE (sh:SizeHistory {file_path: $file_path, date: datetime($date)})
        SET sh.size = $size
        MERGE (ce)-[:HAS_SIZE_HISTORY]->(sh)
        """
        
        self.graph_client.execute_query(cypher, {
            "file_path": file_path,
            "date": date.isoformat(),
            "size": size
        })
    
    def get_complexity_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get complexity trends for files over the specified period."""
        if not self.graph_client:
            return {}
        
        try:
            cypher = """
            MATCH (ce:CodeEvolution)
            WHERE ce.last_updated >= datetime() - duration({days: $days})
            RETURN ce.file_path as file_path,
                   ce.growth_rate as growth_rate,
                   ce.complexity_trend as complexity_trend,
                   ce.commit_count as commit_count
            ORDER BY ce.growth_rate DESC
            """
            
            results = self.graph_client.execute_query(cypher, {"days": days})
            
            trends = {
                "files_analyzed": len(results),
                "high_growth_files": [r for r in results if r["growth_rate"] > 5],
                "increasing_complexity": [r for r in results if r["complexity_trend"] == "increasing"],
                "stable_files": [r for r in results if r["complexity_trend"] == "stable"],
                "improving_files": [r for r in results if r["complexity_trend"] == "decreasing"]
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get complexity trends: {e}")
            return {}
    
    def generate_evolution_report(self, file_path: str) -> Dict[str, Any]:
        """Generate a comprehensive evolution report for a file."""
        evolution = self.track_file_evolution(file_path)
        if not evolution:
            return {"error": "Could not track file evolution"}
        
        report = {
            "file_path": evolution.file_path,
            "analysis_date": datetime.now().isoformat(),
            "commit_history": {
                "total_commits": len(evolution.commits),
                "recent_commits": [
                    {
                        "hash": c.short_hash,
                        "author": c.author,
                        "date": c.date.isoformat(),
                        "message": c.message[:100] + "..." if len(c.message) > 100 else c.message,
                        "lines_changed": c.lines_added + c.lines_deleted
                    }
                    for c in evolution.commits[:5]
                ]
            },
            "size_evolution": {
                "growth_rate": evolution.growth_rate,
                "size_history": [
                    {"date": date.isoformat(), "lines": lines}
                    for date, lines in evolution.size_history
                ]
            },
            "complexity_evolution": {
                "trend": evolution.complexity_trend,
                "complexity_history": [
                    {"date": date.isoformat(), "complexity": complexity}
                    for date, complexity in evolution.complexity_history
                ]
            },
            "recommendations": self._generate_evolution_recommendations(evolution)
        }
        
        return report
    
    def _generate_evolution_recommendations(self, evolution: CodeEvolution) -> List[str]:
        """Generate recommendations based on file evolution."""
        recommendations = []
        
        # High growth rate
        if evolution.growth_rate > 10:
            recommendations.append(
                f"File is growing rapidly ({evolution.growth_rate:.1f} lines/day). "
                "Consider refactoring to prevent it from becoming too large."
            )
        
        # Increasing complexity
        if evolution.complexity_trend == "increasing":
            recommendations.append(
                "Complexity is increasing over time. Consider breaking down complex functions "
                "or extracting helper methods."
            )
        
        # Many recent commits
        if len(evolution.commits) > 20:
            recommendations.append(
                f"File has {len(evolution.commits)} recent commits, indicating high activity. "
                "Ensure proper testing and code review processes."
            )
        
        # Large size changes
        recent_sizes = [size for _, size in evolution.size_history[:5]]
        if recent_sizes and max(recent_sizes) - min(recent_sizes) > 500:
            recommendations.append(
                "File size has changed significantly recently. "
                "Review changes for potential refactoring opportunities."
            )
        
        if not recommendations:
            recommendations.append("File evolution looks healthy. Continue current practices.")
        
        return recommendations 