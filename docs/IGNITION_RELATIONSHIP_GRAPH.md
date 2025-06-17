# Ignition Relationship Graph System

## Overview

The Ignition Relationship Graph System is a sophisticated Neo4j-based knowledge graph that models the complete Ignition platform ecosystem. It serves as the foundational intelligence layer for the IGN Scripts platform, capturing relationships between functions, contexts, templates, deployment patterns, and code intelligence.

## Core Architecture

### 🗄️ Neo4j Graph Database
**Primary Database**: Neo4j container (`ign-scripts-neo4j`)
**Current Scale**: 3,691+ nodes with comprehensive relationship mapping
**Vector Embeddings**: 384-dimensional semantic search capability

### 📊 Graph Schema Overview
**Location**: `src/ignition/graph/schema.py`

The schema defines a comprehensive node and relationship type system organized into distinct functional areas:

## Node Type Categories

### 1. Core Ignition System Nodes
#### Function Nodes (`FUNCTION`)
- **Purpose**: Represents Ignition system functions (400+ functions)
- **Properties**: name, description, parameters, return_type, contexts, category
- **Examples**: `system.tag.readBlocking()`, `system.db.runQuery()`, `system.perspective.sendMessage()`

#### Context Nodes (`CONTEXT`)
- **Purpose**: Execution contexts where functions are available
- **Types**: Gateway, Vision, Perspective, Designer
- **Properties**: name, description, capabilities, restrictions

#### Template Nodes (`TEMPLATE`)
- **Purpose**: Code templates and patterns
- **Properties**: name, description, code, context, uses_functions
- **Examples**: Database query templates, tag reading patterns, HMI event handlers

#### Parameter Nodes (`PARAMETER`)
- **Purpose**: Function parameters and their specifications
- **Properties**: name, type, required, default_value, description

### 2. Intelligence & Learning Nodes
#### Usage Event Nodes (`USAGE_EVENT`)
- **Purpose**: Tracks function and template usage patterns
- **Properties**: timestamp, event_type, session_id, function_name, success

#### User Session Nodes (`USER_SESSION`)
- **Purpose**: User interaction sessions for pattern analysis
- **Properties**: id, user_id, start_time, duration, success_rate

#### Pattern Analysis Nodes (`PATTERN_ANALYSIS`)
- **Purpose**: Analyzed patterns from usage data
- **Properties**: pattern_type, confidence, support, lift, pattern_data

#### Recommendation Nodes (`RECOMMENDATION`)
- **Purpose**: AI-generated recommendations
- **Properties**: recommendation_type, confidence, context, created_date

### 3. Export/Import Intelligence Nodes
#### Export Profile Nodes (`EXPORT_PROFILE`)
- **Purpose**: Export configuration profiles and patterns
- **Properties**: export_type, format, include_patterns, configuration, success_rate

#### Import Job Nodes (`IMPORT_JOB`)
- **Purpose**: Tracks import/deployment jobs and outcomes
- **Properties**: import_type, target_gateway, status, duration, resources_imported

#### Resource Dependency Nodes (`RESOURCE_DEPENDENCY`)
- **Purpose**: Models dependencies between Ignition resources
- **Properties**: source_resource, target_resource, dependency_type, strength

#### Gateway Resource Nodes (`GATEWAY_RESOURCE`)
- **Purpose**: Individual Ignition gateway resources
- **Properties**: resource_type, resource_path, gateway_host, configuration

### 4. Deployment Pattern Learning Nodes
#### Deployment Pattern Nodes (`DEPLOYMENT_PATTERN`)
- **Purpose**: Captures successful deployment configurations
- **Properties**: pattern_type, environment_types, deployment_strategy, success_criteria

#### Deployment Execution Nodes (`DEPLOYMENT_EXECUTION`)
- **Purpose**: Records individual deployment instances
- **Properties**: execution_name, deployment_type, target_environment, status, duration

#### Environment Adaptation Nodes (`ENVIRONMENT_ADAPTATION`)
- **Purpose**: Environment-specific configuration adaptations
- **Properties**: adaptation_name, source_environment, target_environment, adaptation_rules

#### Rollback Scenario Nodes (`ROLLBACK_SCENARIO`)
- **Purpose**: Rollback procedures and recovery patterns
- **Properties**: scenario_name, rollback_type, trigger_conditions, success_rate

