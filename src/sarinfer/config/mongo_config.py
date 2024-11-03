import os
from pymongo import MongoClient


class MongoDBConfig:
    """Handles MongoDB connection and settings with authentication support."""

    def __init__(self):
        self.mongo_uri = self._build_mongo_uri()
        self.db_name = os.getenv("MONGO_DB_NAME", "sarinfer_db")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]

    def _build_mongo_uri(self):
        """Builds the MongoDB URI, including authentication if provided."""
        username = os.getenv("MONGO_USER", None)
        password = os.getenv("MONGO_PASSWORD", None)
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27017")
        auth_db = os.getenv("MONGO_AUTH_DB", "admin")  # Default MongoDB authentication database is 'admin'

        if username and password:
            # Use authentication credentials
            mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/{auth_db}?authSource={auth_db}"
        else:
            # No authentication
            mongo_uri = f"mongodb://{host}:{port}/"

        return mongo_uri

    def get_collection(self, collection_name):
        """Returns a MongoDB collection."""
        return self.db[collection_name]
