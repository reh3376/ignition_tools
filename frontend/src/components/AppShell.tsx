import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Bars3Icon,
  XMarkIcon,
  CommandLineIcon,
  DocumentTextIcon,
  CubeIcon,
  WrenchScrewdriverIcon,
  CloudArrowUpIcon,
  SparklesIcon,
  CogIcon,
  HomeIcon,
} from "@heroicons/react/24/outline";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description: string;
  cliCommand: string;
}

const navigation: NavItem[] = [
  {
    name: "Dashboard",
    href: "/",
    icon: HomeIcon,
    description: "Overview and system status",
    cliCommand: "ign --help",
  },
  {
    name: "Script Generator",
    href: "/script",
    icon: DocumentTextIcon,
    description: "Jython script generation",
    cliCommand: "ign script",
  },
  {
    name: "Template Manager",
    href: "/template",
    icon: CommandLineIcon,
    description: "Template management",
    cliCommand: "ign template",
  },
  {
    name: "Module Development",
    href: "/module",
    icon: CubeIcon,
    description: "Ignition module development",
    cliCommand: "ign module",
  },
  {
    name: "Refactor Tools",
    href: "/refactor",
    icon: WrenchScrewdriverIcon,
    description: "Automated code refactoring",
    cliCommand: "ign refactor",
  },
  {
    name: "Deployment",
    href: "/deploy",
    icon: CloudArrowUpIcon,
    description: "Module deployment & distribution",
    cliCommand: "ign deploy",
  },
  {
    name: "Advanced Features",
    href: "/advanced",
    icon: SparklesIcon,
    description: "Phase 9.8 advanced features",
    cliCommand: "ign advanced",
  },
  {
    name: "Setup",
    href: "/setup",
    icon: CogIcon,
    description: "Interactive setup wizard",
    cliCommand: "ign setup",
  },
];

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const isActive = (href: string) => {
    if (href === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Mobile sidebar */}
      <div
        className={`fixed inset-0 z-50 lg:hidden ${
          sidebarOpen ? "block" : "hidden"
        }`}
      >
        <div
          className="fixed inset-0 bg-slate-900/80"
          onClick={() => setSidebarOpen(false)}
        />
        <div className="fixed inset-y-0 left-0 w-64 bg-slate-800 border-r border-slate-700">
          <SidebarContent
            navigation={navigation}
            isActive={isActive}
            onClose={() => setSidebarOpen(false)}
          />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:block lg:w-64 lg:flex-shrink-0">
        <div className="flex flex-col h-full bg-slate-800 border-r border-slate-700">
          <SidebarContent navigation={navigation} isActive={isActive} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-slate-800 border-b border-slate-700 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center">
            <button
              type="button"
              className="lg:hidden p-2 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-700"
              onClick={() => setSidebarOpen(true)}
            >
              <Bars3Icon className="h-6 w-6" />
            </button>
            <h1 className="ml-3 text-xl font-semibold text-slate-100">
              IGN Scripts
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 text-sm text-slate-400">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>CLI Ready</span>
              </div>
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Backend Connected</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto bg-slate-900">{children}</main>
      </div>
    </div>
  );
}

interface SidebarContentProps {
  navigation: NavItem[];
  isActive: (href: string) => boolean;
  onClose?: () => void;
}

function SidebarContent({
  navigation,
  isActive,
  onClose,
}: SidebarContentProps) {
  return (
    <>
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-slate-700">
        <div className="flex items-center space-x-2">
          <CommandLineIcon className="h-8 w-8 text-blue-400" />
          <span className="text-lg font-bold text-slate-100">IGN Scripts</span>
        </div>
        {onClose && (
          <button
            type="button"
            className="lg:hidden p-1 rounded-md text-slate-400 hover:text-slate-200"
            onClick={onClose}
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.name}
              to={item.href}
              onClick={onClose}
              className={`
                group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors
                ${
                  active
                    ? "bg-slate-700 text-blue-400 border-l-4 border-blue-400"
                    : "text-slate-300 hover:text-slate-100 hover:bg-slate-700"
                }
              `}
            >
              <Icon
                className={`
                  mr-3 h-5 w-5 flex-shrink-0
                  ${active ? "text-blue-400" : "text-slate-400 group-hover:text-slate-300"}
                `}
              />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className="text-xs text-slate-500 group-hover:text-slate-400">
                  {item.cliCommand}
                </div>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-slate-700">
        <div className="text-xs text-slate-500">
          <div>IGN Scripts v0.2.2</div>
          <div>CLI-to-UI Frontend</div>
        </div>
      </div>
    </>
  );
}
