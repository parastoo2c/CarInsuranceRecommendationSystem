"""
Generate realistic seed data for insurance plans and quality signals

This script creates synthetic insurance plans and service quality signals
calibrated to realistic industry benchmarks for California auto insurance.
"""

import json
import random
from datetime import datetime


def generate_plans(insurers, vehicles, num_plans_per_insurer=10):
    """Generate insurance plans for insurers and vehicle types"""
    plans = []
    plan_counter = 0
    
    # Premium ranges by vehicle category
    premium_ranges = {
        'Sedan': (1200, 2500),
        'SUV': (1500, 3000),
        'Truck': (1600, 3200),
        'Electric': (1800, 3500)
    }
    
    # IDV as percentage of typical vehicle value
    idv_ranges = {
        'Sedan': (20000, 35000),
        'SUV': (25000, 45000),
        'Truck': (30000, 50000),
        'Electric': (35000, 55000)
    }
    
    add_ons_options = [
        ['Zero Depreciation', 'Roadside Assistance'],
        ['Zero Depreciation', 'Engine Protection'],
        ['Roadside Assistance', 'Personal Accident Cover'],
        ['Zero Depreciation', 'Roadside Assistance', 'Engine Protection'],
        ['Personal Accident Cover', 'Roadside Assistance'],
        []  # Basic plan
    ]
    
    plan_tiers = ['Basic', 'Standard', 'Premium', 'Elite']
    
    for insurer in insurers:
        insurer_name = insurer['name']
        
        for _ in range(num_plans_per_insurer):
            # Random vehicle
            vehicle = random.choice(vehicles)
            vehicle_str = f"{vehicle['make']} {vehicle['model']} {vehicle.get('variant', '')}"
            category = vehicle['category']
            
            # Random tier
            tier = random.choice(plan_tiers)
            
            # Premium (varies by tier)
            base_premium = random.uniform(*premium_ranges[category])
            tier_multiplier = {'Basic': 0.85, 'Standard': 1.0, 'Premium': 1.15, 'Elite': 1.3}
            premium = base_premium * tier_multiplier[tier]
            
            # IDV
            idv = random.uniform(*idv_ranges[category])
            
            # Add-ons (more for higher tiers)
            if tier in ['Premium', 'Elite']:
                add_ons = random.choice(add_ons_options[:-1])  # Exclude basic
            else:
                add_ons = random.choice(add_ons_options)
            
            plan = {
                'plan_id': f'PLAN_{plan_counter:04d}',
                'insurer_name': insurer_name,
                'plan_name': f'{tier} {category} Coverage',
                'vehicle_types': [vehicle_str],
                'region_codes': random.sample(insurer['region_codes'], k=3),
                'premium_annual': round(premium, 2),
                'idv': round(idv, 2),
                'add_ons': add_ons,
                'tier': tier
            }
            
            plans.append(plan)
            plan_counter += 1
    
    return plans


def generate_signals(plans):
    """Generate service quality signals for each plan"""
    signals = []
    
    # Insurer performance profiles (based on market reputation)
    insurer_profiles = {
        'State Farm': {'service': 0.75, 'reliability': 0.80},
        'Geico': {'service': 0.65, 'reliability': 0.70},
        'Progressive': {'service': 0.70, 'reliability': 0.75},
        'Allstate': {'service': 0.72, 'reliability': 0.77},
        'USAA': {'service': 0.90, 'reliability': 0.95}  # Highest rated
    }
    
    for plan in plans:
        insurer_name = plan['insurer_name']
        profile = insurer_profiles.get(insurer_name, {'service': 0.70, 'reliability': 0.75})
        
        # Generate signals with some randomness around insurer's base profile
        
        # Claim TAT (days): 7-45 days, lower is better
        base_tat = 25
        service_factor = profile['service']
        claim_tat = int(base_tat * (1 - service_factor * 0.5) + random.uniform(-3, 3))
        claim_tat = max(7, min(45, claim_tat))  # Clamp
        
        # Claim approval rate: 60-98%
        base_approval = 78
        approval_rate = base_approval + (service_factor * 20) + random.uniform(-5, 5)
        approval_rate = max(60, min(98, approval_rate))
        
        # Customer satisfaction score: 50-100
        base_csat = 70
        csat_score = base_csat + (service_factor * 30) + random.uniform(-5, 5)
        csat_score = max(50, min(100, csat_score))
        
        # Renewal rate: 60-95%
        base_renewal = 75
        renewal_rate = base_renewal + (profile['reliability'] * 20) + random.uniform(-3, 3)
        renewal_rate = max(60, min(95, renewal_rate))
        
        # Complaint ratio: 0.1-1.5 (lower is better)
        base_complaint = 0.8
        complaint_ratio = base_complaint * (1 - profile['reliability']) + random.uniform(-0.1, 0.1)
        complaint_ratio = max(0.1, min(1.5, complaint_ratio))
        
        signal = {
            'plan_id': plan['plan_id'],
            'claim_tat_days': claim_tat,
            'claim_approval_rate_pct': round(approval_rate, 1),
            'csat_score': round(csat_score, 1),
            'renewal_rate_pct': round(renewal_rate, 1),
            'complaint_ratio': round(complaint_ratio, 2)
        }
        
        signals.append(signal)
    
    return signals


def main():
    """Generate and save seed data"""
    print("Generating seed data...")
    
    # Load insurers and vehicles
    with open('seed_insurers.json', 'r') as f:
        insurers = json.load(f)
    
    with open('seed_vehicles.json', 'r') as f:
        vehicles = json.load(f)
    
    # Generate plans
    print("Generating insurance plans...")
    plans = generate_plans(insurers, vehicles, num_plans_per_insurer=10)
    print(f"Generated {len(plans)} plans")
    
    # Generate signals
    print("Generating service quality signals...")
    signals = generate_signals(plans)
    print(f"Generated {len(signals)} signal records")
    
    # Save to files
    with open('seed_plans.json', 'w') as f:
        json.dump(plans, f, indent=2)
    print("Saved to seed_plans.json")
    
    with open('seed_signals.json', 'w') as f:
        json.dump(signals, f, indent=2)
    print("Saved to seed_signals.json")
    
    print("\nData generation complete!")
    print(f"Total insurers: {len(insurers)}")
    print(f"Total vehicles: {len(vehicles)}")
    print(f"Total plans: {len(plans)}")
    print(f"Total signals: {len(signals)}")


if __name__ == '__main__':
    main()

