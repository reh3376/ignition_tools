import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  DocumentTextIcon,
  CommandLineIcon,
  CodeBracketIcon,
  ArrowDownTrayIcon,
  PlayIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

// Types for script generation
interface ScriptTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  cliCommand: string;
  parameters: TemplateParameter[];
  preview?: string;
  tags?: string[];
  usageCount?: number;
}

interface TemplateParameter {
  name: string;
  type: "string" | "number" | "boolean" | "select" | "multiselect";
  required: boolean;
  description: string;
  defaultValue?: any;
  options?: string[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

interface GeneratedScript {
  content: string;
  filename: string;
  metadata: {
    template: string;
    parameters: Record<string, any>;
    generatedAt: string;
  };
}

// Mock data for demonstration
const mockTemplates: ScriptTemplate[] = [
  {
    id: "opcua-client",
    name: "OPC-UA Client",
    description:
      "Generate OPC-UA client connection script with tag reading capabilities",
    category: "connectivity",
    cliCommand: "ign script generate --type opc-ua-client",
    usageCount: 245,
    tags: ["popular", "connectivity"],
    parameters: [
      {
        name: "serverUrl",
        type: "string",
        required: true,
        description: "OPC-UA server endpoint URL",
        defaultValue: "opc.tcp://localhost:4840",
        validation: { pattern: "^opc\\.tcp://.+" },
      },
      {
        name: "securityPolicy",
        type: "select",
        required: true,
        description: "Security policy for connection",
        defaultValue: "None",
        options: ["None", "Basic128Rsa15", "Basic256", "Basic256Sha256"],
      },
      {
        name: "username",
        type: "string",
        required: false,
        description: "Username for authentication (optional)",
      },
      {
        name: "subscriptionRate",
        type: "number",
        required: false,
        description: "Subscription update rate in milliseconds",
        defaultValue: 1000,
        validation: { min: 100, max: 60000 },
      },
      {
        name: "enableLogging",
        type: "boolean",
        required: false,
        description: "Enable detailed connection logging",
        defaultValue: true,
      },
    ],
  },
  {
    id: "tag-historian",
    name: "Tag Historian",
    description:
      "Generate scripts for historical tag data retrieval and analysis",
    category: "data",
    cliCommand: "ign script generate --type tag-historian",
    usageCount: 189,
    tags: ["data", "analytics"],
    parameters: [
      {
        name: "tagPaths",
        type: "multiselect",
        required: true,
        description: "Tag paths to include in historical query",
        options: [
          "[default]Pump1/Speed",
          "[default]Tank1/Level",
          "[default]Motor1/Current",
        ],
      },
      {
        name: "timeRange",
        type: "select",
        required: true,
        description: "Historical data time range",
        defaultValue: "24h",
        options: ["1h", "24h", "7d", "30d", "custom"],
      },
      {
        name: "aggregation",
        type: "select",
        required: false,
        description: "Data aggregation method",
        defaultValue: "Average",
        options: ["Average", "Maximum", "Minimum", "Sum", "Count"],
      },
      {
        name: "exportFormat",
        type: "select",
        required: false,
        description: "Export format for historical data",
        defaultValue: "CSV",
        options: ["CSV", "JSON", "Excel"],
      },
    ],
  },
  {
    id: "alarm-handler",
    name: "Alarm Handler",
    description: "Generate alarm notification and escalation scripts",
    category: "alarms",
    cliCommand: "ign script generate --type alarm-handler",
    usageCount: 156,
    tags: ["alarms", "notifications"],
    parameters: [
      {
        name: "alarmSources",
        type: "multiselect",
        required: true,
        description: "Alarm sources to monitor",
        options: [
          "Process Alarms",
          "Equipment Alarms",
          "Safety Alarms",
          "System Alarms",
        ],
      },
      {
        name: "priority",
        type: "select",
        required: true,
        description: "Minimum alarm priority to handle",
        defaultValue: "Medium",
        options: ["Low", "Medium", "High", "Critical"],
      },
      {
        name: "notificationMethod",
        type: "select",
        required: true,
        description: "Primary notification method",
        defaultValue: "Email",
        options: ["Email", "SMS", "Database Log", "Custom Script"],
      },
      {
        name: "escalationDelay",
        type: "number",
        required: false,
        description: "Escalation delay in minutes",
        defaultValue: 15,
        validation: { min: 1, max: 1440 },
      },
    ],
  },
];

// Form validation schema
const createParameterSchema = (parameters: TemplateParameter[]) => {
  const schema: Record<string, any> = {};

  parameters.forEach((param) => {
    let fieldSchema: any;

    switch (param.type) {
      case "string":
        fieldSchema = z.string();
        if (param.validation?.pattern) {
          fieldSchema = fieldSchema.regex(new RegExp(param.validation.pattern));
        }
        break;
      case "number":
        fieldSchema = z.number();
        if (param.validation?.min !== undefined) {
          fieldSchema = fieldSchema.min(param.validation.min);
        }
        if (param.validation?.max !== undefined) {
          fieldSchema = fieldSchema.max(param.validation.max);
        }
        break;
      case "boolean":
        fieldSchema = z.boolean();
        break;
      case "select":
      case "multiselect":
        fieldSchema =
          param.type === "multiselect" ? z.array(z.string()) : z.string();
        break;
      default:
        fieldSchema = z.string();
    }

    if (!param.required) {
      fieldSchema = fieldSchema.optional();
    }

    schema[param.name] = fieldSchema;
  });

  return z.object(schema);
};

export function ScriptGeneratorPage() {
  const [selectedTemplate, setSelectedTemplate] =
    useState<ScriptTemplate | null>(null);
  const [generatedScript, setGeneratedScript] =
    useState<GeneratedScript | null>(null);
  const [previewMode, setPreviewMode] = useState<"form" | "preview" | "code">(
    "form",
  );
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  // React Hook Form setup
  const formSchema = selectedTemplate
    ? createParameterSchema(selectedTemplate.parameters)
    : z.object({});
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues:
      selectedTemplate?.parameters.reduce(
        (acc, param) => {
          acc[param.name] = param.defaultValue;
          return acc;
        },
        {} as Record<string, any>,
      ) || {},
  });

