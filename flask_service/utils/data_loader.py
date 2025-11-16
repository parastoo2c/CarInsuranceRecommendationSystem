"""
Data loader utility for seeding database with initial insurance data
"""

import json
import logging
from datetime import datetime
from typing import List, Dict
from bson import ObjectId

logger = logging.getLogger(__name__)


class DataLoader:
    """Load seed data into MongoDB collections"""
    
    def __init__(self, db):
        self.db = db
    
    def load_insurers(self, insurers_data: List[Dict]) -> List[str]:
        """
        Load insurers into database
        
        Args:
            insurers_data: List of insurer dictionaries
        
        Returns:
            List of inserted insurer IDs
        """
        collection = self.db.get_collection('insurers')
        inserted_ids = []
        
        for insurer in insurers_data:
            # Check if already exists
            existing = collection.find_one({'name': insurer['name']})
            if existing:
                inserted_ids.append(str(existing['_id']))
                logger.info(f"Insurer already exists: {insurer['name']}")
                continue
            
            insurer['created_at'] = datetime.now()
            result = collection.insert_one(insurer)
            inserted_ids.append(str(result.inserted_id))
            logger.info(f"Inserted insurer: {insurer['name']}")
        
        return inserted_ids
    
    def load_plans(self, plans_data: List[Dict]) -> List[str]:
        """
        Load insurance plans into database
        
        Args:
            plans_data: List of plan dictionaries
        
        Returns:
            List of inserted plan IDs
        """
        collection = self.db.get_collection('plans')
        inserted_ids = []
        
        for plan in plans_data:
            plan['created_at'] = datetime.now()
            plan['updated_at'] = datetime.now()
            
            result = collection.insert_one(plan)
            inserted_ids.append(str(result.inserted_id))
            logger.info(f"Inserted plan: {plan.get('plan_name', 'Unknown')}")
        
        return inserted_ids
    
    def load_signals(self, signals_data: List[Dict]) -> List[str]:
        """
        Load service quality signals into database
        
        Args:
            signals_data: List of signal dictionaries
        
        Returns:
            List of inserted signal IDs
        """
        collection = self.db.get_collection('signals')
        inserted_ids = []
        
        for signal in signals_data:
            signal['created_at'] = datetime.now()
            signal['updated_at'] = datetime.now()
            
            result = collection.insert_one(signal)
            inserted_ids.append(str(result.inserted_id))
            logger.info(f"Inserted signals for plan: {signal.get('plan_id')}")
        
        return inserted_ids
    
    def load_vehicles(self, vehicles_data: List[Dict]) -> List[str]:
        """
        Load vehicle catalog into database
        
        Args:
            vehicles_data: List of vehicle dictionaries
        
        Returns:
            List of inserted vehicle IDs
        """
        collection = self.db.get_collection('vehicles')
        inserted_ids = []
        
        for vehicle in vehicles_data:
            # Check if already exists
            existing = collection.find_one({
                'make': vehicle['make'],
                'model': vehicle['model'],
                'variant': vehicle.get('variant')
            })
            if existing:
                inserted_ids.append(str(existing['_id']))
                continue
            
            vehicle['created_at'] = datetime.now()
            result = collection.insert_one(vehicle)
            inserted_ids.append(str(result.inserted_id))
            logger.info(f"Inserted vehicle: {vehicle['make']} {vehicle['model']}")
        
        return inserted_ids
    
    def load_from_json_file(self, filepath: str, collection_type: str):
        """
        Load data from JSON file
        
        Args:
            filepath: Path to JSON file
            collection_type: Type of collection ('insurers', 'plans', 'signals', 'vehicles')
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if collection_type == 'insurers':
                return self.load_insurers(data)
            elif collection_type == 'plans':
                return self.load_plans(data)
            elif collection_type == 'signals':
                return self.load_signals(data)
            elif collection_type == 'vehicles':
                return self.load_vehicles(data)
            else:
                raise ValueError(f"Unknown collection type: {collection_type}")
                
        except Exception as e:
            logger.error(f"Error loading from file {filepath}: {e}")
            raise
    
    def clear_collection(self, collection_name: str):
        """Clear all documents from a collection"""
        collection = self.db.get_collection(collection_name)
        result = collection.delete_many({})
        logger.info(f"Cleared {result.deleted_count} documents from {collection_name}")

