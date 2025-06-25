/**
 * Frontend Development Methodology for IGN Scripts Frontend
 *
 * This file provides the core methodology for frontend development, similar to crawl_mcp.py
 * for backend development. It ensures systematic, validated, and production-ready frontend code.
 *
 * CRITICAL PRINCIPLE: Each frontend task must be worked methodically using the step-by-step
 * process defined in this file. Do not find workarounds when encountering problems.
 * Use these principles to work through tasks in a logical and efficient manner.
 */

import { z } from "zod";

// ============================================================================
// CORE METHODOLOGY CONSTANTS
// ============================================================================

export const FRONTEND_METHODOLOGY = {
  VERSION: "1.0.0",
  LAST_UPDATED: "2025-01-10",
  PRINCIPLES: [
    "ENVIRONMENT_VALIDATION_FIRST",
    "COMPREHENSIVE_INPUT_VALIDATION",
    "ROBUST_ERROR_HANDLING",
    "MODULAR_TESTING",
    "PROGRESSIVE_COMPLEXITY",
    "PROPER_RESOURCE_MANAGEMENT",
  ],
};

// ============================================================================
// 1. ENVIRONMENT VALIDATION (Always First!)
// ============================================================================

/**
 * Validate frontend environment before any operation
 * @returns {Promise<EnvironmentValidation>}
 */
export async function validateEnvironment() {
  const validation = {
    valid: true,
    errors: [],
    warnings: [],
    environment: {},
  };

  try {
    // Check Node.js version
    const nodeVersion = process.version;
    const majorVersion = parseInt(nodeVersion.split(".")[0].substring(1));
    if (majorVersion < 18) {
      validation.errors.push(
        `Node.js version ${nodeVersion} is too old. Required: >= 18`,
      );
      validation.valid = false;
    }

    // Check required environment variables
    const requiredEnvVars = [
      "VITE_API_BASE_URL",
      "VITE_NEO4J_URI",
      "VITE_NEO4J_USER",
      "VITE_APP_ENV",
    ];

    for (const envVar of requiredEnvVars) {
      if (!process.env[envVar] && !import.meta.env?.[envVar]) {
        validation.errors.push(
          `Missing required environment variable: ${envVar}`,
        );
        validation.valid = false;
      } else {
        validation.environment[envVar] = "***"; // Masked for security
      }
    }

    // Check optional but recommended environment variables
    const optionalEnvVars = [
      "VITE_SENTRY_DSN",
      "VITE_ANALYTICS_ID",
      "VITE_FEATURE_FLAGS_URL",
    ];

    for (const envVar of optionalEnvVars) {
      if (!process.env[envVar] && !import.meta.env?.[envVar]) {
        validation.warnings.push(
          `Optional environment variable not set: ${envVar}`,
        );
      }
    }

    // Check development dependencies
    try {
      await import("vite");
      await import("vitest");
      await import("@testing-library/react");
    } catch (e) {
      validation.errors.push("Missing required development dependencies");
      validation.valid = false;
    }

    return validation;
  } catch (error) {
    validation.errors.push(`Environment validation failed: ${error.message}`);
    validation.valid = false;
    return validation;
  }
}

// ============================================================================
// 2. INPUT VALIDATION AND SANITIZATION
// ============================================================================

/**
 * Comprehensive input validation using Zod schemas
 */
export const ValidationSchemas = {
  // API Request validation
  apiRequest: z.object({
    endpoint: z
      .string()
      .min(1)
      .regex(/^\/api\/v\d+\//),
    method: z.enum(["GET", "POST", "PUT", "DELETE", "PATCH"]),
    body: z.any().optional(),
    headers: z.record(z.string()).optional(),
    timeout: z.number().min(1000).max(60000).default(10000),
  }),

  // Form data validation
  formData: z.object({
    fields: z.record(z.any()),
    errors: z.record(z.string()).optional(),
    touched: z.record(z.boolean()).optional(),
    isSubmitting: z.boolean().default(false),
  }),

  // Component props validation
  componentProps: z.object({
    className: z.string().optional(),
    children: z.any().optional(),
    disabled: z.boolean().optional(),
    loading: z.boolean().optional(),
    error: z.string().optional(),
  }),

  // Route parameters validation
  routeParams: z.object({
    id: z.string().uuid().optional(),
    slug: z
      .string()
      .regex(/^[a-z0-9-]+$/)
      .optional(),
    page: z.coerce.number().min(1).optional(),
    limit: z.coerce.number().min(1).max(100).optional(),
  }),
};

/**
 * Validate and sanitize input data
 * @template T
 * @param {z.ZodSchema<T>} schema - Zod schema to validate against
 * @param {unknown} data - Data to validate
 * @returns {ValidationResult<T>}
 */
export function validateInput(schema, data) {
  try {
    const validated = schema.parse(data);
    return {
      success: true,
      data: validated,
      errors: null,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        data: null,
        errors: error.errors.map((e) => ({
          path: e.path.join("."),
          message: e.message,
        })),
      };
    }
    return {
      success: false,
      data: null,
      errors: [{ path: "unknown", message: error.message }],
    };
  }
}

