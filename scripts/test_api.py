#!/usr/bin/env python3
"""
Test the Flask recommendation API
"""

import requests
import json


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get('http://localhost:5000/health')
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_stats():
    """Test stats endpoint"""
    print("Testing stats endpoint...")
    response = requests.get('http://localhost:5000/api/stats')
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_recommend():
    """Test recommendation endpoint"""
    print("Testing recommendation endpoint...")
    
    payload = {
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_variant": "SE",
        "vehicle_year": 2022,
        "region_code": "90210",
        "city": "Beverly Hills",
        "top_n": 3,
        "weights": {
            "cost": 0.30,
            "coverage": 0.25,
            "service": 0.25,
            "reliability": 0.20
        }
    }
    
    response = requests.post(
        'http://localhost:5000/api/recommend',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Message: {data.get('message')}")
        print(f"\nRecommendations: {len(data.get('recommendations', []))}")
        
        for rec in data.get('recommendations', []):
            print(f"\n#{rec['rank']} - {rec['insurer_name']}")
            print(f"  Score: {rec['final_score']:.3f}")
            print(f"  Premium: ${rec['premium_annual']:.2f}")
            print(f"  Rationale: {rec['rationale']}")
    else:
        print(json.dumps(response.json(), indent=2))
    
    print()


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Testing Suite")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_stats()
        test_recommend()
        
        print("=" * 60)
        print("All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Flask service")
        print("Make sure it's running: cd flask_service && python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()

