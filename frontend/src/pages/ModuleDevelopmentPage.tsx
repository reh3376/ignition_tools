import React from "react";
import { CubeIcon } from "@heroicons/react/24/outline";

export function ModuleDevelopmentPage() {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <div className="border-b border-slate-700 pb-6 mb-8">
          <div className="flex items-center space-x-3">
            <CubeIcon className="h-8 w-8 text-purple-400" />
            <div>
              <h1 className="text-3xl font-bold text-slate-100">
                Module Development
              </h1>
              <p className="mt-2 text-slate-400">
                Build and manage Ignition modules
              </p>
            </div>
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 mb-8">
          <div className="space-y-2 font-mono text-sm text-slate-400">
            <div>ign module create --name my-module</div>
            <div>ign module build --module-path ./modules/my-module</div>
            <div>
              ign module validate --unsigned-module-path ./dist/my-module.modl
            </div>
          </div>
        </div>

        <div className="text-center py-16">
          <CubeIcon className="h-24 w-24 text-slate-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-300 mb-2">
            Module Development UI Coming Soon
          </h3>
          <p className="text-slate-500">
            Web interface for Ignition module development.
          </p>
        </div>
      </div>
    </div>
  );
}