// ============================================================================
// 3. COMPREHENSIVE ERROR HANDLING
// ============================================================================

/**
 * Error types for frontend application
 */
export const ErrorTypes = {
  NETWORK: "NETWORK_ERROR",
  VALIDATION: "VALIDATION_ERROR",
  AUTHENTICATION: "AUTHENTICATION_ERROR",
  AUTHORIZATION: "AUTHORIZATION_ERROR",
  NOT_FOUND: "NOT_FOUND_ERROR",
  SERVER: "SERVER_ERROR",
  CLIENT: "CLIENT_ERROR",
  TIMEOUT: "TIMEOUT_ERROR",
  UNKNOWN: "UNKNOWN_ERROR",
};

/**
 * Comprehensive error handler with user-friendly messages
 * @param {Error} error - The error to handle
 * @param {string} context - Context where error occurred
 * @returns {ErrorResult}
 */
export function handleError(error, context) {
  console.error(`Error in ${context}:`, error);

  // Determine error type
  let errorType = ErrorTypes.UNKNOWN;
  let userMessage = "An unexpected error occurred. Please try again.";
  let technicalDetails = error.message;
  let statusCode = 500;

  // Network errors
  if (error.name === "NetworkError" || error.message.includes("fetch")) {
    errorType = ErrorTypes.NETWORK;
    userMessage =
      "Unable to connect to the server. Please check your internet connection.";
    statusCode = 0;
  }
  // Timeout errors
  else if (error.name === "TimeoutError" || error.message.includes("timeout")) {
    errorType = ErrorTypes.TIMEOUT;
    userMessage = "The request took too long. Please try again.";
    statusCode = 408;
  }
  // Authentication errors
  else if (error.status === 401 || error.message.includes("unauthorized")) {
    errorType = ErrorTypes.AUTHENTICATION;
    userMessage = "Your session has expired. Please log in again.";
    statusCode = 401;
  }
  // Authorization errors
  else if (error.status === 403 || error.message.includes("forbidden")) {
    errorType = ErrorTypes.AUTHORIZATION;
    userMessage = "You do not have permission to perform this action.";
    statusCode = 403;
  }
  // Not found errors
  else if (error.status === 404) {
    errorType = ErrorTypes.NOT_FOUND;
    userMessage = "The requested resource was not found.";
    statusCode = 404;
  }
  // Validation errors
  else if (error.status === 400 || error.name === "ValidationError") {
    errorType = ErrorTypes.VALIDATION;
    userMessage = "Please check your input and try again.";
    statusCode = 400;
  }
  // Server errors
  else if (error.status >= 500) {
    errorType = ErrorTypes.SERVER;
    userMessage = "A server error occurred. Our team has been notified.";
    statusCode = error.status;
  }

  return {
    type: errorType,
    userMessage,
    technicalDetails,
    statusCode,
    context,
    timestamp: new Date().toISOString(),
    error: error,
  };
}

// ============================================================================
// 4. MODULAR TESTING INTEGRATION
// ============================================================================

/**
 * Testing utilities following frontend best practices
 */