### 5. Code Intelligence Nodes
#### Code File Nodes (`CodeFile`)
- **Purpose**: Python source code files with embeddings
- **Properties**: file_path, content, language, embeddings (384D vector)

#### Class Nodes (`Class`)
- **Purpose**: Python class definitions
- **Properties**: name, file_path, docstring, methods, embeddings

#### Method Nodes (`Method`)
- **Purpose**: Python method/function definitions
- **Properties**: name, class_name, signature, complexity, embeddings

## Relationship Type Categories

### 1. Core System Relationships
- **HAS_PARAMETER**: Functions to their parameters
- **AVAILABLE_IN**: Functions available in specific contexts
- **USES**: Templates using specific functions
- **COMPATIBLE_WITH**: Compatibility relationships
- **BELONGS_TO**: Category membership relationships

### 2. Learning System Relationships
- **USED_TOGETHER**: Co-occurrence patterns
- **OCCURRED_IN_SESSION**: Events within sessions
- **GENERATED_RECOMMENDATION**: Recommendation generation
- **FOLLOWS_PATTERN**: Pattern adherence

### 3. Export/Import Relationships
- **EXPORTS_TO**: Export target relationships
- **IMPORTS_FROM**: Import source relationships
- **DEPLOYED_AS**: Deployment relationships
- **REFERENCES**: Resource reference relationships
- **CONFLICTS_WITH**: Conflict identification

### 4. Deployment Pattern Relationships
- **FOLLOWS_DEPLOYMENT_PATTERN**: Execution follows pattern
- **ADAPTS_TO_ENVIRONMENT**: Environment adaptations
- **TRIGGERS_ROLLBACK**: Rollback triggers
- **LEARNS_FROM_EXECUTION**: Learning relationships

## Key System Components

### 1. Graph Client (`IgnitionGraphClient`)
**Location**: `src/ignition/graph/client.py`

Core database interface providing:
- **Connection Management**: Neo4j driver connection handling
- **Query Execution**: Read/write query execution with parameters
- **Node/Relationship Creation**: Graph entity creation methods
- **Schema Management**: Constraint and index management
- **Transaction Handling**: ACID transaction support

```python
client = IgnitionGraphClient()
client.connect()
result = client.execute_query("MATCH (f:Function) RETURN count(f)")
```

### 2. Graph Populator (`IgnitionGraphPopulator`)
**Location**: `src/ignition/graph/populator.py`

Database population and initialization:
- **Schema Setup**: Creates constraints and indexes
- **Function Loading**: Loads 400+ Ignition functions
- **Template Import**: Populates code templates
- **Relationship Creation**: Establishes function-context relationships

```python
populator = IgnitionGraphPopulator(client)
populator.populate_initial_schema()
populator.populate_ignition_functions()
```

### 3. Vector Embeddings Integration
**Status**: Phase 8.2 Completed
**Embedding Model**: sentence-transformers (384D)

Three operational vector indexes:
- **`class_embeddings`**: Semantic search for class definitions
- **`code_file_embeddings`**: File-level semantic search
- **`method_embeddings`**: Method/function semantic search

```python
# Semantic search example
results = client.execute_query("""
CALL db.index.vector.queryNodes('method_embeddings', 10, $embedding)
YIELD node, score
RETURN node.name, node.signature, score
""", {"embedding": embedding_vector})
```

## Current Database Statistics

### Node Distribution
- **Total Nodes**: 3,691+
- **Functions**: 400+ Ignition system functions
- **Code Files**: 4 (ready for embedding population)
- **Classes**: 8
- **Methods**: 42
- **Templates**: Extensive template library
- **Contexts**: 4 primary contexts (Gateway, Vision, Perspective, Designer)

### Relationship Network
- **Function-Context**: Maps function availability across contexts
- **Function-Parameter**: Detailed parameter specifications
- **Template-Function**: Template usage patterns
- **Deployment Pattern**: Learning relationships for deployment intelligence

## Query Patterns and Examples

### 1. Function Discovery
```cypher
// Find functions available in specific context
MATCH (f:Function)-[:AVAILABLE_IN]->(c:Context {name: 'Gateway'})
RETURN f.name, f.description
ORDER BY f.name

// Find functions by category
MATCH (f:Function)-[:BELONGS_TO]->(cat:Category {name: 'database'})
RETURN f.name, f.description
```

### 2. Template Analysis
```cypher
// Find templates using database functions
MATCH (t:Template)-[:USES]->(f:Function)-[:BELONGS_TO]->(cat:Category {name: 'database'})
RETURN DISTINCT t.name, collect(f.name) as functions_used
```

