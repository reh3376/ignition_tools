#!/usr/bin/env python3
"""Task 2: Database System Expansion Implementation.

===============================================

This module implements comprehensive database system functions for Ignition SCADA.
Provides enhanced database connection management, query execution, transactions,
and datasource operations.

Author: Assistant
Date: 2025-01-23
Task: 2/10 - Database System (HIGH Priority)
Functions: 17 comprehensive database functions
Complexity: ⭐⭐⭐⭐ (High)
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Task 2: Database System Functions
DATABASE_SYSTEM_FUNCTIONS = [
    {
        "name": "system.db.addDatasource",
        "category": "Database Management",
        "subcategory": "Datasource Configuration",
        "description": "Add a new database datasource connection to the gateway",
        "parameters": [
            {"name": "name", "type": "String", "description": "Name of the datasource"},
            {
                "name": "driverClassName",
                "type": "String",
                "description": "JDBC driver class name",
            },
            {
                "name": "connectUrl",
                "type": "String",
                "description": "Database connection URL",
            },
            {"name": "username", "type": "String", "description": "Database username"},
            {"name": "password", "type": "String", "description": "Database password"},
            {
                "name": "props",
                "type": "PyDictionary",
                "description": "Additional connection properties",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if datasource was successfully added",
        },
        "scope": ["Gateway"],
        "code_example": """# Add MySQL datasource
success = system.db.addDatasource(
    name="ProductionDB",
    driverClassName="com.mysql.cj.jdbc.Driver",
    connectUrl="jdbc:mysql://localhost:3306/production",
    username="ignition_user",
    password=os.getenv("DB_PASSWORD", "your_password_here"),
    props={"useSSL": "true", "serverTimezone": "UTC"}
)
print("Datasource added:", success)""",
        "common_patterns": [
            "Dynamic datasource creation",
            "Runtime database configuration",
            "Multi-environment database setup",
            "Database failover configuration",
        ],
    },
    {
        "name": "system.db.removeDatasource",
        "category": "Database Management",
        "subcategory": "Datasource Configuration",
        "description": "Remove an existing database datasource from the gateway",
        "parameters": [
            {
                "name": "name",
                "type": "String",
                "description": "Name of the datasource to remove",
            }
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if datasource was successfully removed",
        },
        "scope": ["Gateway"],
        "code_example": """# Remove datasource
success = system.db.removeDatasource("OldTestDB")
print("Datasource removed:", success)

# Conditional removal
if "TempDB" in system.db.getDatasourceNames():
    system.db.removeDatasource("TempDB")""",
        "common_patterns": [
            "Cleanup operations",
            "Dynamic configuration management",
            "Database maintenance",
            "Environment cleanup",
        ],
    },
    {
        "name": "system.db.setDatasourceConnectURL",
        "category": "Database Management",
        "subcategory": "Datasource Configuration",
        "description": "Update the connection URL for an existing datasource",
        "parameters": [
            {"name": "name", "type": "String", "description": "Name of the datasource"},
            {
                "name": "connectUrl",
                "type": "String",
                "description": "New database connection URL",
            },
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if URL was successfully updated",
        },
        "scope": ["Gateway"],
        "code_example": """# Update connection URL for failover
success = system.db.setDatasourceConnectURL(
    "ProductionDB",
    "jdbc:mysql://backup-server:3306/production"
)

# Environment-specific URL update
env = system.util.getSystemProperty("environment")
if env == "production":
    url = "jdbc:mysql://prod-server:3306/main"
else:
    url = "jdbc:mysql://dev-server:3306/main"

