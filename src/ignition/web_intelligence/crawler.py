"""Web Crawler for IGN Scripts Phase 11.8 - Following crawl_mcp.py methodology.

This module provides intelligent web crawling capabilities with:
- Comprehensive input validation using Pydantic models
- Robust error handling with user-friendly messages
- Modular testing with progressive complexity
- Proper resource management with async context managers
- Open source model integration instead of proprietary APIs
"""

import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig
from pydantic import BaseModel, Field, HttpUrl, validator

from . import format_neo4j_error, validate_neo4j_connection


class CrawlRequest(BaseModel):
    """Input validation model for crawl requests (crawl_mcp.py methodology)."""

    url: HttpUrl = Field(..., description="URL to crawl")
    crawl_type: str = Field(
        default="auto", description="Crawl type: auto, single, sitemap, recursive"
    )
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum crawling depth")
    max_concurrent: int = Field(
        default=5, ge=1, le=20, description="Maximum concurrent requests"
    )
    chunk_size: int = Field(
        default=1000, ge=100, le=10000, description="Content chunk size"
    )
    include_code_blocks: bool = Field(
        default=True, description="Preserve code blocks in content"
    )

    @validator("crawl_type")
    def validate_crawl_type(cls, v) -> Any:
        """Validate crawl type options."""
        allowed_types = ["auto", "single", "sitemap", "recursive"]
        if v not in allowed_types:
            raise ValueError(f"crawl_type must be one of: {allowed_types}")
        return v

    @validator("url")
    def validate_url_format(cls, v) -> Any:
        """Validate URL format and accessibility."""
        url_str = str(v)
        parsed = urlparse(url_str)

        if not parsed.scheme or not parsed.netloc:
            raise ValueError("URL must include scheme (http/https) and domain")

        if parsed.scheme not in ["http", "https"]:
            raise ValueError("URL must use http or https protocol")

        return v


class CrawlResult(BaseModel):
    """Output validation model for crawl results (crawl_mcp.py methodology)."""

    url: str = Field(..., description="Crawled URL")
    title: str = Field(default="", description="Page title")
    content: str = Field(default="", description="Extracted content")
    markdown: str = Field(default="", description="Markdown content")
    links: list[str] = Field(default_factory=list, description="Found links")
    code_blocks: list[dict[str, Any]] = Field(
        default_factory=list, description="Extracted code blocks"
    )
    chunks: list[str] = Field(default_factory=list, description="Content chunks")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    success: bool = Field(default=False, description="Crawl success status")
    error: str = Field(default="", description="Error message if failed")


