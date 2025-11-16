#!/usr/bin/env python3
"""
Load seed data into MongoDB database
Run this after generating seed data with generate_seed_data.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'flask_service'))

from database import get_db, init_db
from utils.data_loader import DataLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Load all seed data into MongoDB"""
    print("=" * 50)
    print("Loading Seed Data into MongoDB")
    print("=" * 50)
    
    # Initialize database
    try:
        db = init_db()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        print("\n❌ Error: Could not connect to MongoDB")
        print("Make sure MongoDB is running:")
        print("  - macOS: brew services start mongodb-community")
        print("  - Linux: sudo systemctl start mongod")
        print("  - Or use MongoDB Atlas cloud connection")
        return 1
    
    # Initialize data loader
    loader = DataLoader(db)
    
    # Data directory
    data_dir = Path(__file__).parent.parent / 'data'
    
    # Clear existing data (optional - uncomment if needed)
    # print("\nClearing existing data...")
    # loader.clear_collection('insurers')
    # loader.clear_collection('plans')
    # loader.clear_collection('signals')
    # loader.clear_collection('vehicles')
    
    try:
        # Load insurers
        print("\n1. Loading insurers...")
        insurer_ids = loader.load_from_json_file(
            str(data_dir / 'seed_insurers.json'),
            'insurers'
        )
        print(f"   ✓ Loaded {len(insurer_ids)} insurers")
        
        # Load vehicles
        print("\n2. Loading vehicles...")
        vehicle_ids = loader.load_from_json_file(
            str(data_dir / 'seed_vehicles.json'),
            'vehicles'
        )
        print(f"   ✓ Loaded {len(vehicle_ids)} vehicles")
        
        # Load plans (need to map insurer names to IDs)
        print("\n3. Loading insurance plans...")
        import json
        with open(data_dir / 'seed_plans.json', 'r') as f:
            plans_data = json.load(f)
        
        # Get insurer name to ID mapping
        insurers_collection = db.get_collection('insurers')
        insurer_map = {
            ins['name']: str(ins['_id']) 
            for ins in insurers_collection.find()
        }
        
        # Map insurer names to IDs in plans
        for plan in plans_data:
            insurer_name = plan.get('insurer_name')
            if insurer_name in insurer_map:
                plan['insurer_id'] = insurer_map[insurer_name]
            else:
                logger.warning(f"Insurer not found: {insurer_name}")
                plan['insurer_id'] = insurer_map.get('State Farm', '')  # Fallback
        
        plan_ids = loader.load_plans(plans_data)
        print(f"   ✓ Loaded {len(plan_ids)} insurance plans")
        
        # Load signals (need to map plan_id to actual _id)
        print("\n4. Loading service quality signals...")
        with open(data_dir / 'seed_signals.json', 'r') as f:
            signals_data = json.load(f)
        
        # Get plan_id to _id mapping
        plans_collection = db.get_collection('plans')
        plan_map = {
            plan.get('plan_id', str(plan['_id'])): str(plan['_id'])
            for plan in plans_collection.find()
        }
        
        # Map plan_ids
        for signal in signals_data:
            old_plan_id = signal.get('plan_id')
            if old_plan_id in plan_map:
                signal['plan_id'] = plan_map[old_plan_id]
        
        signal_ids = loader.load_signals(signals_data)
        print(f"   ✓ Loaded {len(signal_ids)} signal records")
        
        # Print summary
        print("\n" + "=" * 50)
        print("Data Loading Complete!")
        print("=" * 50)
        print(f"Insurers:  {len(insurer_ids)}")
        print(f"Vehicles:  {len(vehicle_ids)}")
        print(f"Plans:     {len(plan_ids)}")
        print(f"Signals:   {len(signal_ids)}")
        print("\nYou can now start the Flask and Django services.")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        print("\n❌ Error: Seed data files not found")
        print("Run this first: cd data && python3 generate_seed_data.py")
        return 1
        
    except Exception as e:
        logger.error(f"Error loading data: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

