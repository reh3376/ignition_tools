import React from "react";
import { WrenchScrewdriverIcon } from "@heroicons/react/24/outline";

export function RefactorToolsPage() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="border-b border-slate-700 pb-6 mb-8">
          <div className="flex items-center space-x-3">
            <WrenchScrewdriverIcon className="h-8 w-8 text-yellow-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-100">
                Refactor Tools
              </h1>
              <p className="mt-2 text-slate-400">
                Automated code refactoring and optimization
              </p>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-8">
          <div className="space-y-2 font-mono text-sm text-slate-400">
            <div>ign refactor detect</div>
            <div>ign refactor analyze --file large_file.py</div>
            <div>ign refactor split --file oversized_module.py</div>
          </div>
        </div>

        <div className="text-center py-16">
          <WrenchScrewdriverIcon className="h-24 w-24 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">
            Refactor Tools UI Coming Soon
          </h3>
          <p className="text-slate-500">
            Web interface for automated code refactoring.
          </p>
        </div>
      </div>
    </div>
  );
}
