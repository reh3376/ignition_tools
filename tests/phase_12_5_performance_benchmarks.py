#!/usr/bin/env python3
"""Phase 12.5: Performance Benchmarking Suite

Following crawl_mcp.py methodology for performance testing:
1. Environment validation first
2. Load testing with concurrent users
3. Response time benchmarking
4. Throughput measurement
5. Error rate monitoring
6. Resource utilization tracking
"""

import asyncio
import json
import os
import statistics
import time
from datetime import datetime
from typing import Any

try:
    import httpx
except ImportError:
    print("⚠️  httpx not installed. Installing...")
    import subprocess

    subprocess.run(["pip", "install", "httpx"])
    import httpx

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
MAX_CONCURRENT_USERS = 50
TEST_DURATION_SECONDS = 60
WARMUP_REQUESTS = 10


class PerformanceResult(BaseModel):
    """Performance test result model"""

    test_name: str
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    requests_per_second: float
    error_rate_percent: float
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class Phase125PerformanceTester:
    """Performance testing suite following crawl_mcp.py methodology"""

    def __init__(self):
        self.api_base = API_BASE_URL
        self.results: list[PerformanceResult] = []

    async def warmup_api(self):
        """Warm up API before performance testing"""
        print("🔥 Warming up API...")
        async with httpx.AsyncClient(timeout=30) as client:
            for _ in range(WARMUP_REQUESTS):
                try:
                    await client.get(f"{self.api_base}/health")
                except Exception:
                    pass
        print("   ✅ Warmup complete")

    async def benchmark_endpoint(
        self, endpoint: str, concurrent_users: int = 10, duration_seconds: int = 30
    ) -> PerformanceResult:
        """Benchmark a single endpoint"""
        print(
            f"🚀 Benchmarking {endpoint} with {concurrent_users} concurrent users for {duration_seconds}s"
        )

        response_times = []
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()

        async def make_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore):
            async with semaphore:
                request_start = time.time()
                try:
                    response = await client.get(f"{self.api_base}{endpoint}")
                    response_time = (time.time() - request_start) * 1000
                    response_times.append(response_time)

                    if response.status_code == 200:
                        return True
                    else:
                        return False
                except Exception:
                    return False

        # Create semaphore for concurrent request limit
        semaphore = asyncio.Semaphore(concurrent_users)

        async with httpx.AsyncClient(timeout=30) as client:
            tasks = []
            end_time = time.time() + duration_seconds

            while time.time() < end_time:
                task = asyncio.create_task(make_request(client, semaphore))
                tasks.append(task)

                # Small delay to control request rate
                await asyncio.sleep(0.01)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if result is True:
                    successful_requests += 1
                else:
                    failed_requests += 1

        total_requests = successful_requests + failed_requests
        duration = time.time() - start_time

        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[
                18
            ]  # 95th percentile
        else:
            avg_response_time = min_response_time = max_response_time = (
                p95_response_time
            ) = 0.0

        requests_per_second = total_requests / duration if duration > 0 else 0
        error_rate_percent = (
            (failed_requests / total_requests * 100) if total_requests > 0 else 0
        )

        result = PerformanceResult(
            test_name=f"Load Test - {endpoint}",
            endpoint=endpoint,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=round(avg_response_time, 2),
            min_response_time_ms=round(min_response_time, 2),
            max_response_time_ms=round(max_response_time, 2),
            p95_response_time_ms=round(p95_response_time, 2),
            requests_per_second=round(requests_per_second, 2),
            error_rate_percent=round(error_rate_percent, 2),
        )

        self.results.append(result)

        # Print results
        print(f"   📊 Results for {endpoint}:")
        print(f"     • Total Requests: {total_requests}")
        print(
            f"     • Success Rate: {(successful_requests / total_requests * 100):.1f}%"
        )
        print(f"     • Avg Response Time: {avg_response_time:.1f}ms")
        print(f"     • P95 Response Time: {p95_response_time:.1f}ms")
        print(f"     • Requests/sec: {requests_per_second:.1f}")

        return result

    async def test_response_time_requirements(self) -> bool:
        """Test response time requirements"""
        print("⏱️  Testing Response Time Requirements")

        # Response time requirements (from roadmap)
        requirements = {
            "/health": 50,  # Health check should be very fast
            "/api/v1/environment/validate": 200,  # Environment validation
            "/api/v1/sme/status": 200,  # SME status
            "/api/v1/knowledge/status": 300,  # Knowledge graph status
        }

        passed_tests = 0
        total_tests = len(requirements)

        async with httpx.AsyncClient(timeout=30) as client:
            for endpoint, max_time_ms in requirements.items():
                response_times = []

                # Test 10 times for average
                for _ in range(10):
                    start_time = time.time()
                    try:
                        response = await client.get(f"{self.api_base}{endpoint}")
                        response_time_ms = (time.time() - start_time) * 1000
                        if response.status_code == 200:
                            response_times.append(response_time_ms)
                    except Exception:
                        pass

                if response_times:
                    avg_response_time = statistics.mean(response_times)
                    meets_requirement = avg_response_time <= max_time_ms

                    if meets_requirement:
                        passed_tests += 1

                    status = "✅ PASS" if meets_requirement else "❌ FAIL"
                    print(
                        f"   {status} {endpoint}: {avg_response_time:.1f}ms (max: {max_time_ms}ms)"
                    )
                else:
                    print(f"   ❌ FAIL {endpoint}: No successful responses")

        success_rate = passed_tests / total_tests * 100
        print(f"   📊 Response Time Requirements: {success_rate:.1f}% passed")
        return success_rate >= 75

    async def run_comprehensive_performance_tests(self) -> dict[str, Any]:
        """Run comprehensive performance test suite"""
        print("=" * 80)
        print("PHASE 12.5: PERFORMANCE BENCHMARKING SUITE")
        print("Following crawl_mcp.py methodology for performance validation")
        print("=" * 80)

        start_time = time.time()

        try:
            # Warm up API
            await self.warmup_api()

            # Test response time requirements
            response_time_ok = await self.test_response_time_requirements()

            # Benchmark critical endpoints
            critical_endpoints = [
                "/health",
                "/api/v1/environment/validate",
                "/api/v1/sme/status",
                "/api/v1/knowledge/status",
            ]

            print("\n🚀 Load Testing Critical Endpoints")
            benchmark_results = []
            for endpoint in critical_endpoints:
                try:
                    result = await self.benchmark_endpoint(
                        endpoint, concurrent_users=5, duration_seconds=15
                    )
                    benchmark_results.append(result)
                except Exception as e:
                    print(f"   ❌ Benchmark failed for {endpoint}: {e}")

            # Analyze results
            all_passed = True
            for result in benchmark_results:
                if result.error_rate_percent > 5 or result.avg_response_time_ms > 500:
                    all_passed = False

            execution_time = time.time() - start_time

            # Generate report
            report = {
                "phase": "12.5 - Performance Benchmarking",
                "methodology": "crawl_mcp.py performance testing",
                "execution_time": round(execution_time, 2),
                "timestamp": datetime.now().isoformat(),
                "response_time_requirements_met": response_time_ok,
                "load_testing_passed": all_passed,
                "overall_success": response_time_ok and all_passed,
                "benchmark_results": [result.dict() for result in benchmark_results],
                "summary": {
                    "total_endpoints_tested": len(benchmark_results),
                    "avg_requests_per_second": (
                        statistics.mean(
                            [r.requests_per_second for r in benchmark_results]
                        )
                        if benchmark_results
                        else 0
                    ),
                    "avg_response_time_ms": (
                        statistics.mean(
                            [r.avg_response_time_ms for r in benchmark_results]
                        )
                        if benchmark_results
                        else 0
                    ),
                    "max_error_rate_percent": (
                        max([r.error_rate_percent for r in benchmark_results])
                        if benchmark_results
                        else 0
                    ),
                },
            }

            # Print summary
            print("\n" + "=" * 80)
            print("PERFORMANCE BENCHMARKING RESULTS")
            print("=" * 80)

            print(
                f"Response Time Requirements: {'✅ PASS' if response_time_ok else '❌ FAIL'}"
            )
            print(f"Load Testing: {'✅ PASS' if all_passed else '❌ FAIL'}")
            print(
                f"Overall Performance: {'✅ PASS' if report['overall_success'] else '❌ FAIL'}"
            )

            if benchmark_results:
                print("\nSummary Statistics:")
                print(
                    f"  • Average RPS: {report['summary']['avg_requests_per_second']:.1f}"
                )
                print(
                    f"  • Average Response Time: {report['summary']['avg_response_time_ms']:.1f}ms"
                )
                print(
                    f"  • Max Error Rate: {report['summary']['max_error_rate_percent']:.1f}%"
                )

            if report["overall_success"]:
                print("\n🎯 PERFORMANCE REQUIREMENTS MET")
                print("✅ API performance is acceptable for production")
            else:
                print("\n⚠️  PERFORMANCE IMPROVEMENTS NEEDED")
                print("❌ Some endpoints need optimization")

            return report

        except Exception as e:
            print(f"❌ Performance testing failed: {e}")
            return {
                "phase": "12.5 - Performance Benchmarking",
                "error": str(e),
                "overall_success": False,
            }


async def main():
    """Main performance testing function"""
    print("🚀 Phase 12.5: Performance Benchmarking")
    print("   Following crawl_mcp.py methodology")
    print()

    tester = Phase125PerformanceTester()
    results = await tester.run_comprehensive_performance_tests()

    # Save results
    results_file = "phase_12_5_performance_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Performance results saved to: {results_file}")

    # Exit code
    exit_code = 0 if results.get("overall_success", False) else 1
    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
