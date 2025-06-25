# Frontend Code Intelligence Framework

## Overview

The Frontend Code Intelligence Framework provides comprehensive code analysis, optimization, and refactoring capabilities for TypeScript/JavaScript development. Following the methodical approach from `crawl_mcp.py`, this framework ensures systematic code quality improvement and maintains consistency with backend development practices.

## Architecture

```
frontend/src/lib/codeIntelligence/
├── analyzer.ts              # AST-based code analysis
├── optimizer.ts             # Performance optimization suggestions
├── refactorer.ts            # Safe code transformations
├── index.ts                 # Unified API and service
└── hooks/
    └── useCodeIntelligence.ts  # React hook integration
```

## Core Components

### 1. Code Analyzer (`analyzer.ts`)

The analyzer performs deep AST-based analysis of TypeScript/JavaScript code:

**Features:**
- Function complexity analysis (cyclomatic complexity)
- React component detection and analysis
- Import/export dependency tracking
- Pattern detection (anti-patterns, best practices)
- Code metrics calculation
- Type coverage analysis

**Usage:**
```typescript
import { getCodeAnalyzer } from '@/lib/codeIntelligence';

const analyzer = getCodeAnalyzer();
const result = await analyzer.analyze({
  filePath: 'src/components/MyComponent.tsx',
  content: sourceCode,
  options: {
    includeMetrics: true,
    includePatterns: true,
    includeSuggestions: true
  }
});
```

### 2. Code Optimizer (`optimizer.ts`)

The optimizer provides performance optimization suggestions:

**Optimization Types:**
- React memoization (React.memo, useMemo, useCallback)
- Code splitting opportunities
- Tree shaking improvements
- Lazy loading suggestions
- Bundle size reduction

**Usage:**
```typescript
import { getCodeOptimizer } from '@/lib/codeIntelligence';

const optimizer = getCodeOptimizer();
const result = await optimizer.optimize({
  analysisResult,
  options: {
    targetComplexity: 'standard',
    enableMemoization: true,
    enableCodeSplitting: true
  }
});
```

### 3. Code Refactorer (`refactorer.ts`)

The refactorer performs safe code transformations:

**Refactoring Operations:**
- Extract function/component
- Convert between function types
- Rename symbols
- Extract/inline variables
- Organize imports
- Remove dead code

**Usage:**
```typescript
import { getCodeRefactorer } from '@/lib/codeIntelligence';

const refactorer = getCodeRefactorer();
const result = await refactorer.refactor({
  filePath: 'src/utils/helper.ts',
  content: sourceCode,
  analysisResult,
  refactoringType: 'extract-function',
  options: {
    targetName: 'extractedFunction',
    dryRun: true
  }
});
```

### 4. Unified Service (`index.ts`)

The unified service provides a single entry point:

**Operations:**
- `analyze`: Perform code analysis
- `optimize`: Get optimization suggestions
- `refactor`: Apply refactoring operations
- `full-analysis`: Complete code intelligence workflow

**Usage:**
```typescript
import { getCodeIntelligenceService } from '@/lib/codeIntelligence';

const service = getCodeIntelligenceService();
await service.initialize();

const result = await service.process({
  filePath: 'src/App.tsx',
  content: sourceCode,
  operation: 'full-analysis',
  options: {
    includeNeo4jValidation: true,
    complexityLevel: 'standard',
    autoFix: false
  }
});
```

## React Integration

### useCodeIntelligence Hook

The framework provides a React hook for easy integration:

```typescript
import { useCodeIntelligence } from '@/lib/codeIntelligence';

function CodeEditor() {
  const {
    isInitialized,
    isAnalyzing,
    result,
    error,
    analyze,
    getRefactoringCandidates,
    applyAutomatedFixes
  } = useCodeIntelligence({
    autoInitialize: true,
    enableRealTimeAnalysis: true,
    realTimeDebounceMs: 1000
  });

  // Use in your component
  const handleAnalyze = async () => {
    const result = await analyze(filePath, content, 'full-analysis');
    console.log('Analysis result:', result);
  };
}
```

### React Query Integration

For advanced caching and state management:

```typescript
import { useCodeAnalysisQuery, useApplyFixesMutation } from '@/lib/codeIntelligence';

function CodeAnalysisPanel({ filePath, content }) {
  // Query for analysis
  const { data, isLoading, error } = useCodeAnalysisQuery(filePath, content, {
    operation: 'analyze',
    enabled: !!filePath && !!content
  });

  // Mutation for applying fixes
  const applyFixes = useApplyFixesMutation();

  const handleApplyFixes = () => {
    applyFixes.mutate({
      filePath,
      content,
      fixType: 'all'
    });
  };
}
```

## Neo4j Integration

The framework integrates with Neo4j for enhanced code intelligence:

### Features:
- Package validation against known libraries
- React pattern validation
- Cross-repository code intelligence
- Best practices enforcement
- Shared knowledge between frontend and backend

### Configuration:
```env
VITE_ENABLE_NEO4J=true
VITE_NEO4J_URI=bolt://localhost:7687
VITE_NEO4J_USER=neo4j
VITE_NEO4J_PASSWORD=your-password
```

