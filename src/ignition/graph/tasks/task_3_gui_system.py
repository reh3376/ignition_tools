#!/usr/bin/env python3
"""Task 3: GUI System Expansion Implementation
==========================================

This module implements comprehensive GUI system functions for Ignition Vision Client.
Provides enhanced window management, dialogs, desktop operations, and user interface
interactions specific to Vision Client environments.

Author: Assistant
Date: 2025-01-23
Task: 3/10 - GUI System (MEDIUM Priority)
Functions: 25 comprehensive GUI functions
Complexity: ⭐⭐⭐ (Medium)
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Task 3: GUI System Functions
GUI_SYSTEM_FUNCTIONS = [
    {
        "name": "system.gui.desktop",
        "category": "GUI Management",
        "subcategory": "Desktop Operations",
        "description": "Access and manipulate the Vision Client desktop environment",
        "parameters": [
            {
                "name": "operation",
                "type": "String",
                "description": "Desktop operation to perform",
            },
            {
                "name": "options",
                "type": "PyDictionary",
                "description": "Operation-specific options",
                "optional": True,
            },
        ],
        "returns": {"type": "Object", "description": "Desktop operation result"},
        "scope": ["Vision Client"],
        "code_example": """# Get desktop information
desktop_info = system.gui.desktop("getInfo")
print("Desktop size:", desktop_info["size"])

# Set desktop properties
system.gui.desktop("setProperty", {
    "background_color": "#F0F0F0",
    "allow_resize": True
})

# Manage desktop state
system.gui.desktop("maximize")
system.gui.desktop("minimize")
system.gui.desktop("restore")""",
        "common_patterns": [
            "Desktop state management",
            "Screen configuration",
            "Multi-monitor support",
            "Desktop customization",
        ],
    },
    {
        "name": "system.gui.chooseColor",
        "category": "GUI Dialogs",
        "subcategory": "Selection Dialogs",
        "description": "Display a color picker dialog for user color selection",
        "parameters": [
            {
                "name": "initialColor",
                "type": "Color",
                "description": "Initial color selection",
                "optional": True,
            },
            {
                "name": "title",
                "type": "String",
                "description": "Dialog title",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Color",
            "description": "Selected color or None if cancelled",
        },
        "scope": ["Vision Client"],
        "code_example": """# Basic color picker
selected_color = system.gui.chooseColor()
if selected_color:
    print("Selected color:", selected_color)

# Color picker with initial color
import java.awt.Color as Color
initial = Color(255, 0, 0)  # Red
color = system.gui.chooseColor(initial, "Choose Background Color")

# Apply color to component
if color:
    event.source.background = color""",
        "common_patterns": [
            "User color selection",
            "Theme customization",
            "Component styling",
            "Visual configuration",
        ],
    },
    {
        "name": "system.gui.warningBox",
        "category": "GUI Dialogs",
        "subcategory": "Message Dialogs",
        "description": "Display a warning message dialog to the user",
        "parameters": [
            {
                "name": "message",
                "type": "String",
                "description": "Warning message to display",
            },
            {
                "name": "title",
                "type": "String",
                "description": "Dialog title",
                "optional": True,
            },
            {
                "name": "options",
                "type": "List",
                "description": "Custom button options",
                "optional": True,
            },
        ],
        "returns": {"type": "String", "description": "User's button selection"},
        "scope": ["Vision Client"],
        "code_example": """# Simple warning
system.gui.warningBox("Temperature exceeded safe limits!")

# Warning with custom title
system.gui.warningBox(
    "Process will be stopped for maintenance",
    "Maintenance Warning"
)

# Warning with custom options
response = system.gui.warningBox(
    "Delete all historical data?",
    "Data Deletion Warning",
    ["Delete", "Cancel", "Backup First"]
)

if response == "Delete":
    # Proceed with deletion
    pass
