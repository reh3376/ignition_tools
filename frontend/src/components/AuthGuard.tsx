import React from "react";
import { useAuth } from "../hooks/useAuth";
import { LoginPage } from "./LoginPage";

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole?: string;
  fallback?: React.ReactNode;
}

/**
 * AuthGuard component that protects routes and requires authentication
 * Optionally requires specific roles for access
 */
export function AuthGuard({
  children,
  requiredRole,
  fallback,
}: AuthGuardProps) {
  const { isAuthenticated, isLoading, user, hasRole } = useAuth();

  // Show loading spinner while authentication is being checked
  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-400 mx-auto mb-4"></div>
          <p className="text-slate-400">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <LoginPage />;
  }

  // Check role-based access if required
  if (requiredRole && !hasRole(requiredRole)) {
    if (fallback) {
      return <>{fallback}</>;
    }

    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="max-w-md w-full bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-8 h-8 text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
                />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-slate-100 mb-2">
              Access Denied
            </h2>
            <p className="text-slate-400 mb-4">
              You don't have the required permissions to access this page.
            </p>
            <div className="text-sm text-slate-500">
              <p>
                Required role:{" "}
                <span className="font-mono text-slate-300">{requiredRole}</span>
              </p>
              <p>
                Your roles:{" "}
                <span className="font-mono text-slate-300">
                  {user?.roles.join(", ") || "none"}
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // User is authenticated and has required role (if any)
  return <>{children}</>;
}
