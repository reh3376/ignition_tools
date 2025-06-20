"""Enhanced wrapper for Ignition system.db functions."""

from dataclasses import dataclass
from typing import Any

from .wrapper_base import (
    IgnitionWrapperBase,
    WrapperError,
    format_sql_query,
    system,
    validate_database_name,
    wrapper_function,
)


@dataclass
class QueryResult:
    """Enhanced result object for database queries."""

    query: str
    database: str
    row_count: int
    execution_time_ms: float
    success: bool
    data: Any = None
    error_message: str | None = None


class SystemDbWrapper(IgnitionWrapperBase):
    """Enhanced wrapper for system.db functions."""

    def get_wrapped_functions(self) -> list[str]:
        """Get list of wrapped database functions."""
        return ["run_query", "run_update_query", "run_prep_query", "run_prep_update"]

    @wrapper_function
    def run_query(self, query: str, database: str = "") -> QueryResult:
        """Enhanced database query with error handling and validation."""
        if self.config.validate_inputs:
            query = format_sql_query(query)
            database = validate_database_name(database)

        import time

        start_time = time.time()

        try:
            result_data = system.db.runQuery(query, database)
            execution_time = (time.time() - start_time) * 1000

            row_count = len(result_data) if result_data else 0

            result = QueryResult(
                query=query,
                database=database or "default",
                row_count=row_count,
                execution_time_ms=execution_time,
                success=True,
                data=result_data,
            )

            self._log_operation(
                "Database query completed",
                f"Returned {row_count} rows in {execution_time:.2f}ms",
            )

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            result = QueryResult(
                query=query,
                database=database or "default",
                row_count=0,
                execution_time_ms=execution_time,
                success=False,
                error_message=str(e),
            )
            raise WrapperError(f"Database query failed: {e}", original_error=e) from e

    @wrapper_function
    def run_update_query(self, query: str, database: str = "") -> dict[str, Any]:
        """Enhanced database update query with error handling."""
        if self.config.validate_inputs:
            query = format_sql_query(query)
            database = validate_database_name(database)

        import time

        start_time = time.time()

        try:
            affected_rows = system.db.runUpdateQuery(query, database)
            execution_time = (time.time() - start_time) * 1000

            result = {
                "query": query,
                "database": database or "default",
                "affected_rows": affected_rows,
                "execution_time_ms": execution_time,
                "success": True,
            }

            self._log_operation(
                "Database update completed",
                f"Affected {affected_rows} rows in {execution_time:.2f}ms",
            )

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            raise WrapperError(f"Database update failed: {e}", original_error=e) from e
