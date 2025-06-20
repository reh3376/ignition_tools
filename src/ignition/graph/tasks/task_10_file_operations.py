"""Task 10 - File Operations Module
Extracted from task_10_file_report_system.py for improved maintainability
Contains 8 file system operation functions.
"""

from typing import Any


def get_file_operations_functions() -> list[dict[str, Any]]:
    """Returns file system operation functions for Ignition system integration.

    This module provides comprehensive file system operations including:
    - File content reading and writing with encoding support
    - Directory listing and monitoring
    - File movement, deletion, and compression operations
    - Archive extraction and validation

    Returns:
        list[dict[str, Any]]: List of 8 file operation function definitions
    """
    functions = []

    # ============================================================================
    # FILE SYSTEM OPERATIONS (8 functions)
    # ============================================================================

    functions.extend(
        [
            {
                "name": "system.file.readFileContent",
                "description": "Read file content with encoding support and error handling",
                "parameters": [
                    {
                        "name": "filePath",
                        "type": "str",
                        "description": "Path to the file to read",
                        "required": True,
                    },
                    {
                        "name": "encoding",
                        "type": "str",
                        "description": "File encoding (utf-8, ascii, latin-1)",
                        "required": False,
                        "default": "utf-8",
                    },
                    {
                        "name": "maxSize",
                        "type": "int",
                        "description": "Maximum file size in bytes to read",
                        "required": False,
                        "default": 10485760,
                    },
                    {
                        "name": "stripWhitespace",
                        "type": "bool",
                        "description": "Strip leading/trailing whitespace",
                        "required": False,
                        "default": False,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "File content as string with metadata",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "file_content_reading",
                    "configuration_file_processing",
                    "log_file_analysis",
                    "data_file_import",
                ],
            },
            {
                "name": "system.file.writeFileContent",
                "description": "Write content to file with backup and atomic operations",
                "parameters": [
                    {
                        "name": "filePath",
                        "type": "str",
                        "description": "Path to the file to write",
                        "required": True,
                    },
                    {
                        "name": "content",
                        "type": "str",
                        "description": "Content to write to file",
                        "required": True,
                    },
                    {
                        "name": "encoding",
                        "type": "str",
                        "description": "File encoding for writing",
                        "required": False,
                        "default": "utf-8",
                    },
                    {
                        "name": "createBackup",
                        "type": "bool",
                        "description": "Create backup before overwriting",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "atomicWrite",
                        "type": "bool",
                        "description": "Use atomic write operation",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "createDirectories",
                        "type": "bool",
                        "description": "Create parent directories if needed",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Write result with backup info and file metadata",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "file_content_writing",
                    "configuration_file_updates",
                    "data_export_operations",
                    "atomic_file_operations",
                ],
            },
            {
                "name": "system.file.listDirectoryContents",
                "description": "list directory contents with filtering and metadata",
                "parameters": [
                    {
                        "name": "directoryPath",
                        "type": "str",
                        "description": "Path to directory to list",
                        "required": True,
                    },
                    {
                        "name": "recursive",
                        "type": "bool",
                        "description": "Recursively list subdirectories",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "filePattern",
                        "type": "str",
                        "description": "File pattern filter (glob style)",
                        "required": False,
                    },
                    {
                        "name": "includeHidden",
                        "type": "bool",
                        "description": "Include hidden files",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "includeMetadata",
                        "type": "bool",
                        "description": "Include file metadata (size, dates)",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "list",
                    "description": "list of files with metadata and directory structure",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "directory_listing",
                    "file_discovery",
                    "file_system_browsing",
                    "batch_file_processing",
                ],
            },
            {
                "name": "system.file.moveFile",
                "description": "Move or rename files with conflict resolution",
                "parameters": [
                    {
                        "name": "sourcePath",
                        "type": "str",
                        "description": "Source file path",
                        "required": True,
                    },
                    {
                        "name": "destinationPath",
                        "type": "str",
                        "description": "Destination file path",
                        "required": True,
                    },
                    {
                        "name": "overwriteExisting",
                        "type": "bool",
                        "description": "Overwrite if destination exists",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "createBackup",
                        "type": "bool",
                        "description": "Create backup of overwritten file",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "preserveAttributes",
                        "type": "bool",
                        "description": "Preserve file attributes and timestamps",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Move operation result with backup information",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "file_relocation",
                    "file_organization",
                    "backup_management",
                    "file_archival",
                ],
            },
            {
                "name": "system.file.deleteFile",
                "description": "Delete files with recovery options and audit logging",
                "parameters": [
                    {
                        "name": "filePath",
                        "type": "str",
                        "description": "Path to file to delete",
                        "required": True,
                    },
                    {
                        "name": "moveToTrash",
                        "type": "bool",
                        "description": "Move to trash instead of permanent delete",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "confirmDelete",
                        "type": "bool",
                        "description": "Require confirmation for deletion",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "auditLog",
                        "type": "bool",
                        "description": "Log deletion operation for audit",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Deletion result with recovery information",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "file_deletion",
                    "cleanup_operations",
                    "audit_logging",
                    "data_management",
                ],
            },
            {
                "name": "system.file.watchDirectory",
                "description": "Monitor directory for file system changes with event handling",
                "parameters": [
                    {
                        "name": "directoryPath",
                        "type": "str",
                        "description": "Directory path to monitor",
                        "required": True,
                    },
                    {
                        "name": "watchSubdirectories",
                        "type": "bool",
                        "description": "Monitor subdirectories recursively",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "eventTypes",
                        "type": "list",
                        "description": "Event types to monitor (created, modified, deleted)",
                        "required": False,
                        "default": "['created', 'modified', 'deleted']",
                    },
                    {
                        "name": "filePattern",
                        "type": "str",
                        "description": "File pattern filter for events",
                        "required": False,
                    },
                    {
                        "name": "callbackFunction",
                        "type": "str",
                        "description": "Callback function name for events",
                        "required": True,
                    },
                ],
                "returns": {
                    "type": "str",
                    "description": "Watch handle ID for stopping the monitor",
                },
                "scope": ["Gateway"],
                "category": "File Operations",
                "patterns": [
                    "file_system_monitoring",
                    "real_time_file_tracking",
                    "automated_file_processing",
                    "event_driven_operations",
                ],
            },
            {
                "name": "system.file.compressFiles",
                "description": "Compress files and directories with various formats",
                "parameters": [
                    {
                        "name": "sourceItems",
                        "type": "list",
                        "description": "list of files/directories to compress",
                        "required": True,
                    },
                    {
                        "name": "archivePath",
                        "type": "str",
                        "description": "Path for the archive file",
                        "required": True,
                    },
                    {
                        "name": "compressionFormat",
                        "type": "str",
                        "description": "Compression format (zip, tar, gzip)",
                        "required": False,
                        "default": "zip",
                    },
                    {
                        "name": "compressionLevel",
                        "type": "int",
                        "description": "Compression level (0-9)",
                        "required": False,
                        "default": 6,
                    },
                    {
                        "name": "includeMetadata",
                        "type": "bool",
                        "description": "Include file metadata in archive",
                        "required": False,
                        "default": True,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Compression result with archive info and statistics",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "file_compression",
                    "data_archival",
                    "backup_creation",
                    "storage_optimization",
                ],
            },
            {
                "name": "system.file.extractArchive",
                "description": "Extract compressed archives with validation and filtering",
                "parameters": [
                    {
                        "name": "archivePath",
                        "type": "str",
                        "description": "Path to archive file",
                        "required": True,
                    },
                    {
                        "name": "extractPath",
                        "type": "str",
                        "description": "Destination path for extraction",
                        "required": True,
                    },
                    {
                        "name": "overwriteExisting",
                        "type": "bool",
                        "description": "Overwrite existing files",
                        "required": False,
                        "default": False,
                    },
                    {
                        "name": "validateArchive",
                        "type": "bool",
                        "description": "Validate archive integrity before extraction",
                        "required": False,
                        "default": True,
                    },
                    {
                        "name": "filePattern",
                        "type": "str",
                        "description": "Pattern filter for files to extract",
                        "required": False,
                    },
                ],
                "returns": {
                    "type": "dict",
                    "description": "Extraction result with extracted files list",
                },
                "scope": ["Gateway", "Vision Client", "Perspective Session"],
                "category": "File Operations",
                "patterns": [
                    "archive_extraction",
                    "data_restoration",
                    "file_deployment",
                    "backup_recovery",
                ],
            },
        ]
    )

    return functions