### Usage:
```typescript
// Neo4j validation is automatic when enabled
const result = await service.process({
  filePath: 'src/App.tsx',
  content: sourceCode,
  operation: 'analyze',
  options: {
    includeNeo4jValidation: true // Validates imports, patterns, etc.
  }
});

// Check validation results
if (result.neo4jValidation?.issues.length > 0) {
  console.warn('Validation issues:', result.neo4jValidation.issues);
}
```

## Progressive Complexity Levels

The framework supports different complexity levels following crawl_mcp.py methodology:

### Basic Level
- Simple analysis and metrics
- Basic memoization suggestions
- Minimal refactoring options

### Standard Level (Default)
- Comprehensive analysis
- Optimization suggestions
- Safe refactoring operations
- Neo4j validation

### Advanced Level
- Deep performance analysis
- Aggressive optimizations
- Complex refactoring patterns
- Full Neo4j integration

### Enterprise Level
- Complete code intelligence
- All optimizations enabled
- Advanced refactoring
- Cross-repository analysis

## Error Handling

Following crawl_mcp.py patterns:

```typescript
try {
  const result = await service.process(request);
  // Handle success
} catch (error) {
  // Errors are user-friendly and actionable
  console.error('Code intelligence error:', error.message);

  // Check error type
  if (error.message.includes('syntax')) {
    // Handle syntax errors
  } else if (error.message.includes('validation')) {
    // Handle validation errors
  }
}
```

## Performance Considerations

### Debouncing
Real-time analysis is automatically debounced:
```typescript
const { analyze } = useCodeIntelligence({
  enableRealTimeAnalysis: true,
  realTimeDebounceMs: 1000 // 1 second debounce
});
```

### Caching
Results are cached using React Query:
- Analysis results: 5 minutes
- Refactoring candidates: 5 minutes
- Applied fixes: Not cached (mutations)

### Resource Management
- Singleton pattern for service instances
- Automatic cleanup on unmount
- Connection pooling for Neo4j

## Testing

### Unit Tests
```typescript
import { getCodeAnalyzer } from '@/lib/codeIntelligence';

describe('Code Analyzer', () => {
  it('should analyze TypeScript code', async () => {
    const analyzer = getCodeAnalyzer();
    const result = await analyzer.analyze({
      filePath: 'test.ts',
      content: 'const x = 1;'
    });

    expect(result.metrics.lines).toBe(1);
    expect(result.functions).toHaveLength(0);
  });
});
```

### Integration Tests
```typescript
import { renderHook } from '@testing-library/react-hooks';
import { useCodeIntelligence } from '@/lib/codeIntelligence';

describe('useCodeIntelligence', () => {
  it('should initialize and analyze code', async () => {
    const { result, waitFor } = renderHook(() =>
      useCodeIntelligence({ autoInitialize: true })
    );

    await waitFor(() => result.current.isInitialized);

    const analysis = await result.current.analyze(
      'test.tsx',
      'const Component = () => <div>Test</div>;'
    );

    expect(analysis.analysis?.components).toHaveLength(1);
  });
});
```

## Best Practices

### 1. Always Validate Environment
```typescript
const envValidation = validateEnvironment();
if (!envValidation.valid) {
  console.warn('Environment issues:', envValidation.errors);
}
```

### 2. Use Progressive Enhancement
```typescript
// Start with basic analysis
const basicResult = await analyze(file, content, 'analyze');

// Add optimizations if needed
if (basicResult.summary.optimizationPotential === 'high') {
  const optimized = await analyze(file, content, 'optimize');
}
```

### 3. Handle Errors Gracefully
```typescript
const { error, result } = useCodeIntelligence();

if (error) {
  return <ErrorBoundary error={error} />;
}

if (result?.summary.criticalIssues > 0) {
  return <CriticalIssuesWarning issues={result.summary.criticalIssues} />;
}
```

### 4. Respect User Preferences
```typescript
const complexityLevel = user.preferences.codeIntelligenceLevel || 'standard';
const result = await service.process({
  // ...
  options: {
    complexityLevel,
    autoFix: user.preferences.autoFix || false
  }
});
```

## Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**
   - Check environment variables
   - Ensure Neo4j is running
   - Verify credentials

2. **Analysis Timeout**
   - Large files may take longer
   - Consider splitting files
   - Increase timeout settings

3. **Invalid Syntax**
   - Ensure valid TypeScript/JavaScript
   - Check for parser compatibility
   - Use appropriate file extensions

### Debug Mode
```typescript
// Enable debug logging
if (import.meta.env.DEV) {
  window.__CODE_INTELLIGENCE_DEBUG__ = true;
}
```

## Future Enhancements

- [ ] AI-powered refactoring suggestions
- [ ] Cross-file refactoring support
- [ ] Custom rule definitions
- [ ] Performance profiling integration
- [ ] Git integration for impact analysis
- [ ] Team-wide code standards enforcement

## Contributing

When contributing to the code intelligence framework:

1. Follow the methodology in `frontend_development_methodology.js`
2. Ensure all changes are tested
3. Update documentation
4. Consider performance impact
5. Maintain backward compatibility

## License

This framework is part of the IGN Scripts project and follows the same licensing terms.