  // Filter templates based on search and category
  const filteredTemplates = mockTemplates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      selectedCategory === "all" || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(mockTemplates.map((t) => t.category)));

  // Generate script (mock API call)
  const generateScript = async (
    templateId: string,
    parameters: Record<string, any>,
  ) => {
    // Simulate API call delay
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const template = mockTemplates.find((t) => t.id === templateId);
    if (!template) throw new Error("Template not found");

    // Mock generated script content
    const mockScript = `# Generated ${template.name} Script
# Generated on: ${new Date().toISOString()}
# Template: ${template.name}
# CLI Command: ${template.cliCommand}

def main():
    """
    ${template.description}
    """
    # Parameters used:
${Object.entries(parameters)
  .map(([key, value]) => `    # ${key}: ${JSON.stringify(value)}`)
  .join("\n")}

    # Implementation would go here
    logger = system.util.getLogger("${template.name.replace(/\s+/g, "")}")
    logger.info("Starting ${template.name} execution")

    try:
        # Your generated code here
        pass
    except Exception as e:
        logger.error("Error in ${template.name}: " + str(e))
        raise

if __name__ == "__main__":
    main()`;

    return {
      content: mockScript,
      filename: `${template.id.replace(/-/g, "_")}_script.py`,
      metadata: {
        template: template.name,
        parameters,
        generatedAt: new Date().toISOString(),
      },
    };
  };

  const handleGenerateScript = async (data: Record<string, any>) => {
    if (!selectedTemplate) return;

    try {
      const result = await generateScript(selectedTemplate.id, data);
      setGeneratedScript(result);
      setPreviewMode("code");
    } catch (error) {
      console.error("Failed to generate script:", error);
    }
  };

  const downloadScript = () => {
    if (!generatedScript) return;

    const blob = new Blob([generatedScript.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = generatedScript.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="border-b border-slate-700 pb-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <DocumentTextIcon className="h-8 w-8 text-green-400" />
              <div>
                <h1 className="text-3xl font-bold text-slate-100">
                  Script Generator
                </h1>
                <p className="mt-2 text-slate-400">
                  Generate Jython scripts for Ignition Gateway with AI-powered
                  assistance
                </p>
              </div>
            </div>

            {selectedTemplate && (
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setPreviewMode("form")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    previewMode === "form"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  Configure
                </button>
                <button
                  onClick={() => setPreviewMode("preview")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    previewMode === "preview"
                      ? "bg-blue-600 text-white"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  <EyeIcon className="h-4 w-4 inline mr-2" />
                  Preview
                </button>
                {generatedScript && (
                  <button
                    onClick={() => setPreviewMode("code")}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      previewMode === "code"
                        ? "bg-blue-600 text-white"
                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    <CodeBracketIcon className="h-4 w-4 inline mr-2" />
                    Generated Code
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Template Selection */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-slate-100 mb-4">
                Select Template
              </h2>

              {/* Search and Filter */}
              <div className="space-y-4 mb-6">
                <input
                  type="text"
                  placeholder="Search templates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />

                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              {/* Template List */}
              <div className="space-y-3">
                {filteredTemplates.map((template) => (
                  <div
                    key={template.id}
                    onClick={() => setSelectedTemplate(template)}
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                      selectedTemplate?.id === template.id
                        ? "border-blue-500 bg-blue-500/10"
                        : "border-slate-600 hover:border-slate-500 hover:bg-slate-700/50"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-slate-100">
                          {template.name}
                        </h3>
                        <p className="text-sm text-slate-400 mt-1">
                          {template.description}
                        </p>
                        <div className="flex items-center space-x-2 mt-2">
                          <span className="text-xs px-2 py-1 bg-slate-700 text-slate-300 rounded">
                            {template.category}
                          </span>
                          {template.tags?.includes("popular") && (
                            <span className="text-xs px-2 py-1 bg-green-600 text-white rounded">
                              Popular
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-slate-400">
                          {template.usageCount} uses
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {!selectedTemplate ? (
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-8 text-center">
                <DocumentTextIcon className="h-24 w-24 text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-300 mb-2">
                  Select a Template to Get Started
                </h3>
                <p className="text-slate-500">
                  Choose from our library of pre-built script templates or
                  create your own.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* CLI Command Reference */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-3">
                    <CommandLineIcon className="h-5 w-5 text-blue-400" />
                    <h3 className="text-lg font-semibold text-slate-200">
                      CLI Command
                    </h3>
                  </div>
                  <code className="text-sm text-green-400 font-mono bg-slate-900 px-3 py-2 rounded">
                    {selectedTemplate.cliCommand}
                  </code>
                </div>

                {/* Parameter Form */}
                {previewMode === "form" && (
                  <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-200 mb-4">
                      Configure Parameters
                    </h3>

                    <form
                      onSubmit={form.handleSubmit(handleGenerateScript)}
                      className="space-y-4"
                    >
                      {selectedTemplate.parameters.map((param) => (
                        <div key={param.name}>
                          <label className="block text-sm font-medium text-slate-300 mb-2">
                            {param.name}
                            {param.required && (
                              <span className="text-red-400 ml-1">*</span>
                            )}
                          </label>
                          <p className="text-xs text-slate-400 mb-2">
                            {param.description}
                          </p>

                          {param.type === "string" && (
                            <input
                              {...form.register(param.name)}
                              type="text"
                              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          )}

                          {param.type === "number" && (
                            <input
                              {...form.register(param.name, {
                                valueAsNumber: true,
                              })}
                              type="number"
                              min={param.validation?.min}
                              max={param.validation?.max}
                              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                          )}

                          {param.type === "boolean" && (
                            <label className="flex items-center space-x-2">
                              <input
                                {...form.register(param.name)}
                                type="checkbox"
                                className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
                              />
                              <span className="text-slate-300">Enable</span>
                            </label>
                          )}

                          {param.type === "select" && (
                            <select
                              {...form.register(param.name)}
                              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              {param.options?.map((option) => (
                                <option key={option} value={option}>
                                  {option}
                                </option>
                              ))}
                            </select>
                          )}

                          {param.type === "multiselect" && (
                            <select
                              {...form.register(param.name)}
                              multiple
                              className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                            >
                              {param.options?.map((option) => (
                                <option key={option} value={option}>
                                  {option}
                                </option>
                              ))}
                            </select>
                          )}

                          {form.formState.errors[param.name] && (
                            <p className="text-red-400 text-sm mt-1">
                              {form.formState.errors[param.name]?.message}
                            </p>
                          )}
                        </div>
                      ))}

                      <div className="flex space-x-4 pt-4">
                        <button
                          type="submit"
                          disabled={form.formState.isSubmitting}
                          className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                        >
                          <PlayIcon className="h-4 w-4" />
                          <span>
                            {form.formState.isSubmitting
                              ? "Generating..."
                              : "Generate Script"}
                          </span>
                        </button>

                        {generatedScript && (
                          <button
                            type="button"
                            onClick={downloadScript}
                            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                          >
                            <ArrowDownTrayIcon className="h-4 w-4" />
                            <span>Download Script</span>
                          </button>
                        )}
                      </div>
                    </form>
                  </div>
                )}

                {/* Preview Mode */}
                {previewMode === "preview" && (
                  <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-slate-200 mb-4">
                      Template Preview
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-slate-300 mb-2">
                          Description
                        </h4>
                        <p className="text-slate-400">
                          {selectedTemplate.description}
                        </p>
                      </div>
                      <div>
                        <h4 className="font-medium text-slate-300 mb-2">
                          Parameters ({selectedTemplate.parameters.length})
                        </h4>
                        <div className="space-y-2">
                          {selectedTemplate.parameters.map((param) => (
                            <div
                              key={param.name}
                              className="flex items-center justify-between p-3 bg-slate-700 rounded"
                            >
                              <div>
                                <span className="font-medium text-slate-200">
                                  {param.name}
                                </span>
                                {param.required && (
                                  <span className="text-red-400 ml-1">*</span>
                                )}
                                <p className="text-sm text-slate-400">
                                  {param.description}
                                </p>
                              </div>
                              <span className="text-xs px-2 py-1 bg-slate-600 text-slate-300 rounded">
                                {param.type}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Generated Code */}
                {previewMode === "code" && generatedScript && (
                  <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-slate-200">
                        Generated Script: {generatedScript.filename}
                      </h3>
                      <button
                        onClick={downloadScript}
                        className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                      >
                        <ArrowDownTrayIcon className="h-4 w-4" />
                        <span>Download</span>
                      </button>
                    </div>

                    <div className="bg-slate-900 rounded-lg p-4 overflow-x-auto">
                      <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap">
                        {generatedScript.content}
                      </pre>
                    </div>

                    <div className="mt-4 text-xs text-slate-400">
                      Generated on:{" "}
                      {new Date(
                        generatedScript.metadata.generatedAt,
                      ).toLocaleString()}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