export const TestingUtils = {
  /**
   * Setup test environment with all required mocks
   */
  async setupTestEnvironment() {
    // Mock environment variables
    process.env.VITE_API_BASE_URL = "http://localhost:8000";
    process.env.VITE_NEO4J_URI = "bolt://localhost:7687";
    process.env.VITE_NEO4J_USER = "neo4j";
    process.env.VITE_APP_ENV = "test";

    // Setup global mocks
    global.fetch = vi.fn();
    global.localStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
    };

    // Mock IntersectionObserver
    global.IntersectionObserver = vi.fn().mockImplementation(() => ({
      observe: vi.fn(),
      unobserve: vi.fn(),
      disconnect: vi.fn(),
    }));
  },

  /**
   * Create mock API response
   */
  createMockResponse(data, options = {}) {
    return {
      ok: options.ok ?? true,
      status: options.status ?? 200,
      statusText: options.statusText ?? "OK",
      headers: new Headers(options.headers ?? {}),
      json: async () => data,
      text: async () => JSON.stringify(data),
      blob: async () => new Blob([JSON.stringify(data)]),
      clone: () => this.createMockResponse(data, options),
    };
  },

  /**
   * Wait for async updates in tests
   */
  async waitForAsync() {
    await new Promise((resolve) => setTimeout(resolve, 0));
  },

  /**
   * Test component rendering with all providers
   */
  renderWithProviders(component, options = {}) {
    const { initialState = {}, route = "/", ...renderOptions } = options;

    // Setup router
    window.history.pushState({}, "Test page", route);

    // Render with all required providers
    return render(
      <BrowserRouter>
        <QueryClientProvider
          client={
            new QueryClient({
              defaultOptions: {
                queries: { retry: false },
                mutations: { retry: false },
              },
            })
          }
        >
          {component}
        </QueryClientProvider>
      </BrowserRouter>,
      renderOptions,
    );
  },
};

// ============================================================================
// 5. PROGRESSIVE COMPLEXITY
// ============================================================================

/**
 * Progressive complexity levels for frontend features
 */
export const ComplexityLevels = {
  BASIC: {
    name: "Basic",
    features: [
      "Static components",
      "Basic routing",
      "Simple forms",
      "Local state management",
      "Basic API calls",
    ],
    requirements: {
      react: ">=18.0.0",
      typescript: ">=4.9.0",
      vite: ">=4.0.0",
    },
  },
  STANDARD: {
    name: "Standard",
    features: [
      "Dynamic components",
      "Advanced routing with guards",
      "Form validation with react-hook-form",
      "Global state with Zustand/Context",
      "API integration with React Query",
      "Error boundaries",
      "Loading states",
    ],
    requirements: {
      "react-router-dom": ">=6.0.0",
      "react-hook-form": ">=7.0.0",
      "@tanstack/react-query": ">=4.0.0",
      zod: ">=3.0.0",
    },
  },
  ADVANCED: {
    name: "Advanced",
    features: [
      "Code splitting",
      "Lazy loading",
      "WebSocket connections",
      "Real-time updates",
      "Optimistic updates",
      "Advanced caching strategies",
      "Performance optimization",
      "PWA features",
    ],
    requirements: {
      "socket.io-client": ">=4.0.0",
      workbox: ">=6.0.0",
      "@sentry/react": ">=7.0.0",
    },
  },
  ENTERPRISE: {
    name: "Enterprise",
    features: [
      "Micro-frontend architecture",
      "Module federation",
      "Advanced security (CSP, CORS)",
      "Multi-tenancy support",
      "Internationalization",
      "Accessibility (WCAG 2.1 AA)",
      "Analytics integration",
      "A/B testing framework",
    ],
    requirements: {
      "@module-federation/enhanced": ">=0.1.0",
      "react-i18next": ">=12.0.0",
      "react-helmet-async": ">=1.3.0",
    },
  },
};

/**
 * Get current complexity level based on package.json
 */
export async function getCurrentComplexityLevel() {
  try {
    const packageJson = await import("../../package.json");
    const dependencies = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies,
    };

    // Check which complexity level we match
    for (const [level, config] of Object.entries(ComplexityLevels).reverse()) {
      const allRequirementsMet = Object.entries(config.requirements).every(
        ([pkg, version]) => dependencies[pkg] !== undefined,
      );

      if (allRequirementsMet) {
        return level;
      }
    }

    return "BASIC";
  } catch (error) {
    console.warn("Could not determine complexity level:", error);
    return "BASIC";
  }
}

// ============================================================================
// 6. RESOURCE MANAGEMENT
// ============================================================================

/**
 * Resource management utilities for frontend
 */
export class ResourceManager {
  constructor() {
    this.resources = new Map();
    this.cleanupFunctions = new Map();
  }

  /**
   * Register a resource with cleanup function
   */
  register(id, resource, cleanupFn) {
    this.resources.set(id, resource);
    if (cleanupFn) {
      this.cleanupFunctions.set(id, cleanupFn);
    }
  }

