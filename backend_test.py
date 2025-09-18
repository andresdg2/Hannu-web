import requests
import sys
import json
from datetime import datetime

class HannuClothesAPITester:
    def __init__(self, base_url="https://style-showcase-27.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_username = "admin"
        self.admin_password = "admin123"

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

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_admin_login(self):
        """Test admin login and get token"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "admin/login",
            200,
            data={"username": self.admin_username, "password": self.admin_password}
        )
        if success and isinstance(response, dict) and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Token obtained successfully")
            return True
        else:
            print(f"   ❌ Failed to get token from response: {response}")
            return False

    def test_get_categories(self):
        """Test getting product categories"""
        return self.run_test("Get Categories", "GET", "categories", 200)

    def test_get_products(self):
        """Test getting all products"""
        return self.run_test("Get All Products", "GET", "products", 200)

    def test_get_products_by_category(self):
        """Test getting products by category"""
        categories = ["vestidos", "enterizos", "conjuntos", "blusas", "faldas", "pantalones"]
        for category in categories:
            success, _ = self.run_test(
                f"Get Products - {category.title()}",
                "GET",
                f"products?category={category}",
                200
            )
            if not success:
                return False
        return True

    def test_admin_profile(self):
        """Test getting admin profile (requires auth)"""
        if not self.token:
            print("❌ Skipping admin profile test - no token available")
            return False
        return self.run_test("Get Admin Profile", "GET", "admin/me", 200)

    def test_catalog_stats(self):
        """Test getting catalog statistics (requires auth)"""
        if not self.token:
            print("❌ Skipping catalog stats test - no token available")
            return False
        return self.run_test("Get Catalog Stats", "GET", "catalog/stats", 200)

    def test_search_products(self):
        """Test product search functionality"""
        return self.run_test(
            "Search Products",
            "GET",
            "catalog/search?query=vestido",
            200
        )

    def test_create_product_with_images_colors(self):
        """Test creating a new product with images and colors arrays (requires auth)"""
        if not self.token:
            print("❌ Skipping create product test - no token available")
            return False
        
        # Test the exact data format from the review request
        test_product = {
            "name": "Vestido de Prueba",
            "description": "Vestido para probar funcionalidad",
            "retail_price": 95000,
            "wholesale_price": 65000,
            "category": "vestidos",
            "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            "colors": ["Rojo", "Azul", "Verde"],
            "composition": "95% Algodón, 5% Elastano",
            "sizes": ["S", "M", "L"],
            "stock": {"S": 5, "M": 10, "L": 8}
        }
        
        success, response = self.run_test(
            "Create Product with Images/Colors Arrays",
            "POST",
            "products",
            200,
            data=test_product
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.test_product_id = response['id']
            print(f"   ✅ Product created with ID: {self.test_product_id}")
            
            # Verify the response contains the arrays
            if 'images' in response and 'colors' in response:
                print(f"   ✅ Response contains images array: {response['images']}")
                print(f"   ✅ Response contains colors array: {response['colors']}")
                
                # Check backward compatibility - should have 'image' field set to first image
                if 'image' in response and response['image'] == test_product['images'][0]:
                    print(f"   ✅ Backward compatibility maintained - image field set correctly")
                else:
                    print(f"   ⚠️  Backward compatibility issue - image field: {response.get('image')}")
                
                return True
            else:
                print(f"   ❌ Response missing images or colors arrays")
                return False
        return False

    def test_create_product_legacy_format(self):
        """Test creating product with legacy single image format"""
        if not self.token:
            print("❌ Skipping legacy product test - no token available")
            return False
        
        test_product = {
            "name": "Legacy Test Product",
            "description": "Testing backward compatibility",
            "retail_price": 80000,
            "wholesale_price": 56000,
            "category": "blusas",
            "image": "https://example.com/legacy-image.jpg",
            "composition": "100% Algodón",
            "sizes": ["S", "M"],
            "stock": {"S": 3, "M": 5}
        }
        
        success, response = self.run_test(
            "Create Product with Legacy Format",
            "POST",
            "products",
            200,
            data=test_product
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.legacy_product_id = response['id']
            print(f"   ✅ Legacy product created with ID: {self.legacy_product_id}")
            
            # Verify backward compatibility - should create images array from single image
            if 'images' in response and response['images'] == [test_product['image']]:
                print(f"   ✅ Legacy compatibility - images array created from single image")
                return True
            else:
                print(f"   ❌ Legacy compatibility issue - images array: {response.get('images')}")
                return False
        return False

    def test_data_validation(self):
        """Test data validation for arrays with empty strings"""
        if not self.token:
            print("❌ Skipping validation test - no token available")
            return False
        
        test_product = {
            "name": "Validation Test Product",
            "description": "Testing empty string filtering",
            "retail_price": 75000,
            "wholesale_price": 52500,
            "category": "faldas",
            "images": ["https://example.com/valid.jpg", "", "https://example.com/valid2.jpg", "   "],
            "colors": ["Azul", "", "Rojo", "   ", "Verde"],
            "composition": "90% Algodón, 10% Elastano",
            "sizes": ["M", "L"],
            "stock": {"M": 4, "L": 6}
        }
        
        success, response = self.run_test(
            "Create Product with Empty Strings in Arrays",
            "POST",
            "products",
            200,
            data=test_product
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            self.validation_product_id = response['id']
            print(f"   ✅ Validation product created with ID: {self.validation_product_id}")
            
            # Check that empty strings were filtered out
            expected_images = ["https://example.com/valid.jpg", "https://example.com/valid2.jpg"]
            expected_colors = ["Azul", "Rojo", "Verde"]
            
            if response.get('images') == expected_images:
                print(f"   ✅ Empty strings filtered from images array correctly")
            else:
                print(f"   ❌ Images filtering failed. Expected: {expected_images}, Got: {response.get('images')}")
                return False
                
            if response.get('colors') == expected_colors:
                print(f"   ✅ Empty strings filtered from colors array correctly")
            else:
                print(f"   ❌ Colors filtering failed. Expected: {expected_colors}, Got: {response.get('colors')}")
                return False
                
            return True
        return False

    def test_get_single_product(self):
        """Test getting a single product by ID"""
        if not hasattr(self, 'test_product_id'):
            print("❌ Skipping single product test - no test product ID available")
            return False
        
        return self.run_test(
            "Get Single Product",
            "GET",
            f"products/{self.test_product_id}",
            200
        )

    def test_update_product(self):
        """Test updating a product (requires auth)"""
        if not self.token or not hasattr(self, 'test_product_id'):
            print("❌ Skipping update product test - no token or product ID available")
            return False
        
        update_data = {
            "name": "Test Vestido API - Actualizado",
            "retail_price": 110000,
            "wholesale_price": 77000
        }
        
        return self.run_test(
            "Update Test Product",
            "PUT",
            f"products/{self.test_product_id}",
            200,
            data=update_data
        )

    def test_product_appears_in_catalog(self):
        """Test that created products appear in the catalog"""
        print("\n🔍 Verifying products appear in catalog after creation...")
        
        success, response = self.run_test(
            "Get All Products After Creation",
            "GET",
            "products",
            200
        )
        
        if not success:
            return False
            
        if not isinstance(response, list):
            print(f"   ❌ Expected list response, got: {type(response)}")
            return False
            
        print(f"   📊 Total products in catalog: {len(response)}")
        
        # Check if our test products are in the catalog
        test_products_found = []
        product_names = [p.get('name', '') for p in response]
        
        expected_products = [
            "Vestido de Prueba",
            "Legacy Test Product", 
            "Validation Test Product"
        ]
        
        for expected_name in expected_products:
            if expected_name in product_names:
                test_products_found.append(expected_name)
                print(f"   ✅ Found test product: {expected_name}")
            else:
                print(f"   ❌ Missing test product: {expected_name}")
        
        # Verify at least one product with images/colors arrays exists
        products_with_arrays = []
        for product in response:
            if product.get('images') and product.get('colors'):
                products_with_arrays.append(product['name'])
                print(f"   ✅ Product with arrays found: {product['name']}")
                print(f"      Images: {product['images']}")
                print(f"      Colors: {product['colors']}")
        
        if len(products_with_arrays) > 0:
            print(f"   ✅ {len(products_with_arrays)} products with images/colors arrays found in catalog")
            return True
        else:
            print(f"   ❌ No products with images/colors arrays found in catalog")
            return False

    def cleanup_test_products(self):
        """Clean up test products created during testing"""
        if not self.token:
            print("❌ Skipping cleanup - no token available")
            return
            
        print("\n🧹 Cleaning up test products...")
        
        # List of product IDs to clean up
        cleanup_ids = []
        if hasattr(self, 'test_product_id'):
            cleanup_ids.append(self.test_product_id)
        if hasattr(self, 'legacy_product_id'):
            cleanup_ids.append(self.legacy_product_id)
        if hasattr(self, 'validation_product_id'):
            cleanup_ids.append(self.validation_product_id)
            
        for product_id in cleanup_ids:
            try:
                success, _ = self.run_test(
                    f"Delete Test Product {product_id[:8]}...",
                    "DELETE",
                    f"products/{product_id}",
                    200
                )
                if success:
                    print(f"   ✅ Cleaned up product {product_id[:8]}...")
            except Exception as e:
                print(f"   ⚠️  Could not clean up product {product_id[:8]}...: {str(e)}")

    def test_create_product(self):
        """Legacy test method - redirects to new comprehensive tests"""
        return self.test_create_product_with_images_colors()

def main():
    print("🚀 Starting HANNU CLOTHES API Testing...")
    print("=" * 60)
    
    tester = HannuClothesAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Admin Login", tester.test_admin_login),
        ("Get Categories", tester.test_get_categories),
        ("Get All Products", tester.test_get_products),
        ("Get Products by Category", tester.test_get_products_by_category),
        ("Admin Profile", tester.test_admin_profile),
        ("Catalog Statistics", tester.test_catalog_stats),
        ("Search Products", tester.test_search_products),
        ("Create Product with Images/Colors", tester.test_create_product_with_images_colors),
        ("Create Product Legacy Format", tester.test_create_product_legacy_format),
        ("Data Validation Test", tester.test_data_validation),
        ("Get Single Product", tester.test_get_single_product),
        ("Update Product", tester.test_update_product),
        ("Product Appears in Catalog", tester.test_product_appears_in_catalog),
        ("Cleanup Test Products", tester.cleanup_test_products),
    ]
    
    print(f"\n📋 Running {len(tests)} test categories...")
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test category '{test_name}' failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"✅ Tests passed: {tester.tests_passed}")
    print(f"❌ Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"📈 Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())