import React from "react";
import { CommandLineIcon } from "@heroicons/react/24/outline";

export function TemplateManagerPage() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="border-b border-slate-700 pb-6 mb-8">
          <div className="flex items-center space-x-3">
            <CommandLineIcon className="h-8 w-8 text-blue-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-100">
                Template Manager
              </h1>
              <p className="mt-2 text-slate-400">
                Manage script templates and configurations
              </p>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-8">
          <div className="space-y-2 font-mono text-sm text-slate-400">
            <div>ign template list</div>
            <div>ign template create --name custom-template</div>
            <div>ign template validate --template-id 123</div>
          </div>
        </div>

        <div className="text-center py-16">
          <CommandLineIcon className="h-24 w-24 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">
            Template Manager UI Coming Soon
          </h3>
          <p className="text-slate-500">
            Web interface for managing script templates.
          </p>
        </div>
      </div>
    </div>
  );
}
