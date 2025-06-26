#!/usr/bin/env python3
"""Phase 12.5: Master Test Runner

Following crawl_mcp.py methodology for comprehensive testing orchestration:
1. Environment validation first
2. Comprehensive test suite execution
3. Performance benchmarking
4. Integration testing  
5. Contract validation
6. Detailed reporting
7. Production readiness assessment
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from phase_12_5_testing_suite import Phase125ComprehensiveTester
    from phase_12_5_performance_benchmarks import Phase125PerformanceTester
    from phase_12_5_integration_tests import Phase125IntegrationTester
except ImportError as e:
    print(f"❌ Error importing test modules: {e}")
    print("📋 Make sure all test files are in the tests/ directory")
    sys.exit(1)

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Phase125MasterResults(BaseModel):
    """Master test results model"""
    
    phase: str = "12.5 - Testing & Validation"
    methodology: str = "crawl_mcp.py systematic testing"
    start_time: str
    end_time: str = ""
    total_execution_time: float = 0.0
    
    # Test category results
    environment_validation: bool = False
    api_functionality: bool = False
    performance_benchmarking: bool = False
    integration_testing: bool = False
    
    # Detailed results
    comprehensive_test_results: dict[str, Any] = Field(default_factory=dict)
    performance_test_results: dict[str, Any] = Field(default_factory=dict)
    integration_test_results: dict[str, Any] = Field(default_factory=dict)
    
    # Summary metrics
    overall_success_rate: float = 0.0
    categories_passed: int = 0
    categories_total: int = 4
    completion_status: str = "NEEDS_IMPROVEMENT"
    
    # Production readiness
    production_ready: bool = False
    blocking_issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class Phase125MasterTestRunner:
    """Master test runner following crawl_mcp.py methodology"""

    def __init__(self):
        self.start_time = datetime.now()
        self.results = Phase125MasterResults(
            start_time=self.start_time.isoformat()
        )

    async def run_comprehensive_testing_suite(self) -> Phase125MasterResults:
        """Run complete Phase 12.5 testing suite"""
        print("=" * 90)
        print("PHASE 12.5: TESTING & VALIDATION - MASTER TEST RUNNER")
        print("Following crawl_mcp.py methodology for comprehensive validation")
        print("=" * 90)
        print(f"🚀 Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        execution_start = time.time()
        
        # === STEP 1: COMPREHENSIVE TESTING SUITE ===
        print("🔍 STEP 1: Comprehensive Testing Suite")
        print("-" * 50)
        try:
            comprehensive_tester = Phase125ComprehensiveTester()
            comprehensive_results = await comprehensive_tester.run_comprehensive_test_suite()
            
            self.results.comprehensive_test_results = comprehensive_results
            self.results.environment_validation = comprehensive_results.get("test_results", {}).get("environment_validation", False)
            self.results.api_functionality = comprehensive_results.get("test_results", {}).get("api_functionality", False)
            
            print(f"✅ Comprehensive testing completed")
            print(f"   Environment Validation: {'✅' if self.results.environment_validation else '❌'}")
            print(f"   API Functionality: {'✅' if self.results.api_functionality else '❌'}")
            
        except Exception as e:
            print(f"❌ Comprehensive testing failed: {e}")
            self.results.blocking_issues.append(f"Comprehensive testing failure: {e}")
        
        print()
        
        # === STEP 2: PERFORMANCE BENCHMARKING ===
        print("🚀 STEP 2: Performance Benchmarking")
        print("-" * 50)
        try:
            performance_tester = Phase125PerformanceTester()
            performance_results = await performance_tester.run_comprehensive_performance_tests()
            
            self.results.performance_test_results = performance_results
            self.results.performance_benchmarking = performance_results.get("overall_success", False)
            
            print(f"✅ Performance benchmarking completed")
            print(f"   Performance Requirements: {'✅' if self.results.performance_benchmarking else '❌'}")
            
            # Check for performance issues
            if not self.results.performance_benchmarking:
                summary = performance_results.get("summary", {})
                if summary.get("max_error_rate_percent", 0) > 5:
                    self.results.blocking_issues.append("High error rate detected in performance tests")
                if summary.get("avg_response_time_ms", 0) > 500:
                    self.results.blocking_issues.append("Slow response times detected")
                    
        except Exception as e:
            print(f"❌ Performance benchmarking failed: {e}")
            self.results.blocking_issues.append(f"Performance benchmarking failure: {e}")
        
        print()
        
        # === STEP 3: INTEGRATION TESTING ===
        print("🔗 STEP 3: CLI-to-API Integration Testing")
        print("-" * 50)
        try:
            integration_tester = Phase125IntegrationTester()
            integration_results = await integration_tester.run_comprehensive_integration_tests()
            
            self.results.integration_test_results = integration_results
            self.results.integration_testing = integration_results.get("overall_success", False)
            
            print(f"✅ Integration testing completed")
            print(f"   CLI-API Integration: {'✅' if self.results.integration_testing else '❌'}")
            
            # Check for integration issues
            if not self.results.integration_testing:
                mapping_rate = integration_results.get("mapping_consistency_rate", 0)
                if mapping_rate < 70:
                    self.results.blocking_issues.append("CLI-API mapping consistency below 70%")
                    
        except Exception as e:
            print(f"❌ Integration testing failed: {e}")
            self.results.blocking_issues.append(f"Integration testing failure: {e}")
        
        print()
        
        # === CALCULATE OVERALL RESULTS ===
        self.results.end_time = datetime.now().isoformat()
        self.results.total_execution_time = round(time.time() - execution_start, 2)
        
        # Count passed categories
        category_results = [
            self.results.environment_validation,
            self.results.api_functionality,
            self.results.performance_benchmarking,
            self.results.integration_testing,
        ]
        
        self.results.categories_passed = sum(category_results)
        self.results.overall_success_rate = (self.results.categories_passed / self.results.categories_total) * 100
        
        # Determine completion status
        if self.results.overall_success_rate >= 90:
            self.results.completion_status = "EXCELLENT"
        elif self.results.overall_success_rate >= 75:
            self.results.completion_status = "COMPLETED"
        elif self.results.overall_success_rate >= 50:
            self.results.completion_status = "NEEDS_IMPROVEMENT"
        else:
            self.results.completion_status = "CRITICAL_ISSUES"
        
        # Determine production readiness
        self.results.production_ready = (
            self.results.overall_success_rate >= 75 and
            len(self.results.blocking_issues) == 0 and
            self.results.environment_validation and
            self.results.api_functionality
        )
        
        # Generate recommendations
        self.results.recommendations = self._generate_master_recommendations()
        
        # === PRINT FINAL RESULTS ===
        self._print_master_summary()
        
        return self.results

    def _generate_master_recommendations(self) -> list[str]:
        """Generate master recommendations based on all test results"""
        recommendations = []
        
        # Critical issues first
        if self.results.blocking_issues:
            recommendations.append("🚨 CRITICAL: Address blocking issues before production deployment")
        
        # Environment issues
        if not self.results.environment_validation:
            recommendations.append("🔧 Fix environment setup - required for all other functionality")
        
        # API issues  
        if not self.results.api_functionality:
            recommendations.append("⚙️ Resolve API functionality issues - critical for Phase 12 completion")
        
        # Performance issues
        if not self.results.performance_benchmarking:
            recommendations.append("🚀 Optimize performance - required for production deployment")
        
        # Integration issues
        if not self.results.integration_testing:
            recommendations.append("🔗 Fix CLI-API integration inconsistencies")
        
        # Success recommendations
        if self.results.production_ready:
            recommendations.append("🎉 Excellent! Phase 12.5 completed successfully - ready for Phase 12.6")
        elif self.results.overall_success_rate >= 75:
            recommendations.append("✅ Good progress! Address remaining issues for production readiness")
        
        # Specific category recommendations
        comprehensive_results = self.results.comprehensive_test_results
        if comprehensive_results and "recommendations" in comprehensive_results:
            recommendations.extend(comprehensive_results["recommendations"])
        
        return recommendations

    def _print_master_summary(self):
        """Print comprehensive master summary"""
        print("=" * 90)
        print("PHASE 12.5: MASTER TEST RESULTS SUMMARY")
        print("=" * 90)
        
        # Test categories
        print("📊 TEST CATEGORY RESULTS:")
        print(f"   Environment Validation:    {'✅ PASS' if self.results.environment_validation else '❌ FAIL'}")
        print(f"   API Functionality:         {'✅ PASS' if self.results.api_functionality else '❌ FAIL'}")
        print(f"   Performance Benchmarking:  {'✅ PASS' if self.results.performance_benchmarking else '❌ FAIL'}")
        print(f"   Integration Testing:       {'✅ PASS' if self.results.integration_testing else '❌ FAIL'}")
        print()
        
        # Overall metrics
        print("📈 OVERALL METRICS:")
        print(f"   Success Rate: {self.results.overall_success_rate:.1f}%")
        print(f"   Categories Passed: {self.results.categories_passed}/{self.results.categories_total}")
        print(f"   Execution Time: {self.results.total_execution_time:.1f} seconds")
        print(f"   Completion Status: {self.results.completion_status}")
        print()
        
        # Production readiness
        print("🎯 PRODUCTION READINESS:")
        if self.results.production_ready:
            print("   ✅ READY FOR PRODUCTION")
            print("   ✅ All critical tests passed")
            print("   ✅ No blocking issues detected")
        else:
            print("   ❌ NOT READY FOR PRODUCTION")
            if self.results.blocking_issues:
                print("   🚨 Blocking Issues:")
                for issue in self.results.blocking_issues:
                    print(f"     • {issue}")
        print()
        
        # Phase 12.5 completion status
        print("🏁 PHASE 12.5 STATUS:")
        if self.results.completion_status == "EXCELLENT":
            print("   🌟 EXCELLENT COMPLETION")
            print("   ✅ All test categories passed with high scores")
            print("   ✅ Ready to proceed to Phase 12.6: Deployment & Infrastructure")
        elif self.results.completion_status == "COMPLETED":
            print("   ✅ PHASE 12.5 COMPLETED")
            print("   ✅ Testing & Validation requirements met")
            print("   ✅ Ready to proceed to Phase 12.6: Deployment & Infrastructure")
        elif self.results.completion_status == "NEEDS_IMPROVEMENT":
            print("   ⚠️  PHASE 12.5 NEEDS IMPROVEMENT")
            print("   ❌ Some test categories require attention")
            print("   📋 Address issues before proceeding to Phase 12.6")
        else:
            print("   🚨 CRITICAL ISSUES DETECTED")
            print("   ❌ Major problems prevent Phase 12.5 completion")
            print("   📋 Immediate attention required")
        print()
        
        # Recommendations
        if self.results.recommendations:
            print("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(self.results.recommendations[:5], 1):
                print(f"   {i}. {rec}")
            if len(self.results.recommendations) > 5:
                print(f"   ... and {len(self.results.recommendations) - 5} more")
        print()
        
        # Next steps
        print("🚀 NEXT STEPS:")
        if self.results.production_ready:
            print("   1. 📄 Review detailed test reports")
            print("   2. 🚀 Proceed to Phase 12.6: Deployment & Infrastructure")
            print("   3. 📋 Update project documentation")
        else:
            print("   1. 🔧 Address failing test categories")
            print("   2. 🔄 Re-run master test suite")
            print("   3. 📋 Review detailed test reports for specific issues")
        
        print("=" * 90)


async def main():
    """Main master test runner function"""
    print("🎯 Phase 12.5: Testing & Validation")
    print("   Master Test Runner")
    print("   Following crawl_mcp.py methodology")
    print()
    
    runner = Phase125MasterTestRunner()
    results = await runner.run_comprehensive_testing_suite()
    
    # Save comprehensive results
    results_file = "phase_12_5_master_results.json"
    with open(results_file, "w") as f:
        json.dump(results.dict(), f, indent=2, default=str)
    
    print(f"📄 Master results saved to: {results_file}")
    
    # Individual result files are saved by each test suite
    print("📄 Individual test reports:")
    print("   • phase_12_5_test_results.json (Comprehensive)")
    print("   • phase_12_5_performance_results.json (Performance)")
    print("   • phase_12_5_integration_results.json (Integration)")
    
    # Exit with appropriate code
    if results.completion_status in ["EXCELLENT", "COMPLETED"]:
        print("\n🎉 Phase 12.5 Testing & Validation COMPLETED!")
        exit_code = 0
    else:
        print("\n⚠️  Phase 12.5 requires additional work")
        exit_code = 1
    
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
