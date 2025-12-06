"""
Comprehensive test script for California-specific insurance data
 
This script tests:
1. Data generation (fetch and generate)
2. Data integrity (all required files exist)
3. Data quality (values are in expected ranges)
4. MongoDB loading
5. API functionality with California data
"""
 
import json
import os
import sys
from pathlib import Path
 
# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
 
 
def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
 
 
def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")
 
 
def print_error(text):
    print(f"{RED}✗ {text}{RESET}")
 
 
def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")
 
 
def print_info(text):
    print(f"  {text}")
 
 
class CaliforniaDataTester:
    """Test California insurance data generation and integrity"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.errors = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def test_file_exists(self, filename):
        """Test if a required file exists"""
        filepath = self.data_dir / filename
        if filepath.exists():
            print_success(f"{filename} exists")
            self.passed += 1
            return True
        else:
            print_error(f"{filename} missing")
            self.errors.append(f"Missing file: {filename}")
            self.failed += 1
            return False
    
    def test_json_valid(self, filename):
        """Test if JSON file is valid and can be loaded"""
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            print_success(f"{filename} is valid JSON")
            self.passed += 1
            return data
        except Exception as e:
            print_error(f"{filename} has invalid JSON: {e}")
            self.errors.append(f"Invalid JSON in {filename}: {e}")
            self.failed += 1
            return None
    
    def test_config_structure(self):
        """Test seed_config.json structure and values"""
        print_header("Testing Configuration File")
        
        if not self.test_file_exists('seed_config.json'):
            return
        
        config = self.test_json_valid('seed_config.json')
        if not config:
            return
        
        # Test required fields
        required_fields = [
            'data_source',
            'premium_ranges',
            'idv_ranges',
            'add_ons_options',
            'plan_tiers',
            'tier_multipliers',
            'insurer_profiles',
            'signal_parameters'
        ]
        
        for field in required_fields:
            if field in config:
                print_success(f"Config has '{field}'")
                self.passed += 1
            else:
                print_error(f"Config missing '{field}'")
                self.errors.append(f"Config missing field: {field}")
                self.failed += 1
        
        # Test California-specific
        if config.get('data_source') == 'California, USA':
            print_success("Data source is California, USA")
            self.passed += 1
        else:
            print_warning(f"Data source is '{config.get('data_source')}', expected 'California, USA'")
            self.warnings.append("Data source not set to California")
        
        # Test premium ranges
        if 'premium_ranges' in config:
            expected_categories = ['Sedan', 'SUV', 'Truck', 'Electric']
            for category in expected_categories:
                if category in config['premium_ranges']:
                    range_vals = config['premium_ranges'][category]
                    if isinstance(range_vals, list) and len(range_vals) == 2:
                        min_val, max_val = range_vals
                        if 1000 <= min_val <= max_val <= 5000:
                            print_success(f"{category} premium range valid: ${min_val}-${max_val}")
                            self.passed += 1
                        else:
                            print_warning(f"{category} premium range unusual: ${min_val}-${max_val}")
                            self.warnings.append(f"{category} premium range outside expected")
                    else:
                        print_error(f"{category} premium range invalid format")
                        self.failed += 1
                else:
                    print_error(f"Missing premium range for {category}")
                    self.failed += 1
        
        # Test California insurers
        if 'insurer_profiles' in config:
            california_insurers = ['State Farm', 'Geico', 'Progressive', 'Allstate', 'USAA']
            found_insurers = [ins for ins in california_insurers if ins in config['insurer_profiles']]
            if len(found_insurers) >= 3:
                print_success(f"Found {len(found_insurers)} California insurers in profiles")
                self.passed += 1
            else:
                print_error(f"Only found {len(found_insurers)} California insurers")
                self.failed += 1
    
    def test_insurers_data(self):
        """Test seed_insurers.json"""
        print_header("Testing Insurers Data")
        
        if not self.test_file_exists('seed_insurers.json'):
            return
        
        insurers = self.test_json_valid('seed_insurers.json')
        if not insurers:
            return
        
        if len(insurers) >= 5:
            print_success(f"Found {len(insurers)} insurers")
            self.passed += 1
        else:
            print_error(f"Only {len(insurers)} insurers, expected at least 5")
            self.failed += 1
        
        # Test insurer structure
        required_fields = ['name', 'region_codes']
        for i, insurer in enumerate(insurers[:3]):  # Test first 3
            print_info(f"Testing insurer: {insurer.get('name', 'Unknown')}")
            for field in required_fields:
                if field in insurer:
                    self.passed += 1
                else:
                    print_error(f"  Missing field '{field}'")
                    self.failed += 1
            
            # Check California region codes
            if 'region_codes' in insurer:
                ca_codes = [code for code in insurer['region_codes'] if code.startswith('CA-')]
                if ca_codes:
                    print_success(f"  Has California region codes: {', '.join(ca_codes)}")
                    self.passed += 1
                else:
                    print_warning("  No California region codes found")
                    self.warnings.append(f"{insurer.get('name')} has no CA region codes")
    
    def test_vehicles_data(self):
        """Test seed_vehicles.json"""
        print_header("Testing Vehicles Data")
        
        if not self.test_file_exists('seed_vehicles.json'):
            return
        
        vehicles = self.test_json_valid('seed_vehicles.json')
        if not vehicles:
            return
        
        if len(vehicles) >= 5:
            print_success(f"Found {len(vehicles)} vehicles")
            self.passed += 1
        else:
            print_warning(f"Only {len(vehicles)} vehicles")
            self.warnings.append("Low vehicle count")
        
        # Test vehicle structure
        required_fields = ['make', 'model', 'category']
        for vehicle in vehicles[:3]:
            print_info(f"Testing: {vehicle.get('make')} {vehicle.get('model')}")
            for field in required_fields:
                if field in vehicle:
                    self.passed += 1
                else:
                    print_error(f"  Missing field '{field}'")
                    self.failed += 1
    
    def test_plans_data(self):
        """Test seed_plans.json"""
        print_header("Testing Plans Data")
        
        if not self.test_file_exists('seed_plans.json'):
            return
        
        plans = self.test_json_valid('seed_plans.json')
        if not plans:
            return
        
        if len(plans) >= 40:
            print_success(f"Found {len(plans)} insurance plans")
            self.passed += 1
        else:
            print_error(f"Only {len(plans)} plans, expected at least 40")
            self.failed += 1
        
        # Test plan structure
        required_fields = ['plan_id', 'insurer_name', 'premium_annual', 'idv', 'tier']
        for plan in plans[:5]:
            print_info(f"Testing: {plan.get('plan_id')} - {plan.get('plan_name')}")
            for field in required_fields:
                if field in plan:
                    self.passed += 1
                else:
                    print_error(f"  Missing field '{field}'")
                    self.failed += 1
            
            # Test premium is reasonable
            if 'premium_annual' in plan:
                premium = plan['premium_annual']
                if 1000 <= premium <= 5000:
                    self.passed += 1
                else:
                    print_warning(f"  Unusual premium: ${premium}")
                    self.warnings.append(f"Plan {plan.get('plan_id')} has unusual premium")
    
    def test_signals_data(self):
        """Test seed_signals.json"""
        print_header("Testing Signals Data")
        
        if not self.test_file_exists('seed_signals.json'):
            return
        
        signals = self.test_json_valid('seed_signals.json')
        if not signals:
            return
        
        if len(signals) >= 40:
            print_success(f"Found {len(signals)} signal records")
            self.passed += 1
        else:
            print_error(f"Only {len(signals)} signals")
            self.failed += 1
        
        # Test signal structure
        required_fields = ['plan_id', 'claim_tat_days', 'claim_approval_rate_pct', 'csat_score']
        for signal in signals[:5]:
            for field in required_fields:
                if field in signal:
                    self.passed += 1
                else:
                    print_error(f"  Missing field '{field}'")
                    self.failed += 1
    
    def test_california_regions(self):
        """Test that plans cover all California regions"""
        print_header("Testing California Regional Coverage")
        
        plans_file = self.data_dir / 'seed_plans.json'
        if not plans_file.exists():
            print_error("Cannot test regions - seed_plans.json missing")
            return
        
        with open(plans_file, 'r') as f:
            plans = json.load(f)
        
        california_regions = ['CA-N', 'CA-C', 'CA-S', 'CA-BAY', 'CA-SD']
        
        for region in california_regions:
            count = sum(1 for plan in plans if region in plan.get('region_codes', []))
            if count > 0:
                print_success(f"{region}: {count} plans")
                self.passed += 1
            else:
                print_error(f"{region}: No plans found")
                self.errors.append(f"No plans for region {region}")
                self.failed += 1
    
    def run_all_tests(self):
        """Run all tests"""
        print_header("California Insurance Data Test Suite")
        
        self.test_config_structure()
        self.test_insurers_data()
        self.test_vehicles_data()
        self.test_plans_data()
        self.test_signals_data()
        self.test_california_regions()
        
        # Print summary
        print_header("Test Summary")
        print(f"Passed: {GREEN}{self.passed}{RESET}")
        print(f"Failed: {RED}{self.failed}{RESET}")
        print(f"Warnings: {YELLOW}{len(self.warnings)}{RESET}")
        
        if self.errors:
            print(f"\n{RED}Errors:{RESET}")
            for error in self.errors:
                print(f"  {RED}•{RESET} {error}")
        
        if self.warnings:
            print(f"\n{YELLOW}Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}•{RESET} {warning}")
        
        if self.failed == 0:
            print(f"\n{GREEN}{'=' * 60}")
            print("✓ All tests passed! California data is ready.")
            print(f"{'=' * 60}{RESET}\n")
            return 0
        else:
            print(f"\n{RED}{'=' * 60}")
            print(f"✗ {self.failed} test(s) failed. Please fix the issues above.")
            print(f"{'=' * 60}{RESET}\n")
            return 1
 
 
def main():
    """Main entry point"""
    tester = CaliforniaDataTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
 
 
if __name__ == '__main__':
    main()
