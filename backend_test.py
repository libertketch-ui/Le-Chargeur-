#!/usr/bin/env python3
"""
BusConnect Cameroun - Comprehensive Backend API Testing
Tests all endpoints for the FlixBus-style bus booking system
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import time

class BusConnectAPITester:
    def __init__(self, base_url="https://ticketcam-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.user_id = None
        self.booking_reference = None

    def log_test(self, name, success, details="", response_data=None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def test_api_health(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else {}
            
            self.log_test(
                "API Health Check", 
                success,
                f"Status: {response.status_code}" if not success else "",
                data
            )
            return success, data
        except Exception as e:
            self.log_test("API Health Check", False, f"Connection error: {str(e)}")
            return False, {}

    def test_get_cities(self):
        """Test cities endpoint"""
        try:
            response = requests.get(f"{self.api_url}/cities", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                cities_count = len(data.get('cities', []))
                success = cities_count >= 100  # Should have 120+ cities
                details = f"Found {cities_count} cities" if success else f"Only {cities_count} cities found, expected 120+"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Get Cities", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Get Cities", False, f"Error: {str(e)}")
            return False, {}

    def test_search_routes(self):
        """Test route search functionality"""
        try:
            search_data = {
                "origin": "Yaoundé",
                "destination": "Douala", 
                "departure_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "passengers": 2
            }
            
            response = requests.post(f"{self.api_url}/search", json=search_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                routes_count = len(data.get('routes', []))
                success = routes_count > 0
                details = f"Found {routes_count} routes" if success else "No routes found"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Search Routes", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Search Routes", False, f"Error: {str(e)}")
            return False, {}

    def test_popular_routes(self):
        """Test popular routes endpoint"""
        try:
            response = requests.get(f"{self.api_url}/routes/popular", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                routes_count = len(data.get('popular_routes', []))
                success = routes_count > 0
                details = f"Found {routes_count} popular routes"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Popular Routes", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Popular Routes", False, f"Error: {str(e)}")
            return False, {}

    def test_create_user(self):
        """Test user creation"""
        try:
            user_data = {
                "email": f"test_{int(time.time())}@busconnect.cm",
                "phone": "+237123456789",
                "first_name": "Jean",
                "last_name": "Dupont",
                "user_type": "client"
            }
            
            response = requests.post(f"{self.api_url}/users", json=user_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.user_id = data.get('id')
                success = self.user_id is not None
                details = f"Created user with ID: {self.user_id}" if success else "No user ID returned"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Create User", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Create User", False, f"Error: {str(e)}")
            return False, {}

    def test_get_user(self):
        """Test get user by ID"""
        if not self.user_id:
            self.log_test("Get User", False, "No user ID available")
            return False, {}
        
        try:
            response = requests.get(f"{self.api_url}/users/{self.user_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get('id') == self.user_id
                details = "User retrieved successfully" if success else "User ID mismatch"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Get User", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Get User", False, f"Error: {str(e)}")
            return False, {}

    def test_baggage_options(self):
        """Test baggage options endpoint"""
        try:
            response = requests.get(f"{self.api_url}/baggage/options", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                options = data.get('baggage_options', [])
                expected_types = ['carry_on', 'checked', 'extra', 'bike', 'sports']
                found_types = [opt.get('type') for opt in options]
                success = all(t in found_types for t in expected_types)
                details = f"Found baggage types: {found_types}" if success else f"Missing types from: {expected_types}"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Baggage Options", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Baggage Options", False, f"Error: {str(e)}")
            return False, {}

    def test_offers(self):
        """Test offers endpoint"""
        try:
            response = requests.get(f"{self.api_url}/offers", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                offers_count = len(data.get('offers', []))
                success = offers_count > 0
                details = f"Found {offers_count} offers"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Get Offers", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Get Offers", False, f"Error: {str(e)}")
            return False, {}

    def test_promo_codes(self):
        """Test promo codes endpoint"""
        try:
            response = requests.get(f"{self.api_url}/promo-codes", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                promo_codes = data.get('promo_codes', [])
                expected_codes = ['BIENVENUE20', 'WEEKEND15', 'ETUDIANT10', 'FIDELITE']
                found_codes = [p.get('code') for p in promo_codes]
                success = all(code in found_codes for code in expected_codes)
                details = f"Found promo codes: {found_codes}"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Promo Codes", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Promo Codes", False, f"Error: {str(e)}")
            return False, {}

    def test_validate_promo(self):
        """Test promo code validation"""
        try:
            response = requests.post(f"{self.api_url}/validate-promo/WEEKEND15", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                success = data.get('valid') == True and data.get('discount_percent') == 15
                details = f"Promo validation: {data}" if success else "Invalid promo response"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Validate Promo Code", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Validate Promo Code", False, f"Error: {str(e)}")
            return False, {}

    def test_create_booking(self):
        """Test booking creation"""
        if not self.user_id:
            self.log_test("Create Booking", False, "No user ID available")
            return False, {}
        
        try:
            booking_data = {
                "user_id": self.user_id,
                "route_id": "test-route-123",
                "passenger_count": 2,
                "seat_numbers": ["1A", "1B"],
                "baggage": [
                    {"type": "extra", "quantity": 1, "price": 2500}
                ],
                "promo_code": "WEEKEND15",
                "carbon_offset": True
            }
            
            response = requests.post(f"{self.api_url}/bookings", json=booking_data, timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.booking_reference = data.get('booking_reference')
                success = self.booking_reference is not None
                details = f"Created booking: {self.booking_reference}" if success else "No booking reference returned"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Create Booking", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Create Booking", False, f"Error: {str(e)}")
            return False, {}

    def test_get_user_bookings(self):
        """Test get user bookings"""
        if not self.user_id:
            self.log_test("Get User Bookings", False, "No user ID available")
            return False, {}
        
        try:
            response = requests.get(f"{self.api_url}/bookings/user/{self.user_id}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                bookings = data.get('bookings', [])
                success = len(bookings) > 0
                details = f"Found {len(bookings)} bookings"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Get User Bookings", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Get User Bookings", False, f"Error: {str(e)}")
            return False, {}

    def test_track_booking(self):
        """Test booking tracking"""
        if not self.booking_reference:
            # Use a test reference
            test_reference = "BC123456"
        else:
            test_reference = self.booking_reference
        
        try:
            response = requests.get(f"{self.api_url}/track/{test_reference}", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['booking_reference', 'status', 'current_location', 'estimated_arrival']
                success = all(field in data for field in required_fields)
                details = f"Tracking data: {data.get('status')} at {data.get('current_location')}" if success else "Missing tracking fields"
            else:
                details = f"Status: {response.status_code}"
                data = {}
            
            self.log_test("Track Booking", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("Track Booking", False, f"Error: {str(e)}")
            return False, {}

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚌 BusConnect Cameroun - Backend API Testing")
        print("=" * 50)
        print(f"Testing API at: {self.api_url}")
        print()

        # Core API tests
        self.test_api_health()
        self.test_get_cities()
        self.test_search_routes()
        self.test_popular_routes()
        
        # User management tests
        self.test_create_user()
        self.test_get_user()
        
        # Booking system tests
        self.test_baggage_options()
        self.test_offers()
        self.test_promo_codes()
        self.test_validate_promo()
        self.test_create_booking()
        self.test_get_user_bookings()
        self.test_track_booking()

        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is fully functional.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = BusConnectAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": tester.tests_run,
        "passed_tests": tester.tests_passed,
        "success_rate": (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0,
        "test_details": tester.test_results
    }
    
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())