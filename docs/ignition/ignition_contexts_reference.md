# Ignition Scripting Contexts Reference

**Target Version**: Ignition 8.1+
**Document Version**: 1.0
**Last Updated**: January 2025

## Overview

Ignition provides three primary scripting contexts that determine where and how scripts execute. Understanding these contexts is crucial for generating compatible Jython code.

## 🎯 **Core Scripting Contexts**

### 1. **Gateway Scope**
**Execution**: On the Ignition Gateway
**Availability**: Always active (regardless of client connections)
**Use Cases**: Server-side operations, data processing, scheduled tasks

**Key Characteristics**:
- ✅ Always running when Gateway is active
- ✅ Single execution instance (no duplicates)
- ✅ Access to all Gateway resources (databases, tags, devices)
- ❌ Cannot access client UI components
- ❌ Cannot use client-specific system functions

**Common Script Types**:
- Gateway Event Scripts (startup, shutdown, timer, tag change)
- Gateway Scheduled Scripts
- Gateway Message Handlers
- Tag Event Scripts (on individual tags)

### 2. **Vision Client Scope**
**Execution**: On the Vision Client computer
**Availability**: Only when Vision Client is running
**Use Cases**: UI interactions, client-side logic, user-specific operations

**Key Characteristics**:
- ✅ Full access to Vision UI components and windows
- ✅ Client-specific system functions (gui.*, nav.*)
- ✅ Multiple instances (one per client)
- ❌ Only runs when client is active
- ❌ Cannot access some Gateway-only functions

**Common Script Types**:
- Component Event Scripts (button clicks, property changes)
- Client Event Scripts (startup, shutdown, timer, keystroke)
- Window Event Scripts
- Client Message Handlers

### 3. **Perspective Session Scope**
**Execution**: On the Gateway (not in browser)
**Availability**: During active Perspective sessions
**Use Cases**: Perspective-specific operations, session management

**Key Characteristics**:
- ✅ Perspective-specific functionality
- ✅ Session state management
- ✅ Executes on Gateway but session-specific
- ❌ Different from pure Gateway scope
- ❌ Cannot access Vision-specific functions

**Common Script Types**:
- Perspective Component Scripts
- Perspective Session Event Scripts
- View Lifecycle Scripts

## 🔧 **System Functions by Scope**

### Gateway-Only Functions
**Database & Data Management**:
- `system.db.*` - Database operations
- `system.tag.*` - Tag operations (read/write/configure)
- `system.dataset.*` - Dataset manipulation

**Device & Communication**:
- `system.device.*` - Device management
- `system.opc.*` - OPC operations
- `system.opcua.*` - OPC-UA operations
- `system.dnp3.*` - DNP3 protocol operations

**System Management**:
- `system.util.audit()` - Audit logging
- `system.util.getLogger()` - Logger creation
- `system.security.*` - User management
- `system.file.*` - File operations

### Vision Client-Only Functions
**GUI Operations**:
- `system.gui.*` - Message boxes, dialogs, color chooser
- `system.nav.*` - Window navigation and management
- `system.print.*` - Printing operations

**Client-Specific**:
- `system.util.exit()` - Client shutdown
- `system.util.retarget()` - Gateway reconnection
- `system.vision.*` - Vision-specific operations

### Perspective Session Functions
**Session Management**:
- `system.perspective.*` - Session operations, navigation, popups
- Session-specific tag operations
- Mobile device interactions (`system.perspective.vibrateDevice()`)

### Universal Functions (All Scopes)
**Core Utilities**:
- `system.date.*` - Date/time operations
- `system.math.*` - Mathematical functions
- `system.util.*` - General utilities (most functions)
- `system.net.*` - Network operations
- `system.alarm.*` - Alarm operations

## 📝 **Script Event Types**

### Gateway Event Scripts

#### Startup Scripts
**Trigger**: Gateway/project startup
**Use Cases**: Initialize systems, start background processes
**Context Variables**: None
**Example Applications**:
- Initialize database connections
- Start scheduled maintenance tasks
- Load configuration data

#### Shutdown Scripts
**Trigger**: Gateway/project shutdown
**Use Cases**: Cleanup operations, save state
**Context Variables**: None
**Example Applications**:
- Clean up temporary files
- Close external connections
- Save runtime data

#### Timer Scripts
**Trigger**: Fixed delay or fixed rate intervals
**Use Cases**: Periodic maintenance, data collection
**Configuration**:
- `delay` (milliseconds)
- `delayType` (Fixed Delay vs Fixed Rate)
- `threading` (Shared vs Dedicated)

#### Tag Change Scripts
**Trigger**: Tag value/quality/timestamp changes
**Use Cases**: React to PLC signals, cascade logic
**Context Variables**:
- `initialChange` (boolean) - First subscription event
- `newValue` (QualifiedValue) - Current tag value
- `previousValue` (QualifiedValue) - Previous tag value
- `event` (TagChangeEvent) - Complete event object