  /**
   * Get a registered resource
   */
  get(id) {
    return this.resources.get(id);
  }

  /**
   * Clean up a specific resource
   */
  async cleanup(id) {
    const cleanupFn = this.cleanupFunctions.get(id);
    if (cleanupFn) {
      try {
        await cleanupFn();
      } catch (error) {
        console.error(`Error cleaning up resource ${id}:`, error);
      }
    }
    this.resources.delete(id);
    this.cleanupFunctions.delete(id);
  }

  /**
   * Clean up all resources
   */
  async cleanupAll() {
    const cleanupPromises = Array.from(this.cleanupFunctions.entries()).map(
      async ([id, cleanupFn]) => {
        try {
          await cleanupFn();
        } catch (error) {
          console.error(`Error cleaning up resource ${id}:`, error);
        }
      },
    );

    await Promise.all(cleanupPromises);
    this.resources.clear();
    this.cleanupFunctions.clear();
  }
}

// Global resource manager instance
export const globalResourceManager = new ResourceManager();

// ============================================================================
// 7. API INTEGRATION PATTERNS
// ============================================================================

/**
 * API client with comprehensive error handling and retries
 */
export class APIClient {
  constructor(baseURL = import.meta.env.VITE_API_BASE_URL) {
    this.baseURL = baseURL;
    this.defaultTimeout = 10000;
    this.maxRetries = 3;
    this.retryDelay = 1000;
  }

  /**
   * Make API request with automatic retries and error handling
   */
  async request(endpoint, options = {}) {
    const validation = validateInput(ValidationSchemas.apiRequest, {
      endpoint,
      method: options.method || "GET",
      body: options.body,
      headers: options.headers,
      timeout: options.timeout || this.defaultTimeout,
    });

    if (!validation.success) {
      throw new Error(
        `Invalid API request: ${JSON.stringify(validation.errors)}`,
      );
    }

    const { data: validatedOptions } = validation;
    let lastError;

    // Retry logic
    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(
          () => controller.abort(),
          validatedOptions.timeout,
        );

        const response = await fetch(
          `${this.baseURL}${validatedOptions.endpoint}`,
          {
            method: validatedOptions.method,
            headers: {
              "Content-Type": "application/json",
              ...validatedOptions.headers,
              Authorization: `Bearer ${localStorage.getItem("auth_token") || ""}`,
            },
            body: validatedOptions.body
              ? JSON.stringify(validatedOptions.body)
              : undefined,
            signal: controller.signal,
          },
        );

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(
            `API error: ${response.status} ${response.statusText}`,
          );
        }

        const data = await response.json();
        return { success: true, data };
      } catch (error) {
        lastError = error;

        // Don't retry on client errors (4xx)
        if (
          error.message.includes("4") &&
          error.message.match(/^API error: 4\d\d/)
        ) {
          break;
        }

        // Wait before retry
        if (attempt < this.maxRetries) {
          await new Promise((resolve) =>
            setTimeout(resolve, this.retryDelay * (attempt + 1)),
          );
        }
      }
    }

    return {
      success: false,
      error: handleError(lastError, `API request to ${endpoint}`),
    };
  }
}

// ============================================================================
// 8. STATE MANAGEMENT PATTERNS
// ============================================================================

/**
 * State management utilities with persistence
 */
export class StateManager {
  constructor(storageKey = "app_state") {
    this.storageKey = storageKey;
    this.subscribers = new Set();
    this.state = this.loadState();
  }

  /**
   * Load state from localStorage
   */
  loadState() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error("Failed to load state:", error);
      return {};
    }
  }

  /**
   * Save state to localStorage
   */
  saveState() {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.state));
    } catch (error) {
      console.error("Failed to save state:", error);
    }
  }

  /**
   * Get state value
   */
  get(key) {
    return this.state[key];
  }

  /**
   * Set state value
   */
  set(key, value) {
    this.state[key] = value;
    this.saveState();
    this.notify();
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  /**
   * Notify subscribers of state changes
   */
  notify() {
    this.subscribers.forEach((callback) => callback(this.state));
  }

  /**
   * Clear state
   */
  clear() {
    this.state = {};
    this.saveState();
    this.notify();
  }
}

// ============================================================================
// 9. PERFORMANCE MONITORING
// ============================================================================

/**
 * Performance monitoring utilities
 */
