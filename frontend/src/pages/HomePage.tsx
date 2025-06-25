import React from "react";
import {
  CommandLineIcon,
  DocumentTextIcon,
  CubeIcon,
  WrenchScrewdriverIcon,
  CloudArrowUpIcon,
  SparklesIcon,
  CogIcon,
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";

interface QuickAction {
  name: string;
  description: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  cliCommand: string;
  color: string;
}

const quickActions: QuickAction[] = [
  {
    name: "Generate Script",
    description: "Create Jython scripts for Ignition",
    href: "/script",
    icon: DocumentTextIcon,
    cliCommand: "ign script generate",
    color: "text-green-400 hover:text-green-300",
  },
  {
    name: "Manage Templates",
    description: "Create and manage script templates",
    href: "/template",
    icon: CommandLineIcon,
    cliCommand: "ign template list",
    color: "text-blue-400 hover:text-blue-300",
  },
  {
    name: "Develop Module",
    description: "Build Ignition modules",
    href: "/module",
    icon: CubeIcon,
    cliCommand: "ign module create",
    color: "text-purple-400 hover:text-purple-300",
  },
  {
    name: "Refactor Code",
    description: "Automated code refactoring tools",
    href: "/refactor",
    icon: WrenchScrewdriverIcon,
    cliCommand: "ign refactor detect",
    color: "text-yellow-400 hover:text-yellow-300",
  },
  {
    name: "Deploy Module",
    description: "Deploy and distribute modules",
    href: "/deploy",
    icon: CloudArrowUpIcon,
    cliCommand: "ign deploy package",
    color: "text-indigo-400 hover:text-indigo-300",
  },
  {
    name: "Advanced Features",
    description: "Phase 9.8 advanced capabilities",
    href: "/advanced",
    icon: SparklesIcon,
    cliCommand: "ign advanced ai-assistant",
    color: "text-pink-400 hover:text-pink-300",
  },
];

interface SystemStatus {
  name: string;
  status: "online" | "offline" | "warning";
  lastCheck: string;
  details: string;
}

const systemStatuses: SystemStatus[] = [
  {
    name: "CLI Backend",
    status: "online",
    lastCheck: "2 minutes ago",
    details: "All CLI commands available",
  },
  {
    name: "Neo4j Database",
    status: "online",
    lastCheck: "5 minutes ago",
    details: "3,691+ nodes indexed",
  },
  {
    name: "Vector Embeddings",
    status: "online",
    lastCheck: "1 minute ago",
    details: "384D embeddings ready",
  },
  {
    name: "SME Agent",
    status: "warning",
    lastCheck: "10 minutes ago",
    details: "Human evaluation pending",
  },
];

interface RecentActivity {
  action: string;
  timestamp: string;
  status: "success" | "error" | "pending";
}

const recentActivities: RecentActivity[] = [
  {
    action: "Script generated for OPC-UA client",
    timestamp: "5 minutes ago",
    status: "success",
  },
  {
    action: "Module refactoring completed",
    timestamp: "15 minutes ago",
    status: "success",
  },
  {
    action: "Template validation in progress",
    timestamp: "20 minutes ago",
    status: "pending",
  },
  {
    action: "Deployment package created",
    timestamp: "1 hour ago",
    status: "success",
  },
];

export function HomePage() {
  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="border-b border-slate-700 pb-6">
        <h1 className="text-3xl font-bold text-slate-100">
          IGN Scripts Dashboard
        </h1>
        <p className="mt-2 text-slate-400">
          Command-line interface for Ignition development - now with web UI
        </p>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {systemStatuses.map((system) => (
          <div
            key={system.name}
            className="bg-slate-800 border border-slate-700 rounded-lg p-4"
          >
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-slate-200">
                {system.name}
              </h3>
              <div
                className={`w-3 h-3 rounded-full ${
                  system.status === "online"
                    ? "bg-green-500"
                    : system.status === "warning"
                      ? "bg-yellow-500"
                      : "bg-red-500"
                }`}
              />
            </div>
            <p className="mt-2 text-xs text-slate-400">{system.details}</p>
            <p className="mt-1 text-xs text-slate-500">
              Last check: {system.lastCheck}
            </p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-slate-100 mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.name}
                to={action.href}
                className="group bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`h-8 w-8 ${action.color}`} />
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-slate-200 group-hover:text-slate-100">
                      {action.name}
                    </h3>
                    <p className="text-sm text-slate-400 mt-1">
                      {action.description}
                    </p>
                    <code className="text-xs text-slate-500 mt-2 block font-mono">
                      {action.cliCommand}
                    </code>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity & CLI Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <div>
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            Recent Activity
          </h2>
          <div className="bg-slate-800 border border-slate-700 rounded-lg">
            <div className="p-4 space-y-3">
              {recentActivities.map((activity, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div
                    className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      activity.status === "success"
                        ? "bg-green-500"
                        : activity.status === "error"
                          ? "bg-red-500"
                          : "bg-yellow-500"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-200 truncate">
                      {activity.action}
                    </p>
                    <p className="text-xs text-slate-500">
                      {activity.timestamp}
                    </p>
                  </div>
                  {activity.status === "success" && (
                    <CheckCircleIcon className="h-4 w-4 text-green-500" />
                  )}
                  {activity.status === "pending" && (
                    <ClockIcon className="h-4 w-4 text-yellow-500" />
                  )}
                  {activity.status === "error" && (
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CLI Statistics */}
        <div>
          <h2 className="text-xl font-semibold text-slate-100 mb-4">
            CLI Statistics
          </h2>
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Total Commands</span>
              <span className="text-lg font-semibold text-slate-200">27</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Scripts Generated</span>
              <span className="text-lg font-semibold text-green-400">156</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Modules Built</span>
              <span className="text-lg font-semibold text-blue-400">23</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">
                Refactoring Operations
              </span>
              <span className="text-lg font-semibold text-yellow-400">89</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Deployments</span>
              <span className="text-lg font-semibold text-purple-400">34</span>
            </div>
          </div>
        </div>
      </div>

      {/* CLI Command Reference */}
      <div>
        <h2 className="text-xl font-semibold text-slate-100 mb-4">
          CLI Command Reference
        </h2>
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h3 className="font-medium text-slate-200 mb-2">Core Commands</h3>
              <div className="space-y-1 font-mono text-slate-400">
                <div>ign script generate</div>
                <div>ign template create</div>
                <div>ign module build</div>
                <div>ign refactor detect</div>
              </div>
            </div>
            <div>
              <h3 className="font-medium text-slate-200 mb-2">
                Advanced Commands
              </h3>
              <div className="space-y-1 font-mono text-slate-400">
                <div>ign deploy package</div>
                <div>ign advanced ai-assistant</div>
                <div>ign setup wizard</div>
                <div>ign --help</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
