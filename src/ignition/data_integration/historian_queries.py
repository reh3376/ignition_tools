"""Historian Query collections.abc.Generator for Time Series Data.

This module provides query generation capabilities for various historian/time series databases
commonly used in industrial automation environments.

Features:
- Multi-historian support (InfluxDB, TimescaleDB, PI System, Wonderware, etc.)
- Optimized query generation for time series data
- Aggregation functions (avg, min, max, sum, count, etc.)
- Time range handling and optimization
- Tag-based filtering and grouping
- Performance-optimized queries for large datasets
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class HistorianType(Enum):
    """Supported historian database types."""

    INFLUXDB = "influxdb"
    TIMESCALEDB = "timescaledb"
    PI_SYSTEM = "pi_system"
    WONDERWARE = "wonderware"
    CANARY = "canary"
    IGNITION_HISTORIAN = "ignition_historian"


class AggregationType(Enum):
    """Supported aggregation types."""

    AVERAGE = "avg"
    MINIMUM = "min"
    MAXIMUM = "max"
    SUM = "sum"
    COUNT = "count"
    FIRST = "first"
    LAST = "last"
    STDDEV = "stddev"
    MEDIAN = "median"
    RANGE = "range"


class TimeUnit(Enum):
    """Time units for aggregation."""

    SECOND = "s"
    MINUTE = "m"
    HOUR = "h"
    DAY = "d"
    WEEK = "w"
    MONTH = "mo"
    YEAR = "y"


@dataclass
class TimeRange:
    """Time range specification for historian queries."""

    start_time: datetime
    end_time: datetime

    def to_string(self, historian_type: HistorianType) -> str:
        """Convert time range to historian-specific format."""
        if historian_type == HistorianType.INFLUXDB:
            return f"time >= '{self.start_time.isoformat()}' AND time <= '{self.end_time.isoformat()}'"
        elif historian_type == HistorianType.TIMESCALEDB:
            return f"timestamp >= '{self.start_time.isoformat()}' AND timestamp <= '{self.end_time.isoformat()}'"
        elif historian_type == HistorianType.IGNITION_HISTORIAN:
            # Ignition uses milliseconds since epoch
            start_ms = int(self.start_time.timestamp() * 1000)
            end_ms = int(self.end_time.timestamp() * 1000)
            return f"t_stamp >= {start_ms} AND t_stamp <= {end_ms}"
        else:
            return f"timestamp >= '{self.start_time.isoformat()}' AND timestamp <= '{self.end_time.isoformat()}'"

    def duration_hours(self) -> float:
        """Get duration in hours."""
        return (self.end_time - self.start_time).total_seconds() / 3600


@dataclass
class TagFilter:
    """Tag filtering specification."""

    tag_name: str
    tag_path: str | None = None
    tag_group: str | None = None
    quality_filter: str | None = None

    def to_filter_string(self, historian_type: HistorianType) -> str:
        """Convert to historian-specific filter string."""
        if historian_type == HistorianType.INFLUXDB:
            filters = [f'tagname = "{self.tag_name}"']
            if self.tag_path:
                filters.append(f'tagpath = "{self.tag_path}"')
            if self.tag_group:
                filters.append(f'taggroup = "{self.tag_group}"')
            return " AND ".join(filters)
        elif historian_type == HistorianType.TIMESCALEDB:
            filters = [f"tag_name = '{self.tag_name}'"]
            if self.tag_path:
                filters.append(f"tag_path = '{self.tag_path}'")
            return " AND ".join(filters)
        elif historian_type == HistorianType.IGNITION_HISTORIAN:
            return f"tagpath = '{self.tag_path or self.tag_name}'"
        else:
            return f"tag_name = '{self.tag_name}'"


@dataclass
class QueryOptions:
    """Options for historian queries."""

    limit: int | None = None
    offset: int | None = None
    order_by: str = "time"
    order_desc: bool = False
    include_quality: bool = True
    interpolation: str | None = None
    fill_method: str | None = None


class HistorianQueryGenerator:
    """collections.abc.Generator for historian database queries."""

    def __init__(self, historian_type: HistorianType) -> None:
        """Initialize the query generator."""
        self.historian_type = historian_type
        self.logger = logging.getLogger(f"{__name__}.{historian_type.value}")

    def generate_raw_data_query(
        self,
        tags: list[TagFilter],
        time_range: TimeRange,
        options: QueryOptions | None = None,
    ) -> str:
        """Generate query for raw historical data."""
        if options is None:
            options = QueryOptions()

        if self.historian_type == HistorianType.INFLUXDB:
            return self._generate_influxdb_raw_query(tags, time_range, options)
        elif self.historian_type == HistorianType.TIMESCALEDB:
            return self._generate_timescaledb_raw_query(tags, time_range, options)
        elif self.historian_type == HistorianType.IGNITION_HISTORIAN:
            return self._generate_ignition_raw_query(tags, time_range, options)
        else:
            raise ValueError(f"Raw data queries not supported for {self.historian_type}")

    def generate_aggregated_query(
        self,
        tags: list[TagFilter],
        time_range: TimeRange,
        aggregation: AggregationType,
        interval: str,
        time_unit: TimeUnit,
        options: QueryOptions | None = None,
    ) -> str:
        """Generate query for aggregated historical data."""
        if options is None:
            options = QueryOptions()

        if self.historian_type == HistorianType.INFLUXDB:
            return self._generate_influxdb_aggregated_query(tags, time_range, aggregation, interval, time_unit, options)
        elif self.historian_type == HistorianType.TIMESCALEDB:
            return self._generate_timescaledb_aggregated_query(
                tags, time_range, aggregation, interval, time_unit, options
            )
        elif self.historian_type == HistorianType.IGNITION_HISTORIAN:
            return self._generate_ignition_aggregated_query(tags, time_range, aggregation, interval, time_unit, options)
        else:
            raise ValueError(f"Aggregated queries not supported for {self.historian_type}")

    def _generate_influxdb_raw_query(self, tags: list[TagFilter], time_range: TimeRange, options: QueryOptions) -> str:
        """Generate InfluxDB raw data query."""
        # Build tag filters
        tag_filters = []
        for tag in tags:
            tag_filters.append(tag.to_filter_string(self.historian_type))

        # Combine filters
        where_clause = f"WHERE {time_range.to_string(self.historian_type)}"
        if tag_filters:
            tag_filter_str = " OR ".join(f"({tf})" for tf in tag_filters)
            where_clause += f" AND ({tag_filter_str})"

        # Build query
        query_parts = [
            "SELECT",
            "time, tagname, value" + (", quality" if options.include_quality else ""),
            "FROM historian_data",
            where_clause,
            f"ORDER BY time {'DESC' if options.order_desc else 'ASC'}",
        ]

        if options.limit:
            query_parts.append(f"LIMIT {options.limit}")

        return " ".join(query_parts)

    def _generate_influxdb_aggregated_query(
        self,
        tags: list[TagFilter],
        time_range: TimeRange,
        aggregation: AggregationType,
        interval: str,
        time_unit: TimeUnit,
        options: QueryOptions,
    ) -> str:
        """Generate InfluxDB aggregated query."""
        # Build aggregation function
        agg_func = self._get_influxdb_aggregation_function(aggregation)

        # Build tag filters
        tag_filters = []
        for tag in tags:
            tag_filters.append(tag.to_filter_string(self.historian_type))

        # Build time grouping
        time_group = f"{interval}{time_unit.value}"

        # Combine filters
        where_clause = f"WHERE {time_range.to_string(self.historian_type)}"
        if tag_filters:
            tag_filter_str = " OR ".join(f"({tf})" for tf in tag_filters)
            where_clause += f" AND ({tag_filter_str})"

        # Build query
        query_parts = [
            "SELECT",
            f"time, tagname, {agg_func}(value) as aggregated_value",
            "FROM historian_data",
            where_clause,
            f"GROUP BY time({time_group}), tagname",
            f"ORDER BY time {'DESC' if options.order_desc else 'ASC'}",
        ]

        if options.fill_method:
            query_parts.insert(-1, f"FILL({options.fill_method})")

        if options.limit:
            query_parts.append(f"LIMIT {options.limit}")

        return " ".join(query_parts)

    def _generate_timescaledb_raw_query(
        self, tags: list[TagFilter], time_range: TimeRange, options: QueryOptions
    ) -> str:
        """Generate TimescaleDB raw data query."""
        # Build tag filters
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(tag.to_filter_string(self.historian_type))

        # Build WHERE clause
        where_parts = [time_range.to_string(self.historian_type)]
        if tag_conditions:
            where_parts.append(f"({' OR '.join(tag_conditions)})")

        # Build query
        select_fields = ["timestamp", "tag_name", "value"]
        if options.include_quality:
            select_fields.append("quality")

        query_parts = [
            f"SELECT {', '.join(select_fields)}",
            "FROM historian_data",
            f"WHERE {' AND '.join(where_parts)}",
            f"ORDER BY timestamp {'DESC' if options.order_desc else 'ASC'}",
        ]

        if options.limit:
            query_parts.append(f"LIMIT {options.limit}")

        if options.offset:
            query_parts.append(f"OFFSET {options.offset}")

        return " ".join(query_parts)

    def _generate_timescaledb_aggregated_query(
        self,
        tags: list[TagFilter],
        time_range: TimeRange,
        aggregation: AggregationType,
        interval: str,
        time_unit: TimeUnit,
        options: QueryOptions,
    ) -> str:
        """Generate TimescaleDB aggregated query."""
        # Build aggregation function
        agg_func = self._get_timescaledb_aggregation_function(aggregation)

        # Build time bucket
        time_bucket = self._get_timescaledb_time_bucket(interval, time_unit)

        # Build tag filters
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(tag.to_filter_string(self.historian_type))

        # Build WHERE clause
        where_parts = [time_range.to_string(self.historian_type)]
        if tag_conditions:
            where_parts.append(f"({' OR '.join(tag_conditions)})")

        # Build query
        query_parts = [
            "SELECT",
            f"time_bucket('{time_bucket}', timestamp) as time_bucket,",
            "tag_name,",
            f"{agg_func}(value) as aggregated_value",
            "FROM historian_data",
            f"WHERE {' AND '.join(where_parts)}",
            "GROUP BY time_bucket, tag_name",
            f"ORDER BY time_bucket {'DESC' if options.order_desc else 'ASC'}",
        ]

        if options.limit:
            query_parts.append(f"LIMIT {options.limit}")

        return " ".join(query_parts)

    def _generate_ignition_raw_query(self, tags: list[TagFilter], time_range: TimeRange, options: QueryOptions) -> str:
        """Generate Ignition historian raw data query."""
        # Build tag filters
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(tag.to_filter_string(self.historian_type))

        # Build WHERE clause
        where_parts = [time_range.to_string(self.historian_type)]
        if tag_conditions:
            where_parts.append(f"({' OR '.join(tag_conditions)})")

        # Build query for Ignition's historian tables
        select_fields = ["t_stamp", "tagpath", "floatvalue", "intvalue", "stringvalue"]
        if options.include_quality:
            select_fields.append("dataintegrity")

        query_parts = [
            f"SELECT {', '.join(select_fields)}",
            "FROM sqlt_data_1_",  # Ignition's default partition
            f"WHERE {' AND '.join(where_parts)}",
            f"ORDER BY t_stamp {'DESC' if options.order_desc else 'ASC'}",
        ]

        if options.limit:
            query_parts.append(f"LIMIT {options.limit}")

        return " ".join(query_parts)

    def _generate_ignition_aggregated_query(
        self,
        tags: list[TagFilter],
        time_range: TimeRange,
        aggregation: AggregationType,
        interval: str,
        time_unit: TimeUnit,
        options: QueryOptions,
    ) -> str:
        """Generate Ignition historian aggregated query."""
        # For Ignition, we'll use a more complex query with time bucketing
        agg_func = self._get_ignition_aggregation_function(aggregation)

        # Convert interval to milliseconds for Ignition
        interval_ms = self._convert_to_milliseconds(interval, time_unit)

        # Build tag filters
        tag_conditions = []
        for tag in tags:
            tag_conditions.append(tag.to_filter_string(self.historian_type))

        # Build WHERE clause
        where_parts = [time_range.to_string(self.historian_type)]
        if tag_conditions:
            where_parts.append(f"({' OR '.join(tag_conditions)})")

        # Build query with time bucketing
        query_parts = [
            "SELECT",
            f"FLOOR(t_stamp / {interval_ms}) * {interval_ms} as time_bucket,",
            "tagpath,",
            f"{agg_func}(COALESCE(floatvalue, intvalue)) as aggregated_value",
            "FROM sqlt_data_1_",
            f"WHERE {' AND '.join(where_parts)}",
            "AND (floatvalue IS NOT NULL OR intvalue IS NOT NULL)",
            "GROUP BY FLOOR(t_stamp / {interval_ms}), tagpath",
            f"ORDER BY time_bucket {'DESC' if options.order_desc else 'ASC'}",
        ]

        if options.limit:
            query_parts.append(f"LIMIT {options.limit}")

        return " ".join(query_parts)

    def _get_influxdb_aggregation_function(self, aggregation: AggregationType) -> str:
        """Get InfluxDB aggregation function name."""
        mapping = {
            AggregationType.AVERAGE: "MEAN",
            AggregationType.MINIMUM: "MIN",
            AggregationType.MAXIMUM: "MAX",
            AggregationType.SUM: "SUM",
            AggregationType.COUNT: "COUNT",
            AggregationType.FIRST: "FIRST",
            AggregationType.LAST: "LAST",
            AggregationType.STDDEV: "STDDEV",
            AggregationType.MEDIAN: "MEDIAN",
        }
        return mapping.get(aggregation, "MEAN")

    def _get_timescaledb_aggregation_function(self, aggregation: AggregationType) -> str:
        """Get TimescaleDB aggregation function name."""
        mapping = {
            AggregationType.AVERAGE: "AVG",
            AggregationType.MINIMUM: "MIN",
            AggregationType.MAXIMUM: "MAX",
            AggregationType.SUM: "SUM",
            AggregationType.COUNT: "COUNT",
            AggregationType.FIRST: "FIRST",
            AggregationType.LAST: "LAST",
            AggregationType.STDDEV: "STDDEV",
            AggregationType.MEDIAN: "PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY value)",
        }
        return mapping.get(aggregation, "AVG")

    def _get_ignition_aggregation_function(self, aggregation: AggregationType) -> str:
        """Get Ignition historian aggregation function name."""
        mapping = {
            AggregationType.AVERAGE: "AVG",
            AggregationType.MINIMUM: "MIN",
            AggregationType.MAXIMUM: "MAX",
            AggregationType.SUM: "SUM",
            AggregationType.COUNT: "COUNT",
            AggregationType.STDDEV: "STDEV",
        }
        return mapping.get(aggregation, "AVG")

    def _get_timescaledb_time_bucket(self, interval: str, time_unit: TimeUnit) -> str:
        """Get TimescaleDB time bucket string."""
        unit_mapping = {
            TimeUnit.SECOND: "seconds",
            TimeUnit.MINUTE: "minutes",
            TimeUnit.HOUR: "hours",
            TimeUnit.DAY: "days",
            TimeUnit.WEEK: "weeks",
            TimeUnit.MONTH: "months",
            TimeUnit.YEAR: "years",
        }
        unit_name = unit_mapping.get(time_unit, "minutes")
        return f"{interval} {unit_name}"

    def _convert_to_milliseconds(self, interval: str, time_unit: TimeUnit) -> int:
        """Convert interval to milliseconds for Ignition."""
        interval_num = int(interval)
        multipliers = {
            TimeUnit.SECOND: 1000,
            TimeUnit.MINUTE: 60 * 1000,
            TimeUnit.HOUR: 60 * 60 * 1000,
            TimeUnit.DAY: 24 * 60 * 60 * 1000,
            TimeUnit.WEEK: 7 * 24 * 60 * 60 * 1000,
            TimeUnit.MONTH: 30 * 24 * 60 * 60 * 1000,  # Approximate
            TimeUnit.YEAR: 365 * 24 * 60 * 60 * 1000,  # Approximate
        }
        return interval_num * multipliers.get(time_unit, 60 * 1000)

    def generate_tag_list_query(self, tag_pattern: str | None = None) -> str:
        """Generate query to list available tags."""
        if self.historian_type == HistorianType.INFLUXDB:
            base_query = "SHOW TAG VALUES FROM historian_data WITH KEY = tagname"
            if tag_pattern:
                base_query += f" WHERE tagname =~ /{tag_pattern}/"
            return base_query
        elif self.historian_type == HistorianType.TIMESCALEDB:
            base_query = "SELECT DISTINCT tag_name FROM historian_data"
            if tag_pattern:
                base_query += f" WHERE tag_name LIKE '%{tag_pattern}%'"
            return base_query + " ORDER BY tag_name"
        elif self.historian_type == HistorianType.IGNITION_HISTORIAN:
            base_query = "SELECT DISTINCT tagpath FROM sqlt_data_1_"
            if tag_pattern:
                base_query += f" WHERE tagpath LIKE '%{tag_pattern}%'"
            return base_query + " ORDER BY tagpath"
        else:
            raise ValueError(f"Tag listing not supported for {self.historian_type}")

    def generate_data_availability_query(self, tags: list[TagFilter], time_range: TimeRange) -> str:
        """Generate query to check data availability for tags."""
        if self.historian_type == HistorianType.INFLUXDB:
            tag_filters = []
            for tag in tags:
                tag_filters.append(tag.to_filter_string(self.historian_type))

            where_clause = f"WHERE {time_range.to_string(self.historian_type)}"
            if tag_filters:
                tag_filter_str = " OR ".join(f"({tf})" for tf in tag_filters)
                where_clause += f" AND ({tag_filter_str})"

            return f"""
            SELECT tagname,
                   COUNT(*) as point_count,
                   MIN(time) as first_timestamp,
                   MAX(time) as last_timestamp
            FROM historian_data
            {where_clause}
            GROUP BY tagname
            ORDER BY tagname
            """
        elif self.historian_type == HistorianType.TIMESCALEDB:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(tag.to_filter_string(self.historian_type))

            where_parts = [time_range.to_string(self.historian_type)]
            if tag_conditions:
                where_parts.append(f"({' OR '.join(tag_conditions)})")

            return f"""
            SELECT tag_name,
                   COUNT(*) as point_count,
                   MIN(timestamp) as first_timestamp,
                   MAX(timestamp) as last_timestamp
            FROM historian_data
            WHERE {" AND ".join(where_parts)}
            GROUP BY tag_name
            ORDER BY tag_name
            """
        else:
            raise ValueError(f"Data availability queries not supported for {self.historian_type}")

    def create_time_range_from_duration(self, duration_hours: int, end_time: datetime | None = None) -> TimeRange:
        """Create a time range from duration in hours."""
        if end_time is None:
            end_time = datetime.now()

        start_time = end_time - timedelta(hours=duration_hours)
        return TimeRange(start_time=start_time, end_time=end_time)

    def create_time_range_from_dates(
        self, start_date: str, end_date: str, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> TimeRange:
        """Create a time range from date strings."""
        start_time = datetime.strptime(start_date, date_format)
        end_time = datetime.strptime(end_date, date_format)
        return TimeRange(start_time=start_time, end_time=end_time)
