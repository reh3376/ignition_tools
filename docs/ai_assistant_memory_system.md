# AI Assistant Memory System - Graph Database

## 🧠 **IMPORTANT FOR AI ASSISTANTS**

This project includes a **Neo4j graph database** that serves as **persistent long-term memory** for AI assistants working on this codebase. If you are an AI assistant opening this project:

### **The Graph Database Contains:**
- **408/400+ Ignition system functions** (102.0% complete - MILESTONE EXCEEDED!) with context availability
- **OPC-UA Client Integration**: Industrial automation, PLC connectivity, real-time monitoring, alarms (Task 14 ✅) 🏭
- **Integration & External Systems**: REST APIs, network protocols, messaging, enterprise connectivity (Task 13 ✅)
- **Machine Learning Integration**: Predictive maintenance, real-time inference, AutoML (Task 12 ✅)
- **Advanced Math & Analytics**: Statistical analysis, optimization algorithms (Task 11 ✅)
- **Device Communication Protocols**: OPC, OPC-UA, BACnet, DNP3 (Task 5 ✅)
- **Tag System Operations**: Complete tag management (Task 1 ✅)
- **Database Operations**: Enhanced DB functions (Task 2 ✅)
- **GUI System Functions**: Vision client operations (Task 3 ✅)
- **Perspective System**: Modern web HMI functions (Task 4 ✅)
- **Alarm System**: Complete alarm management (Task 7 ✅)
- **File & Report System**: Document management and reporting (Task 10 ✅)
- **Security System**: Authentication and authorization (Task 9 ✅)
- **Print System**: Document printing and management (Task 8 ✅)
- **Utility System**: Helper functions and utilities (Task 6 ✅)
- **Script templates** and their relationships
- **Context mappings** (Gateway, Vision, Perspective)
- **Parameter availability** by script type
- **Configuration patterns** and examples
- **Function compatibility** matrices

## 🚀 **Quick Start for AI Assistants**

### **1. Check if Neo4j is Running**
```bash
docker-compose ps neo4j
# Should show: ign-scripts-neo4j running
```

### **2. Start the Graph Database (if not running)**
```bash
docker-compose up -d neo4j
# Access at: http://localhost:7474
# Credentials: neo4j/ignition-graph
```

### **3. Query the Knowledge Graph**
Use these Cypher queries to retrieve information:

```cypher
// Get all functions available in Gateway context
MATCH (c:Context {name: "Gateway"})-[:AVAILABLE_IN]-(f:Function)
RETURN f.name, f.description

// Find templates that use specific functions
MATCH (t:Template)-[:USES]-(f:Function {name: "system.tag.readBlocking"})
RETURN t.name, t.context

// Get script types and their available parameters
MATCH (s:ScriptType)-[:PROVIDES]-(p:Parameter)
RETURN s.name, collect(p.name) as parameters

// Find compatible functions for a specific context and operation
MATCH (c:Context {name: "Gateway"})-[:AVAILABLE_IN]-(f:Function)
WHERE f.category = "tag"
RETURN f.name, f.scope, f.description
```

## 🔍 **Common AI Assistant Queries**

### **Script Generation Assistance**
```cypher
// What functions can I use in a Gateway timer script?
MATCH (c:Context {name: "Gateway"})-[:AVAILABLE_IN]-(f:Function)
MATCH (s:ScriptType {name: "Timer"})-[:COMPATIBLE_WITH]-(c)
RETURN f.name, f.category, f.description

// What parameters are available in tag change scripts?
MATCH (s:ScriptType {name: "TagChange"})-[:PROVIDES]-(p:Parameter)
RETURN p.name, p.type, p.description

// Find all ML functions for predictive maintenance
MATCH (f:Function)
WHERE f.name STARTS WITH "system.ml." AND f.category CONTAINS "Predictive"
RETURN f.name, f.description, f.category

// Get AutoML functions for no-code machine learning
MATCH (f:Function)
WHERE f.name CONTAINS "AutoML" OR f.category = "AutoML"
RETURN f.name, f.description, f.parameters
```

