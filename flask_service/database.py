"""
Database connection and utility functions for MongoDB
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
from config import Config
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB Database Handler"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(
                Config.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[Config.MONGODB_DB_NAME]
            logger.info(f"Connected to MongoDB: {Config.MONGODB_DB_NAME}")
            self._create_indexes()
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Insurers collection
            self.db[Config.COLLECTION_INSURERS].create_index([
                ('name', ASCENDING)
            ], unique=True)
            
            # Plans collection
            self.db[Config.COLLECTION_PLANS].create_index([
                ('insurer_id', ASCENDING),
                ('region_code', ASCENDING)
            ])
            
            self.db[Config.COLLECTION_PLANS].create_index([
                ('vehicle_types', ASCENDING)
            ])
            
            # Signals collection
            self.db[Config.COLLECTION_SIGNALS].create_index([
                ('plan_id', ASCENDING)
            ])
            
            # Vehicles collection
            self.db[Config.COLLECTION_VEHICLES].create_index([
                ('make', ASCENDING),
                ('model', ASCENDING)
            ])
            
            # Query logs
            self.db[Config.COLLECTION_QUERY_LOGS].create_index([
                ('timestamp', DESCENDING)
            ])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    def get_collection(self, collection_name):
        """Get a MongoDB collection"""
        return self.db[collection_name]
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Global database instance
db_instance = None


def get_db():
    """Get database instance (singleton pattern)"""
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance


def init_db():
    """Initialize database with collections"""
    db = get_db()
    
    collections = [
        Config.COLLECTION_INSURERS,
        Config.COLLECTION_PLANS,
        Config.COLLECTION_SIGNALS,
        Config.COLLECTION_VEHICLES,
        Config.COLLECTION_QUERY_LOGS
    ]
    
    existing_collections = db.db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            db.db.create_collection(collection)
            logger.info(f"Created collection: {collection}")
        else:
            logger.info(f"Collection already exists: {collection}")
    
    return db

