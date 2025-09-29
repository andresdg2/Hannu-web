import requests
import sys
import json
from datetime import datetime

class FinalVerificationTester:
    def __init__(self, base_url="https://fashion-admin-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict) and len(str(response_data)) < 200:
                        print(f"   Response: {response_data}")
                    elif isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_manager_authentication(self):
        """Test manager/hannu2024 credentials"""
        print("\n🔐 TESTING MANAGER AUTHENTICATION (manager/hannu2024)")
        success, response = self.run_test(
            "Manager Login (manager/hannu2024)",
            "POST",
            "admin/login",
            200,
            data={"username": "manager", "password": "hannu2024"}
        )
        if success and isinstance(response, dict) and 'access_token' in response:
            self.manager_token = response['access_token']
            print(f"   ✅ Manager token obtained successfully")
            return True
        else:
            print(f"   ❌ Manager authentication failed: {response}")
            return False

    def test_admin_authentication(self):
        """Test admin/admin123 credentials"""
        print("\n🔐 TESTING ADMIN AUTHENTICATION (admin/admin123)")
        success, response = self.run_test(
            "Admin Login (admin/admin123)",
            "POST",
            "admin/login",
            200,
            data={"username": "admin", "password": "admin123"}
        )
        if success and isinstance(response, dict) and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Admin token obtained successfully")
            return True
        else:
            print(f"   ❌ Admin authentication failed: {response}")
            return False

    def test_total_products_116(self):
        """Test that all 116 products are available"""
        print("\n📊 TESTING TOTAL PRODUCTS COUNT (Expected: 116)")
        
        # Test with limit=1000 to get all products
        success, response = self.run_test(
            "Get All Products (limit=1000)",
            "GET",
            "products?limit=1000",
            200
        )
        
        if success and isinstance(response, list):
            total_products = len(response)
            print(f"   📈 Total products found: {total_products}")
            
            if total_products == 116:
                print(f"   ✅ PERFECT: Exactly 116 products as expected!")
                return True
            elif total_products > 116:
                print(f"   ✅ GOOD: {total_products} products found (more than expected 116)")
                return True
            else:
                print(f"   ⚠️  WARNING: Only {total_products} products found (expected 116)")
                return False
        else:
            print(f"   ❌ Failed to get products list")
            return False

    def test_products_by_creation_date(self):
        """Test that products are ordered by creation date (newest first)"""
        print("\n📅 TESTING PRODUCT ORDERING BY CREATION DATE")
        
        success, response = self.run_test(
            "Get Products (default limit)",
            "GET",
            "products",
            200
        )
        
        if success and isinstance(response, list) and len(response) > 1:
            print(f"   📋 Analyzing {len(response)} products for date ordering...")
            
            # Check if products are ordered by created_at descending (newest first)
            dates_in_order = True
            for i in range(len(response) - 1):
                current_date = response[i].get('created_at', '')
                next_date = response[i + 1].get('created_at', '')
                
                if current_date and next_date:
                    if current_date < next_date:  # Should be >= for descending order
                        dates_in_order = False
                        break
            
            if dates_in_order:
                print(f"   ✅ Products correctly ordered by creation date (newest first)")
                print(f"   📅 Newest product: {response[0].get('name', 'Unknown')} ({response[0].get('created_at', 'No date')})")
                if len(response) > 1:
                    print(f"   📅 Second product: {response[1].get('name', 'Unknown')} ({response[1].get('created_at', 'No date')})")
                return True
            else:
                print(f"   ❌ Products NOT properly ordered by creation date")
                return False
        else:
            print(f"   ❌ Failed to get products for date ordering test")
            return False

    def test_crud_operations_comprehensive(self):
        """Test complete CRUD operations with persistence verification"""
        if not self.token:
            print("❌ Skipping CRUD test - no admin token available")
            return False
            
        print("\n🔧 TESTING COMPREHENSIVE CRUD OPERATIONS")
        
        # 1. CREATE - Create a new product
        print("\n1️⃣ CREATE OPERATION:")
        test_product = {
            "name": "CRUD Test Product Final",
            "description": "Testing CRUD operations for final verification",
            "retail_price": 120000,
            "wholesale_price": 84000,
            "category": "vestidos",
            "images": ["https://example.com/crud-test1.jpg", "https://example.com/crud-test2.jpg"],
            "colors": ["Azul", "Rojo", "Verde"],
            "composition": "95% Algodón, 5% Elastano",
            "sizes": ["S", "M", "L"],
            "stock": {"S": 5, "M": 10, "L": 8}
        }
        
        success, response = self.run_test(
            "Create Test Product",
            "POST",
            "products",
            200,
            data=test_product
        )
        
        if not success or not isinstance(response, dict) or 'id' not in response:
            print("   ❌ CREATE operation failed")
            return False
            
        product_id = response['id']
        print(f"   ✅ Product created with ID: {product_id}")
        
        # 2. READ - Verify product exists and can be retrieved
        print("\n2️⃣ READ OPERATION:")
        success, response = self.run_test(
            "Get Created Product by ID",
            "GET",
            f"products/{product_id}",
            200
        )
        
        if not success or not isinstance(response, dict):
            print("   ❌ READ operation failed")
            return False
            
        print(f"   ✅ Product retrieved successfully: {response.get('name', 'Unknown')}")
        
        # 3. UPDATE - Edit the product
        print("\n3️⃣ UPDATE OPERATION:")
        update_data = {
            "name": "CRUD Test Product Final - UPDATED",
            "retail_price": 135000,
            "wholesale_price": 94500,
            "colors": ["Azul", "Rojo", "Verde", "Negro"]  # Added one more color
        }
        
        success, response = self.run_test(
            "Update Test Product",
            "PUT",
            f"products/{product_id}",
            200,
            data=update_data
        )
        
        if not success or not isinstance(response, dict):
            print("   ❌ UPDATE operation failed")
            return False
            
        print(f"   ✅ Product updated successfully")
        print(f"   📝 New name: {response.get('name', 'Unknown')}")
        print(f"   💰 New retail price: {response.get('retail_price', 'Unknown')}")
        print(f"   🎨 New colors: {response.get('colors', [])}")
        
        # 4. PERSISTENCE CHECK - Verify changes persist
        print("\n4️⃣ PERSISTENCE VERIFICATION:")
        success, response = self.run_test(
            "Verify Updated Product Persists",
            "GET",
            f"products/{product_id}",
            200
        )
        
        if not success or not isinstance(response, dict):
            print("   ❌ PERSISTENCE verification failed")
            return False
            
        # Check if updates persisted
        if (response.get('name') == "CRUD Test Product Final - UPDATED" and
            response.get('retail_price') == 135000 and
            len(response.get('colors', [])) == 4):
            print(f"   ✅ All changes persisted correctly")
        else:
            print(f"   ❌ Changes did not persist properly")
            return False
        
        # 5. DELETE - Remove the product
        print("\n5️⃣ DELETE OPERATION:")
        success, response = self.run_test(
            "Delete Test Product",
            "DELETE",
            f"products/{product_id}",
            200
        )
        
        if not success:
            print("   ❌ DELETE operation failed")
            return False
            
        print(f"   ✅ Product deleted successfully")
        
        # 6. VERIFY DELETION - Confirm product no longer exists
        print("\n6️⃣ DELETION VERIFICATION:")
        success, response = self.run_test(
            "Verify Product Deleted (should fail)",
            "GET",
            f"products/{product_id}",
            404  # Should return 404 Not Found
        )
        
        if success:
            print(f"   ✅ Product properly deleted - returns 404 as expected")
            return True
        else:
            print(f"   ❌ Product still exists after deletion")
            return False

    def test_price_integrity_final(self):
        """Final check for price integrity issues"""
        print("\n💰 FINAL PRICE INTEGRITY CHECK")
        
        success, response = self.run_test(
            "Get All Products for Price Check",
            "GET",
            "products?limit=1000",
            200
        )
        
        if not success or not isinstance(response, list):
            print("   ❌ Failed to get products for price check")
            return False
            
        print(f"   📊 Analyzing {len(response)} products for price issues...")
        
        invalid_products = []
        for product in response:
            name = product.get('name', 'Unknown')
            wholesale = product.get('wholesale_price', 0)
            retail = product.get('retail_price', 0)
            
            if wholesale <= 0 or wholesale >= retail:
                invalid_products.append({
                    'name': name,
                    'wholesale_price': wholesale,
                    'retail_price': retail
                })
        
        if len(invalid_products) == 0:
            print(f"   ✅ EXCELLENT: All products have valid pricing!")
            return True
        else:
            print(f"   ❌ CRITICAL: {len(invalid_products)} products have invalid pricing:")
            for product in invalid_products:
                print(f"      • {product['name']}: wholesale={product['wholesale_price']}, retail={product['retail_price']}")
            return False

def main():
    print("🎯 FINAL VERIFICATION TESTING - HANNU CLOTHES CATALOG")
    print("=" * 70)
    print("Testing requirements from review request:")
    print("1. Verify 116 products total")
    print("2. Test manager/hannu2024 and admin/admin123 authentication")
    print("3. Test complete CRUD operations with persistence")
    print("4. Verify limit=1000 returns all products")
    print("5. Verify sorting by creation date")
    print("=" * 70)
    
    tester = FinalVerificationTester()
    
    # Test sequence based on review requirements
    tests = [
        ("🔐 Manager Authentication (manager/hannu2024)", tester.test_manager_authentication),
        ("🔐 Admin Authentication (admin/admin123)", tester.test_admin_authentication),
        ("📊 Total Products Count (116 expected)", tester.test_total_products_116),
        ("📅 Product Ordering by Creation Date", tester.test_products_by_creation_date),
        ("🔧 Complete CRUD Operations", tester.test_crud_operations_comprehensive),
        ("💰 Final Price Integrity Check", tester.test_price_integrity_final),
    ]
    
    print(f"\n📋 Running {len(tests)} verification tests...")
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
            results[test_name] = False
    
    # Print final results
    print("\n" + "="*70)
    print("🎯 FINAL VERIFICATION RESULTS")
    print("="*70)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Tests passed: {passed_tests}")
    print(f"❌ Tests failed: {total_tests - passed_tests}")
    print(f"📈 Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL VERIFICATION TESTS PASSED!")
        print("🚀 CATALOG IS READY FOR CLIENT SHARING THIS WEEK!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} verification tests failed.")
        print("🔧 Issues must be resolved before sharing with clients.")
        return 1

if __name__ == "__main__":
    sys.exit(main())