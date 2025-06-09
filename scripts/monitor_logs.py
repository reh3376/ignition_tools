#!/usr/bin/env python3
"""Docker log monitoring and analysis script for IGN Scripts testing."""

import argparse
import json
import re
import subprocess
import time
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class LogAnalyzer:
    """Analyze Docker logs for performance insights and optimization opportunities."""
    
    def __init__(self):
        self.containers = ["ign_scripts_test", "ign_scripts_dev", "ign_scripts_benchmark"]
        self.log_patterns = {
            "errors": [
                r"ERROR",
                r"FAILED",
                r"Exception",
                r"Traceback",
                r"❌"
            ],
            "warnings": [
                r"WARNING",
                r"WARN",
                r"⚠️"
            ],
            "performance": [
                r"duration.*?(\d+\.?\d*)\s*s",
                r"Memory usage.*?(\d+\.?\d*)\s*MB",
                r"(\d+\.?\d*)\s*ms",
                r"took\s+(\d+\.?\d*)\s*seconds?"
            ],
            "test_results": [
                r"(\d+)\s+passed",
                r"(\d+)\s+failed",
                r"(\d+)\s+skipped",
                r"✅\s+(.+?)\s+passed",
                r"❌\s+(.+?)\s+failed"
            ]
        }
        
    def get_container_logs(self, container: str, since: Optional[str] = None) -> str:
        """Get logs from a specific container."""
        try:
            cmd = ["docker", "logs", container]
            if since:
                cmd.extend(["--since", since])
                
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout + result.stderr
            else:
                print(f"⚠️ Could not get logs for {container}: {result.stderr}")
                return ""
        except Exception as e:
            print(f"❌ Error getting logs for {container}: {e}")
            return ""
    
    def parse_log_entry(self, line: str) -> Dict[str, Any]:
        """Parse a single log line and extract structured information."""
        entry = {
            "timestamp": None,
            "level": "INFO",
            "message": line.strip(),
            "container": None,
            "metrics": {}
        }
        
        # Extract timestamp (various formats)
        timestamp_patterns = [
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})",
            r"(\d{2}:\d{2}:\d{2})",
            r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                entry["timestamp"] = match.group(1)
                break
        
        # Extract log level
        level_pattern = r"\[(DEBUG|INFO|WARNING|ERROR|CRITICAL)\]"
        level_match = re.search(level_pattern, line)
        if level_match:
            entry["level"] = level_match.group(1)
        
        # Extract performance metrics
        for metric_type, patterns in self.log_patterns["performance"]:
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    if match.groups():
                        value = float(match.group(1))
                        if "duration" in pattern or "seconds" in pattern:
                            entry["metrics"]["duration_seconds"] = value
                        elif "MB" in pattern:
                            entry["metrics"]["memory_mb"] = value
                        elif "ms" in pattern:
                            entry["metrics"]["duration_ms"] = value
        
        return entry
    
    def analyze_logs(self, container: str, since: Optional[str] = None) -> Dict[str, Any]:
        """Analyze logs from a container and return insights."""
        logs = self.get_container_logs(container, since)
        if not logs:
            return {"error": f"No logs available for {container}"}
        
        lines = logs.split('\n')
        parsed_entries = [self.parse_log_entry(line) for line in lines if line.strip()]
        
        analysis = {
            "container": container,
            "total_lines": len(lines),
            "entries": len(parsed_entries),
            "levels": Counter(),
            "errors": [],
            "warnings": [],
            "performance_metrics": {
                "durations": [],
                "memory_usage": [],
                "test_results": {}
            },
            "patterns": defaultdict(int),
            "recommendations": []
        }
        
        # Analyze each entry
        for entry in parsed_entries:
            analysis["levels"][entry["level"]] += 1
            
            # Collect errors and warnings
            message = entry["message"]
            for pattern in self.log_patterns["errors"]:
                if re.search(pattern, message, re.IGNORECASE):
                    analysis["errors"].append({
                        "timestamp": entry["timestamp"],
                        "message": message[:200] + "..." if len(message) > 200 else message
                    })
            
            for pattern in self.log_patterns["warnings"]:
                if re.search(pattern, message, re.IGNORECASE):
                    analysis["warnings"].append({
                        "timestamp": entry["timestamp"],
                        "message": message[:200] + "..." if len(message) > 200 else message
                    })
            
            # Collect performance metrics
            if "duration_seconds" in entry["metrics"]:
                analysis["performance_metrics"]["durations"].append(entry["metrics"]["duration_seconds"])
            
            if "memory_mb" in entry["metrics"]:
                analysis["performance_metrics"]["memory_usage"].append(entry["metrics"]["memory_mb"])
            
            # Track test results
            for pattern in self.log_patterns["test_results"]:
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    if "passed" in pattern:
                        analysis["performance_metrics"]["test_results"]["passed"] = int(match.group(1))
                    elif "failed" in pattern:
                        analysis["performance_metrics"]["test_results"]["failed"] = int(match.group(1))
                    elif "skipped" in pattern:
                        analysis["performance_metrics"]["test_results"]["skipped"] = int(match.group(1))
        
        # Generate recommendations
        analysis["recommendations"] = self.generate_recommendations(analysis)
        
        return analysis
    
    def generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations based on log analysis."""
        recommendations = []
        
        # Error analysis
        error_count = len(analysis["errors"])
        if error_count > 10:
            recommendations.append(
                f"High error count ({error_count}). Review error patterns and add error handling."
            )
        
        # Performance analysis
        durations = analysis["performance_metrics"]["durations"]
        if durations:
            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)
            
            if avg_duration > 5.0:
                recommendations.append(
                    f"Average execution time is high ({avg_duration:.2f}s). Consider optimizing templates or caching."
                )
            
            if max_duration > 30.0:
                recommendations.append(
                    f"Maximum execution time is very high ({max_duration:.2f}s). Investigate performance bottlenecks."
                )
        
        # Memory analysis
        memory_usage = analysis["performance_metrics"]["memory_usage"]
        if memory_usage:
            max_memory = max(memory_usage)
            if max_memory > 500:  # 500MB
                recommendations.append(
                    f"High memory usage detected ({max_memory:.2f}MB). Consider memory optimization."
                )
        
        # Test failure analysis
        test_results = analysis["performance_metrics"]["test_results"]
        if "failed" in test_results and test_results["failed"] > 0:
            failed = test_results["failed"]
            total = test_results.get("passed", 0) + failed
            failure_rate = (failed / total) * 100 if total > 0 else 0
            
            if failure_rate > 10:
                recommendations.append(
                    f"High test failure rate ({failure_rate:.1f}%). Review failed tests and fix issues."
                )
        
        # Log level analysis
        if analysis["levels"]["ERROR"] > analysis["levels"]["INFO"] * 0.1:
            recommendations.append(
                "High error-to-info ratio detected. Review error handling and logging levels."
            )
        
        return recommendations
    
    def generate_report(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive report from multiple container analyses."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "containers": len(analyses),
            "summary": {
                "total_errors": 0,
                "total_warnings": 0,
                "avg_duration": 0,
                "max_memory": 0,
                "test_summary": {"passed": 0, "failed": 0, "skipped": 0}
            },
            "recommendations": [],
            "detailed_analyses": analyses
        }
        
        all_durations = []
        all_memory = []
        
        for analysis in analyses:
            if "error" in analysis:
                continue
                
            report["summary"]["total_errors"] += len(analysis["errors"])
            report["summary"]["total_warnings"] += len(analysis["warnings"])
            
            durations = analysis["performance_metrics"]["durations"]
            memory = analysis["performance_metrics"]["memory_usage"]
            test_results = analysis["performance_metrics"]["test_results"]
            
            all_durations.extend(durations)
            all_memory.extend(memory)
            
            for key in ["passed", "failed", "skipped"]:
                if key in test_results:
                    report["summary"]["test_summary"][key] += test_results[key]
            
            report["recommendations"].extend(analysis["recommendations"])
        
        # Calculate summary statistics
        if all_durations:
            report["summary"]["avg_duration"] = sum(all_durations) / len(all_durations)
        
        if all_memory:
            report["summary"]["max_memory"] = max(all_memory)
        
        # Deduplicate recommendations
        report["recommendations"] = list(set(report["recommendations"]))
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_file: Path) -> None:
        """Save the analysis report to a file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Report saved to {output_file}")
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print a summary of the analysis report."""
        print("\n" + "="*60)
        print("DOCKER LOG ANALYSIS SUMMARY")
        print("="*60)
        
        summary = report["summary"]
        
        print(f"📊 Containers analyzed: {report['containers']}")
        print(f"❌ Total errors: {summary['total_errors']}")
        print(f"⚠️ Total warnings: {summary['total_warnings']}")
        
        if summary["avg_duration"] > 0:
            print(f"⏱️ Average duration: {summary['avg_duration']:.2f}s")
        
        if summary["max_memory"] > 0:
            print(f"💾 Max memory usage: {summary['max_memory']:.2f}MB")
        
        test_summary = summary["test_summary"]
        if any(test_summary.values()):
            total_tests = sum(test_summary.values())
            print(f"🧪 Test results: {test_summary['passed']} passed, {test_summary['failed']} failed, {test_summary['skipped']} skipped (Total: {total_tests})")
        
        if report["recommendations"]:
            print("\n🔍 RECOMMENDATIONS:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"  {i}. {rec}")
        else:
            print("\n✅ No specific recommendations - system appears to be running well!")


def monitor_live_logs(containers: List[str], analyzer: LogAnalyzer) -> None:
    """Monitor container logs in real-time."""
    print("👀 Starting live log monitoring (Ctrl+C to stop)...")
    
    processes = []
    
    try:
        for container in containers:
            # Check if container is running
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", f"name={container}"],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                print(f"📋 Monitoring logs for {container}")
                proc = subprocess.Popen(
                    ["docker", "logs", "-f", container],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                processes.append((container, proc))
        
        if not processes:
            print("⚠️ No running containers found to monitor")
            return
        
        # Monitor logs in real-time
        while True:
            for container, proc in processes:
                if proc.poll() is not None:
                    continue
                
                try:
                    line = proc.stdout.readline()
                    if line:
                        # Parse and analyze each line
                        entry = analyzer.parse_log_entry(line)
                        
                        # Highlight important entries
                        if entry["level"] == "ERROR" or any(pattern in line for pattern in ["❌", "FAILED"]):
                            print(f"🔴 [{container}] {line.strip()}")
                        elif entry["level"] == "WARNING" or "⚠️" in line:
                            print(f"🟡 [{container}] {line.strip()}")
                        elif any(metric in entry["metrics"] for metric in ["duration_seconds", "memory_mb"]):
                            print(f"⚡ [{container}] {line.strip()}")
                        elif any(pattern in line for pattern in ["✅", "passed", "completed"]):
                            print(f"🟢 [{container}] {line.strip()}")
                        else:
                            # Regular log entry
                            print(f"📝 [{container}] {line.strip()}")
                            
                except Exception as e:
                    print(f"❌ Error reading from {container}: {e}")
                    break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopping log monitoring...")
    finally:
        # Clean up processes
        for container, proc in processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="IGN Scripts Docker Log Monitor and Analyzer")
    parser.add_argument("--analyze", action="store_true", help="Analyze logs from all containers")
    parser.add_argument("--container", type=str, help="Analyze logs from specific container")
    parser.add_argument("--since", type=str, help="Analyze logs since specific time (e.g., '1h', '30m')")
    parser.add_argument("--output", type=str, help="Output file for analysis report")
    parser.add_argument("--live", action="store_true", help="Monitor logs in real-time")
    parser.add_argument("--report-only", action="store_true", help="Generate report without printing summary")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    
    if args.live:
        monitor_live_logs(analyzer.containers, analyzer)
        return
    
    # Determine containers to analyze
    if args.container:
        containers = [args.container]
    else:
        containers = analyzer.containers
    
    # Analyze logs
    analyses = []
    for container in containers:
        print(f"🔍 Analyzing logs for {container}...")
        analysis = analyzer.analyze_logs(container, args.since)
        analyses.append(analysis)
    
    # Generate report
    report = analyzer.generate_report(analyses)
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        analyzer.save_report(report, output_path)
    else:
        # Default output location
        output_path = Path("test-results") / f"log_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.save_report(report, output_path)
    
    # Print summary unless report-only mode
    if not args.report_only:
        analyzer.print_summary(report)


if __name__ == "__main__":
    main() 