class WebCrawler:
    """Web crawler with open source model integration (crawl_mcp.py methodology)."""

    def __init__(self) -> None:
        """Initialize crawler with environment validation."""
        self.crawler: AsyncWebCrawler | None = None
        self.knowledge_validator: Any | None = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize crawler and validate environment (crawl_mcp.py patterns).

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Validate environment first (crawl_mcp.py methodology)
            from . import validate_environment  # type: ignore

            if not validate_environment():
                return False

            # Initialize browser configuration
            browser_config = BrowserConfig(
                headless=True,
                verbose=False,
                extra_args=["--no-sandbox", "--disable-dev-shm-usage"],
            )

            # Initialize the crawler
            self.crawler = AsyncWebCrawler(config=browser_config)
            await self.crawler.__aenter__()

            # Initialize knowledge graph validator if available
            if validate_neo4j_connection():
                try:
                    # Import knowledge graph components if available
                    from ..code_intelligence.enhanced_validator import (
                        EnhancedCodeValidator,  # type: ignore
                    )

                    neo4j_uri = os.getenv("NEO4J_URI")
                    neo4j_user = os.getenv("NEO4J_USER")
                    neo4j_password = os.getenv("NEO4J_PASSWORD")

                    self.knowledge_validator = EnhancedCodeValidator(
                        neo4j_uri, neo4j_user, neo4j_password
                    )
                    await self.knowledge_validator.initialize()
                    print("✓ Knowledge graph validator initialized")

                except Exception as e:
                    print(
                        f"Warning: Knowledge validator initialization failed: {format_neo4j_error(e)}"
                    )
                    self.knowledge_validator = None

            self._initialized = True
            return True

        except Exception as e:
            print(f"Crawler initialization failed: {e!s}")
            return False

    async def crawl(self, request: CrawlRequest) -> CrawlResult:
        """Crawl URL with comprehensive validation and error handling.

        Args:
            request: Validated crawl request

        Returns:
            CrawlResult: Crawl results with validation status
        """
        if not self._initialized:
            return CrawlResult(
                url=str(request.url),
                success=False,
                error="Crawler not initialized. Call initialize() first.",
            )

        try:
            # Determine crawl method based on request type
            if request.crawl_type == "auto":
                crawl_type = self._detect_crawl_type(str(request.url))
            else:
                crawl_type = request.crawl_type

            # Execute crawl based on detected/specified type
            if crawl_type == "sitemap":
                return await self._crawl_sitemap(request)
            elif crawl_type == "recursive":
                return await self._crawl_recursive(request)
            else:
                return await self._crawl_single(request)

        except Exception as e:
            return CrawlResult(
                url=str(request.url), success=False, error=f"Crawl failed: {e!s}"
            )

    def _detect_crawl_type(self, url: str) -> str:
        """Detect appropriate crawl type from URL (crawl_mcp.py patterns)."""
        url_lower = url.lower()

        if "sitemap" in url_lower and url_lower.endswith(".xml"):
            return "sitemap"
        elif url_lower.endswith((".txt", ".md")):
            return "single"
        elif "docs" in url_lower or "documentation" in url_lower:
            return "recursive"
        else:
            return "single"

    async def _crawl_single(self, request: CrawlRequest) -> CrawlResult:
        """Crawl single page with content extraction."""
        try:
            # Following crawl_mcp.py patterns for API usage
            from crawl4ai import CacheMode, CrawlerRunConfig

            config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)

            # Use correct API pattern from crawl_mcp.py
            async for result in self.crawler.arun(url=str(request.url), config=config):  # type: ignore
                if not result.success or not result.markdown:
                    return CrawlResult(
                        url=str(request.url),
                        success=False,
                        error=result.error_message or "Unknown crawl error",
                    )
                break  # Take the first successful result
            else:
                return CrawlResult(
                    url=str(request.url),
                    success=False,
                    error="No successful crawl results",
                )

            if result.success and result.markdown:
                # Extract and process content
                content = result.markdown or ""

                # Extract code blocks if enabled
                code_blocks = []
                if request.include_code_blocks:
                    code_blocks = self._extract_code_blocks(content)

                # Create intelligent chunks preserving code blocks
                chunks = self._create_intelligent_chunks(
                    content,
                    request.chunk_size,
                    preserve_code=request.include_code_blocks,
                )

                return CrawlResult(
                    url=str(request.url),
                    title=getattr(result, "title", "") or "",
                    content=content,
                    markdown=result.markdown,
                    links=getattr(result, "links", {}).get("internal", [])
                    + getattr(result, "links", {}).get("external", []),
                    code_blocks=code_blocks,
                    chunks=chunks,
                    metadata={"content_length": len(result.markdown)},
                    success=True,
                )
            else:
                return CrawlResult(
                    url=str(request.url),
                    success=False,
                    error=getattr(result, "error_message", None)
                    or "Unknown crawl error",
                )

        except Exception as e:
            return CrawlResult(
                url=str(request.url),
                success=False,
                error=f"Single page crawl error: {e!s}",
            )

    async def _crawl_sitemap(self, request: CrawlRequest) -> CrawlResult:
        """Crawl sitemap XML and extract URLs."""
        # Implementation for sitemap crawling
        # This would parse XML and crawl multiple URLs
        return CrawlResult(
            url=str(request.url),
            success=False,
            error="Sitemap crawling not yet implemented",
        )

    async def _crawl_recursive(self, request: CrawlRequest) -> CrawlResult:
        """Crawl recursively following internal links."""
        # Implementation for recursive crawling
        # This would follow links up to max_depth
        return CrawlResult(
            url=str(request.url),
            success=False,
            error="Recursive crawling not yet implemented",
        )

    def _extract_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """Extract code blocks from content (crawl_mcp.py patterns)."""
        code_blocks = []

        # Extract markdown code blocks
        code_pattern = r"```(\w+)?\n(.*?)\n```"
        matches = re.findall(code_pattern, content, re.DOTALL)

        for i, (language, code) in enumerate(matches):
            code_blocks.append(
                {
                    "index": i,
                    "language": language or "text",
                    "code": code.strip(),
                    "lines": len(code.strip().split("\n")),
                }
            )

        return code_blocks

    def _create_intelligent_chunks(
        self, content: str, chunk_size: int, preserve_code: bool = True
    ) -> list[str]:
        """Create intelligent content chunks preserving code blocks."""
        if not content:
            return []

        if not preserve_code:
            # Simple chunking without code preservation
            return [
                content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
            ]

        # Intelligent chunking preserving code blocks
        chunks = []
        current_chunk = ""

        # Split by lines and preserve code block boundaries
        lines = content.split("\n")
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            # Add line to current chunk
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line

            # Check if we should create a new chunk
            if (
                len(current_chunk) >= chunk_size
                and not in_code_block
                and not line.strip().startswith("```")
            ):
                chunks.append(current_chunk)
                current_chunk = ""

        # Add remaining content
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    async def close(self) -> None:
        """Clean up resources (crawl_mcp.py methodology)."""
        try:
            if self.crawler:
                await self.crawler.__aexit__(None, None, None)
                print("✓ Web crawler closed")

            if self.knowledge_validator:
                await self.knowledge_validator.close()
                print("✓ Knowledge validator closed")

        except Exception as e:
            print(f"Error during crawler cleanup: {e!s}")


@asynccontextmanager
async def get_crawler() -> AsyncIterator[WebCrawler]:
    """Get crawler instance with proper lifecycle management (crawl_mcp.py patterns)."""
    crawler = WebCrawler()

    try:
        if await crawler.initialize():
            yield crawler
        else:
            raise RuntimeError("Failed to initialize web crawler")
    finally:
        await crawler.close()


# Helper function for validation
def validate_crawl_request(url: str, **kwargs) -> dict[str, Any]:
    """Validate crawl request and return error info if invalid (crawl_mcp.py patterns)."""
    try:
        request = CrawlRequest(url=url, **kwargs)
        return {"valid": True, "request": request}
    except Exception as e:
        return {"valid": False, "error": str(e)}


__all__ = [
    "CrawlRequest",
    "CrawlResult",
    "WebCrawler",
    "get_crawler",
    "validate_crawl_request",
]
