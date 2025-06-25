import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "./components/AppShell";
import { AuthGuard } from "./components/AuthGuard";
import { HomePage } from "./pages/HomePage";
import { ScriptGeneratorPage } from "./pages/ScriptGeneratorPage";
import { TemplateManagerPage } from "./pages/TemplateManagerPage";
import { ModuleDevelopmentPage } from "./pages/ModuleDevelopmentPage";
import { RefactorToolsPage } from "./pages/RefactorToolsPage";
import { DeploymentPage } from "./pages/DeploymentPage";
import { AdvancedFeaturesPage } from "./pages/AdvancedFeaturesPage";
import { SetupPage } from "./pages/SetupPage";
import "./index.css";

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-900 text-white">
          <AuthGuard>
            <AppShell>
              <Routes>
                {/* Home Dashboard */}
                <Route path="/" element={<HomePage />} />

                {/* CLI Command Group Pages */}
                <Route path="/script/*" element={<ScriptGeneratorPage />} />
                <Route path="/template/*" element={<TemplateManagerPage />} />
                <Route path="/module/*" element={<ModuleDevelopmentPage />} />
                <Route path="/refactor/*" element={<RefactorToolsPage />} />
                <Route path="/deploy/*" element={<DeploymentPage />} />
                <Route path="/advanced/*" element={<AdvancedFeaturesPage />} />
                <Route path="/setup" element={<SetupPage />} />

                {/* Fallback */}
                <Route path="*" element={<HomePage />} />
              </Routes>
            </AppShell>
          </AuthGuard>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
