import os
from neo4j import GraphDatabase

class Neo4jClient:
    """
    Neo4j Database Client for Account Linkage and Graph Operations.
    """
    def __init__(self, uri=None, user=None, password=None):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def add_transaction(self, tx_id, user_id, merchant_id, amount, timestamp):
        """
        Creates User and Merchant nodes and links them with a TRANSACTS_WITH edge.
        """
        query = (
            "MERGE (u:User {id: $user_id}) "
            "MERGE (m:Merchant {id: $merchant_id}) "
            "CREATE (u)-[r:TRANSACTS_WITH {tx_id: $tx_id, amount: $amount, timestamp: $timestamp}]->(m)"
        )
        with self.driver.session() as session:
            session.run(query, user_id=user_id, merchant_id=merchant_id, 
                        tx_id=tx_id, amount=amount, timestamp=timestamp)

    def get_user_network_risk(self, user_id):
        """
        Calculates a basic network risk score based on the number of flagged merchants
        a user has transacted with.
        """
        query = (
            "MATCH (u:User {id: $user_id})-[:TRANSACTS_WITH]->(m:Merchant) "
            "WHERE m.is_flagged = true "
            "RETURN count(m) AS flagged_connections"
        )
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            record = result.single()
            if record:
                return float(record["flagged_connections"])
            return 0.0
