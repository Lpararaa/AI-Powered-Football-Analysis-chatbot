# app/neo4j_client.py
from neo4j import GraphDatabase
import os, time

NEO_URI = os.environ.get("NEO4J_URI")
NEO_USER = os.environ.get("NEO4J_USER")
NEO_PASS = os.environ.get("NEO4J_PASS")

class Neo4jClient:
    def __init__(self, uri=NEO_URI, auth=(NEO_USER, NEO_PASS)):
        self.uri = uri
        self.auth = auth
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)
        # cache for schema metadata
        self._labels = None
        self._rels = None
        self._prop_keys = None
        self._ts = 0
        self._ttl = 300

    def close(self):
        self.driver.close()

    def query(self, query, params=None, timeout_seconds=30):
        # runs query and returns list of dict rows
        with self.driver.session() as session:
            result = session.run(query, params or {})
            # convert to dicts
            rows = [record.data() for record in result]
            return rows

    # Schema helpers (cached)
    def _refresh_schema(self, force=False):
        if not force and self._labels and (time.time() - self._ts) < self._ttl:
            return
        with self.driver.session() as session:
            try:
                labels = [r["label"] for r in session.run("CALL db.labels()")]
            except Exception:
                labels = []
            try:
                rels = [r["relationshipType"] for r in session.run("CALL db.relationshipTypes()")]
            except Exception:
                rels = []
            try:
                prop_rows = session.run("CALL db.propertyKeys()")
                prop_keys = [r.value(0) for r in prop_rows]
            except Exception:
                prop_keys = []
        self._labels = set(labels)
        self._rels = set(rels)
        self._prop_keys = set(prop_keys)
        self._ts = time.time()

    def get_labels(self, refresh=False):
        self._refresh_schema(force=refresh)
        return list(self._labels or [])

    def get_rel_types(self, refresh=False):
        self._refresh_schema(force=refresh)
        return list(self._rels or [])

    def get_property_keys(self, refresh=False):
        self._refresh_schema(force=refresh)
        return list(self._prop_keys or [])

# single exported client instance
db = Neo4jClient()
