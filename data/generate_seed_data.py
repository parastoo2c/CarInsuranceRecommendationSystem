"""
Generate realistic seed data for insurance plans and quality signals
 
This script creates synthetic insurance plans and service quality signals
calibrated to realistic industry benchmarks for California auto insurance.
All configuration is loaded dynamically from seed_config.json.
"""
 
import json
import random
from datetime import datetime
 
 
def load_config(config_file='seed_config.json'):
    """Load configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)
 
 
def generate_plans(insurers, vehicles, config, num_plans_per_insurer=10):
    """Generate insurance plans for insurers and vehicle types"""
    plans = []
    plan_counter = 0
    
    # Load configuration from config object
    premium_ranges = config['premium_ranges']
    idv_ranges = config['idv_ranges']
    add_ons_options = config['add_ons_options']
    plan_tiers = config['plan_tiers']
    tier_multipliers = config['tier_multipliers']
    
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
            premium = base_premium * tier_multipliers[tier]
            
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
 
 
def generate_signals(plans, config):
    """Generate service quality signals for each plan"""
    signals = []
    
    # Load configuration
    insurer_profiles = config['insurer_profiles']
    default_profile = config['default_insurer_profile']
    signal_params = config['signal_parameters']
    
    for plan in plans:
        insurer_name = plan['insurer_name']
        profile = insurer_profiles.get(insurer_name, default_profile)
        
        # Generate signals with some randomness around insurer's base profile
        service_factor = profile['service']
        reliability_factor = profile['reliability']
        
        # Claim TAT (days): lower is better
        tat_config = signal_params['claim_tat']
        claim_tat = int(
            tat_config['base'] * (1 - service_factor * 0.5) + 
            random.uniform(-tat_config['variance'], tat_config['variance'])
        )
        claim_tat = max(tat_config['min'], min(tat_config['max'], claim_tat))
        
        # Claim approval rate
        approval_config = signal_params['claim_approval_rate']
        approval_rate = (
            approval_config['base'] + 
            (service_factor * 20) + 
            random.uniform(-approval_config['variance'], approval_config['variance'])
        )
        approval_rate = max(approval_config['min'], min(approval_config['max'], approval_rate))
        
        # Customer satisfaction score
        csat_config = signal_params['customer_satisfaction']
        csat_score = (
            csat_config['base'] + 
            (service_factor * 30) + 
            random.uniform(-csat_config['variance'], csat_config['variance'])
        )
        csat_score = max(csat_config['min'], min(csat_config['max'], csat_score))
        
        # Renewal rate
        renewal_config = signal_params['renewal_rate']
        renewal_rate = (
            renewal_config['base'] + 
            (reliability_factor * 20) + 
            random.uniform(-renewal_config['variance'], renewal_config['variance'])
        )
        renewal_rate = max(renewal_config['min'], min(renewal_config['max'], renewal_rate))
        
        # Complaint ratio: lower is better
        complaint_config = signal_params['complaint_ratio']
        complaint_ratio = (
            complaint_config['base'] * (1 - reliability_factor) + 
            random.uniform(-complaint_config['variance'], complaint_config['variance'])
        )
        complaint_ratio = max(complaint_config['min'], min(complaint_config['max'], complaint_ratio))
        
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
    
    # Load configuration
    print("Loading configuration...")
    config = load_config('seed_config.json')
    print("✓ Configuration loaded")
    
    # Load insurers and vehicles
    with open('seed_insurers.json', 'r') as f:
        insurers = json.load(f)
    
    with open('seed_vehicles.json', 'r') as f:
        vehicles = json.load(f)
    
    # Generate plans
    print("Generating insurance plans...")
    plans = generate_plans(insurers, vehicles, config, num_plans_per_insurer=10)
    print(f"✓ Generated {len(plans)} plans")
    
    # Generate signals
    print("Generating service quality signals...")
    signals = generate_signals(plans, config)
    print(f"✓ Generated {len(signals)} signal records")
    
    # Save to files
    with open('seed_plans.json', 'w') as f:
        json.dump(plans, f, indent=2)
    print("✓ Saved to seed_plans.json")
    
    with open('seed_signals.json', 'w') as f:
        json.dump(signals, f, indent=2)
    print("✓ Saved to seed_signals.json")
    
    print("\nData generation complete!")
    print(f"Total insurers: {len(insurers)}")
    print(f"Total vehicles: {len(vehicles)}")
    print(f"Total plans: {len(plans)}")
    print(f"Total signals: {len(signals)}")
 
 
if __name__ == '__main__':
    main()
 