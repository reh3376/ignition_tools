# Repository Analysis System

**Version**: 1.0.0
**Date**: January 28, 2025
**Status**: Production Ready

## Overview

The Repository Analysis System is a comprehensive framework for analyzing external code repositories and converting them into detailed graph database representations. This system provides rich context for LLM agents by creating a Neo4j graph that captures repository structure, dependencies, code patterns, and AI-specific components.

## Key Features

### 🏗️ **Comprehensive Repository Analysis**
- **Complete Structure Mapping**: Directories, files, packages, modules
- **Code Intelligence**: Classes, functions, methods with AST analysis
- **Dependency Tracking**: Runtime, development, and optional dependencies
- **AI Component Detection**: Agents, tools, and model integrations

### 🧠 **Vector Embeddings & Semantic Search**
- **384-dimensional embeddings** using SentenceTransformers
- **Semantic similarity search** across all components
- **Context-aware indexing** for LLM agent queries
- **Multi-modal search** across code, documentation, and comments

### 📊 **Neo4j Graph Database Integration**
- **Sophisticated schema** with 10+ node types and 15+ relationship types
- **Performance optimized** with strategic indexes and constraints
- **Vector search capabilities** for similarity-based queries
- **Rich metadata** including complexity metrics and type information

## Architecture

### Core Components

```
Repository Analysis System
├── 📋 Schema Definition (repository_schema.py)
│   ├── Node Types: Repository, Directory, File, Package, Module, etc.
│   ├── Relationship Types: CONTAINS, IMPORTS, DEPENDS_ON, etc.
│   └── Vector Indexes: 384D embeddings for semantic search
│
├── 🔍 Repository Analyzer (repository_analyzer.py)
│   ├── Git Repository Cloning
│   ├── AST-based Python Analysis
│   ├── Dependency Parsing (pyproject.toml, requirements.txt)
│   └── AI Component Detection
│
├── 🖥️ CLI Commands (cli_commands.py)
│   ├── Repository Analysis: analyze, list, info
│   ├── Component Exploration: components, search
│   └── Database Management: clear, schema info
│
└── 🚀 Demo Scripts
    ├── analyze_pydantic_ai.py: Full Pydantic AI analysis
    └── demo_repository_analysis.py: Interactive demo
```

### Node Types

| Node Type | Description | Key Properties |
|-----------|-------------|----------------|
| `Repository` | Root repository node | name, url, stars, description, topics |
| `Directory` | Directory structure | path, file_count, total_lines, purpose |
| `File` | Individual files | path, size, lines, file_type, language |
| `Package` | Python packages | name, version, module_count, exports |
| `Module` | Python modules | name, docstring, complexity, function_count |
| `Function` | Functions/methods | signature, parameters, is_async, decorators |
| `Class` | Class definitions | base_classes, method_count, is_pydantic_model |
| `Dependency` | External deps | name, version, dependency_type, source |
| `Agent` | AI agents | agent_type, model_support, capabilities |
| `Tool` | AI tools | tool_type, parameters, return_type |

### Relationship Types

| Relationship | Description | Usage |
|--------------|-------------|-------|
| `CONTAINS` | Structural containment | Repository → Directory → File |
| `IMPORTS` | Import dependencies | Module → Module/Package |
| `DEPENDS_ON` | External dependencies | Repository → Dependency |
| `INHERITS_FROM` | Class inheritance | Class → Class |
| `DEFINES` | Definition relationships | Module → Class/Function |
| `USES` | Usage patterns | Function → Function/Class |
| `IMPLEMENTS` | Interface implementation | Class → Interface |
| `CONFIGURES` | Configuration relationships | Config → Component |

## Installation & Setup

### Prerequisites

```bash
# Ensure Neo4j is running
docker-compose up -d neo4j

# Install required dependencies
pip install -r requirements.txt
```

### Required Dependencies

```python
# Core analysis
requests>=2.31.0
sentence-transformers>=2.2.2
neo4j>=5.14.0

# Python parsing
tomli>=2.0.1  # For pyproject.toml
ast  # Built-in AST parsing

# CLI and UI
click>=8.0.0
rich>=13.7.0
```

## Usage Guide

### 1. Analyze Pydantic AI Repository

```bash
# Full Pydantic AI analysis
python scripts/analyze_pydantic_ai.py

# With options
python scripts/analyze_pydantic_ai.py --clear-existing --verbose

# Custom repository
python scripts/analyze_pydantic_ai.py --repo-url https://github.com/user/repo.git
```