system.db.setDatasourceConnectURL("MainDB", url)""",
        "common_patterns": [
            "Database failover handling",
            "Environment-specific configuration",
            "Dynamic URL updates",
            "Connection string management",
        ],
    },
    {
        "name": "system.db.getDatasourceNames",
        "category": "Database Management",
        "subcategory": "Datasource Information",
        "description": "Get a list of all configured datasource names",
        "parameters": [],
        "returns": {"type": "list[String]", "description": "list of datasource names"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Get all datasources
datasources = system.db.getDatasourceNames()
print("Available datasources:", datasources)

# Check for specific datasource
if "ProductionDB" in datasources:
    # Perform database operations
    data = system.db.runQuery("SELECT * FROM orders", "ProductionDB")

# Iterate through all datasources
for ds_name in datasources:
    try:
        # Test connection
        system.db.runScalarQuery("SELECT 1", ds_name)
        print(f"Datasource {ds_name} is healthy")
    except:
        print(f"Datasource {ds_name} has issues")""",
        "common_patterns": [
            "Datasource validation",
            "Health checks",
            "Dynamic database selection",
            "Configuration verification",
        ],
    },
    {
        "name": "system.db.createConnection",
        "category": "Database Management",
        "subcategory": "Connection Management",
        "description": "Create a direct database connection with custom parameters",
        "parameters": [
            {"name": "jdbcUrl", "type": "String", "description": "JDBC connection URL"},
            {"name": "username", "type": "String", "description": "Database username"},
            {"name": "password", "type": "String", "description": "Database password"},
            {
                "name": "driverClassName",
                "type": "String",
                "description": "JDBC driver class name",
            },
            {
                "name": "props",
                "type": "PyDictionary",
                "description": "Additional connection properties",
                "optional": True,
            },
        ],
        "returns": {"type": "Connection", "description": "Database connection object"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Create direct connection
conn = system.db.createConnection(
    jdbcUrl="jdbc:postgresql://localhost:5432/analytics",
    username="analyst",
    password=os.getenv("ANALYTICS_DB_PASSWORD", "your_password_here"),
    driverClassName="org.postgresql.Driver",
    props={
        "ssl": "true",
        "sslmode": "require",
        "connectTimeout": "30"
    }
)

try:
    # Use connection for operations
    stmt = conn.createStatement()
    rs = stmt.executeQuery("SELECT COUNT(*) FROM transactions")
    # Process results
finally:
    # Always close connection
    system.db.closeConnection(conn)""",
        "common_patterns": [
            "External database access",
            "Temporary connections",
            "Ad-hoc database queries",
            "Connection pooling bypass",
        ],
    },
    {
        "name": "system.db.closeConnection",
        "category": "Database Management",
        "subcategory": "Connection Management",
        "description": "Close a database connection to free resources",
        "parameters": [
            {
                "name": "connection",
                "type": "Connection",
                "description": "Database connection to close",
            }
        ],
        "returns": {"type": "None", "description": "No return value"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Proper connection handling
conn = None
try:
    conn = system.db.createConnection(
        "jdbc:mysql://localhost:3306/temp",
        "user", "pass", "com.mysql.cj.jdbc.Driver"
    )
    # Perform database operations
    stmt = conn.createStatement()
    result = stmt.executeQuery("SELECT * FROM temp_data")

finally:
    # Always close in finally block
    if conn is not None:
        system.db.closeConnection(conn)

# Connection management pattern
def with_connection(jdbc_url, username, password, driver):
    def decorator(func):
        def wrapper(*args, **kwargs):
            conn = system.db.createConnection(jdbc_url, username, password, driver)
            try:
                return func(conn, *args, **kwargs)
            finally:
                system.db.closeConnection(conn)
        return wrapper
    return decorator""",
        "common_patterns": [
            "Resource cleanup",
            "Connection lifecycle management",
            "Memory leak prevention",
            "Exception-safe patterns",
        ],
    },
    {
        "name": "system.db.beginNamedQueryTransaction",
        "category": "Database Operations",
        "subcategory": "Transaction Management",
        "description": "Begin a named query transaction for atomic operations",
        "parameters": [
            {
                "name": "datasource",
                "type": "String",
                "description": "Name of the datasource",
            },
            {
                "name": "isolationLevel",
                "type": "Integer",
                "description": "Transaction isolation level",
                "optional": True,
            },
            {
                "name": "timeout",
                "type": "Integer",
                "description": "Transaction timeout in seconds",
                "optional": True,
            },
        ],
        "returns": {"type": "String", "description": "Transaction identifier"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Begin transaction for batch operations
tx_id = system.db.beginNamedQueryTransaction(
    datasource="ProductionDB",
    isolationLevel=2,  # READ_COMMITTED
    timeout=30
)

try:
    # Perform multiple related operations
    system.db.runNamedQuery("UpdateInventory", {"qty": 100, "item": "A123"}, tx_id)
    system.db.runNamedQuery("LogTransaction", {"action": "inventory_update"}, tx_id)
    system.db.runNamedQuery("UpdateAuditLog", {"user": "system"}, tx_id)

    # Commit all changes
    system.db.commitNamedQueryTransaction(tx_id)
    print("Transaction completed successfully")

except Exception as e:
    # Rollback on error
    system.db.rollbackNamedQueryTransaction(tx_id)
    print("Transaction rolled back:", str(e))""",
        "common_patterns": [
            "Atomic batch operations",
            "Data consistency maintenance",
            "Multi-step workflows",
            "Error handling with rollback",
        ],
    },
    {
        "name": "system.db.commitNamedQueryTransaction",
        "category": "Database Operations",
        "subcategory": "Transaction Management",
        "description": "Commit a named query transaction to make changes permanent",
        "parameters": [
            {
                "name": "transactionId",
                "type": "String",
                "description": "Transaction identifier to commit",
            }
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if transaction was successfully committed",
        },
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Complete transaction pattern
def transfer_inventory(from_location, to_location, item_id, quantity):
    tx_id = system.db.beginNamedQueryTransaction("InventoryDB")

    try:
        # Check source availability
        available = system.db.runNamedQuery(
            "CheckInventory",
            {"location": from_location, "item": item_id},
            tx_id
        )[0]["quantity"]

        if available < quantity:
            raise Exception("Insufficient inventory")

        # Perform transfer
        system.db.runNamedQuery("DeductInventory", {
            "location": from_location,
            "item": item_id,
            "qty": quantity
        }, tx_id)

        system.db.runNamedQuery("AddInventory", {
            "location": to_location,
            "item": item_id,
            "qty": quantity
        }, tx_id)

        # Commit transaction
        success = system.db.commitNamedQueryTransaction(tx_id)
        return success

    except Exception as e:
        system.db.rollbackNamedQueryTransaction(tx_id)
        raise e""",
        "common_patterns": [
            "Transaction completion",
            "Data integrity assurance",
            "Batch operation finalization",
            "Consistent state management",
        ],
    },
    {
        "name": "system.db.rollbackNamedQueryTransaction",
        "category": "Database Operations",
        "subcategory": "Transaction Management",
        "description": "Rollback a named query transaction to undo changes",
        "parameters": [
            {
                "name": "transactionId",
                "type": "String",
                "description": "Transaction identifier to rollback",
            }
        ],
        "returns": {
            "type": "Boolean",
            "description": "True if transaction was successfully rolled back",
        },
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Error handling with rollback
def process_batch_orders(orders):
    tx_id = system.db.beginNamedQueryTransaction("OrderDB")
    processed_count = 0

    try:
        for order in orders:
            # Validate order
            if not validate_order(order):
                raise Exception(f"Invalid order: {order['id']}")

            # Process order
            system.db.runNamedQuery("CreateOrder", order, tx_id)
            system.db.runNamedQuery("UpdateInventory", {
                "item": order["item_id"],
                "qty": -order["quantity"]
            }, tx_id)

            processed_count += 1

        # All orders processed successfully
        system.db.commitNamedQueryTransaction(tx_id)
        return {"success": True, "processed": processed_count}

    except Exception as e:
        # Rollback all changes on any error
        rollback_success = system.db.rollbackNamedQueryTransaction(tx_id)
        return {
            "success": False,
            "processed": 0,
            "error": str(e),
            "rollback_success": rollback_success
        }""",
        "common_patterns": [
            "Error recovery",
            "Data consistency maintenance",
            "Failed operation cleanup",
            "Atomic operation guarantee",
        ],
    },
    {
        "name": "system.db.runNamedQuery",
        "category": "Database Operations",
        "subcategory": "Query Execution",
        "description": "Execute a named query with parameters and optional transaction context",
        "parameters": [
            {
                "name": "queryName",
                "type": "String",
                "description": "Name of the configured named query",
            },
            {
                "name": "parameters",
                "type": "PyDictionary",
                "description": "Query parameters",
                "optional": True,
            },
            {
                "name": "transactionId",
                "type": "String",
                "description": "Transaction identifier",
                "optional": True,
            },
        ],
        "returns": {"type": "PyDataSet", "description": "Query results as dataset"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Execute named query with parameters
results = system.db.runNamedQuery(
    "GetProductsByCategory",
    {"category": "Electronics", "min_price": 100}
)

# Process results
for row in results:
    print(f"Product: {row['name']}, Price: ${row['price']}")

# Named query in transaction
tx_id = system.db.beginNamedQueryTransaction("ProductDB")
try:
    # Get current inventory
    inventory = system.db.runNamedQuery(
        "GetInventoryLevels",
        {"location": "Warehouse A"},
        tx_id
    )

    # Update based on results
    for item in inventory:
        if item["quantity"] < item["reorder_point"]:
            system.db.runNamedQuery("CreatePurchaseOrder", {
                "item_id": item["id"],
                "quantity": item["reorder_quantity"]
            }, tx_id)

    system.db.commitNamedQueryTransaction(tx_id)
except:
    system.db.rollbackNamedQueryTransaction(tx_id)""",
        "common_patterns": [
            "Parameterized queries",
            "Reusable query execution",
            "Transaction-aware queries",
            "Complex data retrieval",
        ],
    },
    {
        "name": "system.db.runNamedQueryUpdate",
        "category": "Database Operations",
        "subcategory": "Query Execution",
        "description": "Execute a named update query (INSERT/UPDATE/DELETE) with parameters",
        "parameters": [
            {
                "name": "queryName",
                "type": "String",
                "description": "Name of the configured named query",
            },
            {
                "name": "parameters",
                "type": "PyDictionary",
                "description": "Query parameters",
                "optional": True,
            },
            {
                "name": "transactionId",
                "type": "String",
                "description": "Transaction identifier",
                "optional": True,
            },
        ],
        "returns": {"type": "Integer", "description": "Number of affected rows"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Execute named update query
rows_affected = system.db.runNamedQueryUpdate(
    "UpdateProductPrice",
    {"product_id": "PROD-123", "new_price": 149.99}
)
print(f"Updated {rows_affected} rows")

# Batch update operations
def update_product_prices(price_updates):
    tx_id = system.db.beginNamedQueryTransaction("ProductDB")
    total_updated = 0

    try:
        for product_id, new_price in price_updates.items():
            updated = system.db.runNamedQueryUpdate(
                "UpdateProductPrice",
                {"product_id": product_id, "new_price": new_price},
                tx_id
            )
            total_updated += updated

        system.db.commitNamedQueryTransaction(tx_id)
        return total_updated

    except Exception as e:
        system.db.rollbackNamedQueryTransaction(tx_id)
        raise e

# Usage
updates = {"PROD-123": 149.99, "PROD-456": 89.99}
updated_count = update_product_prices(updates)""",
        "common_patterns": [
            "Data modification operations",
            "Batch updates",
            "Parameterized modifications",
            "Transaction-safe updates",
        ],
    },
    {
        "name": "system.db.runPrepQuery",
        "category": "Database Operations",
        "subcategory": "Prepared Statements",
        "description": "Execute a prepared query with enhanced parameter binding and caching",
        "parameters": [
            {
                "name": "query",
                "type": "String",
                "description": "SQL query with parameter placeholders",
            },
            {"name": "args", "type": "list", "description": "Query parameter values"},
            {
                "name": "database",
                "type": "String",
                "description": "Database name",
                "optional": True,
            },
            {
                "name": "cacheKey",
                "type": "String",
                "description": "Cache key for prepared statement",
                "optional": True,
            },
        ],
        "returns": {"type": "PyDataSet", "description": "Query results as dataset"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Enhanced prepared query with caching
results = system.db.runPrepQuery(
    "SELECT * FROM orders WHERE customer_id = ? AND order_date >= ?",
    [customer_id, start_date],
    database="OrderDB",
    cacheKey="orders_by_customer_date"
)

# Dynamic query building
def get_filtered_products(filters):
    conditions = []
    params = []

    if "category" in filters:
        conditions.append("category = ?")
        params.append(filters["category"])

    if "min_price" in filters:
        conditions.append("price >= ?")
        params.append(filters["min_price"])

    if "in_stock" in filters and filters["in_stock"]:
        conditions.append("stock_quantity > 0")

    query = "SELECT * FROM products"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    return system.db.runPrepQuery(query, params, "ProductDB")

# Usage
products = get_filtered_products({
    "category": "Electronics",
    "min_price": 50,
    "in_stock": True
})""",
        "common_patterns": [
            "Dynamic query construction",
            "Performance optimization",
            "SQL injection protection",
            "Cached prepared statements",
        ],
    },
    {
        "name": "system.db.runPrepUpdate",
        "category": "Database Operations",
        "subcategory": "Prepared Statements",
        "description": "Execute a prepared update statement with enhanced parameter binding",
        "parameters": [
            {
                "name": "query",
                "type": "String",
                "description": "SQL update query with parameter placeholders",
            },
            {"name": "args", "type": "list", "description": "Query parameter values"},
            {
                "name": "database",
                "type": "String",
                "description": "Database name",
                "optional": True,
            },
            {
                "name": "getKeys",
                "type": "Boolean",
                "description": "Return generated keys",
                "optional": True,
            },
        ],
        "returns": {
            "type": "Integer|PyDataSet",
            "description": "Affected rows count or generated keys",
        },
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Enhanced prepared update
rows_updated = system.db.runPrepUpdate(
    "UPDATE products SET price = ?, last_updated = ? WHERE category = ?",
    [new_price, system.date.now(), "Electronics"],
    database="ProductDB"
)

# Insert with generated key return
new_keys = system.db.runPrepUpdate(
    "INSERT INTO orders (customer_id, order_date, total) VALUES (?, ?, ?)",
    [customer_id, system.date.now(), total_amount],
    database="OrderDB",
    getKeys=True
)
new_order_id = new_keys[0]["GENERATED_KEYS"]

# Batch update with error handling
def batch_update_inventory(updates):
    success_count = 0
    errors = []

    for item_id, new_quantity in updates:
        try:
            affected = system.db.runPrepUpdate(
                "UPDATE inventory SET quantity = ?, last_updated = ? WHERE item_id = ?",
                [new_quantity, system.date.now(), item_id],
                "InventoryDB"
            )
            if affected > 0:
                success_count += 1
            else:
                errors.append(f"Item {item_id} not found")
        except Exception as e:
            errors.append(f"Error updating {item_id}: {str(e)}")

    return {"success_count": success_count, "errors": errors}""",
        "common_patterns": [
            "Batch data modifications",
            "Generated key retrieval",
            "Error-resistant updates",
            "Performance-optimized updates",
        ],
    },
    {
        "name": "system.db.runScalarQuery",
        "category": "Database Operations",
        "subcategory": "Scalar Queries",
        "description": "Execute a query that returns a single scalar value",
        "parameters": [
            {
                "name": "query",
                "type": "String",
                "description": "SQL query returning single value",
            },
            {
                "name": "database",
                "type": "String",
                "description": "Database name",
                "optional": True,
            },
        ],
        "returns": {"type": "Object", "description": "Single scalar result value"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Get single values efficiently
total_orders = system.db.runScalarQuery(
    "SELECT COUNT(*) FROM orders WHERE status = 'active'",
    "OrderDB"
)

# Get latest timestamp
last_update = system.db.runScalarQuery(
    "SELECT MAX(updated_at) FROM inventory",
    "InventoryDB"
)

# Health check queries
def database_health_check(databases):
    health_status = {}

    for db_name in databases:
        try:
            # Simple connectivity test
            result = system.db.runScalarQuery("SELECT 1", db_name)
            if result == 1:
                # Get record counts for validation
                table_counts = {}
                tables = ["orders", "products", "customers"]

                for table in tables:
                    try:
                        count = system.db.runScalarQuery(
                            f"SELECT COUNT(*) FROM {table}",
                            db_name
                        )
                        table_counts[table] = count
                    except:
                        table_counts[table] = "ERROR"

                health_status[db_name] = {
                    "status": "HEALTHY",
                    "table_counts": table_counts
                }
            else:
                health_status[db_name] = {"status": "UNHEALTHY"}

        except Exception as e:
            health_status[db_name] = {
                "status": "ERROR",
                "error": str(e)
            }

    return health_status""",
        "common_patterns": [
            "Aggregate calculations",
            "Existence checks",
            "Health monitoring",
            "Simple data retrieval",
        ],
    },
    {
        "name": "system.db.runScalarPrepQuery",
        "category": "Database Operations",
        "subcategory": "Scalar Queries",
        "description": "Execute a prepared query that returns a single scalar value with parameters",
        "parameters": [
            {
                "name": "query",
                "type": "String",
                "description": "SQL query with parameter placeholders",
            },
            {"name": "args", "type": "list", "description": "Query parameter values"},
            {
                "name": "database",
                "type": "String",
                "description": "Database name",
                "optional": True,
            },
        ],
        "returns": {"type": "Object", "description": "Single scalar result value"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Parameterized scalar queries
customer_order_count = system.db.runScalarPrepQuery(
    "SELECT COUNT(*) FROM orders WHERE customer_id = ? AND order_date >= ?",
    [customer_id, start_date],
    "OrderDB"
)

# Dynamic aggregation
def get_metric(metric_type, filters):
    if metric_type == "total_sales":
        query = "SELECT SUM(total_amount) FROM orders WHERE status = ?"
        args = ["completed"]
    elif metric_type == "avg_order_value":
        query = "SELECT AVG(total_amount) FROM orders WHERE customer_id = ?"
        args = [filters["customer_id"]]
    elif metric_type == "inventory_value":
        query = "SELECT SUM(quantity * unit_cost) FROM inventory WHERE location = ?"
        args = [filters["location"]]
    else:
        return None

    return system.db.runScalarPrepQuery(query, args, "MainDB")

# Usage examples
total_sales = get_metric("total_sales", {})
avg_value = get_metric("avg_order_value", {"customer_id": "CUST-123"})
inventory_val = get_metric("inventory_value", {"location": "Warehouse A"})

# Conditional logic based on scalar results
stock_level = system.db.runScalarPrepQuery(
    "SELECT quantity FROM inventory WHERE item_id = ?",
    ["ITEM-456"],
    "InventoryDB"
)

if stock_level < 10:
    # Trigger reorder
    system.db.runPrepUpdate(
        "INSERT INTO purchase_orders (item_id, quantity, status) VALUES (?, ?, ?)",
        ["ITEM-456", 100, "pending"],
        "InventoryDB"
    )""",
        "common_patterns": [
            "Conditional operations",
            "Metric calculations",
            "Parameterized aggregations",
            "Decision-making queries",
        ],
    },
    {
        "name": "system.db.refresh",
        "category": "Database Management",
        "subcategory": "Connection Management",
        "description": "Refresh database connections and clear connection pools",
        "parameters": [
            {
                "name": "datasource",
                "type": "String",
                "description": "Specific datasource to refresh",
                "optional": True,
            }
        ],
        "returns": {"type": "Boolean", "description": "True if refresh was successful"},
        "scope": ["Gateway"],
        "code_example": """# Refresh all database connections
success = system.db.refresh()
print("Database refresh successful:", success)

# Refresh specific datasource
system.db.refresh("ProductionDB")

# Database maintenance routine
def perform_database_maintenance():
    datasources = system.db.getDatasourceNames()
    maintenance_log = []

    for ds_name in datasources:
        try:
            # Test connection before refresh
            pre_test = system.db.runScalarQuery("SELECT 1", ds_name)

            # Refresh datasource
            refresh_success = system.db.refresh(ds_name)

            # Test connection after refresh
            post_test = system.db.runScalarQuery("SELECT 1", ds_name)

            maintenance_log.append({
                "datasource": ds_name,
                "pre_test": pre_test == 1,
                "refresh_success": refresh_success,
                "post_test": post_test == 1,
                "status": "SUCCESS" if refresh_success and post_test == 1 else "FAILED"
            })

        except Exception as e:
            maintenance_log.append({
                "datasource": ds_name,
                "status": "ERROR",
                "error": str(e)
            })

    return maintenance_log

# Scheduled maintenance
maintenance_results = perform_database_maintenance()""",
        "common_patterns": [
            "Connection pool maintenance",
            "Database health restoration",
            "Scheduled maintenance",
            "Connection troubleshooting",
        ],
    },
    {
        "name": "system.db.execSQLUpdate",
        "category": "Database Operations",
        "subcategory": "Direct SQL Execution",
        "description": "Execute direct SQL update statements with enhanced error handling",
        "parameters": [
            {
                "name": "query",
                "type": "String",
                "description": "SQL update/insert/delete statement",
            },
            {
                "name": "database",
                "type": "String",
                "description": "Database name",
                "optional": True,
            },
            {
                "name": "skipAudit",
                "type": "Boolean",
                "description": "Skip audit logging",
                "optional": True,
            },
        ],
        "returns": {"type": "Integer", "description": "Number of affected rows"},
        "scope": ["Gateway", "Vision Client", "Perspective Session"],
        "code_example": """# Direct SQL execution
rows_affected = system.db.execSQLUpdate(
    "UPDATE products SET discontinued = 1 WHERE category = 'Old Electronics'",
    "ProductDB"
)
print(f"Marked {rows_affected} products as discontinued")

# Batch SQL operations
def execute_maintenance_sql(database):
    maintenance_queries = [
        "DELETE FROM temp_data WHERE created_date < DATE_SUB(NOW(), INTERVAL 30 DAY)",
        "UPDATE statistics SET last_calculated = NOW() WHERE stat_type = 'daily'",
        "INSERT INTO audit_log (action, timestamp) VALUES ('maintenance_run', NOW())"
    ]

    results = []
    for query in maintenance_queries:
        try:
            affected = system.db.execSQLUpdate(query, database)
            results.append({
                "query": query[:50] + "...",
                "affected_rows": affected,
                "status": "SUCCESS"
            })
        except Exception as e:
            results.append({
                "query": query[:50] + "...",
                "error": str(e),
                "status": "FAILED"
            })

    return results

# Usage
maintenance_results = execute_maintenance_sql("MainDB")

# Conditional SQL execution
current_hour = system.date.getHour24(system.date.now())
if current_hour == 2:  # 2 AM maintenance window
    # Archive old records
    archived = system.db.execSQLUpdate(
        "INSERT INTO archive_orders SELECT * FROM orders WHERE order_date < DATE_SUB(NOW(), INTERVAL 1 YEAR)",
        "OrderDB"
    )

    # Delete archived records from main table
    deleted = system.db.execSQLUpdate(
        "DELETE FROM orders WHERE order_date < DATE_SUB(NOW(), INTERVAL 1 YEAR)",
        "OrderDB"
    )

    print(f"Archived {archived} orders, deleted {deleted} from main table")""",
        "common_patterns": [
            "Database maintenance",
            "Bulk data operations",
            "Schema modifications",
            "Administrative SQL tasks",
        ],
    },
]


def get_database_system_functions() -> list[dict[str, Any]]:
    """Get all database system function definitions.

    Returns:
        list[dict[str, Any]]: list of database system function definitions
    """
    return DATABASE_SYSTEM_FUNCTIONS


def get_function_by_name(function_name: str) -> dict[str, Any] | None:
    """Get a specific database system function by name.

    Args:
        function_name (str): Name of the function to retrieve

    Returns:
        dict[str, Any] | None: Function definition if found, None otherwise
    """
    for func in DATABASE_SYSTEM_FUNCTIONS:
        if func["name"] == function_name:
            return func
    return None


def get_functions_by_category(category: str) -> list[dict[str, Any]]:
    """Get database system functions by category.

    Args:
        category (str): Category to filter by

    Returns:
        list[dict[str, Any]]: list of functions in the category
    """
    return [func for func in DATABASE_SYSTEM_FUNCTIONS if func["category"] == category]


def get_functions_by_subcategory(subcategory: str) -> list[dict[str, Any]]:
    """Get database system functions by subcategory.

    Args:
        subcategory (str): Subcategory to filter by

    Returns:
        list[dict[str, Any]]: list of functions in the subcategory
    """
    return [func for func in DATABASE_SYSTEM_FUNCTIONS if func["subcategory"] == subcategory]


if __name__ == "__main__":
    # Display function summary
    print("Task 2: Database System Functions")
    print("=" * 50)
    print(f"Total Functions: {len(DATABASE_SYSTEM_FUNCTIONS)}")

    categories = {}
    for func in DATABASE_SYSTEM_FUNCTIONS:
        category = func["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append(func["name"])

    for category, functions in categories.items():
        print(f"\n{category}:")
        for func_name in functions:
            print(f"  - {func_name}")