elif response == "Backup First":
    # Perform backup then delete
    pass""",
        "common_patterns": [
            "User warnings",
            "Safety confirmations",
            "Process notifications",
            "Risk acknowledgments",
        ],
    },
    {
        "name": "system.gui.errorBox",
        "category": "GUI Dialogs",
        "subcategory": "Message Dialogs",
        "description": "Display an error message dialog to the user",
        "parameters": [
            {
                "name": "message",
                "type": "String",
                "description": "Error message to display",
            },
            {
                "name": "title",
                "type": "String",
                "description": "Dialog title",
                "optional": True,
            },
            {
                "name": "details",
                "type": "String",
                "description": "Detailed error information",
                "optional": True,
            },
        ],
        "returns": {"type": "None", "description": "No return value"},
        "scope": ["Vision Client"],
        "code_example": """# Simple error message
system.gui.errorBox("Failed to connect to database")

# Error with custom title
system.gui.errorBox(
    "Communication timeout",
    "Device Connection Error"
)

# Detailed error information
try:
    # Some operation that might fail
    dangerous_operation()
except Exception as e:
    system.gui.errorBox(
        "Operation failed",
        "System Error",
        str(e)
    )""",
        "common_patterns": [
            "Error reporting",
            "Exception handling",
            "User notifications",
            "Troubleshooting aids",
        ],
    },
    {
        "name": "system.gui.getRootContainer",
        "category": "GUI Management",
        "subcategory": "Container Access",
        "description": "Get reference to the root container of the current window",
        "parameters": [],
        "returns": {"type": "Container", "description": "Root container object"},
        "scope": ["Vision Client"],
        "code_example": """# Get root container
root = system.gui.getRootContainer()

# Access root properties
print("Root size:", root.size)
print("Root background:", root.background)

# Add components to root
new_label = system.gui.createComponent("Label")
new_label.text = "Dynamic Label"
root.add(new_label)

# Modify root container
root.background = java.awt.Color.LIGHT_GRAY
root.layout = BorderLayout()""",
        "common_patterns": [
            "Dynamic UI creation",
            "Container manipulation",
            "Layout management",
            "Component hierarchy access",
        ],
    },
    {
        "name": "system.gui.getParentWindow",
        "category": "GUI Management",
        "subcategory": "Window Management",
        "description": "Get reference to the parent window of the current component",
        "parameters": [
            {
                "name": "component",
                "type": "Component",
                "description": "Component to find parent for",
                "optional": True,
            }
        ],
        "returns": {"type": "Window", "description": "Parent window object"},
        "scope": ["Vision Client"],
        "code_example": """# Get parent window from current context
parent_window = system.gui.getParentWindow()

# Get parent window of specific component
parent = system.gui.getParentWindow(event.source)

# Window operations
parent_window.title = "Updated Title"
parent_window.size = (800, 600)
parent_window.location = (100, 100)

# Check window state
if parent_window.visible:
    print("Window is visible")""",
        "common_patterns": [
            "Window management",
            "Parent-child relationships",
            "Window property access",
            "Cross-window communication",
        ],
    },
    {
        "name": "system.gui.getWindow",
        "category": "GUI Management",
        "subcategory": "Window Management",
        "description": "Get reference to a specific window by name or path",
        "parameters": [
            {
                "name": "windowPath",
                "type": "String",
                "description": "Path to the window",
            }
        ],
        "returns": {"type": "Window", "description": "Window object reference"},
        "scope": ["Vision Client"],
        "code_example": """# Get window by path
main_window = system.gui.getWindow("Main Windows/Overview")

# Check if window exists
if main_window:
    main_window.visible = True
    main_window.location = (0, 0)

# Get popup window
popup = system.gui.getWindow("Popups/AlarmDetails")
if popup:
    popup.size = (400, 300)

# Window validation
try:
    target_window = system.gui.getWindow("NonExistent")
except:
    print("Window not found")""",
        "common_patterns": [
            "Window reference management",
            "Cross-window operations",
            "Window existence checking",
            "Dynamic window access",
        ],
    },
    {
        "name": "system.gui.getWindowNames",
        "category": "GUI Management",
        "subcategory": "Window Management",
        "description": "Get list of all available window names in the project",
        "parameters": [],
        "returns": {"type": "List[String]", "description": "List of window names"},
        "scope": ["Vision Client"],
        "code_example": """# Get all window names
window_names = system.gui.getWindowNames()
print("Available windows:", window_names)