### 2. Interactive Demo

```bash
# Start with smaller repository
python scripts/demo_repository_analysis.py

# Full analysis including Pydantic AI
python scripts/demo_repository_analysis.py --full-analysis

# Clear all data first
python scripts/demo_repository_analysis.py --clear-all
```

### 3. CLI Commands

```bash
# Analyze a repository
ign repo analyze https://github.com/pydantic/pydantic-ai.git

# List analyzed repositories
ign repo list

# Get repository details
ign repo info pydantic-ai

# Show components
ign repo components pydantic-ai --node-type agents
ign repo components pydantic-ai --node-type tools

# Semantic search
ign repo search "async agent streaming" --repository pydantic-ai

# Clear repository data
ign repo clear --confirm
```

## Example Queries

### Basic Repository Information

```cypher
// List all repositories
MATCH (r:Repository)
RETURN r.name, r.description, r.stars, r.language
ORDER BY r.stars DESC

// Repository statistics
MATCH (r:Repository {name: "pydantic-ai"})
OPTIONAL MATCH (r)-[:CONTAINS*]->(f:File)
OPTIONAL MATCH (r)-[:CONTAINS*]->(c:Class)
OPTIONAL MATCH (r)-[:CONTAINS*]->(fn:Function)
RETURN r.name,
       count(DISTINCT f) as files,
       count(DISTINCT c) as classes,
       count(DISTINCT fn) as functions
```

### AI Component Analysis

```cypher
// Find all AI agents
MATCH (a:Agent)
RETURN a.name, a.agent_type, a.model_support, a.module
ORDER BY a.name

// Find tools with specific capabilities
MATCH (t:Tool)
WHERE any(param IN t.parameters WHERE param CONTAINS "context")
RETURN t.name, t.parameters, t.module

// Async functions in agents
MATCH (f:Function)
WHERE f.is_async = true AND f.module CONTAINS "agent"
RETURN f.name, f.signature, f.module
```

### Dependency Analysis

```cypher
// External dependencies by type
MATCH (d:Dependency)
RETURN d.dependency_type, count(d) as count, collect(d.name)[0..5] as examples
ORDER BY count DESC

// Pydantic model classes
MATCH (c:Class)
WHERE c.is_pydantic_model = true
RETURN c.name, c.module, c.base_classes
ORDER BY c.name
```

### Vector Similarity Search

```cypher
// Find similar functions (requires embedding)
MATCH (f:Function)
WHERE f.embedding IS NOT NULL
WITH f, vector.similarity.cosine(f.embedding, $query_embedding) AS score
WHERE score > 0.7
RETURN f.name, f.module, f.docstring, score
ORDER BY score DESC
LIMIT 10
```

## Advanced Features

### 1. Custom Repository Analysis

```python
from ignition.graph.client import IgnitionGraphClient
from ignition.code_intelligence.repository_analyzer import RepositoryAnalyzer

# Initialize
client = IgnitionGraphClient()
client.connect()

analyzer = RepositoryAnalyzer(client)

# Analyze custom repository
success = analyzer.analyze_repository(
    "https://github.com/your-org/your-repo.git",
    branch="main"
)
```

### 2. Semantic Search Integration

```python
from sentence_transformers import SentenceTransformer

# Create embeddings for search
embedder = SentenceTransformer('all-MiniLM-L6-v2')
query_embedding = embedder.encode("async agent with streaming").tolist()

# Search similar components
query = """
MATCH (f:Function)
WHERE f.embedding IS NOT NULL
WITH f, vector.similarity.cosine(f.embedding, $query_embedding) AS score
WHERE score > 0.5
RETURN f.name, f.module, score
ORDER BY score DESC
LIMIT 10
"""

results = client.execute_query(query, {"query_embedding": query_embedding})
```

### 3. Custom Component Detection

```python
# Extend analyzer for custom patterns
class CustomRepositoryAnalyzer(RepositoryAnalyzer):
    def _analyze_custom_components(self, repo_path, repo_name):
        """Analyze custom patterns specific to your domain."""
        # Custom analysis logic here
        pass
```

## Performance Considerations

### Database Optimization

- **Indexes**: Strategic indexes on frequently queried properties
- **Constraints**: Unique constraints prevent data duplication
- **Vector Indexes**: Optimized for similarity search with 384D embeddings
- **Batch Operations**: Efficient bulk data loading

### Memory Management

