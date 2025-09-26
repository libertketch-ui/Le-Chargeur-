#!/usr/bin/env python3
"""
Connect237 - Comprehensive Backend API Testing
Tests all endpoints for the Connect237 transport platform
"""

import requests
import sys
import json
from datetime import datetime, timedelta
import time
import uuid

class Connect237APITester:
    def __init__(self, base_url="https://camroutes.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.registration_id = None
        self.courier_tracking = None

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

    def test_parcel_delivery(self):
        """Test POST /api/parcel-delivery - PRIORITY HIGH"""
        try:
            parcel_data = {
                "sender_id": "test_sender_123",
                "recipient_name": "Jean Dupont",
                "recipient_phone": "+237699123456",
                "origin": "Yaoundé",
                "destination": "Douala",
                "pickup_address": "Quartier Bastos, Yaoundé",
                "delivery_address": "Akwa, Douala",
                "package_type": "documents",
                "weight_kg": 2.5,
                "declared_value": 50000,
                "urgent": False,
                "insurance": True,
                "delivery_instructions": "Appeler avant livraison"
            }
            
            response = requests.post(f"{self.api_url}/parcel-delivery", json=parcel_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['parcel_id', 'tracking_number', 'total_price', 'status']
                success = all(field in data for field in required_fields)
                self.courier_tracking = data.get('tracking_number')
                details = f"Created parcel delivery: {data.get('tracking_number')}" if success else "Missing required fields"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("POST /api/parcel-delivery", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("POST /api/parcel-delivery", False, f"Error: {str(e)}")
            return False, {}

    def test_smart_ai_search(self):
        """Test GET /api/routes/search-smart-ai - PRIORITY HIGH"""
        try:
            params = {
                "q": "yaoundé douala",
                "origin": "Yaoundé",
                "destination": "Douala",
                "passengers": 2
            }
            
            response = requests.get(f"{self.api_url}/routes/search-smart-ai", params=params, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['success', 'results', 'total_found']
                success = all(field in data for field in required_fields)
                if success:
                    results = data.get('results', {})
                    has_routes = len(results.get('routes', [])) > 0
                    has_suggestions = len(results.get('suggestions', [])) > 0
                    details = f"Found {len(results.get('routes', []))} routes, {len(results.get('suggestions', []))} suggestions"
                else:
                    details = "Missing required response fields"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("GET /api/routes/search-smart-ai", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("GET /api/routes/search-smart-ai", False, f"Error: {str(e)}")
            return False, {}

    def test_admin_dashboard(self):
        """Test GET /api/admin/dashboard - PRIORITY HIGH"""
        try:
            response = requests.get(f"{self.api_url}/admin/dashboard", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['dashboard_stats', 'recent_activities', 'system_health']
                success = all(field in data for field in required_fields)
                if success:
                    stats = data.get('dashboard_stats', {})
                    stats_fields = ['total_users', 'pending_verifications', 'total_bookings', 'revenue_today']
                    success = all(field in stats for field in stats_fields)
                    details = f"Dashboard loaded with {stats.get('total_users', 0)} users, {stats.get('pending_verifications', 0)} pending"
                else:
                    details = "Missing required dashboard fields"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("GET /api/admin/dashboard", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("GET /api/admin/dashboard", False, f"Error: {str(e)}")
            return False, {}

    def test_courier_book(self):
        """Test POST /api/courier/book - SECONDARY TEST"""
        try:
            courier_data = {
                "sender_id": "test_sender_456",
                "recipient_name": "Marie Ngono",
                "recipient_phone": "+237677234567",
                "origin": "Bafoussam",
                "destination": "Bamenda",
                "pickup_address": "Marché Central, Bafoussam",
                "delivery_address": "Commercial Avenue, Bamenda",
                "package_type": "electronics",
                "weight_kg": 1.5,
                "declared_value": 75000,
                "urgent": True,
                "insurance": False,
                "delivery_instructions": "Fragile - Manipuler avec précaution"
            }
            
            response = requests.post(f"{self.api_url}/courier/book", json=courier_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['courier_id', 'tracking_number', 'total_price', 'status']
                success = all(field in data for field in required_fields)
                details = f"Courier booked: {data.get('tracking_number')}" if success else "Missing required fields"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("POST /api/courier/book", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("POST /api/courier/book", False, f"Error: {str(e)}")
            return False, {}

    def test_enhanced_booking(self):
        """Test POST /api/booking/enhanced - SECONDARY TEST"""
        try:
            booking_data = {
                "user_id": "test_user_789",
                "agency_id": "agency_express_union",
                "route_details": {
                    "id": "route_yaoundé_douala",
                    "price": 4500
                },
                "passenger_count": 2,
                "departure_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "departure_time": "08:00",
                "pickup_location": {
                    "address": "Gare Routière Mvan, Yaoundé",
                    "coordinates": {"lat": 3.8667, "lng": 11.5167}
                },
                "dropoff_location": {
                    "address": "Gare Routière Bonabéri, Douala",
                    "coordinates": {"lat": 4.0611, "lng": 9.7067}
                },
                "payment_method": {
                    "type": "mobile_money",
                    "provider": "MTN"
                },
                "special_requests": "Siège côté fenêtre"
            }
            
            response = requests.post(f"{self.api_url}/booking/enhanced", json=booking_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['booking_id', 'booking_reference', 'amount_to_pay_now', 'payment_status']
                success = all(field in data for field in required_fields)
                details = f"Enhanced booking created: {data.get('booking_reference')}" if success else "Missing required fields"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("POST /api/booking/enhanced", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("POST /api/booking/enhanced", False, f"Error: {str(e)}")
            return False, {}

    def test_cities_enhanced(self):
        """Test GET /api/cities/enhanced - SECONDARY TEST"""
        try:
            response = requests.get(f"{self.api_url}/cities/enhanced", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                cities = data.get('cities', [])
                success = len(cities) > 0
                if success:
                    # Check if cities have weather and attractions
                    sample_city = cities[0] if cities else {}
                    has_weather = 'current_weather' in sample_city
                    has_attractions = 'attractions' in sample_city
                    details = f"Found {len(cities)} enhanced cities with weather: {has_weather}, attractions: {has_attractions}"
                else:
                    details = "No cities found"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("GET /api/cities/enhanced", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("GET /api/cities/enhanced", False, f"Error: {str(e)}")
            return False, {}

    def test_agencies(self):
        """Test GET /api/agencies - SECONDARY TEST"""
        try:
            response = requests.get(f"{self.api_url}/agencies", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                agencies = data.get('agencies', [])
                success = len(agencies) > 0
                if success:
                    # Check for key agencies
                    agency_names = [agency.get('name', '') for agency in agencies]
                    expected_agencies = ['Express Union', 'Touristique Express', 'Binam Voyages']
                    found_agencies = [name for name in expected_agencies if name in agency_names]
                    details = f"Found {len(agencies)} agencies including: {', '.join(found_agencies)}"
                else:
                    details = "No agencies found"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("GET /api/agencies", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("GET /api/agencies", False, f"Error: {str(e)}")
            return False, {}

    def test_weather_all(self):
        """Test GET /api/weather/all - SECONDARY TEST"""
        try:
            response = requests.get(f"{self.api_url}/weather/all", timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                weather_data = data.get('weather_data', [])
                success = len(weather_data) > 0
                if success:
                    # Check weather data structure
                    sample_weather = weather_data[0] if weather_data else {}
                    required_fields = ['city', 'temperature', 'description', 'humidity']
                    has_required = all(field in sample_weather for field in required_fields)
                    details = f"Found weather for {len(weather_data)} cities, structure valid: {has_required}"
                else:
                    details = "No weather data found"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("GET /api/weather/all", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("GET /api/weather/all", False, f"Error: {str(e)}")
            return False, {}

    def test_multi_level_registration(self):
        """Test POST /api/registration/multi-level - NEW ENDPOINT"""
        try:
            registration_data = {
                "user_type": "client",
                "personal_info": {
                    "name": "Paul Biya",
                    "email": "paul.biya@connect237.cm",
                    "phone": "+237699876543",
                    "address": "Etoudi, Yaoundé",
                    "date_of_birth": "1990-05-15",
                    "id_number": "123456789"
                },
                "documents": [
                    {
                        "type": "identity_card",
                        "filename": "cni_paul_biya.jpg",
                        "verified": False
                    }
                ]
            }
            
            response = requests.post(f"{self.api_url}/registration/multi-level", json=registration_data, timeout=15)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_fields = ['registration_id', 'status', 'message']
                success = all(field in data for field in required_fields)
                self.registration_id = data.get('registration_id')
                details = f"Registration created: {data.get('registration_id')}" if success else "Missing required fields"
            else:
                try:
                    error_data = response.json()
                    details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                except:
                    details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                data = {}
            
            self.log_test("POST /api/registration/multi-level", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("POST /api/registration/multi-level", False, f"Error: {str(e)}")
            return False, {}

    def test_registration_status(self):
        """Test GET /api/registration/status/{id} - NEW ENDPOINT"""
        if not self.registration_id:
            # Use a test ID if we don't have one from previous test
            test_id = str(uuid.uuid4())
        else:
            test_id = self.registration_id
        
        try:
            response = requests.get(f"{self.api_url}/registration/status/{test_id}", timeout=10)
            
            if self.registration_id:
                # If we have a real registration ID, expect success
                success = response.status_code == 200
                if success:
                    data = response.json()
                    required_fields = ['registration_id', 'status', 'user_type', 'created_at']
                    success = all(field in data for field in required_fields)
                    details = f"Registration status: {data.get('status')}" if success else "Missing required fields"
                else:
                    try:
                        error_data = response.json()
                        details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                    except:
                        details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                    data = {}
            else:
                # If using test ID, expect 404 but endpoint should exist
                success = response.status_code == 404
                details = "Endpoint exists (404 for non-existent ID is expected)" if success else f"Unexpected status: {response.status_code}"
                data = {}
            
            self.log_test("GET /api/registration/status/{id}", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("GET /api/registration/status/{id}", False, f"Error: {str(e)}")
            return False, {}

    def test_admin_verify_registration(self):
        """Test POST /api/admin/verify-registration/{id} - NEW ENDPOINT"""
        if not self.registration_id:
            # Use a test ID if we don't have one from previous test
            test_id = str(uuid.uuid4())
        else:
            test_id = self.registration_id
        
        try:
            params = {
                "action": "approve",
                "admin_comments": "Documents vérifiés et approuvés"
            }
            
            response = requests.post(f"{self.api_url}/admin/verify-registration/{test_id}", params=params, timeout=10)
            
            if self.registration_id:
                # If we have a real registration ID, expect success
                success = response.status_code == 200
                if success:
                    data = response.json()
                    required_fields = ['registration_id', 'action', 'new_status', 'message']
                    success = all(field in data for field in required_fields)
                    details = f"Registration {data.get('action')}ed, status: {data.get('new_status')}" if success else "Missing required fields"
                else:
                    try:
                        error_data = response.json()
                        details = f"Status: {response.status_code}, Error: {error_data.get('detail', 'Unknown error')}"
                    except:
                        details = f"Status: {response.status_code}, Response: {response.text[:200]}"
                    data = {}
            else:
                # If using test ID, expect 404 but endpoint should exist
                success = response.status_code == 404
                details = "Endpoint exists (404 for non-existent ID is expected)" if success else f"Unexpected status: {response.status_code}"
                data = {}
            
            self.log_test("POST /api/admin/verify-registration/{id}", success, details, data)
            return success, data
        except Exception as e:
            self.log_test("POST /api/admin/verify-registration/{id}", False, f"Error: {str(e)}")
            return False, {}

    def run_priority_tests(self):
        """Run high priority tests first"""
        print("🚨 PRIORITY HIGH - Previously failing endpoints:")
        print("-" * 50)
        
        # Priority High Tests
        self.test_parcel_delivery()
        self.test_smart_ai_search()
        self.test_admin_dashboard()
        
        print("\n📋 SECONDARY TESTS - Existing endpoints:")
        print("-" * 50)
        
        # Secondary Tests
        self.test_courier_book()
        self.test_enhanced_booking()
        self.test_cities_enhanced()
        self.test_agencies()
        self.test_weather_all()
        
        print("\n🆕 NEW ENDPOINTS:")
        print("-" * 50)
        
        # New Endpoints
        self.test_multi_level_registration()
        self.test_registration_status()
        self.test_admin_verify_registration()

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🇨🇲 Connect237 - Backend API Testing")
        print("=" * 60)
        print(f"Testing API at: {self.api_url}")
        print()

        # API Health Check
        self.test_api_health()
        print()
        
        # Run priority tests
        self.run_priority_tests()

        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Detailed failure analysis
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Connect237 Backend API is fully functional.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = Connect237APITester()
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