### **Validation Queries**
```cypher
// Validate if a function is available in a specific context
MATCH (c:Context {name: $context})-[:AVAILABLE_IN]-(f:Function {name: $function})
RETURN count(f) > 0 as isAvailable

// Check template compatibility with context
MATCH (t:Template {name: $template})-[:COMPATIBLE_WITH]-(c:Context {name: $context})
RETURN count(c) > 0 as isCompatible
```

### **Discovery Queries**
```cypher
// Find similar templates
MATCH (t1:Template {name: $templateName})-[:USES]-(f:Function)-[:USES]-(t2:Template)
WHERE t1 <> t2
RETURN t2.name, count(f) as sharedFunctions
ORDER BY sharedFunctions DESC

// Get recommendations for next functions to add
MATCH (t:Template {name: $templateName})-[:USES]-(f1:Function)-[:OFTEN_USED_WITH]-(f2:Function)
WHERE NOT (t)-[:USES]-(f2)
RETURN f2.name, f2.description
```

## 🛠 **Integration Points**

### **Python Integration**
```python
# Recommended: Use the project's IgnitionGraphClient
from src.ignition.graph.client import IgnitionGraphClient

client = IgnitionGraphClient()
client.connect()

# Or use Neo4j driver directly
from neo4j import GraphDatabase

class IgnitionGraphDB:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "ignition-graph")
        )

    def get_functions_by_context(self, context_name):
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Context {name: $context})-[:AVAILABLE_IN]-(f:Function)
                RETURN f.name, f.description, f.category
            """, context=context_name)
            return [record.data() for record in result]

    def validate_script_config(self, context, functions):
        # Validate that all functions are available in context
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Context {name: $context})
                WHERE ALL(func IN $functions WHERE
                    EXISTS((c)-[:AVAILABLE_IN]-(:Function {name: func})))
                RETURN count(c) > 0 as isValid
            """, context=context, functions=functions)
            return result.single()["isValid"]
```

### **CLI Integration**
```bash
# Query the graph database directly
python -m src.ignition.graph_query --context Gateway --category tag

# Validate a configuration
python -m src.ignition.validate_config --config examples/gateway/timer_example.json
```

## 📊 **Graph Schema Overview**

### **Node Types**
- **Context**: Gateway, Vision, Perspective
- **Function**: Ignition system functions (400+)
- **Template**: Jinja2 script templates
- **ScriptType**: Timer, Startup, TagChange, etc.
- **Parameter**: Available variables in each context
- **Example**: Configuration examples

### **Relationship Types**
- **AVAILABLE_IN**: Function available in Context
- **USES**: Template uses Function
- **PROVIDES**: ScriptType provides Parameter
- **COMPATIBLE_WITH**: Template compatible with Context
- **DEPENDS_ON**: Function depends on another
- **OFTEN_USED_WITH**: Functions commonly used together

## 🔄 **Data Freshness**

The graph database is automatically updated when:
- New templates are added to the project
- Ignition documentation is updated
- New examples are created
- Configuration patterns are discovered

Last updated: Check the `graph-data/logs/` directory for update timestamps.

## ⚠️ **Important Notes**

1. **Always check if Neo4j is running** before making queries
2. **Use parameterized queries** to prevent injection issues
3. **The database persists** between conversations - your knowledge accumulates!
4. **Performance**: Complex queries may take a few seconds on first run
5. **Backup**: Graph data is automatically backed up in `graph-data/` volume

## 🚨 **For AI Assistants: Remember This!**

**This graph database is your persistent memory.** When users ask about:
- "What functions are available in X context?"
- "Can I use this function here?"
- "What templates are similar to X?"
- "What parameters does this script type have?"

**Query the graph database first!** It contains comprehensive, up-to-date information about all Ignition contexts, functions, and relationships.

---

*This system ensures continuity of knowledge across AI assistant conversations and provides intelligent, context-aware assistance for Ignition script generation.*