- **Streaming Analysis**: Large repositories processed in chunks
- **Temporary Cleanup**: Cloned repositories automatically cleaned up
- **Connection Pooling**: Efficient Neo4j connection management

### Scalability

- **Repository Size**: Tested with repositories up to 10,000+ files
- **Concurrent Analysis**: Multiple repositories can be analyzed in parallel
- **Incremental Updates**: Support for updating existing repository data

## Troubleshooting

### Common Issues

**1. Neo4j Connection Failed**
```bash
# Check if Neo4j is running
docker-compose ps neo4j

# Start Neo4j if not running
docker-compose up -d neo4j

# Check logs
docker-compose logs neo4j
```

**2. Git Clone Timeout**
```bash
# For large repositories, increase timeout
git config --global http.postBuffer 524288000
```

**3. Memory Issues with Large Repositories**
```python
# Use smaller batch sizes for large repos
analyzer = RepositoryAnalyzer(client, batch_size=100)
```

**4. Missing Dependencies**
```bash
# Install missing dependencies
pip install tomli sentence-transformers
```

### Debug Mode

```bash
# Enable verbose logging
python scripts/analyze_pydantic_ai.py --verbose

# Check Neo4j browser
# URL: http://localhost:7474
# Username: neo4j
# Password: ignition-graph
```

## Integration with LLM Agents

### Context Retrieval

The repository analysis system provides rich context for LLM agents through:

1. **Structured Queries**: Precise component lookup by type, name, or properties
2. **Semantic Search**: Vector similarity for finding related components
3. **Relationship Traversal**: Understanding dependencies and usage patterns
4. **Metadata Enrichment**: Complexity metrics, type information, and documentation

### Example LLM Context Queries

```python
def get_agent_context(agent_name: str) -> dict:
    """Get comprehensive context for an AI agent."""
    query = """
    MATCH (a:Agent {name: $agent_name})
    OPTIONAL MATCH (a)-[:DEFINED_IN]->(m:Module)
    OPTIONAL MATCH (m)-[:CONTAINS]->(f:Function)
    OPTIONAL MATCH (a)-[:USES]->(t:Tool)
    RETURN a, m, collect(f) as functions, collect(t) as tools
    """
    return client.execute_query(query, {"agent_name": agent_name})

def find_similar_patterns(description: str) -> list:
    """Find similar code patterns using vector search."""
    embedding = embedder.encode(description).tolist()
    query = """
    MATCH (n)
    WHERE n.embedding IS NOT NULL
    WITH n, vector.similarity.cosine(n.embedding, $embedding) AS score
    WHERE score > 0.6
    RETURN n, score
    ORDER BY score DESC
    LIMIT 20
    """
    return client.execute_query(query, {"embedding": embedding})
```

## Future Enhancements

### Planned Features

1. **Multi-Language Support**: Extend beyond Python to JavaScript, TypeScript, etc.
2. **Real-time Updates**: Webhook integration for automatic repository updates
3. **Advanced Analytics**: Code quality metrics, security analysis
4. **Integration APIs**: REST/GraphQL APIs for external tool integration
5. **Visualization**: Interactive graph visualization for repository exploration

### Roadmap

- **Phase 1**: Multi-language support (JavaScript/TypeScript)
- **Phase 2**: Real-time update mechanisms
- **Phase 3**: Advanced analytics and reporting
- **Phase 4**: External API and integration layer

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd IGN_scripts

# Install development dependencies
pip install -r requirements-test.txt

# Run tests
pytest tests/test_repository_analysis.py

# Run linting
ruff check src/ignition/code_intelligence/
mypy src/ignition/code_intelligence/
```

### Adding New Node Types

1. Define node type in `repository_schema.py`
2. Add parsing logic in `repository_analyzer.py`
3. Create database constraints and indexes
4. Add CLI commands for the new type
5. Update documentation and tests

### Testing

```bash
# Run repository analysis tests
pytest tests/test_repository_analysis.py -v

# Test with demo repository
python scripts/demo_repository_analysis.py --verbose

# Integration tests
pytest tests/integration/test_full_analysis.py
```

## Conclusion

The Repository Analysis System provides a powerful foundation for creating LLM agents with deep understanding of code repositories. By combining AST analysis, vector embeddings, and graph database storage, it enables sophisticated code intelligence and semantic search capabilities.

The system is production-ready and has been successfully tested with the [Pydantic AI repository](https://github.com/pydantic/pydantic-ai.git), demonstrating its ability to handle real-world, complex codebases and extract meaningful patterns for AI agent development.
