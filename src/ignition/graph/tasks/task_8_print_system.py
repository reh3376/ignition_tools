"""Task 8: Print System Expansion.

Print operations and document management functions for Ignition SCADA systems.

This module provides comprehensive print operations including:
- Report Printing Operations
- Document Print Management
- Print Job Operations
- Print Queue Management
- Print Configuration & Settings

Total Functions: 18 functions
Contexts: Gateway, Vision Client, Perspective Session
Dependencies: Tag System (Task 1), Database System (Task 2), GUI System (Task 3)
"""

from typing import Any


def get_print_system_functions() -> list[dict[str, Any]]:
    """Get comprehensive print system functions for Task 8.

    Returns:
        List[Dict[str, Any]]: List of print function definitions
    """
    functions = []

    # ============================================================================
    # REPORT PRINTING OPERATIONS (6 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.report.executeAndDistribute",
                "description": "Execute a report and distribute to specified destinations including printers",
                "parameters": [
                    {
                        "name": "project",
                        "type": "str",
                        "description": "Name of the project containing the report",
                        "required": True,
                    },
                    {
                        "name": "path",
                        "type": "str",
                        "description": "Path to the report within the project",
                        "required": True,
                    },
                    {
                        "name": "parameters",
                        "type": "dict",
                        "description": "Parameters to pass to the report",
                        "required": False,
                        "default": {},
                    },
                    {
                        "name": "action",
                        "type": "str",
                        "description": "Distribution action (print, email, save, etc.)",
                        "required": True,
                    },
                    {
                        "name": "actionSettings",
                        "type": "dict",
                        "description": "Settings specific to the distribution action",
                        "required": False,
                        "default": {},
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "Execution ID for tracking the report execution",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Operations",
                "patterns": [
                    "report_automated_printing",
                    "report_scheduled_distribution",
                    "report_batch_processing",
                    "report_multi_destination",
                ],
            },
            {
                "name": "system.print.createPrintJob",
                "description": "Create a new print job for documents, reports, or custom content",
                "parameters": [
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the target printer",
                        "required": True,
                    },
                    {
                        "name": "document",
                        "type": "bytes",
                        "description": "Document content to print",
                        "required": True,
                    },
                    {
                        "name": "jobName",
                        "type": "str",
                        "description": "Name for the print job",
                        "required": False,
                        "default": "Ignition Print Job",
                    },
                    {
                        "name": "copies",
                        "type": "int",
                        "description": "Number of copies to print",
                        "required": False,
                        "default": 1,
                    },
                    {
                        "name": "pageRange",
                        "type": "str",
                        "description": "Page range to print (e.g., '1-5,10')",
                        "required": False,
                    },
                    {
                        "name": "orientation",
                        "type": "str",
                        "description": "Page orientation (portrait, landscape)",
                        "required": False,
                        "default": "portrait",
                    },
                    {
                        "name": "paperSize",
                        "type": "str",
                        "description": "Paper size (A4, Letter, Legal, etc.)",
                        "required": False,
                        "default": "A4",
                    },
                    {
                        "name": "quality",
                        "type": "str",
                        "description": "Print quality (draft, normal, high)",
                        "required": False,
                        "default": "normal",
                    },
                    {
                        "name": "colorMode",
                        "type": "str",
                        "description": "Color mode (color, grayscale, monochrome)",
                        "required": False,
                        "default": "color",
                    },
                    {
                        "name": "duplex",
                        "type": "bool",
                        "description": "Enable duplex (double-sided) printing",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "Print job ID for tracking and management",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Operations",
                "patterns": [
                    "document_printing",
                    "report_physical_output",
                    "custom_print_formatting",
                    "print_job_creation",
                ],
            },
            {
                "name": "system.print.printHTMLContent",
                "description": "Print HTML content directly with formatting and styling options",
                "parameters": [
                    {
                        "name": "htmlContent",
                        "type": "str",
                        "description": "HTML content to print",
                        "required": True,
                    },
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to use",
                        "required": False,
                    },
                    {
                        "name": "pageSetup",
                        "type": "dict",
                        "description": "Page setup configuration",
                        "required": False,
                        "default": {},
                    },
                    {
                        "name": "showPreview",
                        "type": "bool",
                        "description": "Show print preview dialog",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "margins",
                        "type": "dict",
                        "description": "Page margins (top, bottom, left, right)",
                        "required": False,
                    },
                    {
                        "name": "scale",
                        "type": "float",
                        "description": "Print scaling factor",
                        "required": False,
                        "default": 1.0,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if print operation was successful",
                },
                "scope": ["Vision Client", "Perspective Session"],
                "category": "Print Operations",
                "patterns": [
                    "html_document_printing",
                    "formatted_content_output",
                    "web_content_printing",
                    "styled_report_printing",
                ],
            },
            {
                "name": "system.print.printDataset",
                "description": "Print dataset content in tabular format with customizable styling",
                "parameters": [
                    {
                        "name": "dataset",
                        "type": "Dataset",
                        "description": "Dataset to print",
                        "required": True,
                    },
                    {
                        "name": "title",
                        "type": "str",
                        "description": "Title for the printed document",
                        "required": False,
                    },
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to use",
                        "required": False,
                    },
                    {
                        "name": "columnHeaders",
                        "type": "bool",
                        "description": "Include column headers in print output",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "rowNumbers",
                        "type": "bool",
                        "description": "Include row numbers in print output",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "pageBreaks",
                        "type": "bool",
                        "description": "Enable automatic page breaks",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "formatting",
                        "type": "dict",
                        "description": "Column formatting options",
                        "required": False,
                    },
                    {
                        "name": "fitToPage",
                        "type": "bool",
                        "description": "Automatically scale to fit page width",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if dataset was successfully printed",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Operations",
                "patterns": [
                    "dataset_printing",
                    "table_data_output",
                    "data_report_printing",
                    "tabular_formatting",
                ],
            },
            {
                "name": "system.print.printComponent",
                "description": "Print visual components like charts, gauges, or custom displays",
                "parameters": [
                    {
                        "name": "component",
                        "type": "Component",
                        "description": "Component to print",
                        "required": True,
                    },
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to use",
                        "required": False,
                    },
                    {
                        "name": "includeBackground",
                        "type": "bool",
                        "description": "Include component background in print",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "resolution",
                        "type": "int",
                        "description": "Print resolution in DPI",
                        "required": False,
                        "default": 300,
                    },
                    {
                        "name": "scale",
                        "type": "float",
                        "description": "Scaling factor for the component",
                        "required": False,
                        "default": 1.0,
                    },
                    {
                        "name": "crop",
                        "type": "dict",
                        "description": "Crop settings for the component",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if component was successfully printed",
                },
                "scope": ["Vision Client", "Perspective Session"],
                "category": "Print Operations",
                "patterns": [
                    "component_printing",
                    "visual_element_output",
                    "chart_printing",
                    "display_capture_printing",
                ],
            },
            {
                "name": "system.print.generatePDF",
                "description": "Generate PDF documents from various content sources for printing or distribution",
                "parameters": [
                    {
                        "name": "content",
                        "type": "Any",
                        "description": "Content to convert to PDF (HTML, Dataset, Component, etc.)",
                        "required": True,
                    },
                    {
                        "name": "outputPath",
                        "type": "str",
                        "description": "Output file path for the PDF",
                        "required": True,
                    },
                    {
                        "name": "pageSettings",
                        "type": "dict",
                        "description": "PDF page configuration",
                        "required": False,
                        "default": {},
                    },
                    {
                        "name": "metadata",
                        "type": "dict",
                        "description": "PDF metadata (title, author, subject, etc.)",
                        "required": False,
                    },
                    {
                        "name": "watermark",
                        "type": "str",
                        "description": "Watermark text for the PDF",
                        "required": False,
                    },
                    {
                        "name": "security",
                        "type": "dict",
                        "description": "PDF security settings (password, permissions)",
                        "required": False,
                    },
                    {
                        "name": "compression",
                        "type": "bool",
                        "description": "Enable PDF compression",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "Path to the generated PDF file",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Operations",
                "patterns": [
                    "pdf_generation",
                    "document_creation",
                    "report_pdf_output",
                    "archive_document_creation",
                ],
            },
        ]
    )

    # ============================================================================
    # PRINT JOB MANAGEMENT (6 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.print.getJobStatus",
                "description": "Retrieve the current status of a print job",
                "parameters": [
                    {
                        "name": "jobId",
                        "type": "str",
                        "description": "Print job ID to check",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Print job status information including state, progress, and errors",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Management",
                "patterns": [
                    "print_job_monitoring",
                    "print_status_tracking",
                    "print_progress_monitoring",
                    "print_error_detection",
                ],
            },
            {
                "name": "system.print.cancelJob",
                "description": "Cancel a pending or active print job",
                "parameters": [
                    {
                        "name": "jobId",
                        "type": "str",
                        "description": "Print job ID to cancel",
                        "required": True,
                    },
                    {
                        "name": "reason",
                        "type": "str",
                        "description": "Reason for canceling the job",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if job was successfully canceled",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Management",
                "patterns": [
                    "print_job_cancellation",
                    "print_job_control",
                    "print_queue_management",
                    "print_error_recovery",
                ],
            },
            {
                "name": "system.print.pauseJob",
                "description": "Pause a print job temporarily",
                "parameters": [
                    {
                        "name": "jobId",
                        "type": "str",
                        "description": "Print job ID to pause",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if job was successfully paused",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Management",
                "patterns": [
                    "print_job_control",
                    "print_queue_management",
                    "print_workflow_control",
                ],
            },
            {
                "name": "system.print.resumeJob",
                "description": "Resume a paused print job",
                "parameters": [
                    {
                        "name": "jobId",
                        "type": "str",
                        "description": "Print job ID to resume",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if job was successfully resumed",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Management",
                "patterns": [
                    "print_job_control",
                    "print_queue_management",
                    "print_workflow_resumption",
                ],
            },
            {
                "name": "system.print.getJobHistory",
                "description": "Retrieve print job history with filtering and search capabilities",
                "parameters": [
                    {
                        "name": "startDate",
                        "type": "datetime",
                        "description": "Start date for history query",
                        "required": False,
                    },
                    {
                        "name": "endDate",
                        "type": "datetime",
                        "description": "End date for history query",
                        "required": False,
                    },
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Filter by printer name",
                        "required": False,
                    },
                    {
                        "name": "status",
                        "type": "list",
                        "description": "Filter by job status (completed, failed, canceled)",
                        "required": False,
                    },
                    {
                        "name": "user",
                        "type": "str",
                        "description": "Filter by user who submitted the job",
                        "required": False,
                    },
                    {
                        "name": "limit",
                        "type": "int",
                        "description": "Maximum number of records to return",
                        "required": False,
                        "default": 100,
                    },
                ],
                "returns": {
                    "type": "Dataset",
                    "description": "Print job history records",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Management",
                "patterns": [
                    "print_history_analysis",
                    "print_audit_trail",
                    "print_usage_tracking",
                    "print_performance_analysis",
                ],
            },
            {
                "name": "system.print.retryJob",
                "description": "Retry a failed print job with optional parameter modifications",
                "parameters": [
                    {
                        "name": "jobId",
                        "type": "str",
                        "description": "Print job ID to retry",
                        "required": True,
                    },
                    {
                        "name": "modifiedSettings",
                        "type": "dict",
                        "description": "Modified print settings for the retry",
                        "required": False,
                    },
                    {
                        "name": "newPrinter",
                        "type": "str",
                        "description": "Alternative printer for the retry",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "New job ID for the retry attempt",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Management",
                "patterns": [
                    "print_error_recovery",
                    "print_job_retry",
                    "print_reliability_enhancement",
                    "print_failure_handling",
                ],
            },
        ]
    )

    # ============================================================================
    # PRINT CONFIGURATION & SYSTEM (6 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.print.getPrinters",
                "description": "Retrieve list of available printers with their capabilities and status",
                "parameters": [
                    {
                        "name": "includeOffline",
                        "type": "bool",
                        "description": "Include offline printers in the list",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "filterType",
                        "type": "str",
                        "description": "Filter printers by type (local, network, pdf, etc.)",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "List of available printers with their properties",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Configuration",
                "patterns": [
                    "printer_discovery",
                    "print_system_inspection",
                    "printer_availability_check",
                    "print_setup_validation",
                ],
            },
            {
                "name": "system.print.getPrinterCapabilities",
                "description": "Get detailed capabilities and settings for a specific printer",
                "parameters": [
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to query",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Printer capabilities including paper sizes, resolutions, and features",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Configuration",
                "patterns": [
                    "printer_capability_query",
                    "print_setup_optimization",
                    "printer_feature_detection",
                    "print_compatibility_check",
                ],
            },
            {
                "name": "system.print.setDefaultPrinter",
                "description": "Set the default printer for the system or current session",
                "parameters": [
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to set as default",
                        "required": True,
                    },
                    {
                        "name": "scope",
                        "type": "str",
                        "description": "Scope of the setting (system, session, user)",
                        "required": False,
                        "default": "session",
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if default printer was successfully set",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Configuration",
                "patterns": [
                    "printer_configuration",
                    "print_setup_management",
                    "printer_preference_setting",
                    "print_system_configuration",
                ],
            },
            {
                "name": "system.print.getPrintQueue",
                "description": "Retrieve current print queue status with job details",
                "parameters": [
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to query (all printers if not specified)",
                        "required": False,
                    },
                    {
                        "name": "includeCompleted",
                        "type": "bool",
                        "description": "Include recently completed jobs",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "Dataset",
                    "description": "Current print queue with job details and status",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "Print Configuration",
                "patterns": [
                    "print_queue_monitoring",
                    "print_status_overview",
                    "print_job_tracking",
                    "print_system_monitoring",
                ],
            },
            {
                "name": "system.print.clearPrintQueue",
                "description": "Clear pending jobs from the print queue",
                "parameters": [
                    {
                        "name": "printerName",
                        "type": "str",
                        "description": "Name of the printer to clear (all printers if not specified)",
                        "required": False,
                    },
                    {
                        "name": "jobStatus",
                        "type": "list",
                        "description": "Only clear jobs with specific status (pending, paused, error)",
                        "required": False,
                    },
                    {
                        "name": "confirm",
                        "type": "bool",
                        "description": "Confirmation flag to prevent accidental clearing",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "int",
                    "description": "Number of jobs cleared from the queue",
                },
                "scope": ["Gateway"],
                "category": "Print Configuration",
                "patterns": [
                    "print_queue_management",
                    "print_system_maintenance",
                    "print_error_recovery",
                    "print_queue_cleanup",
                ],
            },
            {
                "name": "system.print.configurePrintSettings",
                "description": "Configure global print settings and preferences",
                "parameters": [
                    {
                        "name": "settings",
                        "type": "dict",
                        "description": "Print settings to configure",
                        "required": True,
                    },
                    {
                        "name": "scope",
                        "type": "str",
                        "description": "Scope of the settings (global, user, session)",
                        "required": False,
                        "default": "global",
                    },
                    {
                        "name": "persistent",
                        "type": "bool",
                        "description": "Whether settings should persist across sessions",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "bool",
                    "description": "True if settings were successfully configured",
                },
                "scope": ["Gateway"],
                "category": "Print Configuration",
                "patterns": [
                    "print_system_configuration",
                    "print_preference_management",
                    "print_setup_automation",
                    "print_standardization",
                ],
            },
        ]
    )

    return functions


def get_task_8_metadata() -> dict[str, Any]:
    """Get metadata about Task 8: Print System Expansion.

    Returns:
        Dict containing task metadata
    """
    return {
        "task_number": 8,
        "task_name": "Print System Expansion",
        "description": "Print operations and document management functions",
        "total_functions": 18,
        "categories": [
            "Report Printing Operations",
            "Print Job Management",
            "Print Configuration & System",
        ],
        "contexts": ["Gateway", "Vision Client", "Perspective Session"],
        "dependencies": [
            "Task 1: Tag System",
            "Task 2: Database System",
            "Task 3: GUI System",
        ],
        "priority": "LOW",
        "estimated_completion": "Week 9",
    }


if __name__ == "__main__":
    """Test the function definitions."""
    functions = get_print_system_functions()
    metadata = get_task_8_metadata()

    print(f"Task 8: {metadata['task_name']}")
    print(f"Total Functions: {len(functions)}")
    print(f"Expected: {metadata['total_functions']}")

    print("✅ Task 8 structure created!")
