"""Performance and benchmark tests for IGN Scripts."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from src.ignition.generators.script_generator import IgnitionScriptGenerator
from typing import Any, Self


class TestPerformance:
    """Performance test cases for IGN Scripts."""

    @pytest.mark.performance
    def test_script_generator_initialization_speed(self: Self, benchmark: Any):
        """Benchmark script generator initialization."""

        def create_generator():
            return IgnitionScriptGenerator()

        result = benchmark(create_generator)
        assert result is not None

    @pytest.mark.performance
    def test_template_listing_speed(self: Self, script_generator, benchmark):
        """Benchmark template listing performance."""

        def list_templates():
            return script_generator.list_templates()

        templates = benchmark(list_templates)
        assert isinstance(templates, list)

    @pytest.mark.performance
    def test_single_script_generation_speed(self: Self, script_generator, sample_button_config, benchmark):
        """Benchmark single script generation."""

        def generate_script():
            return script_generator.generate_script(sample_button_config["template"], sample_button_config)

        result = benchmark(generate_script)
        assert result is not None
        assert len(result) > 0

    @pytest.mark.performance
    def test_batch_script_generation(self: Self, script_generator, performance_monitor):
        """Test batch script generation performance."""
        configs = []
        for i in range(50):
            config = {
                "template": "vision/button_click_handler.jinja2",
                "component_name": f"BatchButton_{i}",
                "action_type": "navigation",
                "target_window": f"Window_{i}",
                "logging_enabled": True,
            }
            configs.append(config)

        performance_monitor.start()

        results = []
        for config in configs:
            result = script_generator.generate_script(config["template"], config)
            results.append(result)

        performance_monitor.stop()

        duration = performance_monitor.get_duration()
        memory_usage = performance_monitor.get_memory_usage()

        assert len(results) == 50
        assert all(result is not None for result in results)
        assert duration < 10.0  # Should complete in under 10 seconds

        # Log performance metrics
        print(f"Batch generation: {duration:.2f}s for 50 scripts")
        print(f"Memory usage: {memory_usage / 1024 / 1024:.2f} MB")

    @pytest.mark.performance
    def test_concurrent_script_generation(self: Self, script_generator, performance_monitor):
        """Test concurrent script generation performance."""
        configs = []
        for i in range(20):
            config = {
                "template": "vision/button_click_handler.jinja2",
                "component_name": f"ConcurrentButton_{i}",
                "action_type": "navigation",
                "target_window": f"Window_{i}",
                "logging_enabled": True,
            }
            configs.append(config)

        def generate_single_script(config: Any):
            return script_generator.generate_script(config["template"], config)

        performance_monitor.start()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_single_script, config) for config in configs]
            results = [future.result() for future in as_completed(futures)]

        performance_monitor.stop()

        duration = performance_monitor.get_duration()
        memory_usage = performance_monitor.get_memory_usage()

        assert len(results) == 20
        assert all(result is not None for result in results)
        assert duration < 5.0  # Should be faster than sequential

        print(f"Concurrent generation: {duration:.2f}s for 20 scripts")
        print(f"Memory usage: {memory_usage / 1024 / 1024:.2f} MB")

    @pytest.mark.performance
    def test_template_parsing_performance(self: Self, script_generator, benchmark):
        """Benchmark template parsing performance."""
        template_name = "vision/button_click_handler.jinja2"
        context = {
            "component_name": "PerformanceTest",
            "action_type": "navigation",
            "target_window": "TestWindow",
        }

        def parse_template():
            return script_generator.generate_script(template_name, context)

        result = benchmark(parse_template)
        assert "PerformanceTest" in result

    @pytest.mark.performance
    def test_large_context_handling(self: Self, script_generator, performance_monitor):
        """Test performance with large context objects."""
        # Create a large context with many variables
        large_context = {
            "template": "vision/button_click_handler.jinja2",
            "component_name": "LargeContextButton",
            "action_type": "custom",
            "logging_enabled": True,
            "custom_code": "# " + "Large comment block\n" * 1000,
            "window_params": {f"param_{i}": f"value_{i}" for i in range(1000)},
            "metadata": {
                "large_data": list(range(10000)),
                "nested": {"deep": {"structure": {f"key_{i}": f"value_{i}" for i in range(100)}}},
            },
        }

        performance_monitor.start()

        result = script_generator.generate_script(large_context["template"], large_context)

        performance_monitor.stop()

        duration = performance_monitor.get_duration()
        memory_usage = performance_monitor.get_memory_usage()

        assert result is not None
        assert "LargeContextButton" in result
        assert duration < 5.0  # Should handle large contexts reasonably fast

        print(f"Large context processing: {duration:.2f}s")
        print(f"Memory usage: {memory_usage / 1024 / 1024:.2f} MB")

    @pytest.mark.performance
    def test_memory_usage_stability(self: Self, script_generator, performance_monitor):
        """Test memory usage stability over multiple generations."""
        initial_memory = performance_monitor.process.memory_info().rss

        config = {
            "template": "vision/button_click_handler.jinja2",
            "component_name": "MemoryTestButton",
            "action_type": "navigation",
            "target_window": "TestWindow",
        }

        memory_readings = []

        for i in range(100):
            script_generator.generate_script(config["template"], config)

            if i % 10 == 0:  # Take readings every 10 iterations
                current_memory = performance_monitor.process.memory_info().rss
                memory_readings.append(current_memory)

        final_memory = performance_monitor.process.memory_info().rss
        memory_growth = final_memory - initial_memory

        # Memory should not grow excessively
        assert memory_growth < 50 * 1024 * 1024  # Less than 50MB growth

        # Check for memory leak patterns
        if len(memory_readings) > 5:
            recent_trend = memory_readings[-3:]
            avg_recent = sum(recent_trend) / len(recent_trend)
            early_readings = memory_readings[:3]
            avg_early = sum(early_readings) / len(early_readings)

            growth_rate = (avg_recent - avg_early) / avg_early
            assert growth_rate < 0.1  # Less than 10% growth

        print(f"Memory growth after 100 generations: {memory_growth / 1024 / 1024:.2f} MB")

    @pytest.mark.performance
    def test_jinja2_filter_performance(self: Self, script_generator, benchmark):
        """Benchmark custom Jinja2 filter performance."""
        test_data = {
            "complex_object": {
                "lists": [list(range(100)) for _ in range(10)],
                "dicts": {f"key_{i}": {"nested": list(range(50))} for i in range(20)},
                "booleans": [True, False] * 50,
                "nulls": [None] * 100,
            }
        }

        jython_filter = script_generator.env.filters["jython_json"]

        def apply_filter():
            return jython_filter(test_data)

        result = benchmark(apply_filter)
        assert isinstance(result, str)
        assert "True" in result  # Python True -> Jython True

    @pytest.mark.performance
    def test_template_caching_effectiveness(self: Self, script_generator, performance_monitor):
        """Test effectiveness of template caching."""
        template_name = "vision/button_click_handler.jinja2"
        base_config = {
            "component_name": "CacheTestButton",
            "action_type": "navigation",
            "target_window": "TestWindow",
        }

        # First generation (cold cache)
        performance_monitor.start()
        script_generator.generate_script(template_name, base_config)
        performance_monitor.stop()
        cold_duration = performance_monitor.get_duration()

        # Subsequent generations (warm cache)
        warm_durations = []
        for i in range(10):
            config = base_config.copy()
            config["component_name"] = f"CacheTestButton_{i}"

            start_time = time.time()
            script_generator.generate_script(template_name, config)
            end_time = time.time()

            warm_durations.append(end_time - start_time)

        avg_warm_duration = sum(warm_durations) / len(warm_durations)

        # Warm cache should be faster than cold cache
        # (Note: This may not always be true with Jinja2's built-in caching)
        print(f"Cold cache duration: {cold_duration:.4f}s")
        print(f"Average warm cache duration: {avg_warm_duration:.4f}s")
        print(f"Cache effectiveness: {((cold_duration - avg_warm_duration) / cold_duration * 100):.1f}%")

    @pytest.mark.performance
    def test_cli_performance(self: Self, performance_monitor, temp_dir):
        """Test CLI performance for script generation."""
        from click.testing import CliRunner

        from src.core.enhanced_cli import main as cli

        runner = CliRunner()
        output_file = temp_dir / "cli_perf_test.py"

        performance_monitor.start()

        result = runner.invoke(
            cli,
            [
                "script",
                "generate",
                "--template",
                "vision/button_click_handler.jinja2",
                "--component-name",
                "CLIPerformanceTest",
                "--output",
                str(output_file),
            ],
        )

        performance_monitor.stop()

        duration = performance_monitor.get_duration()

        assert result.exit_code == 0
        assert output_file.exists()
        assert duration < 3.0  # CLI should be reasonably fast

        print(f"CLI generation time: {duration:.2f}s")

    @pytest.mark.slow
    @pytest.mark.performance
    def test_stress_test_script_generation(self: Self, script_generator: Any):
        """Stress test with many script generations."""
        import gc

        script_generator.__class__.__dict__.get("_memory_baseline", 0)

        configs = []
        for i in range(500):
            config = {
                "template": "vision/button_click_handler.jinja2",
                "component_name": f"StressButton_{i}",
                "action_type": ["navigation", "tag_write", "popup", "custom"][i % 4],
                "target_window": f"Window_{i}" if i % 4 == 0 else None,
                "target_tag": f"[default]Tag_{i}" if i % 4 == 1 else None,
                "popup_window": f"Popup_{i}" if i % 4 == 2 else None,
                "custom_code": f"print('Custom code {i}')" if i % 4 == 3 else None,
                "logging_enabled": i % 2 == 0,
            }
            configs.append(config)

        start_time = time.time()

        successful_generations = 0
        for i, config in enumerate(configs):
            try:
                result = script_generator.generate_script(config["template"], config)
                if result and len(result) > 0:
                    successful_generations += 1

                # Periodic garbage collection
                if i % 100 == 0:
                    gc.collect()

            except Exception as e:
                print(f"Generation {i} failed: {e}")

        end_time = time.time()
        duration = end_time - start_time

        success_rate = successful_generations / len(configs) * 100
        avg_time_per_script = duration / len(configs)

        assert success_rate > 95  # At least 95% success rate
        assert avg_time_per_script < 0.1  # Less than 100ms per script on average

        print("Stress test results:")
        print(f"  Total scripts: {len(configs)}")
        print(f"  Successful: {successful_generations}")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Total time: {duration:.2f}s")
        print(f"  Avg time per script: {avg_time_per_script:.4f}s")
