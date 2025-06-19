"""Ignition Graph Database Client.

Handles connections to Neo4j and provides methods for querying
and updating the Ignition knowledge graph.
"""

import logging
import os
from contextlib import contextmanager
from typing import Any

from dotenv import load_dotenv
from neo4j.exceptions import AuthError, ServiceUnavailable

from neo4j import GraphDatabase

from .schema import GraphNode, GraphRelationship, IgnitionGraphSchema

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class IgnitionGraphClient:
    """Client for interacting with the Ignition knowledge graph database."""

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        """Initialize the graph database client.

        Args:
            uri: Neo4j connection URI (defaults to NEO4J_URI env var)
            username: Database username (defaults to NEO4J_USERNAME env var)
            password: Database password (defaults to NEO4J_PASSWORD env var)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "ignition-graph")
        self.driver = None
        self._connected = False

    def connect(self) -> bool:
        """Connect to the Neo4j database.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.username, self.password)
            )

            # Test the connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()

            self._connected = True
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
            return True

        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from the Neo4j database."""
        if self.driver:
            self.driver.close()
            self._connected = False
            logger.info("Disconnected from Neo4j")

    def is_connected(self) -> bool:
        """Check if connected to the database."""
        return self._connected and self.driver is not None

    @contextmanager
    def session(self):
        """Context manager for database sessions."""
        if not self.is_connected() and not self.connect():
            raise RuntimeError("Cannot connect to Neo4j database")

        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def execute_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results.

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            list of result records as dictionaries
        """
        if parameters is None:
            parameters = {}

        try:
            with self.session() as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise

    def execute_write_query(
        self, query: str, parameters: dict[str, Any] | None = None
    ) -> Any:
        """Execute a write query (CREATE, MERGE, etc.).

        Args:
            query: Cypher query string
            parameters: Query parameters

        Returns:
            Query result summary
        """
        if parameters is None:
            parameters = {}

        try:
            with self.session() as session:
                result = session.write_transaction(
                    lambda tx: tx.run(query, parameters).consume()
                )
                return result
        except Exception as e:
            logger.error(f"Write query execution failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise

    def create_node(self, node: GraphNode) -> bool:
        """Create a node in the graph.

        Args:
            node: GraphNode to create

        Returns:
            True if successful, False otherwise
        """
        try:
            query = node.to_cypher_merge()
            self.execute_write_query(query, node.properties)
            logger.debug(
                f"Created node: {node.node_type.value} - {node.properties.get('name', 'unknown')}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            return False

    def create_relationship(self, relationship: GraphRelationship) -> bool:
        """Create a relationship in the graph.

        Args:
            relationship: GraphRelationship to create

        Returns:
            True if successful, False otherwise
        """
        try:
            query = relationship.to_cypher_create()
            params = {
                "from_name": relationship.from_name,
                "to_name": relationship.to_name,
            }
            if relationship.properties:
                params.update(relationship.properties)

            self.execute_write_query(query, params)
            logger.debug(
                f"Created relationship: {relationship.from_name} "
                f"-[{relationship.relationship_type.value}]-> {relationship.to_name}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    def setup_schema(self) -> bool:
        """set up database constraints and indexes.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create constraints
            for constraint in IgnitionGraphSchema.get_constraints():
                try:
                    self.execute_write_query(constraint)
                    logger.debug(f"Created constraint: {constraint[:50]}...")
                except Exception as e:
                    # Constraint might already exist
                    logger.debug(f"Constraint creation skipped (might exist): {e}")

            # Create indexes
            for index in IgnitionGraphSchema.get_indexes():
                try:
                    self.execute_write_query(index)
                    logger.debug(f"Created index: {index[:50]}...")
                except Exception as e:
                    # Index might already exist
                    logger.debug(f"Index creation skipped (might exist): {e}")

            logger.info("Database schema setup completed")
            return True

        except Exception as e:
            logger.error(f"Schema setup failed: {e}")
            return False

    def clear_database(self) -> bool:
        """Clear all nodes and relationships from the database.

        ⚠️  WARNING: This will delete all data!

        Returns:
            True if successful, False otherwise
        """
        try:
            self.execute_write_query("MATCH (n) DETACH DELETE n")
            logger.warning("Database cleared - all data deleted!")
            return True
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return False

    def get_node_count(self) -> int:
        """Get total number of nodes in the database.

        Returns:
            Number of nodes
        """
        try:
            result = self.execute_query("MATCH (n) RETURN count(n) as total")
            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Failed to get node count: {e}")
            return 0

    def get_relationship_count(self) -> int:
        """Get total number of relationships in the database.

        Returns:
            Number of relationships
        """
        try:
            result = self.execute_query("MATCH ()-[r]->() RETURN count(r) as total")
            return result[0]["total"] if result else 0
        except Exception as e:
            logger.error(f"Failed to get relationship count: {e}")
            return 0

    def get_database_stats(self) -> dict[str, Any]:
        """Get comprehensive database statistics.

        Returns:
            Dictionary with database statistics
        """
        try:
            stats = {
                "total_nodes": self.get_node_count(),
                "total_relationships": self.get_relationship_count(),
                "node_types": {},
                "is_connected": self.is_connected(),
            }

            # Get node counts by type
            node_type_query = """
            MATCH (n)
            RETURN labels(n)[0] as node_type, count(n) as count
            ORDER BY count DESC
            """

            node_type_results = self.execute_query(node_type_query)
            for result in node_type_results:
                stats["node_types"][result["node_type"]] = result["count"]

            return stats

        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"error": str(e)}

    def health_check(self) -> dict[str, Any]:
        """Perform a health check on the database connection.

        Returns:
            Health check results
        """
        health = {
            "connected": False,
            "readable": False,
            "writable": False,
            "node_count": 0,
            "errors": [],
        }

        try:
            # Test connection
            if self.connect():
                health["connected"] = True

                # Test read
                try:
                    count = self.get_node_count()
                    health["readable"] = True
                    health["node_count"] = count
                except Exception as e:
                    health["errors"].append(f"Read test failed: {e}")

                # Test write (create and delete a temporary node)
                try:
                    test_query = "CREATE (test:HealthCheck {name: 'test', timestamp: timestamp()}) RETURN test"
                    self.execute_write_query(test_query)

                    cleanup_query = (
                        "MATCH (test:HealthCheck {name: 'test'}) DELETE test"
                    )
                    self.execute_write_query(cleanup_query)

                    health["writable"] = True
                except Exception as e:
                    health["errors"].append(f"Write test failed: {e}")

        except Exception as e:
            health["errors"].append(f"Connection failed: {e}")

        return health
