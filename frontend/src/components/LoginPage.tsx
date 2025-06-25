import React from "react";
import { useAuth } from "../hooks/useAuth";
import {
  CommandLineIcon,
  BuildingOfficeIcon,
} from "@heroicons/react/24/outline";

export function LoginPage() {
  const { loginWithWhiskeyHouse, isLoading, error } = useAuth();

  const handleLogin = async () => {
    try {
      await loginWithWhiskeyHouse();
    } catch (err) {
      console.error("Login failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          {/* Logo and Title */}
          <div className="flex justify-center mb-6">
            <div className="bg-green-400/20 p-4 rounded-full">
              <CommandLineIcon className="h-12 w-12 text-green-400" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-slate-100 mb-2">
            IGN Scripts
          </h2>
          <p className="text-slate-400 mb-8">
            Industrial Automation Development Platform
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 space-y-6">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-slate-100 mb-2">
              Sign in to continue
            </h3>
            <p className="text-sm text-slate-400">
              Access your Ignition development tools and resources
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <svg
                  className="w-5 h-5 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <span className="text-red-400 text-sm font-medium">
                  Login Failed
                </span>
              </div>
              <p className="text-red-300 text-sm mt-2">{error}</p>
            </div>
          )}

          {/* Whiskey House SSO Button */}
          <button
            onClick={handleLogin}
            disabled={isLoading}
            className={`
              w-full flex items-center justify-center space-x-3 px-6 py-3 rounded-lg
              bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed
              text-white font-medium transition-colors duration-200
              ${isLoading ? "opacity-75" : ""}
            `}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Signing in...</span>
              </>
            ) : (
              <>
                <BuildingOfficeIcon className="h-5 w-5" />
                <span>Sign in with Whiskey House</span>
              </>
            )}
          </button>

          <div className="text-center">
            <p className="text-xs text-slate-500">
              Sign in using your{" "}
              <span className="font-mono">username@whiskeyhouse.com</span>{" "}
              account
            </p>
          </div>
        </div>

        {/* Additional Information */}
        <div className="text-center space-y-4">
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-slate-300 mb-2">
              What you'll get access to:
            </h4>
            <ul className="text-xs text-slate-400 space-y-1">
              <li>• Jython script generation for Ignition</li>
              <li>• Template management and sharing</li>
              <li>• Module development tools</li>
              <li>• Code refactoring and optimization</li>
              <li>• Advanced deployment features</li>
            </ul>
          </div>

          <p className="text-xs text-slate-500">
            Need help? Contact your system administrator or check the{" "}
            <a href="#" className="text-blue-400 hover:text-blue-300">
              documentation
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