#### Message Handlers
**Trigger**: `system.util.sendMessage()` calls
**Use Cases**: Inter-project communication, remote execution
**Context Variables**:
- `payload` (dict) - Message data

#### Scheduled Scripts (8.1.6+)
**Trigger**: Cron-based scheduling
**Use Cases**: Daily reports, maintenance windows
**Configuration**: Cron expressions for complex scheduling

### Vision Client Event Scripts

#### Client Startup/Shutdown Scripts
**Trigger**: Vision client login/logout
**Use Cases**: User-specific initialization, cleanup

#### Client Timer Scripts
**Trigger**: Client-side timers
**Use Cases**: UI updates, client-specific polling
**Note**: Multiple instances (one per client)

#### Keystroke Scripts
**Trigger**: Keyboard combinations
**Use Cases**: Shortcuts, accessibility features
**Configuration**: Key combinations, modifiers, actions

#### Client Tag Change Scripts
**Trigger**: Tag changes (including Client Tags)
**Use Cases**: UI updates based on tag changes

#### Menubar Scripts
**Trigger**: Menu item selection
**Use Cases**: Custom menu actions, navigation

### Component Event Scripts

#### Vision Component Events
- `actionPerformed` - Button clicks, user actions
- `propertyChange` - Property value changes
- `mouseClicked`, `mousePressed`, etc. - Mouse interactions
- `focusGained`, `focusLost` - Focus events
- `componentResized` - Size changes

#### Perspective Component Events
- Event-driven based on component interactions
- Session-scoped execution on Gateway

## ⚠️ **Common Pitfalls and Best Practices**

### Scope Awareness
**❌ Common Mistake**: Using `system.gui.messageBox()` in Gateway scripts
**✅ Correct Approach**: Use `system.util.getLogger()` for Gateway logging

### Performance Considerations
**❌ Avoid**: Long-running operations in shared timer threads
**✅ Use**: Dedicated threads for time-intensive operations

### Tag Change Scripts
**❌ Common Issue**: Not handling `initialChange` events
**✅ Best Practice**: Always check `initialChange` flag when needed

```python
# Proper tag change script pattern
if not initialChange:
    # Only execute on actual changes
    if newValue.value != previousValue.value:
        # Handle the change
        pass
```

### Error Handling
**✅ Best Practice**: Always include try/except blocks for external operations

```python
try:
    # Database operation or external call
    result = system.db.runQuery("SELECT * FROM table")
except Exception as e:
    # Log error appropriately for the scope
    logger = system.util.getLogger("ScriptName")
    logger.error("Database query failed: " + str(e))
```

## 🔗 **System Function Categories**

### Critical Functions by Category

#### Database Operations (Gateway/Perspective)
- `system.db.runQuery()` - Execute SELECT queries
- `system.db.runUpdateQuery()` - Execute INSERT/UPDATE/DELETE
- `system.db.runPrepQuery()` - Prepared statements
- `system.db.runNamedQuery()` - Named query execution

#### Tag Operations (All Scopes)
- `system.tag.readBlocking()` - Synchronous tag reads
- `system.tag.readAsync()` - Asynchronous tag reads
- `system.tag.writeBlocking()` - Synchronous tag writes
- `system.tag.writeAsync()` - Asynchronous tag writes

#### Navigation (Vision Client Only)
- `system.nav.openWindow()` - Open new windows
- `system.nav.closeWindow()` - Close windows
- `system.nav.swapWindow()` - Replace windows
- `system.nav.centerWindow()` - Center windows

#### User Interface (Vision Client Only)
- `system.gui.messageBox()` - Display messages
- `system.gui.confirm()` - Confirmation dialogs
- `system.gui.inputBox()` - User input
- `system.gui.errorBox()` - Error messages

#### Perspective Operations (Perspective Session)
- `system.perspective.navigate()` - Page navigation
- `system.perspective.openPopup()` - Open popups
- `system.perspective.sendMessage()` - Component messaging
- `system.perspective.print()` - Print operations

## 📋 **Template Generation Guidelines**

### Scope-Appropriate Code Generation
1. **Check target scope** before including system functions
2. **Validate function availability** for target Ignition version
3. **Include proper error handling** for scope-appropriate operations
4. **Use correct logging methods** for each scope

### Context Variable Usage
- Include **context variables** (newValue, event, payload) when applicable
- Provide **proper typing** and documentation in comments
- Handle **edge cases** (initialChange, null values, etc.)

### Jython 2.7 Compatibility
- Use **compatible syntax** (print statements, string formatting)
- **Avoid Python 3** specific features
- Include **proper imports** for Java classes when needed

---

**References**:
- [Ignition System Functions Documentation](https://docs.inductiveautomation.com/docs/8.1/appendix/scripting-functions)
- [Gateway Event Scripts](https://docs.inductiveautomation.com/docs/8.1/platform/scripting/scripting-in-ignition/gateway-event-scripts)
- [Client Event Scripts](https://docs.inductiveautomation.com/docs/8.1/ignition-modules/vision/scripting-in-vision/client-event-scripts)