### 3. Deployment Intelligence
```cypher
// Find successful deployment patterns for environment
MATCH (dp:DeploymentPattern)
WHERE 'production' IN dp.environment_types
AND dp.confidence_score > 0.8
RETURN dp.name, dp.deployment_strategy, dp.success_count
ORDER BY dp.confidence_score DESC
```

### 4. Code Intelligence Search
```cypher
// Semantic search for methods
CALL db.index.vector.queryNodes('method_embeddings', 5, $embedding)
YIELD node, score
WHERE score > 0.8
RETURN node.name, node.signature, score
```

## Integration Points

### 1. CLI Integration
The graph system integrates with multiple CLI commands:
- **`ign graph`**: Direct graph operations and querying
- **`ign functions`**: Function discovery and analysis
- **`ign templates`**: Template management
- **`ign deploy`**: Deployment pattern intelligence
- **`ign refactor`**: Code intelligence and refactoring

### 2. Learning Systems
- **Usage Tracking**: Records function and template usage
- **Pattern Analysis**: Identifies co-occurrence patterns
- **Recommendation Engine**: Generates intelligent suggestions
- **Performance Monitoring**: Tracks system performance metrics

### 3. Export/Import Intelligence
- **Dependency Analysis**: Resource dependency mapping
- **Configuration Patterns**: Export/import configuration intelligence
- **Deployment Optimization**: Environment-specific adaptations

## Performance and Optimization

### Database Configuration
- **Memory**: Optimized heap settings for graph operations
- **Indexes**: Strategic indexing on frequently queried properties
- **Constraints**: Unique constraints ensuring data integrity
- **Connection Pooling**: Efficient connection management

### Query Optimization
- **Index Usage**: Leverages property and vector indexes
- **Query Planning**: Cypher query optimization
- **Batch Operations**: Efficient bulk data operations
- **Caching**: Result caching for frequently accessed data

## Security and Access Control

### Data Protection
- **Connection Security**: Encrypted Neo4j connections
- **Access Control**: Role-based access to graph data
- **Audit Logging**: Comprehensive operation logging
- **Data Encryption**: Sensitive data encryption at rest

### API Security
- **Authentication**: Secure API authentication
- **Authorization**: Granular permission controls
- **Input Validation**: Query parameter validation
- **Rate Limiting**: Protection against abuse

## Development and Maintenance

### Schema Evolution
The graph schema supports controlled evolution:
- **Versioned Schema**: Schema version tracking
- **Migration Scripts**: Automated schema migrations
- **Backward Compatibility**: Maintains compatibility across versions
- **Testing Framework**: Comprehensive schema testing

### Monitoring and Maintenance
- **Health Checks**: Database health monitoring
- **Performance Metrics**: Query performance tracking
- **Backup Management**: Automated backup procedures
- **Data Validation**: Integrity checking and validation

## Future Enhancements

### Planned Improvements
1. **Advanced ML Integration**: Enhanced machine learning models
2. **Real-time Analytics**: Live performance monitoring
3. **GraphQL API**: Modern API interface
4. **Advanced Visualizations**: Interactive graph visualizations
5. **Multi-tenant Support**: Support for multiple organizations

### Scalability Roadmap
- **Cluster Deployment**: Neo4j clustering for high availability
- **Horizontal Scaling**: Distributed query processing
- **Caching Layers**: Advanced caching strategies
- **Performance Optimization**: Continuous query optimization

## Best Practices

### 1. Data Modeling
- Use consistent naming conventions for nodes and relationships
- Leverage property types effectively for querying
- Design relationships to support common query patterns
- Maintain data quality through constraints

### 2. Query Development
- Use indexes for frequently filtered properties
- Prefer specific relationship types over generic ones
- Leverage vector indexes for semantic search
- Monitor query performance and optimize as needed

### 3. Integration Development
- Use the provided client classes for database access
- Implement proper error handling and logging
- Leverage existing query patterns and utilities
- Follow the established schema conventions

## Conclusion

The Ignition Relationship Graph System provides a sophisticated foundation for intelligent automation in the Ignition platform. By modeling the complex relationships between functions, contexts, deployments, and code, it enables advanced features like semantic search, deployment pattern learning, and intelligent recommendations. The system is designed for scale, performance, and extensibility, making it a robust platform for current and future AI-powered capabilities.
