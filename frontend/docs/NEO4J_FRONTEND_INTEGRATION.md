# Neo4j Frontend Integration Guide

## Overview

This guide documents the Neo4j knowledge graph integration for the IGN Scripts frontend, enabling AI coding assistants to maintain deep understanding of backend functionality while developing the frontend in a separate repository.

## Architecture

### 1. Frontend Neo4j Client (`frontend/src/lib/neo4j/client.ts`)

The frontend Neo4j client provides **read-only access** to the knowledge graph through secure API endpoints. It follows the same methodical approach as `crawl_mcp.py` but adapted for browser environments.

**Key Features:**
- TypeScript-native with full type safety
- Environment-based configuration
- Automatic connection validation
- Comprehensive error handling
- Singleton pattern for resource efficiency

**Configuration:**
```typescript
// Environment variables (in .env)
VITE_NEO4J_URI=bolt://localhost:7687
VITE_NEO4J_USER=neo4j
VITE_NEO4J_PASSWORD=your-password
VITE_NEO4J_DATABASE=neo4j
VITE_API_BASE_URL=http://localhost:8000
```

### 2. React Hook Integration (`frontend/src/hooks/useNeo4j.ts`)

The `useNeo4j` hook provides a convenient interface for React components to access the knowledge graph.

**Usage Example:**
```tsx
import { useNeo4j } from '../hooks/useNeo4j';

function CodeSearchComponent() {
  const { isInitialized, searchClasses, searchFunctions } = useNeo4j();

  const handleSearch = async (query: string) => {
    const classes = await searchClasses(query);
    const functions = await searchFunctions(query);
    // Process results...
  };
}
```

### 3. Frontend Development Methodology (`frontend/docs/frontend_development_methodology.js`)

This file serves as the frontend equivalent of `crawl_mcp.py`, providing:
- Environment validation functions
- Input validation with Zod schemas
- Error handling patterns
- Progressive complexity implementation
- Performance monitoring
- Testing utilities

## Available Features

### 1. Code Search and Discovery

```typescript
// Search for classes
const classes = await searchClasses('DataIntegration');

// Search for functions
const functions = await searchFunctions('validate');

// Semantic search (uses backend embeddings)
const results = await semanticCodeSearch('process OPC UA data');
```

### 2. Code Intelligence

```typescript
// Get code patterns for context
const patterns = await getCodePatterns('react-component');

// Validate imports
const validation = await validateImports([
  'src/ignition/modules/data_integration',
  'src/api/routers/sme_agent'
]);

// Find similar implementations
const similar = await getSimilarImplementations('async def process_data');
```

### 3. Dependency Analysis

```typescript
// Get dependency graph
const dependencies = await getDependencyGraph('src.ignition.modules');

// Get code quality metrics
const metrics = await getCodeQualityMetrics('src/components/Dashboard.tsx');
```

## API Endpoints Required

The frontend requires these API endpoints to be available on the backend:

### 1. Knowledge Graph Query Endpoint
```
POST /api/v1/knowledge/query
{
  "query": "MATCH (c:Class) WHERE c.name = $name RETURN c",
  "parameters": { "name": "DataIntegrationModule" },
  "readOnly": true
}
```

### 2. Semantic Search Endpoint
```
POST /api/v1/knowledge/semantic-search
{
  "query": "process industrial data",
  "repository": "IGN_scripts",
  "limit": 10
}
```

### 3. Health Check Endpoint
```
GET /api/v1/knowledge/health
```

## Security Considerations

### 1. Read-Only Access
- All queries are forced to be read-only
- No write operations allowed from frontend
- Query validation on backend

### 2. Authentication
- JWT tokens stored in localStorage
- Bearer token authentication for all requests
- Token refresh mechanism

### 3. Environment Variables
- Sensitive credentials in .env files
- Never commit .env files
- Use .env.example for templates

## Development Workflow

### 1. Initial Setup
```bash
# In frontend repository
cd frontend
npm install

# Create .env file
cp .env.example .env
# Edit .env with your Neo4j credentials
```

### 2. Testing Connection
```typescript
import { getNeo4jClient } from './lib/neo4j/client';

async function testConnection() {
  try {
    const client = await getNeo4jClient();
    const repos = await client.getRepositories();
    console.log('Connected! Repositories:', repos);
  } catch (error) {
    console.error('Connection failed:', error);
  }
}
```

### 3. Using in Components
```tsx
function MyComponent() {
  const { searchClasses, isLoading, error } = useNeo4j();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  // Use searchClasses and other methods...
}
```

## Performance Optimization

### 1. Query Caching
- Results cached in memory
- Cache invalidation on updates
- Configurable cache TTL

### 2. Batch Queries
- Combine multiple queries when possible
- Reduce network round trips
- Optimize for mobile networks

### 3. Lazy Loading
- Load data on demand
- Progressive enhancement
- Skeleton loaders for UX

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check Neo4j is running
   - Verify credentials in .env
   - Check network connectivity

2. **Authentication Error**
   - Ensure JWT token is valid
   - Check API endpoint configuration
   - Verify CORS settings

3. **Query Timeout**
   - Check query complexity
   - Verify Neo4j indexes
   - Consider pagination

### Debug Mode
```typescript
// Enable debug logging
localStorage.setItem('neo4j_debug', 'true');

// Check console for detailed logs
```

## Migration Checklist

When migrating frontend to separate repository:

- [ ] Copy `frontend/` directory to new repository
- [ ] Set up environment variables
- [ ] Configure API base URL
- [ ] Test Neo4j connectivity
- [ ] Verify authentication flow
- [ ] Test all knowledge graph features
- [ ] Set up CI/CD pipeline
- [ ] Configure production deployment

## Best Practices

1. **Always validate inputs** using Zod schemas
2. **Handle errors gracefully** with user-friendly messages
3. **Use TypeScript** for type safety
4. **Follow the methodology** in frontend_development_methodology.js
5. **Test thoroughly** with unit and integration tests
6. **Monitor performance** using built-in utilities
7. **Document changes** for AI agents and developers

## Conclusion

This Neo4j frontend integration enables AI coding assistants to maintain deep understanding of the backend codebase while developing the frontend independently. By following the methodical approach established in `crawl_mcp.py` and adapted for frontend in `frontend_development_methodology.js`, we ensure consistent, high-quality development across both repositories.