export class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.observers = new Map();
  }

  /**
   * Start timing an operation
   */
  startTiming(operation) {
    this.metrics.set(operation, {
      start: performance.now(),
      end: null,
      duration: null,
    });
  }

  /**
   * End timing an operation
   */
  endTiming(operation) {
    const metric = this.metrics.get(operation);
    if (metric) {
      metric.end = performance.now();
      metric.duration = metric.end - metric.start;
      console.debug(`${operation} took ${metric.duration.toFixed(2)}ms`);
    }
  }

  /**
   * Monitor component render performance
   */
  monitorComponent(componentName) {
    return {
      onRender: (
        id,
        phase,
        actualDuration,
        baseDuration,
        startTime,
        commitTime,
      ) => {
        console.debug(`${componentName} (${phase}):`, {
          actualDuration: actualDuration.toFixed(2),
          baseDuration: baseDuration.toFixed(2),
        });
      },
    };
  }

  /**
   * Get performance report
   */
  getReport() {
    const report = {
      timings: Object.fromEntries(this.metrics),
      navigation: performance.getEntriesByType("navigation")[0],
      resources: performance.getEntriesByType("resource").map((r) => ({
        name: r.name,
        duration: r.duration,
        size: r.transferSize,
      })),
    };

    return report;
  }
}

// ============================================================================
// 10. DEVELOPMENT WORKFLOW HELPERS
// ============================================================================

/**
 * Development workflow utilities
 */
export const DevelopmentWorkflow = {
  /**
   * Check if running in development mode
   */
  isDevelopment() {
    return import.meta.env.MODE === "development";
  },

  /**
   * Check if running in production mode
   */
  isProduction() {
    return import.meta.env.MODE === "production";
  },

  /**
   * Log debug information in development only
   */
  debug(...args) {
    if (this.isDevelopment()) {
      console.debug("[DEBUG]", ...args);
    }
  },

  /**
   * Performance profiling wrapper
   */
  async profile(name, fn) {
    if (this.isDevelopment()) {
      console.time(name);
      try {
        const result = await fn();
        console.timeEnd(name);
        return result;
      } catch (error) {
        console.timeEnd(name);
        throw error;
      }
    } else {
      return fn();
    }
  },

  /**
   * Feature flag checking
   */
  isFeatureEnabled(feature) {
    const flags = import.meta.env.VITE_FEATURE_FLAGS || "";
    return flags.split(",").includes(feature);
  },
};

// ============================================================================
// USAGE EXAMPLE
// ============================================================================

/**
 * Example of using the frontend methodology in a component
 *
 * @example
 * ```jsx
 * import { validateEnvironment, validateInput, handleError, APIClient } from './frontend_development_methodology';
 *
 * function MyComponent() {
 *   const [loading, setLoading] = useState(false);
 *   const [error, setError] = useState(null);
 *   const apiClient = new APIClient();
 *
 *   useEffect(() => {
 *     // 1. Always validate environment first
 *     validateEnvironment().then(validation => {
 *       if (!validation.valid) {
 *         console.error('Environment validation failed:', validation.errors);
 *       }
 *     });
 *   }, []);
 *
 *   const handleSubmit = async (formData) => {
 *     // 2. Validate inputs
 *     const validation = validateInput(FormSchema, formData);
 *     if (!validation.success) {
 *       setError(validation.errors);
 *       return;
 *     }
 *
 *     // 3. Make API call with error handling
 *     setLoading(true);
 *     try {
 *       const result = await apiClient.request('/api/v1/submit', {
 *         method: 'POST',
 *         body: validation.data
 *       });
 *
 *       if (result.success) {
 *         // Handle success
 *       } else {
 *         setError(result.error.userMessage);
 *       }
 *     } catch (err) {
 *       const errorResult = handleError(err, 'form submission');
 *       setError(errorResult.userMessage);
 *     } finally {
 *       setLoading(false);
 *     }
 *   };
 *
 *   return (
 *     // Component JSX
 *   );
 * }
 * ```
 */

// Export all utilities
export default {
  FRONTEND_METHODOLOGY,
  validateEnvironment,
  ValidationSchemas,
  validateInput,
  ErrorTypes,
  handleError,
  TestingUtils,
  ComplexityLevels,
  getCurrentComplexityLevel,
  ResourceManager,
  globalResourceManager,
  APIClient,
  StateManager,
  PerformanceMonitor,
  DevelopmentWorkflow,
};
