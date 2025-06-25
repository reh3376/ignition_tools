import { useState, useEffect } from "react";
import { authService, type AuthState, type User } from "../lib/auth";

/**
 * Custom hook for managing authentication state
 * Provides reactive access to authentication status and actions
 */
export function useAuth() {
  const [authState, setAuthState] = useState<AuthState>(authService.getState());

  useEffect(() => {
    // Subscribe to auth state changes
    const unsubscribe = authService.subscribe(setAuthState);

    // Cleanup subscription on unmount
    return unsubscribe;
  }, []);

  return {
    // Authentication state
    isAuthenticated: authState.isAuthenticated,
    isLoading: authState.isLoading,
    user: authState.user,
    error: authState.error,

    // Authentication actions
    loginWithWhiskeyHouse: () => authService.loginWithWhiskeyHouse(),
    logout: () => authService.logout(),

    // Utility functions
    hasRole: (role: string) => authService.hasRole(role),
    isAdmin: () => authService.isAdmin(),
    isDeveloper: () => authService.isDeveloper(),
    getAccessToken: () => authService.getAccessToken(),
  };
}

/**
 * Hook for getting user information
 * Returns null if user is not authenticated
 */
export function useUser(): User | null {
  const { user } = useAuth();
  return user;
}

/**
 * Hook for checking if user has specific role
 */
export function useHasRole(role: string): boolean {
  const { hasRole } = useAuth();
  return hasRole(role);
}

/**
 * Hook for checking if user is admin
 */
export function useIsAdmin(): boolean {
  const { isAdmin } = useAuth();
  return isAdmin();
}

/**
 * Hook for checking if user is developer
 */
export function useIsDeveloper(): boolean {
  const { isDeveloper } = useAuth();
  return isDeveloper();
}
