/**
 * React Hook for Neo4j Knowledge Graph Integration
 *
 * This hook provides a convenient interface for React components to access
 * the Neo4j knowledge graph following the frontend development methodology.
 */

import { useState, useEffect, useCallback } from "react";
import {
  getNeo4jClient,
  closeNeo4jClient,
  Neo4jFrontendClient,
} from "../lib/neo4j/client";
import { handleError } from "../docs/frontend_development_methodology";

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

export interface UseNeo4jState {
  isInitialized: boolean;
  isLoading: boolean;
  error: Error | null;
}

export interface UseNeo4jResult extends UseNeo4jState {
  client: Neo4jFrontendClient | null;
  searchClasses: (searchTerm: string, repository?: string) => Promise<any[]>;
  searchFunctions: (searchTerm: string, repository?: string) => Promise<any[]>;
  getClassDetails: (className: string) => Promise<any>;
  getCodePatterns: (context: string, limit?: number) => Promise<any[]>;
  validateImports: (imports: string[]) => Promise<Record<string, boolean>>;
  getSimilarImplementations: (
    functionSignature: string,
    limit?: number,
  ) => Promise<any[]>;
  semanticCodeSearch: (
    query: string,
    repository?: string,
    limit?: number,
  ) => Promise<any[]>;
  getCodeQualityMetrics: (filePath: string) => Promise<any>;
  getDependencyGraph: (moduleName: string) => Promise<any>;
  getRepositories: () => Promise<string[]>;
}

// ============================================================================
// CUSTOM HOOK
// ============================================================================

/**
 * Hook for accessing Neo4j knowledge graph in React components
 */
export function useNeo4j(): UseNeo4jResult {
  const [state, setState] = useState<UseNeo4jState>({
    isInitialized: false,
    isLoading: true,
    error: null,
  });

  const [client, setClient] = useState<Neo4jFrontendClient | null>(null);

  // Initialize client on mount
  useEffect(() => {
    let mounted = true;

    const initializeClient = async () => {
      try {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));

        const neo4jClient = await getNeo4jClient();

        if (mounted) {
          setClient(neo4jClient);
          setState({
            isInitialized: true,
            isLoading: false,
            error: null,
          });
        }
      } catch (error) {
        if (mounted) {
          const errorResult = handleError(
            error as Error,
            "Neo4j initialization",
          );
          setState({
            isInitialized: false,
            isLoading: false,
            error: new Error(errorResult.userMessage),
          });
        }
      }
    };

    initializeClient();

    // Cleanup on unmount
    return () => {
      mounted = false;
    };
  }, []);

  // Wrapped methods with error handling
  const searchClasses = useCallback(
    async (searchTerm: string, repository?: string): Promise<any[]> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.searchClasses(searchTerm, repository);
      } catch (error) {
        const errorResult = handleError(error as Error, "Class search");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const searchFunctions = useCallback(
    async (searchTerm: string, repository?: string): Promise<any[]> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.searchFunctions(searchTerm, repository);
      } catch (error) {
        const errorResult = handleError(error as Error, "Function search");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const getClassDetails = useCallback(
    async (className: string): Promise<any> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.getClassDetails(className);
      } catch (error) {
        const errorResult = handleError(error as Error, "Get class details");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const getCodePatterns = useCallback(
    async (context: string, limit: number = 5): Promise<any[]> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.getCodePatterns(context, limit);
      } catch (error) {
        const errorResult = handleError(error as Error, "Get code patterns");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const validateImports = useCallback(
    async (imports: string[]): Promise<Record<string, boolean>> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.validateImports(imports);
      } catch (error) {
        const errorResult = handleError(error as Error, "Validate imports");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const getSimilarImplementations = useCallback(
    async (functionSignature: string, limit: number = 5): Promise<any[]> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.getSimilarImplementations(functionSignature, limit);
      } catch (error) {
        const errorResult = handleError(
          error as Error,
          "Get similar implementations",
        );
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const semanticCodeSearch = useCallback(
    async (
      query: string,
      repository?: string,
      limit: number = 10,
    ): Promise<any[]> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.semanticCodeSearch(query, repository, limit);
      } catch (error) {
        const errorResult = handleError(error as Error, "Semantic code search");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const getCodeQualityMetrics = useCallback(
    async (filePath: string): Promise<any> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.getCodeQualityMetrics(filePath);
      } catch (error) {
        const errorResult = handleError(
          error as Error,
          "Get code quality metrics",
        );
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const getDependencyGraph = useCallback(
    async (moduleName: string): Promise<any> => {
      if (!client || !state.isInitialized) {
        throw new Error("Neo4j client not initialized");
      }

      try {
        return await client.getDependencyGraph(moduleName);
      } catch (error) {
        const errorResult = handleError(error as Error, "Get dependency graph");
        throw new Error(errorResult.userMessage);
      }
    },
    [client, state.isInitialized],
  );

  const getRepositories = useCallback(async (): Promise<string[]> => {
    if (!client || !state.isInitialized) {
      throw new Error("Neo4j client not initialized");
    }

    try {
      return await client.getRepositories();
    } catch (error) {
      const errorResult = handleError(error as Error, "Get repositories");
      throw new Error(errorResult.userMessage);
    }
  }, [client, state.isInitialized]);

  return {
    ...state,
    client,
    searchClasses,
    searchFunctions,
    getClassDetails,
    getCodePatterns,
    validateImports,
    getSimilarImplementations,
    semanticCodeSearch,
    getCodeQualityMetrics,
    getDependencyGraph,
    getRepositories,
  };
}

// ============================================================================
// EXAMPLE USAGE IN COMPONENTS
// ============================================================================

/**
 * Example usage in a React component:
 *
 * ```tsx
 * import { useNeo4j } from '../hooks/useNeo4j';
 *
 * function CodeSearchComponent() {
 *   const { isInitialized, isLoading, error, searchClasses } = useNeo4j();
 *   const [results, setResults] = useState([]);
 *
 *   const handleSearch = async (searchTerm: string) => {
 *     try {
 *       const classes = await searchClasses(searchTerm);
 *       setResults(classes);
 *     } catch (error) {
 *       console.error('Search failed:', error);
 *     }
 *   };
 *
 *   if (isLoading) return <div>Loading Neo4j...</div>;
 *   if (error) return <div>Error: {error.message}</div>;
 *   if (!isInitialized) return <div>Neo4j not available</div>;
 *
 *   return (
 *     <div>
 *       <input onChange={e => handleSearch(e.target.value)} />
 *       {results.map(result => (
 *         <div key={result.name}>{result.name}</div>
 *       ))}
 *     </div>
 *   );
 * }
 * ```
 */
