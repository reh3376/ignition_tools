/**
 * TypeScript Type Definitions for Frontend Development Methodology
 */

import { z } from "zod";

// Environment Validation Types
export interface EnvironmentValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  environment: Record<string, string>;
}

// Validation Result Types
export interface ValidationResult<T> {
  success: boolean;
  data: T | null;
  errors: ValidationError[] | null;
}

export interface ValidationError {
  path: string;
  message: string;
}

// Error Handling Types
export interface ErrorResult {
  type: string;
  userMessage: string;
  technicalDetails: string;
  statusCode: number;
  context: string;
  timestamp: string;
  error: Error;
}

// API Types
export interface APIRequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  body?: any;
  headers?: Record<string, string>;
  timeout?: number;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: ErrorResult;
}

// Complexity Level Types
export interface ComplexityLevel {
  name: string;
  features: string[];
  requirements: Record<string, string>;
}

// Performance Metric Types
export interface PerformanceMetric {
  start: number;
  end: number | null;
  duration: number | null;
}

export interface PerformanceReport {
  timings: Record<string, PerformanceMetric>;
  navigation: PerformanceNavigationTiming;
  resources: Array<{
    name: string;
    duration: number;
    size: number;
  }>;
}

// Test Mock Types
export interface MockResponseOptions {
  ok?: boolean;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
}

export interface RenderOptions {
  initialState?: Record<string, any>;
  route?: string;
}

// State Manager Types
export type StateSubscriber = (state: Record<string, any>) => void;

// Resource Manager Types
export type CleanupFunction = () => void | Promise<void>;

// Schema Types (inferred from Zod)
export type APIRequestSchema = z.infer<
  typeof import("./frontend_development_methodology").ValidationSchemas.apiRequest
>;
export type FormDataSchema = z.infer<
  typeof import("./frontend_development_methodology").ValidationSchemas.formData
>;
export type ComponentPropsSchema = z.infer<
  typeof import("./frontend_development_methodology").ValidationSchemas.componentProps
>;
export type RouteParamsSchema = z.infer<
  typeof import("./frontend_development_methodology").ValidationSchemas.routeParams
>;
