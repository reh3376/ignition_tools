"""Enhanced wrapper for Ignition system.tag functions."""

from dataclasses import dataclass
from typing import Any

from .wrapper_base import (
    IgnitionWrapperBase,
    WrapperError,
    system,
    validate_tag_paths,
    wrapper_function,
)


@dataclass
class TagResult:
    """Enhanced result object for tag operations."""

    tag_path: str
    value: Any
    quality: int
    quality_name: str
    timestamp: float
    success: bool
    error_message: str | None = None


class SystemTagWrapper(IgnitionWrapperBase):
    """Enhanced wrapper for system.tag functions."""

    QUALITY_CODES = {
        192: "GOOD",
        68: "BAD_NOT_CONNECTED",
        72: "BAD_DEVICE_FAILURE",
        76: "BAD_SENSOR_FAILURE",
        80: "BAD_LAST_KNOWN_VALUE",
        84: "BAD_COMM_FAILURE",
        88: "BAD_OUT_OF_SERVICE",
        400: "UNCERTAIN_LAST_USABLE_VALUE",
        404: "UNCERTAIN_SENSOR_NOT_ACCURATE",
        408: "UNCERTAIN_EU_EXCEEDED",
        412: "UNCERTAIN_SUB_NORMAL",
    }

    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped tag functions."""
        return ["read_blocking", "write_blocking", "read_async", "write_async"]

    def get_tag_quality_name(self, quality_code: int) -> str:
        """Get human-readable quality name from quality code."""
        return self.QUALITY_CODES.get(quality_code, f"UNKNOWN_QUALITY_{quality_code}")

    @wrapper_function
    def read_blocking(self, tag_paths: str | list[str], timeout_ms: int = 45000) -> list[TagResult]:
        """Enhanced blocking tag read with comprehensive error handling."""
        if self.config.validate_inputs:
            tag_paths = validate_tag_paths(tag_paths)
            if timeout_ms <= 0:
                raise WrapperError("Timeout must be positive")

        if isinstance(tag_paths, str):
            tag_paths = [tag_paths]

        try:
            qualified_values = system.tag.readBlocking(tag_paths, timeout_ms)

            results = []
            for i, qv in enumerate(qualified_values):
                tag_path = tag_paths[i] if i < len(tag_paths) else f"unknown_{i}"
                quality_name = self.get_tag_quality_name(qv.quality)

                result = TagResult(
                    tag_path=tag_path,
                    value=qv.value,
                    quality=qv.quality,
                    quality_name=quality_name,
                    timestamp=qv.timestamp,
                    success=qv.quality == 192,
                )

                if not result.success:
                    result.error_message = f"Tag quality is {quality_name} ({qv.quality})"

                results.append(result)

            successful_reads = sum(1 for r in results if r.success)
            self._log_operation(
                "Tag read completed",
                f"{successful_reads}/{len(results)} tags read successfully",
            )

            return results

        except Exception as e:
            raise WrapperError(f"Tag read operation failed: {e}", original_error=e) from e

    @wrapper_function
    def write_blocking(
        self,
        tag_paths: str | list[str],
        values: Any | list[Any],
        timeout_ms: int = 45000,
    ) -> list[dict[str, Any]]:
        """Enhanced blocking tag write with comprehensive error handling."""
        if self.config.validate_inputs:
            tag_paths = validate_tag_paths(tag_paths)
            if timeout_ms <= 0:
                raise WrapperError("Timeout must be positive")

        if isinstance(tag_paths, str):
            tag_paths = [tag_paths]
        if not isinstance(values, list):
            values = [values]

        if len(tag_paths) != len(values):
            raise WrapperError(f"Tag path count ({len(tag_paths)}) must match value count ({len(values)})")

        try:
            quality_codes = system.tag.writeBlocking(tag_paths, values, timeout_ms)

            results = []
            for i, quality_code in enumerate(quality_codes):
                tag_path = tag_paths[i] if i < len(tag_paths) else f"unknown_{i}"
                code = quality_code.code if hasattr(quality_code, "code") else quality_code
                quality_name = self.get_tag_quality_name(code)

                result = {
                    "tag_path": tag_path,
                    "quality": code,
                    "quality_name": quality_name,
                    "success": code == 192,
                    "error_message": None,
                }

                if not result["success"]:
                    result["error_message"] = f"Write failed with quality {quality_name} ({code})"

                results.append(result)

            successful_writes = sum(1 for r in results if r["success"])
            self._log_operation(
                "Tag write completed",
                f"{successful_writes}/{len(results)} tags written successfully",
            )

            return results

        except Exception as e:
            raise WrapperError(f"Tag write operation failed: {e}", original_error=e) from e