# Filter specific windows
main_windows = [name for name in window_names if "Main" in name]
popups = [name for name in window_names if "Popup" in name]

# Dynamic window navigation
def open_random_window():
    import random
    windows = system.gui.getWindowNames()
    if windows:
        random_window = random.choice(windows)
        system.nav.openWindow(random_window)""",
        "common_patterns": [
            "Window discovery",
            "Dynamic navigation",
            "Window inventory",
            "Navigation menu creation",
        ],
    },
    {
        "name": "system.gui.transform",
        "category": "GUI Management",
        "subcategory": "Coordinate Operations",
        "description": "Transform coordinates between different component coordinate systems",
        "parameters": [
            {
                "name": "source",
                "type": "Component",
                "description": "Source coordinate system",
            },
            {
                "name": "target",
                "type": "Component",
                "description": "Target coordinate system",
            },
            {"name": "point", "type": "Point", "description": "Point to transform"},
        ],
        "returns": {"type": "Point", "description": "Transformed point coordinates"},
        "scope": ["Vision Client"],
        "code_example": """# Transform coordinates between components
import java.awt.Point as Point

source_point = Point(10, 20)
transformed = system.gui.transform(
    event.source,      # Source component
    root_container,    # Target component
    source_point
)

# Mouse position transformation
def onMouseClick(event):
    # Transform click coordinates to root container space
    root_coords = system.gui.transform(
        event.source,
        system.gui.getRootContainer(),
        Point(event.x, event.y)
    )
    print("Root coordinates:", root_coords)""",
        "common_patterns": [
            "Coordinate system conversion",
            "Mouse event handling",
            "Drag and drop operations",
            "Component positioning",
        ],
    },
    {
        "name": "system.gui.openDesktop",
        "category": "GUI Management",
        "subcategory": "Desktop Operations",
        "description": "Open or switch to a specific desktop in the Vision Client",
        "parameters": [
            {
                "name": "desktopName",
                "type": "String",
                "description": "Name of desktop to open",
            },
            {
                "name": "options",
                "type": "PyDictionary",
                "description": "Desktop opening options",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if desktop opened successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Open specific desktop
success = system.gui.openDesktop("Production Dashboard")

# Open desktop with options
system.gui.openDesktop("Maintenance View", {
    "maximized": True,
    "clear_existing": False
})

# Desktop switching logic
current_shift = system.date.getHour24(system.date.now())
if current_shift < 8:
    system.gui.openDesktop("Night Shift")
elif current_shift < 16:
    system.gui.openDesktop("Day Shift")
else:
    system.gui.openDesktop("Evening Shift")""",
        "common_patterns": [
            "Desktop switching",
            "Context-based navigation",
            "Shift-based interfaces",
            "Role-based desktops",
        ],
    },
    {
        "name": "system.gui.closeDesktop",
        "category": "GUI Management",
        "subcategory": "Desktop Operations",
        "description": "Close the current or specified desktop",
        "parameters": [
            {
                "name": "desktopName",
                "type": "String",
                "description": "Name of desktop to close",
                "optional": True,
            },
            {
                "name": "force",
                "type": "Boolean",
                "description": "Force close without confirmation",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if desktop closed successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Close current desktop
system.gui.closeDesktop()

# Close specific desktop
system.gui.closeDesktop("Temporary Dashboard")

# Force close without confirmation
system.gui.closeDesktop("Old Interface", True)

# Conditional desktop closure
if system.security.getUsername() != "admin":
    system.gui.closeDesktop("Admin Console", True)""",
        "common_patterns": [
            "Desktop cleanup",
            "Session management",
            "Security-based closure",
            "Resource management",
        ],
    },
    {
        "name": "system.gui.getClientId",
        "category": "GUI Management",
        "subcategory": "Client Information",
        "description": "Get unique identifier for the current Vision Client session",
        "parameters": [],
        "returns": {"type": "String", "description": "Unique client identifier"},
        "scope": ["Vision Client"],
        "code_example": """# Get client ID
client_id = system.gui.getClientId()
print("Client ID:", client_id)

# Use for session tracking
system.tag.write("[default]Client_Sessions/" + client_id, {
    "timestamp": system.date.now(),
    "user": system.security.getUsername(),
    "status": "active"
})

# Client-specific operations
if client_id.startswith("STATION"):
    # Station-specific logic
    pass
elif client_id.startswith("MOBILE"):
    # Mobile client logic
    pass""",
        "common_patterns": [
            "Session tracking",
            "Client identification",
            "Multi-client management",
            "User activity monitoring",
        ],
    },
    {
        "name": "system.gui.getQuality",
        "category": "GUI Management",
        "subcategory": "Data Quality",
        "description": "Get data quality information for GUI elements",
        "parameters": [
            {
                "name": "component",
                "type": "Component",
                "description": "Component to check quality for",
            },
            {
                "name": "property",
                "type": "String",
                "description": "Property name to check",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Quality",
            "description": "Quality object with status information",
        },
        "scope": ["Vision Client"],
        "code_example": """# Check component quality
quality = system.gui.getQuality(event.source)
print("Quality code:", quality.qualityCode)

# Check specific property quality
temp_quality = system.gui.getQuality(temp_display, "text")

# Quality-based styling
if quality.isGood():
    event.source.background = java.awt.Color.WHITE
elif quality.isBad():
    event.source.background = java.awt.Color.RED
else:
    event.source.background = java.awt.Color.YELLOW""",
        "common_patterns": [
            "Data quality visualization",
            "Component validation",
            "Error indication",
            "Quality-based styling",
        ],
    },
    {
        "name": "system.gui.getScreens",
        "category": "GUI Management",
        "subcategory": "Screen Management",
        "description": "Get information about available screens/monitors",
        "parameters": [],
        "returns": {
            "type": "List[Screen]",
            "description": "List of screen information objects",
        },
        "scope": ["Vision Client"],
        "code_example": """# Get all screens
screens = system.gui.getScreens()
for i, screen in enumerate(screens):
    print(f"Screen {i}: {screen.width}x{screen.height}")

# Find primary screen
primary = None
for screen in screens:
    if screen.isPrimary():
        primary = screen
        break

# Multi-monitor window positioning
if len(screens) > 1:
    # Place window on second monitor
    second_screen = screens[1]
    window.location = (second_screen.x, second_screen.y)""",
        "common_patterns": [
            "Multi-monitor support",
            "Screen resolution detection",
            "Window positioning",
            "Display configuration",
        ],
    },
    {
        "name": "system.gui.setScreenIndex",
        "category": "GUI Management",
        "subcategory": "Screen Management",
        "description": "Set the active screen index for window operations",
        "parameters": [
            {
                "name": "screenIndex",
                "type": "Integer",
                "description": "Index of screen to set as active",
            }
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if screen index set successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Set primary screen
system.gui.setScreenIndex(0)

# Switch to secondary screen
if len(system.gui.getScreens()) > 1:
    system.gui.setScreenIndex(1)

# Screen-based window management
def moveToScreen(screen_index):
    if system.gui.setScreenIndex(screen_index):
        # Open new windows on this screen
        system.nav.openWindow("Dashboard")
        return True
    return False""",
        "common_patterns": [
            "Screen switching",
            "Multi-monitor workflows",
            "Display management",
            "Window placement control",
        ],
    },
    {
        "name": "system.gui.createComponent",
        "category": "GUI Components",
        "subcategory": "Dynamic Creation",
        "description": "Dynamically create GUI components at runtime",
        "parameters": [
            {
                "name": "componentType",
                "type": "String",
                "description": "Type of component to create",
            },
            {
                "name": "properties",
                "type": "PyDictionary",
                "description": "Initial component properties",
                "optional": True,
            },
        ],
        "returns": {"type": "Component", "description": "Created component object"},
        "scope": ["Vision Client"],
        "code_example": """# Create basic label
label = system.gui.createComponent("Label", {
    "text": "Dynamic Label",
    "font": "Arial-BOLD-14"
})

# Create button with event
button = system.gui.createComponent("Button", {
    "text": "Click Me",
    "background": java.awt.Color.BLUE
})

# Add to container
container = event.source.parent
container.add(label)
container.add(button)

# Create complex component
chart = system.gui.createComponent("Chart", {
    "chartType": "line",
    "title": "Trend Data"
})""",
        "common_patterns": [
            "Dynamic UI generation",
            "Runtime component creation",
            "Conditional interfaces",
            "Data-driven layouts",
        ],
    },
    {
        "name": "system.gui.removeComponent",
        "category": "GUI Components",
        "subcategory": "Dynamic Management",
        "description": "Remove components from their parent containers",
        "parameters": [
            {
                "name": "component",
                "type": "Component",
                "description": "Component to remove",
            },
            {
                "name": "dispose",
                "type": "Boolean",
                "description": "Whether to dispose component resources",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if component removed successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Remove specific component
success = system.gui.removeComponent(old_label)

# Remove with resource disposal
system.gui.removeComponent(temp_chart, True)

# Conditional removal
if not component.visible:
    system.gui.removeComponent(component)

# Clean up dynamic components
for component in container.components:
    if hasattr(component, 'temporary'):
        system.gui.removeComponent(component, True)""",
        "common_patterns": [
            "Component cleanup",
            "Dynamic UI management",
            "Memory management",
            "Conditional removal",
        ],
    },
    {
        "name": "system.gui.refreshComponent",
        "category": "GUI Components",
        "subcategory": "Component Operations",
        "description": "Refresh component display and data bindings",
        "parameters": [
            {
                "name": "component",
                "type": "Component",
                "description": "Component to refresh",
            },
            {
                "name": "deep",
                "type": "Boolean",
                "description": "Whether to refresh child components",
                "optional": True,
            },
        ],
        "returns": {"type": "None", "description": "No return value"},
        "scope": ["Vision Client"],
        "code_example": """# Refresh single component
system.gui.refreshComponent(data_table)

# Deep refresh including children
system.gui.refreshComponent(root_container, True)

# Refresh after data update
system.tag.write("Production/Rate", new_rate)
system.gui.refreshComponent(rate_display)

# Periodic refresh
def refreshDashboard():
    system.gui.refreshComponent(dashboard_panel, True)""",
        "common_patterns": [
            "Data synchronization",
            "UI updates",
            "Binding refresh",
            "Display updates",
        ],
    },
    {
        "name": "system.gui.getComponentAt",
        "category": "GUI Components",
        "subcategory": "Component Discovery",
        "description": "Get component at specific coordinates within a container",
        "parameters": [
            {
                "name": "container",
                "type": "Container",
                "description": "Container to search in",
            },
            {"name": "x", "type": "Integer", "description": "X coordinate"},
            {"name": "y", "type": "Integer", "description": "Y coordinate"},
        ],
        "returns": {
            "type": "Component",
            "description": "Component at coordinates or None",
        },
        "scope": ["Vision Client"],
        "code_example": """# Get component at mouse position
def onMouseClick(event):
    clicked_component = system.gui.getComponentAt(
        event.source.parent,
        event.x,
        event.y
    )
    if clicked_component:
        print("Clicked on:", clicked_component.name)

# Hit testing
root = system.gui.getRootContainer()
component_at_center = system.gui.getComponentAt(
    root,
    root.width // 2,
    root.height // 2
)""",
        "common_patterns": [
            "Hit testing",
            "Mouse interaction",
            "Component discovery",
            "Coordinate-based selection",
        ],
    },
    {
        "name": "system.gui.setClipboard",
        "category": "GUI Operations",
        "subcategory": "System Integration",
        "description": "Set text content to the system clipboard",
        "parameters": [
            {
                "name": "text",
                "type": "String",
                "description": "Text to copy to clipboard",
            }
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if clipboard set successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Copy text to clipboard
system.gui.setClipboard("Copied data value")

# Copy tag value
tag_value = system.tag.read("Production/CurrentRate").value
system.gui.setClipboard(str(tag_value))

# Copy formatted data
data = "Timestamp: %s, Value: %.2f" % (
    system.date.format(system.date.now(), "yyyy-MM-dd HH:mm:ss"),
    production_rate
)
system.gui.setClipboard(data)""",
        "common_patterns": [
            "Data copying",
            "Export functionality",
            "User assistance",
            "Data sharing",
        ],
    },
    {
        "name": "system.gui.getClipboard",
        "category": "GUI Operations",
        "subcategory": "System Integration",
        "description": "Get text content from the system clipboard",
        "parameters": [],
        "returns": {"type": "String", "description": "Clipboard text content"},
        "scope": ["Vision Client"],
        "code_example": """# Get clipboard content
clipboard_text = system.gui.getClipboard()
if clipboard_text:
    print("Clipboard contains:", clipboard_text)

# Paste into component
def pasteData(component):
    text = system.gui.getClipboard()
    if text and hasattr(component, 'text'):
        component.text = text

# Validate clipboard data
clipboard_data = system.gui.getClipboard()
try:
    numeric_value = float(clipboard_data)
    # Use numeric value
except:
    print("Clipboard does not contain numeric data")""",
        "common_patterns": [
            "Data pasting",
            "Import functionality",
            "Data validation",
            "User input assistance",
        ],
    },
    {
        "name": "system.gui.showKeyboard",
        "category": "GUI Operations",
        "subcategory": "Input Methods",
        "description": "Show or hide the on-screen virtual keyboard",
        "parameters": [
            {
                "name": "show",
                "type": "Boolean",
                "description": "Whether to show or hide keyboard",
            },
            {
                "name": "keyboardType",
                "type": "String",
                "description": "Type of keyboard to display",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if keyboard state changed successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Show virtual keyboard
system.gui.showKeyboard(True)

# Show numeric keyboard
system.gui.showKeyboard(True, "numeric")

# Hide keyboard
system.gui.showKeyboard(False)

# Touch-friendly input
def onTextFieldFocus(event):
    # Show keyboard when text field gains focus
    system.gui.showKeyboard(True)

def onTextFieldBlur(event):
    # Hide keyboard when text field loses focus
    system.gui.showKeyboard(False)""",
        "common_patterns": [
            "Touch interface support",
            "Mobile-friendly input",
            "Accessibility features",
            "Kiosk applications",
        ],
    },
    {
        "name": "system.gui.setCursor",
        "category": "GUI Operations",
        "subcategory": "Mouse Operations",
        "description": "Set the mouse cursor type for a component or globally",
        "parameters": [
            {
                "name": "cursorType",
                "type": "String",
                "description": "Type of cursor to display",
            },
            {
                "name": "component",
                "type": "Component",
                "description": "Component to apply cursor to",
                "optional": True,
            },
        ],
        "returns": {"type": "None", "description": "No return value"},
        "scope": ["Vision Client"],
        "code_example": """# Set wait cursor globally
system.gui.setCursor("wait")

# Set hand cursor for button
system.gui.setCursor("hand", button_component)

# Set crosshair for drawing area
system.gui.setCursor("crosshair", drawing_panel)

# Reset to default
system.gui.setCursor("default")

# Context-sensitive cursors
def onMouseEnter(event):
    if event.source.enabled:
        system.gui.setCursor("hand", event.source)
    else:
        system.gui.setCursor("no", event.source)""",
        "common_patterns": [
            "User feedback",
            "Operation indication",
            "Interactive cues",
            "State visualization",
        ],
    },
    {
        "name": "system.gui.playSound",
        "category": "GUI Operations",
        "subcategory": "Audio Feedback",
        "description": "Play system sounds or audio files for user feedback",
        "parameters": [
            {
                "name": "soundName",
                "type": "String",
                "description": "Name of sound to play",
            },
            {
                "name": "volume",
                "type": "Float",
                "description": "Volume level (0.0 to 1.0)",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if sound played successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Play system beep
system.gui.playSound("beep")

# Play alarm sound
system.gui.playSound("alarm", 0.8)

# Play custom sound file
system.gui.playSound("sounds/notification.wav")

# Audio feedback for actions
def onButtonClick(event):
    if operation_successful:
        system.gui.playSound("success")
    else:
        system.gui.playSound("error")

# Volume control
system.gui.playSound("alert", 0.5)  # 50% volume""",
        "common_patterns": [
            "Audio feedback",
            "Alarm notifications",
            "User interaction sounds",
            "System alerts",
        ],
    },
    {
        "name": "system.gui.vibrate",
        "category": "GUI Operations",
        "subcategory": "Haptic Feedback",
        "description": "Trigger device vibration for haptic feedback",
        "parameters": [
            {
                "name": "duration",
                "type": "Integer",
                "description": "Vibration duration in milliseconds",
            },
            {
                "name": "intensity",
                "type": "Float",
                "description": "Vibration intensity (0.0 to 1.0)",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if vibration triggered successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Short vibration
system.gui.vibrate(100)

# Long vibration with intensity
system.gui.vibrate(500, 0.8)

# Vibration patterns for different events
def vibrateForAlarm(alarm_level):
    if alarm_level == "critical":
        system.gui.vibrate(1000, 1.0)
    elif alarm_level == "warning":
        system.gui.vibrate(300, 0.6)
    else:
        system.gui.vibrate(100, 0.3)

# Touch feedback
def onButtonPress(event):
    system.gui.vibrate(50, 0.4)  # Light haptic feedback""",
        "common_patterns": [
            "Haptic feedback",
            "Mobile device interaction",
            "Accessibility support",
            "Touch confirmation",
        ],
    },
    {
        "name": "system.gui.fullscreen",
        "category": "GUI Management",
        "subcategory": "Display Control",
        "description": "Enter or exit fullscreen mode for the Vision Client",
        "parameters": [
            {
                "name": "enable",
                "type": "Boolean",
                "description": "Whether to enable or disable fullscreen",
            },
            {
                "name": "screen",
                "type": "Integer",
                "description": "Screen index for fullscreen",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if fullscreen state changed successfully",
        },
        "scope": ["Vision Client"],
        "code_example": """# Enter fullscreen
system.gui.fullscreen(True)

# Exit fullscreen
system.gui.fullscreen(False)

# Fullscreen on specific monitor
system.gui.fullscreen(True, 1)  # Second monitor

# Toggle fullscreen
current_state = system.gui.isFullscreen()
system.gui.fullscreen(not current_state)

# Kiosk mode setup
def enterKioskMode():
    system.gui.fullscreen(True)
    system.gui.setCursor("none")  # Hide cursor""",
        "common_patterns": [
            "Kiosk applications",
            "Presentation mode",
            "Immersive interfaces",
            "Display optimization",
        ],
    },
]


def get_gui_system_functions() -> list[dict[str, Any]]:
    """Get all GUI system function definitions.

    Returns:
        List[Dict[str, Any]]: List of GUI system function definitions
    """
    return GUI_SYSTEM_FUNCTIONS


def get_function_by_name(function_name: str) -> Optional[dict[str, Any]]:
    """Get a specific GUI system function by name.

    Args:
        function_name (str): Name of the function to retrieve

    Returns:
        Optional[Dict[str, Any]]: Function definition if found, None otherwise
    """
    for func in GUI_SYSTEM_FUNCTIONS:
        if func["name"] == function_name:
            return func
    return None


def get_functions_by_category(category: str) -> list[dict[str, Any]]:
    """Get GUI system functions by category.

    Args:
        category (str): Category to filter by

    Returns:
        List[Dict[str, Any]]: List of functions in the category
    """
    return [func for func in GUI_SYSTEM_FUNCTIONS if func["category"] == category]


def get_functions_by_subcategory(subcategory: str) -> list[dict[str, Any]]:
    """Get GUI system functions by subcategory.

    Args:
        subcategory (str): Subcategory to filter by

    Returns:
        List[Dict[str, Any]]: List of functions in the subcategory
    """
    return [func for func in GUI_SYSTEM_FUNCTIONS if func["subcategory"] == subcategory]


if __name__ == "__main__":
    # Display function summary
    print("Task 3: GUI System Functions")
    print("=" * 50)
    print(f"Total Functions: {len(GUI_SYSTEM_FUNCTIONS)}")

    categories = {}
    for func in GUI_SYSTEM_FUNCTIONS:
        category = func["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(func["name"])

    for category, functions in categories.items():
        print(f"\n{category}:")
        for func_name in functions:
            print(f"  - {func_name}")
