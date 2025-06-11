"""Task 4: Perspective System Expansion.

This module contains Ignition Perspective system functions for modern web-based HMI development.
Covers session management, navigation, messaging, components, and device interaction.

Total functions: 22
Categories: Session Management, Navigation, Messaging, Components, Device Operations
"""

from typing import Any


def get_task_4_perspective_functions() -> list[dict[str, Any]]:
    """Returns all Task 4 Perspective system functions with comprehensive metadata.

    Returns:
        List of function dictionaries with complete specifications
    """
    functions = [
        # Session Management Functions (6 functions)
        {
            "name": "getSessionInfo",
            "category": "Perspective System",
            "subcategory": "Session Management",
            "description": "Retrieves information about the current Perspective session",
            "syntax": "system.perspective.getSessionInfo(sessionId=None)",
            "parameters": [
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                }
            ],
            "returns": {
                "type": "PyDictionary",
                "description": "Dictionary containing session information including user, props, quality",
            },
            "scope": ["Perspective Session"],
            "tags": ["session", "info", "user", "perspective"],
            "code_example": """# Get current session info
session_info = system.perspective.getSessionInfo()
user = session_info.get('user', {})
username = user.get('userName', 'Anonymous')

# Get specific session info
other_session = system.perspective.getSessionInfo("session-123")""",
            "common_patterns": [
                "User authentication checks",
                "Session state monitoring",
                "User role validation",
                "Session debugging",
            ],
        },
        {
            "name": "getSessionProps",
            "category": "Perspective System",
            "subcategory": "Session Management",
            "description": "Gets session-scoped custom properties",
            "syntax": "system.perspective.getSessionProps(sessionId=None)",
            "parameters": [
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                }
            ],
            "returns": {
                "type": "PyDictionary",
                "description": "Dictionary of session properties",
            },
            "scope": ["Perspective Session"],
            "tags": ["session", "properties", "custom", "perspective"],
            "code_example": """# Get session properties
props = system.perspective.getSessionProps()
theme = props.get('theme', 'light')
language = props.get('language', 'en')

# Check if property exists
if 'userPreferences' in props:
    prefs = props['userPreferences']""",
            "common_patterns": [
                "Theme management",
                "User preferences",
                "Session configuration",
                "State persistence",
            ],
        },
        {
            "name": "setSessionProps",
            "category": "Perspective System",
            "subcategory": "Session Management",
            "description": "Sets session-scoped custom properties",
            "syntax": "system.perspective.setSessionProps(props, sessionId=None)",
            "parameters": [
                {
                    "name": "props",
                    "type": "PyDictionary",
                    "description": "Dictionary of properties to set",
                    "required": True,
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["session", "properties", "set", "perspective"],
            "code_example": """# Set session properties
system.perspective.setSessionProps({
    'theme': 'dark',
    'language': 'es',
    'userPreferences': {
        'showAdvanced': True,
        'refreshRate': 5000
    }
})

# Update single property
current_props = system.perspective.getSessionProps()
current_props['lastActivity'] = system.date.now()
system.perspective.setSessionProps(current_props)""",
            "common_patterns": [
                "User preference storage",
                "Theme switching",
                "Configuration persistence",
                "Session state management",
            ],
        },
        {
            "name": "vibrateDevice",
            "category": "Perspective System",
            "subcategory": "Session Management",
            "description": "Triggers device vibration on mobile devices",
            "syntax": "system.perspective.vibrateDevice(duration=200, sessionId=None)",
            "parameters": [
                {
                    "name": "duration",
                    "type": "Integer",
                    "description": "Vibration duration in milliseconds",
                    "required": False,
                    "default": "200",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["device", "vibration", "mobile", "feedback"],
            "code_example": """# Short vibration for button press
system.perspective.vibrateDevice(100)

# Longer vibration for alert
system.perspective.vibrateDevice(500)

# Vibrate specific session
system.perspective.vibrateDevice(300, "mobile-session-123")""",
            "common_patterns": [
                "Button press feedback",
                "Alert notifications",
                "Touch interactions",
                "Mobile UX enhancement",
            ],
        },
        {
            "name": "logout",
            "category": "Perspective System",
            "subcategory": "Session Management",
            "description": "Logs out the current user and redirects to login page",
            "syntax": "system.perspective.logout(sessionId=None)",
            "parameters": [
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                }
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["logout", "authentication", "security", "session"],
            "code_example": """# Logout current user
system.perspective.logout()

# Logout specific session
system.perspective.logout("session-456")

# Logout with confirmation
if system.gui.confirm("Are you sure you want to logout?"):
    system.perspective.logout()""",
            "common_patterns": [
                "User logout functionality",
                "Security enforcement",
                "Session termination",
                "Authentication workflows",
            ],
        },
        {
            "name": "closePage",
            "category": "Perspective System",
            "subcategory": "Session Management",
            "description": "Closes the current page/tab in the browser",
            "syntax": "system.perspective.closePage(sessionId=None)",
            "parameters": [
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                }
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["page", "close", "browser", "navigation"],
            "code_example": """# Close current page
system.perspective.closePage()

# Close with confirmation
if system.gui.confirm("Close this page?"):
    system.perspective.closePage()

# Close specific session page
system.perspective.closePage("session-789")""",
            "common_patterns": [
                "Application exit",
                "Page closure workflows",
                "Session cleanup",
                "Browser tab management",
            ],
        },
        # Navigation Functions (4 functions)
        {
            "name": "navigate",
            "category": "Perspective System",
            "subcategory": "Navigation",
            "description": "Navigates to a different page in the Perspective session",
            "syntax": "system.perspective.navigate(page, params=None, sessionId=None)",
            "parameters": [
                {
                    "name": "page",
                    "type": "String",
                    "description": "Target page path to navigate to",
                    "required": True,
                },
                {
                    "name": "params",
                    "type": "PyDictionary",
                    "description": "Optional parameters to pass to the target page",
                    "required": False,
                    "default": "None",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["navigation", "page", "routing", "perspective"],
            "code_example": """# Navigate to home page
system.perspective.navigate("/home")

# Navigate with parameters
params = {
    'equipmentId': 'PUMP-001',
    'mode': 'edit'
}
system.perspective.navigate("/equipment/details", params)

# Navigate specific session
system.perspective.navigate("/dashboard", None, "session-123")""",
            "common_patterns": [
                "Page routing",
                "Parameter passing",
                "Dynamic navigation",
                "Application flow control",
            ],
        },
        {
            "name": "openPopup",
            "category": "Perspective System",
            "subcategory": "Navigation",
            "description": "Opens a popup window with the specified view",
            "syntax": "system.perspective.openPopup(id, view, params=None, title='', position=None, sessionId=None)",
            "parameters": [
                {
                    "name": "id",
                    "type": "String",
                    "description": "Unique identifier for the popup",
                    "required": True,
                },
                {
                    "name": "view",
                    "type": "String",
                    "description": "Path to the view to display in popup",
                    "required": True,
                },
                {
                    "name": "params",
                    "type": "PyDictionary",
                    "description": "Optional parameters to pass to the view",
                    "required": False,
                    "default": "None",
                },
                {
                    "name": "title",
                    "type": "String",
                    "description": "Title for the popup window",
                    "required": False,
                    "default": "''",
                },
                {
                    "name": "position",
                    "type": "PyDictionary",
                    "description": "Position and size configuration",
                    "required": False,
                    "default": "None",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["popup", "modal", "dialog", "view"],
            "code_example": """# Simple popup
system.perspective.openPopup(
    "alert-popup",
    "Popups/AlertDialog",
    title="Alert"
)

# Popup with parameters and position
params = {'message': 'Process complete', 'type': 'success'}
position = {'width': 400, 'height': 300, 'x': 100, 'y': 100}
system.perspective.openPopup(
    "status-popup",
    "Popups/StatusDialog",
    params,
    "Status Update",
    position
)""",
            "common_patterns": [
                "Modal dialogs",
                "Configuration windows",
                "Detail views",
                "Alert notifications",
            ],
        },
        {
            "name": "closePopup",
            "category": "Perspective System",
            "subcategory": "Navigation",
            "description": "Closes a popup window by its identifier",
            "syntax": "system.perspective.closePopup(id, sessionId=None)",
            "parameters": [
                {
                    "name": "id",
                    "type": "String",
                    "description": "Identifier of the popup to close",
                    "required": True,
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["popup", "close", "modal", "dialog"],
            "code_example": """# Close specific popup
system.perspective.closePopup("alert-popup")

# Close popup after delay
system.util.invokeLater(
    lambda: system.perspective.closePopup("temp-popup"),
    5000
)

# Close multiple popups
popup_ids = ["popup-1", "popup-2", "popup-3"]
for popup_id in popup_ids:
    system.perspective.closePopup(popup_id)""",
            "common_patterns": [
                "Dialog dismissal",
                "Auto-close functionality",
                "Cleanup operations",
                "Modal management",
            ],
        },
        {
            "name": "print",
            "category": "Perspective System",
            "subcategory": "Navigation",
            "description": "Triggers the browser's print dialog for the current page",
            "syntax": "system.perspective.print(sessionId=None)",
            "parameters": [
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                }
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["print", "browser", "document", "export"],
            "code_example": """# Print current page
system.perspective.print()

# Print after confirmation
if system.gui.confirm("Print this report?"):
    system.perspective.print()

# Print specific session
system.perspective.print("report-session-456")""",
            "common_patterns": [
                "Report printing",
                "Document export",
                "Hard copy generation",
                "Print preview",
            ],
        },
        # Messaging Functions (4 functions)
        {
            "name": "sendMessage",
            "category": "Perspective System",
            "subcategory": "Messaging",
            "description": "Sends a message to one or more Perspective sessions",
            "syntax": "system.perspective.sendMessage(messageType, payload=None, scope='session', sessionId=None)",
            "parameters": [
                {
                    "name": "messageType",
                    "type": "String",
                    "description": "Type/category of the message",
                    "required": True,
                },
                {
                    "name": "payload",
                    "type": "PyDictionary",
                    "description": "Optional data payload to send with message",
                    "required": False,
                    "default": "None",
                },
                {
                    "name": "scope",
                    "type": "String",
                    "description": "Message scope: 'session', 'project', or 'gateway'",
                    "required": False,
                    "default": "'session'",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Target session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["message", "communication", "broadcast", "session"],
            "code_example": """# Send alert to current session
system.perspective.sendMessage("alert", {
    "title": "Equipment Alarm",
    "message": "Pump pressure exceeded threshold",
    "severity": "high"
})

# Broadcast to all sessions in project
system.perspective.sendMessage(
    "system-update",
    {"version": "1.2.3", "restart_required": True},
    scope="project"
)

# Send to specific session
system.perspective.sendMessage(
    "user-notification",
    {"text": "Your report is ready"},
    sessionId="operator-session-123"
)""",
            "common_patterns": [
                "Real-time notifications",
                "Alert broadcasting",
                "System announcements",
                "Inter-session communication",
            ],
        },
        {
            "name": "subscribe",
            "category": "Perspective System",
            "subcategory": "Messaging",
            "description": "Subscribes to messages of a specific type",
            "syntax": "system.perspective.subscribe(messageType, callback)",
            "parameters": [
                {
                    "name": "messageType",
                    "type": "String",
                    "description": "Type of messages to subscribe to",
                    "required": True,
                },
                {
                    "name": "callback",
                    "type": "Function",
                    "description": "Function to call when message is received",
                    "required": True,
                },
            ],
            "returns": {
                "type": "String",
                "description": "Subscription ID for later unsubscribing",
            },
            "scope": ["Perspective Session"],
            "tags": ["subscribe", "message", "callback", "event"],
            "code_example": """# Subscribe to alerts
def handle_alert(payload):
    title = payload.get('title', 'Alert')
    message = payload.get('message', '')
    system.gui.messageBox(message, title)

subscription_id = system.perspective.subscribe("alert", handle_alert)

# Subscribe to system updates
def handle_system_update(payload):
    if payload.get('restart_required'):
        system.gui.warningBox("System restart required for update")

system.perspective.subscribe("system-update", handle_system_update)""",
            "common_patterns": [
                "Event handling",
                "Message processing",
                "Real-time updates",
                "Notification handling",
            ],
        },
        {
            "name": "unsubscribe",
            "category": "Perspective System",
            "subcategory": "Messaging",
            "description": "Unsubscribes from messages using subscription ID",
            "syntax": "system.perspective.unsubscribe(subscriptionId)",
            "parameters": [
                {
                    "name": "subscriptionId",
                    "type": "String",
                    "description": "ID returned from subscribe function",
                    "required": True,
                }
            ],
            "returns": {
                "type": "Boolean",
                "description": "True if successfully unsubscribed",
            },
            "scope": ["Perspective Session"],
            "tags": ["unsubscribe", "message", "cleanup", "subscription"],
            "code_example": """# Store subscription ID
alert_subscription = system.perspective.subscribe("alert", handle_alert)

# Later unsubscribe
success = system.perspective.unsubscribe(alert_subscription)
if success:
    print("Successfully unsubscribed from alerts")

# Cleanup multiple subscriptions
subscriptions = [sub1, sub2, sub3]
for sub_id in subscriptions:
    system.perspective.unsubscribe(sub_id)""",
            "common_patterns": [
                "Cleanup operations",
                "Subscription management",
                "Memory management",
                "Event handler removal",
            ],
        },
        {
            "name": "messageFromOtherSession",
            "category": "Perspective System",
            "subcategory": "Messaging",
            "description": "Checks if current event was triggered by message from another session",
            "syntax": "system.perspective.messageFromOtherSession()",
            "parameters": [],
            "returns": {
                "type": "Boolean",
                "description": "True if message originated from another session",
            },
            "scope": ["Perspective Session"],
            "tags": ["message", "session", "origin", "event"],
            "code_example": """# In message handler
def handle_data_update(payload):
    if system.perspective.messageFromOtherSession():
        # Update came from another session
        print("Received update from another session")
        refresh_display(payload)
    else:
        # Update originated locally
        print("Local update, no need to refresh")

# Use in conditional logic
if not system.perspective.messageFromOtherSession():
    # Only execute for local events
    save_local_state()""",
            "common_patterns": [
                "Event origin detection",
                "Preventing feedback loops",
                "Conditional processing",
                "Session-aware logic",
            ],
        },
        # Component Functions (4 functions)
        {
            "name": "alterFilter",
            "category": "Perspective System",
            "subcategory": "Components",
            "description": "Modifies filter criteria for Perspective Table or other filterable components",
            "syntax": "system.perspective.alterFilter(component, filter, sessionId=None)",
            "parameters": [
                {
                    "name": "component",
                    "type": "Component",
                    "description": "Reference to the component to modify",
                    "required": True,
                },
                {
                    "name": "filter",
                    "type": "PyDictionary",
                    "description": "Filter configuration dictionary",
                    "required": True,
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["filter", "table", "component", "data"],
            "code_example": """# Filter table by status
table = self.getSibling("DataTable")
filter_config = {
    "column": "status",
    "condition": "equals",
    "value": "active"
}
system.perspective.alterFilter(table, filter_config)

# Multiple filter conditions
complex_filter = {
    "conditions": [
        {"column": "priority", "condition": ">=", "value": 3},
        {"column": "assigned", "condition": "equals", "value": True}
    ],
    "logic": "AND"
}
system.perspective.alterFilter(table, complex_filter)""",
            "common_patterns": [
                "Dynamic table filtering",
                "Search functionality",
                "Data presentation",
                "User-driven filtering",
            ],
        },
        {
            "name": "alterSort",
            "category": "Perspective System",
            "subcategory": "Components",
            "description": "Changes sort configuration for Perspective Table or other sortable components",
            "syntax": "system.perspective.alterSort(component, sorts, sessionId=None)",
            "parameters": [
                {
                    "name": "component",
                    "type": "Component",
                    "description": "Reference to the component to modify",
                    "required": True,
                },
                {
                    "name": "sorts",
                    "type": "PyList",
                    "description": "List of sort configurations",
                    "required": True,
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["sort", "table", "component", "order"],
            "code_example": """# Sort by single column
table = self.getSibling("EquipmentTable")
sorts = [{"column": "lastMaintenance", "direction": "desc"}]
system.perspective.alterSort(table, sorts)

# Multi-column sort
sorts = [
    {"column": "priority", "direction": "desc"},
    {"column": "name", "direction": "asc"}
]
system.perspective.alterSort(table, sorts)

# Clear sorting
system.perspective.alterSort(table, [])""",
            "common_patterns": [
                "Dynamic table sorting",
                "Data organization",
                "User-controlled ordering",
                "Multi-level sorting",
            ],
        },
        {
            "name": "download",
            "category": "Perspective System",
            "subcategory": "Components",
            "description": "Initiates download of data or file in the browser",
            "syntax": "system.perspective.download(filename, data, contentType='text/plain', sessionId=None)",
            "parameters": [
                {
                    "name": "filename",
                    "type": "String",
                    "description": "Name for the downloaded file",
                    "required": True,
                },
                {
                    "name": "data",
                    "type": "String",
                    "description": "Data content to download",
                    "required": True,
                },
                {
                    "name": "contentType",
                    "type": "String",
                    "description": "MIME type of the content",
                    "required": False,
                    "default": "'text/plain'",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["download", "export", "file", "data"],
            "code_example": """# Download CSV data
csv_data = "Name,Value,Timestamp\\nPump1,85.2,2024-01-15"
system.perspective.download("equipment_data.csv", csv_data, "text/csv")

# Download JSON configuration
import system.util
config = {"setting1": "value1", "setting2": True}
json_data = system.util.jsonEncode(config)
system.perspective.download("config.json", json_data, "application/json")

# Download report
report_content = generate_report()
system.perspective.download("daily_report.txt", report_content)""",
            "common_patterns": [
                "Data export",
                "Report generation",
                "Configuration backup",
                "File creation",
            ],
        },
        {
            "name": "refresh",
            "category": "Perspective System",
            "subcategory": "Components",
            "description": "Refreshes a specific component or binding",
            "syntax": "system.perspective.refresh(component, sessionId=None)",
            "parameters": [
                {
                    "name": "component",
                    "type": "Component",
                    "description": "Component reference to refresh",
                    "required": True,
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["refresh", "component", "update", "binding"],
            "code_example": """# Refresh a table component
table = self.getSibling("DataTable")
system.perspective.refresh(table)

# Refresh chart after data update
chart = self.getSibling("TrendChart")
system.perspective.refresh(chart)

# Refresh multiple components
components = [
    self.getSibling("Table1"),
    self.getSibling("Chart1"),
    self.getSibling("Gauge1")
]
for comp in components:
    system.perspective.refresh(comp)""",
            "common_patterns": [
                "Data refresh",
                "Component updates",
                "Binding refresh",
                "UI synchronization",
            ],
        },
        # Device Operations (4 functions)
        {
            "name": "requestMobilePickerOpen",
            "category": "Perspective System",
            "subcategory": "Device Operations",
            "description": "Opens native mobile picker (date, time, select) on mobile devices",
            "syntax": "system.perspective.requestMobilePickerOpen(component, pickerType, sessionId=None)",
            "parameters": [
                {
                    "name": "component",
                    "type": "Component",
                    "description": "Component that should receive the picked value",
                    "required": True,
                },
                {
                    "name": "pickerType",
                    "type": "String",
                    "description": "Type of picker: 'date', 'time', 'datetime', 'select'",
                    "required": True,
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["mobile", "picker", "native", "input"],
            "code_example": """# Open date picker
date_input = self.getSibling("DateInput")
system.perspective.requestMobilePickerOpen(date_input, "date")

# Open time picker
time_input = self.getSibling("TimeInput")
system.perspective.requestMobilePickerOpen(time_input, "time")

# Open datetime picker
datetime_input = self.getSibling("DateTimeInput")
system.perspective.requestMobilePickerOpen(datetime_input, "datetime")""",
            "common_patterns": [
                "Mobile-friendly input",
                "Native UI integration",
                "Touch interface optimization",
                "Device-specific functionality",
            ],
        },
        {
            "name": "requestFileUpload",
            "category": "Perspective System",
            "subcategory": "Device Operations",
            "description": "Opens file upload dialog and handles file selection",
            "syntax": "system.perspective.requestFileUpload(callback, accept=None, multiple=False, sessionId=None)",
            "parameters": [
                {
                    "name": "callback",
                    "type": "Function",
                    "description": "Function to call with selected file(s)",
                    "required": True,
                },
                {
                    "name": "accept",
                    "type": "String",
                    "description": "File types to accept (MIME types or extensions)",
                    "required": False,
                    "default": "None",
                },
                {
                    "name": "multiple",
                    "type": "Boolean",
                    "description": "Whether to allow multiple file selection",
                    "required": False,
                    "default": "False",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["file", "upload", "dialog", "selection"],
            "code_example": """# Simple file upload
def handle_file(files):
    for file_info in files:
        filename = file_info['name']
        content = file_info['content']
        print("Uploaded: " + filename)

system.perspective.requestFileUpload(handle_file)

# Image upload only
def handle_image(files):
    image = files[0]
    # Process image
    display_uploaded_image(image)

system.perspective.requestFileUpload(
    handle_image,
    accept="image/*",
    multiple=False
)""",
            "common_patterns": [
                "File upload functionality",
                "Configuration import",
                "Image/document upload",
                "Data file processing",
            ],
        },
        {
            "name": "requestCamera",
            "category": "Perspective System",
            "subcategory": "Device Operations",
            "description": "Requests access to device camera for photo capture",
            "syntax": "system.perspective.requestCamera(callback, facingMode='user', sessionId=None)",
            "parameters": [
                {
                    "name": "callback",
                    "type": "Function",
                    "description": "Function to call with captured image",
                    "required": True,
                },
                {
                    "name": "facingMode",
                    "type": "String",
                    "description": "Camera facing mode: 'user' (front) or 'environment' (back)",
                    "required": False,
                    "default": "'user'",
                },
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                },
            ],
            "returns": {"type": "None", "description": "No return value"},
            "scope": ["Perspective Session"],
            "tags": ["camera", "photo", "capture", "device"],
            "code_example": """# Capture photo with front camera
def handle_photo(image_data):
    # Save or process the captured image
    save_inspection_photo(image_data)

system.perspective.requestCamera(handle_photo, "user")

# Use back camera for inspection
def handle_inspection_photo(image_data):
    equipment_id = self.custom.equipmentId
    save_equipment_photo(equipment_id, image_data)

system.perspective.requestCamera(handle_inspection_photo, "environment")""",
            "common_patterns": [
                "Photo capture",
                "Equipment inspection",
                "Documentation",
                "QR code scanning",
            ],
        },
        {
            "name": "isViewportMobile",
            "category": "Perspective System",
            "subcategory": "Device Operations",
            "description": "Checks if the current viewport is considered mobile-sized",
            "syntax": "system.perspective.isViewportMobile(sessionId=None)",
            "parameters": [
                {
                    "name": "sessionId",
                    "type": "String",
                    "description": "Optional session ID. If None, uses current session",
                    "required": False,
                    "default": "None",
                }
            ],
            "returns": {
                "type": "Boolean",
                "description": "True if viewport is mobile-sized",
            },
            "scope": ["Perspective Session"],
            "tags": ["mobile", "viewport", "responsive", "detection"],
            "code_example": """# Responsive behavior
if system.perspective.isViewportMobile():
    # Mobile layout
    self.custom.showDetails = False
    self.getSibling("Sidebar").visible = False
else:
    # Desktop layout
    self.custom.showDetails = True
    self.getSibling("Sidebar").visible = True

# Conditional component sizing
button_size = "small" if system.perspective.isViewportMobile() else "large"
self.getSibling("ActionButton").props.size = button_size""",
            "common_patterns": [
                "Responsive design",
                "Mobile optimization",
                "Layout adaptation",
                "Device-specific UI",
            ],
        },
    ]

    return functions


def get_task_4_metadata() -> dict[str, Any]:
    """Returns metadata about Task 4."""
    return {
        "task_number": 4,
        "task_name": "Perspective System Expansion",
        "description": "Comprehensive Perspective system functions for modern web-based HMI development",
        "total_functions": 22,
        "categories": {
            "Session Management": 6,
            "Navigation": 4,
            "Messaging": 4,
            "Components": 4,
            "Device Operations": 4,
        },
        "scope_distribution": {"Perspective Session": 22},
        "key_features": [
            "Session lifecycle management",
            "Page navigation and routing",
            "Real-time messaging system",
            "Component interaction and control",
            "Mobile device integration",
            "File operations and downloads",
            "Responsive design utilities",
        ],
    }
