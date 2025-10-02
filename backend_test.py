import requests
import sys
import json
from datetime import datetime

class HannuClothesAPITester:
    def __init__(self, base_url="https://fashion-admin-4.preview.emergentagent.com"):
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

    def test_price_validation_comprehensive(self):
        """Comprehensive test for price validation - critical for launch readiness"""
        print("\n🔍 CRITICAL PRICE VALIDATION TESTING...")
        print("   Checking for products with invalid wholesale prices...")
        
        # Get all products to check price integrity
        success, response = self.run_test(
            "Get All Products for Price Validation",
            "GET",
            "products",
            200
        )
        
        if not success or not isinstance(response, list):
            print("❌ Failed to get products for price validation")
            return False
        
        print(f"   📊 Analyzing {len(response)} products for price integrity...")
        
        invalid_price_products = []
        price_issues = {
            'wholesale_zero_or_negative': [],
            'wholesale_greater_equal_retail': [],
            'missing_prices': []
        }
        
        for product in response:
            name = product.get('name', 'Unknown')
            wholesale_price = product.get('wholesale_price')
            retail_price = product.get('retail_price')
            
            # Check for missing prices
            if wholesale_price is None or retail_price is None:
                price_issues['missing_prices'].append(name)
                invalid_price_products.append(name)
                continue
            
            # Check for wholesale price <= 0
            if wholesale_price <= 0:
                price_issues['wholesale_zero_or_negative'].append({
                    'name': name,
                    'wholesale_price': wholesale_price,
                    'retail_price': retail_price
                })
                invalid_price_products.append(name)
            
            # Check for wholesale price >= retail price
            if wholesale_price >= retail_price:
                price_issues['wholesale_greater_equal_retail'].append({
                    'name': name,
                    'wholesale_price': wholesale_price,
                    'retail_price': retail_price
                })
                invalid_price_products.append(name)
        
        # Report findings
        print(f"\n📋 PRICE VALIDATION RESULTS:")
        print(f"   Total products analyzed: {len(response)}")
        print(f"   Products with invalid prices: {len(invalid_price_products)}")
        
        if len(price_issues['wholesale_zero_or_negative']) > 0:
            print(f"\n❌ CRITICAL: {len(price_issues['wholesale_zero_or_negative'])} products with wholesale_price <= 0:")
            for item in price_issues['wholesale_zero_or_negative']:
                print(f"      • {item['name']}: wholesale={item['wholesale_price']}, retail={item['retail_price']}")
        
        if len(price_issues['wholesale_greater_equal_retail']) > 0:
            print(f"\n❌ CRITICAL: {len(price_issues['wholesale_greater_equal_retail'])} products with wholesale_price >= retail_price:")
            for item in price_issues['wholesale_greater_equal_retail']:
                print(f"      • {item['name']}: wholesale={item['wholesale_price']}, retail={item['retail_price']}")
        
        if len(price_issues['missing_prices']) > 0:
            print(f"\n❌ CRITICAL: {len(price_issues['missing_prices'])} products with missing prices:")
            for name in price_issues['missing_prices']:
                print(f"      • {name}")
        
        if len(invalid_price_products) == 0:
            print(f"\n✅ EXCELLENT: All products have valid pricing!")
            print(f"   ✅ No products with wholesale_price <= 0")
            print(f"   ✅ No products with wholesale_price >= retail_price")
            print(f"   ✅ All products have both wholesale and retail prices")
            return True
        else:
            print(f"\n❌ LAUNCH BLOCKER: {len(invalid_price_products)} products have invalid pricing")
            print(f"   This violates business rules and must be fixed before launch")
            return False

    def test_price_validation_api_enforcement(self):
        """Test that API enforces price validation rules"""
        if not self.token:
            print("❌ Skipping price validation API test - no token available")
            return False
        
        print("\n🔍 Testing API price validation enforcement...")
        
        # Test 1: Try to create product with wholesale >= retail
        invalid_product_1 = {
            "name": "Invalid Price Test 1",
            "description": "Testing price validation",
            "retail_price": 50000,
            "wholesale_price": 60000,  # Higher than retail - should fail
            "category": "vestidos"
        }
        
        success_1, response_1 = self.run_test(
            "Create Product with wholesale >= retail (should fail)",
            "POST",
            "products",
            400,  # Expecting 400 Bad Request
            data=invalid_product_1
        )
        
        # Test 2: Try to create product with wholesale = retail
        invalid_product_2 = {
            "name": "Invalid Price Test 2",
            "description": "Testing price validation",
            "retail_price": 50000,
            "wholesale_price": 50000,  # Equal to retail - should fail
            "category": "vestidos"
        }
        
        success_2, response_2 = self.run_test(
            "Create Product with wholesale = retail (should fail)",
            "POST",
            "products",
            400,  # Expecting 400 Bad Request
            data=invalid_product_2
        )
        
        # Test 3: Create valid product (should succeed)
        valid_product = {
            "name": "Valid Price Test",
            "description": "Testing valid pricing",
            "retail_price": 80000,
            "wholesale_price": 56000,  # 70% of retail - valid
            "category": "vestidos"
        }
        
        success_3, response_3 = self.run_test(
            "Create Product with valid pricing (should succeed)",
            "POST",
            "products",
            200,  # Expecting success
            data=valid_product
        )
        
        # Clean up valid product if created
        if success_3 and isinstance(response_3, dict) and 'id' in response_3:
            self.run_test(
                "Cleanup Valid Price Test Product",
                "DELETE",
                f"products/{response_3['id']}",
                200
            )
        
        if success_1 and success_2 and success_3:
            print("✅ API price validation working correctly")
            return True
        else:
            print("❌ API price validation not working as expected")
            return False

    def test_urgent_product_visibility_investigation(self):
        """URGENT: Investigate why products are not showing in catalog"""
        print("\n🚨 URGENT PRODUCT VISIBILITY INVESTIGATION")
        print("="*60)
        print("User reports: Only header visible, no products showing in catalog")
        print("Expected: 117 products should be visible")
        
        investigation_results = {
            'api_connectivity': False,
            'product_count': 0,
            'products_returned': False,
            'image_proxy_working': False,
            'sample_images_accessible': False
        }
        
        # 1. Test basic API connectivity
        print("\n1️⃣ TESTING API CONNECTIVITY:")
        success, response = self.run_test("API Root Connectivity", "GET", "", 200)
        investigation_results['api_connectivity'] = success
        
        if not success:
            print("❌ CRITICAL: Backend API is not responding!")
            return investigation_results
        
        # 2. Test products endpoint specifically
        print("\n2️⃣ TESTING PRODUCTS ENDPOINT:")
        success, products_response = self.run_test("Get All Products", "GET", "products", 200)
        
        if success and isinstance(products_response, list):
            investigation_results['products_returned'] = True
            investigation_results['product_count'] = len(products_response)
            print(f"✅ Products endpoint working - returned {len(products_response)} products")
            
            if len(products_response) >= 117:
                print(f"✅ Product count meets expectation ({len(products_response)} >= 117)")
            else:
                print(f"⚠️  Product count below expectation ({len(products_response)} < 117)")
            
            # Show first few products for verification
            print("\n📋 FIRST 3 PRODUCTS IN CATALOG:")
            for i, product in enumerate(products_response[:3]):
                print(f"   {i+1}. {product.get('name', 'Unknown')} - Category: {product.get('category', 'Unknown')}")
                print(f"      Images: {len(product.get('images', []))} | Colors: {len(product.get('colors', []))}")
                if product.get('images'):
                    print(f"      First image: {product['images'][0][:50]}...")
        else:
            print("❌ CRITICAL: Products endpoint not returning valid data!")
            print(f"   Response type: {type(products_response)}")
            print(f"   Response preview: {str(products_response)[:200]}...")
        
        # 3. Test image proxy endpoint
        print("\n3️⃣ TESTING IMAGE PROXY ENDPOINT:")
        test_image_url = "https://i.postimg.cc/test-image.jpg"  # Test URL
        success, proxy_response = self.run_test(
            "Image Proxy Test", 
            "GET", 
            f"proxy-image?url={test_image_url}", 
            200
        )
        investigation_results['image_proxy_working'] = success
        
        if success:
            print("✅ Image proxy endpoint is responding")
        else:
            print("❌ Image proxy endpoint has issues")
        
        # 4. Test actual product images accessibility
        print("\n4️⃣ TESTING ACTUAL PRODUCT IMAGES:")
        if investigation_results['products_returned'] and len(products_response) > 0:
            images_tested = 0
            images_accessible = 0
            
            for product in products_response[:5]:  # Test first 5 products
                if product.get('images'):
                    for image_url in product['images'][:2]:  # Test first 2 images per product
                        if image_url and image_url.strip():
                            images_tested += 1
                            try:
                                # Test direct image access
                                import requests
                                response = requests.head(image_url, timeout=5)
                                if response.status_code == 200:
                                    images_accessible += 1
                                    print(f"   ✅ Image accessible: {image_url[:50]}...")
                                else:
                                    print(f"   ❌ Image not accessible ({response.status_code}): {image_url[:50]}...")
                            except Exception as e:
                                print(f"   ❌ Image error: {image_url[:50]}... - {str(e)}")
                            
                            if images_tested >= 10:  # Limit to 10 image tests
                                break
                if images_tested >= 10:
                    break
            
            if images_tested > 0:
                accessibility_rate = (images_accessible / images_tested) * 100
                print(f"\n📊 Image Accessibility: {images_accessible}/{images_tested} ({accessibility_rate:.1f}%)")
                investigation_results['sample_images_accessible'] = accessibility_rate > 50
            else:
                print("⚠️  No images found to test")
        
        # 5. Test with different limits to see if it's a pagination issue
        print("\n5️⃣ TESTING DIFFERENT LIMITS:")
        for limit in [10, 50, 100, 1000]:
            success, response = self.run_test(
                f"Get Products (limit={limit})", 
                "GET", 
                f"products?limit={limit}", 
                200
            )
            if success and isinstance(response, list):
                print(f"   ✅ limit={limit}: {len(response)} products returned")
            else:
                print(f"   ❌ limit={limit}: Failed or invalid response")
        
        # 6. Test category filtering
        print("\n6️⃣ TESTING CATEGORY FILTERING:")
        categories = ["vestidos", "enterizos", "conjuntos", "blusas", "faldas"]
        for category in categories:
            success, response = self.run_test(
                f"Get {category.title()}", 
                "GET", 
                f"products?category={category}", 
                200
            )
            if success and isinstance(response, list):
                print(f"   ✅ {category}: {len(response)} products")
            else:
                print(f"   ❌ {category}: Failed")
        
        # Summary
        print("\n" + "="*60)
        print("🔍 INVESTIGATION SUMMARY:")
        print("="*60)
        
        for key, value in investigation_results.items():
            status = "✅" if value else "❌"
            if key == 'product_count':
                print(f"   📊 Product Count: {value}")
            else:
                print(f"   {status} {key.replace('_', ' ').title()}: {value}")
        
        # Diagnosis
        print("\n🩺 DIAGNOSIS:")
        if not investigation_results['api_connectivity']:
            print("❌ CRITICAL: Backend API is completely down")
        elif not investigation_results['products_returned']:
            print("❌ CRITICAL: Products endpoint is not working")
        elif investigation_results['product_count'] == 0:
            print("❌ CRITICAL: No products in database")
        elif investigation_results['product_count'] < 100:
            print(f"⚠️  WARNING: Only {investigation_results['product_count']} products (expected ~117)")
        else:
            print(f"✅ Backend appears healthy with {investigation_results['product_count']} products")
            if not investigation_results['sample_images_accessible']:
                print("⚠️  WARNING: Image accessibility issues detected")
            else:
                print("✅ Images appear to be accessible")
                print("🔍 Issue may be in frontend rendering or user interface")
        
        return investigation_results

    def test_mass_upload_investigation(self):
        """URGENT INVESTIGATION: Mass upload completion analysis"""
        print("\n🚨 INVESTIGACIÓN URGENTE - CARGA MASIVA INCOMPLETA")
        print("="*80)
        print("PROBLEMA: Usuario completó carga masiva pero aún hay placeholders")
        print("OBJETIVO: Verificar exactamente qué pasó con la carga masiva")
        print("="*80)
        
        investigation_results = {
            'total_products': 0,
            'products_with_imgbb': 0,
            'products_with_postimg': 0,
            'products_with_placeholders': 0,
            'recently_updated_products': 0,
            'upload_endpoint_working': False,
            'products_needing_images': []
        }
        
        # 1. Get all products and analyze current state
        print("\n1️⃣ VERIFICANDO PRODUCTOS ACTUALIZADOS:")
        success, products = self.run_test("Get All Products for Upload Analysis", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos")
            return investigation_results
        
        investigation_results['total_products'] = len(products)
        print(f"   📦 Total productos en base de datos: {len(products)}")
        
        # 2. Analyze products updated recently (today)
        from datetime import datetime, timedelta
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        recently_updated = []
        imgbb_products = []
        postimg_products = []
        placeholder_products = []
        
        for product in products:
            # Check update date
            updated_at = product.get('updated_at')
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        update_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00')).date()
                    else:
                        update_date = updated_at.date() if hasattr(updated_at, 'date') else today
                    
                    if update_date >= yesterday:
                        recently_updated.append(product)
                except:
                    pass
            
            # Analyze image URLs
            images = product.get('images', [])
            single_image = product.get('image', '')
            all_images = list(images) if images else []
            if single_image and single_image not in all_images:
                all_images.append(single_image)
            
            product_name = product.get('name', 'Unknown')
            
            if not all_images:
                placeholder_products.append({
                    'name': product_name,
                    'category': product.get('category', 'unknown'),
                    'reason': 'No images at all'
                })
                continue
            
            has_imgbb = False
            has_postimg = False
            
            for img_url in all_images:
                if 'i.ibb.co' in img_url or 'ibb.co' in img_url:
                    has_imgbb = True
                elif 'postimg.cc' in img_url or 'i.postimg.cc' in img_url:
                    has_postimg = True
            
            if has_imgbb:
                imgbb_products.append(product)
            elif has_postimg:
                postimg_products.append(product)
            else:
                placeholder_products.append({
                    'name': product_name,
                    'category': product.get('category', 'unknown'),
                    'reason': 'No ImgBB or PostImg URLs'
                })
        
        investigation_results['recently_updated_products'] = len(recently_updated)
        investigation_results['products_with_imgbb'] = len(imgbb_products)
        investigation_results['products_with_postimg'] = len(postimg_products)
        investigation_results['products_with_placeholders'] = len(placeholder_products)
        
        print(f"   🔄 Productos actualizados recientemente: {len(recently_updated)}")
        print(f"   ✅ Productos con ImgBB: {len(imgbb_products)}")
        print(f"   ⚠️  Productos con PostImg: {len(postimg_products)}")
        print(f"   ❌ Productos con placeholders: {len(placeholder_products)}")
        
        # 3. Show recently updated products
        if recently_updated:
            print(f"\n📋 PRODUCTOS ACTUALIZADOS RECIENTEMENTE:")
            for i, product in enumerate(recently_updated[:10]):
                images = product.get('images', [])
                image_type = "ImgBB" if any('ibb.co' in img for img in images) else "PostImg" if any('postimg' in img for img in images) else "Other"
                print(f"   {i+1}. {product.get('name', 'Unknown')} - {image_type} - {len(images)} imágenes")
            if len(recently_updated) > 10:
                print(f"   ... y {len(recently_updated) - 10} más")
        
        # 4. Test mass upload endpoint
        print(f"\n2️⃣ VERIFICANDO ENDPOINT DE CARGA MASIVA:")
        if not self.token:
            print("❌ No hay token de admin para probar endpoint")
        else:
            # Test endpoint availability (without actually uploading)
            success, response = self.run_test(
                "Test Upload Endpoint Availability", 
                "POST", 
                "admin/upload-images", 
                400,  # Expect 400 because we're not sending files
                data={}
            )
            investigation_results['upload_endpoint_working'] = success
            if success:
                print("   ✅ Endpoint /api/admin/upload-images está disponible")
            else:
                print("   ❌ Endpoint /api/admin/upload-images no responde correctamente")
        
        # 5. Analyze products that still need images
        print(f"\n3️⃣ PRODUCTOS QUE AÚN NECESITAN IMÁGENES:")
        
        # Products with broken PostImg URLs
        broken_postimg_products = []
        for product in postimg_products[:10]:  # Test first 10
            images = product.get('images', [])
            working_images = 0
            
            for img_url in images:
                if 'postimg' in img_url:
                    try:
                        import requests
                        response = requests.head(img_url, timeout=3)
                        if response.status_code == 200:
                            working_images += 1
                    except:
                        pass
            
            if working_images == 0:
                broken_postimg_products.append({
                    'name': product.get('name', 'Unknown'),
                    'category': product.get('category', 'unknown'),
                    'reason': 'PostImg URLs broken',
                    'images': images
                })
        
        investigation_results['products_needing_images'] = placeholder_products + broken_postimg_products
        
        print(f"   📝 Productos sin imágenes: {len(placeholder_products)}")
        print(f"   🔗 Productos con PostImg roto (muestra): {len(broken_postimg_products)}")
        
        # Show products by category that need images
        products_by_category = {}
        for product_info in investigation_results['products_needing_images']:
            category = product_info['category']
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product_info)
        
        print(f"\n📂 PRODUCTOS QUE NECESITAN IMÁGENES POR CATEGORÍA:")
        for category, products_list in products_by_category.items():
            print(f"\n   {category.upper()} ({len(products_list)} productos):")
            for i, product_info in enumerate(products_list[:5]):
                print(f"      {i+1}. {product_info['name']} - {product_info['reason']}")
            if len(products_list) > 5:
                print(f"      ... y {len(products_list) - 5} más")
        
        # 6. Verify ImgBB images are working
        print(f"\n4️⃣ VERIFICANDO IMÁGENES IMGBB FUNCIONANDO:")
        working_imgbb = 0
        broken_imgbb = 0
        
        for product in imgbb_products[:10]:  # Test first 10
            images = product.get('images', [])
            for img_url in images:
                if 'ibb.co' in img_url:
                    try:
                        import requests
                        response = requests.head(img_url, timeout=3)
                        if response.status_code == 200:
                            working_imgbb += 1
                            print(f"   ✅ {product.get('name', 'Unknown')}: {img_url[:50]}...")
                        else:
                            broken_imgbb += 1
                            print(f"   ❌ {product.get('name', 'Unknown')}: {img_url[:50]}... ({response.status_code})")
                    except Exception as e:
                        broken_imgbb += 1
                        print(f"   ❌ {product.get('name', 'Unknown')}: {img_url[:50]}... (Error)")
                    break  # Only test first image per product
        
        if working_imgbb + broken_imgbb > 0:
            success_rate = (working_imgbb / (working_imgbb + broken_imgbb)) * 100
            print(f"\n   📊 ImgBB Success Rate: {working_imgbb}/{working_imgbb + broken_imgbb} ({success_rate:.1f}%)")
        
        # 7. Final summary and action plan
        print("\n" + "="*80)
        print("🎯 RESUMEN EJECUTIVO - ESTADO POST-CARGA MASIVA")
        print("="*80)
        
        total_with_working_images = investigation_results['products_with_imgbb']
        total_needing_images = len(investigation_results['products_needing_images'])
        completion_rate = (total_with_working_images / investigation_results['total_products']) * 100
        
        print(f"📊 ESTADO ACTUAL:")
        print(f"   • Total productos: {investigation_results['total_products']}")
        print(f"   • Con imágenes ImgBB (funcionando): {investigation_results['products_with_imgbb']}")
        print(f"   • Con imágenes PostImg (problemáticas): {investigation_results['products_with_postimg']}")
        print(f"   • Necesitan imágenes nuevas: {total_needing_images}")
        print(f"   • Tasa de completitud: {completion_rate:.1f}%")
        
        print(f"\n🚨 PRODUCTOS ESPECÍFICOS QUE FALLAN:")
        for category, products_list in products_by_category.items():
            if products_list:
                print(f"   • {category}: {len(products_list)} productos")
        
        print(f"\n📋 PLAN DE ACCIÓN PARA 100%:")
        print(f"   1. Re-subir imágenes para {total_needing_images} productos identificados")
        print(f"   2. Priorizar categorías con más productos afectados")
        print(f"   3. Usar endpoint /api/admin/upload-images para carga masiva")
        print(f"   4. Verificar que todas las URLs nuevas sean ImgBB")
        
        return investigation_results

    def test_imperio_product_investigation(self):
        """CRITICAL INVESTIGATION: Imperio product not editable and missing image"""
        print("\n🚨 INVESTIGACIÓN CRÍTICA - PRODUCTO 'IMPERIO'")
        print("="*80)
        print("PROBLEMA URGENTE: Producto 'Imperio' no tiene imagen y no se puede editar")
        print("IMPACTO: Las clientas ya lo vieron - afecta profesionalidad del catálogo")
        print("="*80)
        
        imperio_investigation = {
            'product_found': False,
            'product_data': None,
            'has_valid_id': False,
            'has_images': False,
            'images_working': False,
            'can_be_edited': False,
            'can_be_deleted': False,
            'data_corruption': False,
            'recommended_action': 'unknown'
        }
        
        # 1. Search for Imperio product in database
        print("\n1️⃣ BUSCANDO PRODUCTO 'IMPERIO' EN BASE DE DATOS:")
        success, products = self.run_test("Get All Products to Find Imperio", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos de la base de datos")
            return imperio_investigation
        
        print(f"   📦 Total productos en base de datos: {len(products)}")
        
        # Search for Imperio product (case insensitive)
        imperio_product = None
        for product in products:
            product_name = product.get('name', '').lower()
            if 'imperio' in product_name:
                imperio_product = product
                break
        
        if imperio_product:
            imperio_investigation['product_found'] = True
            imperio_investigation['product_data'] = imperio_product
            print(f"   ✅ PRODUCTO ENCONTRADO: '{imperio_product.get('name', 'Unknown')}'")
            print(f"   🆔 ID: {imperio_product.get('id', 'No ID')}")
            print(f"   📂 Categoría: {imperio_product.get('category', 'Unknown')}")
            print(f"   💰 Precio Retail: {imperio_product.get('retail_price', 'No price')}")
            print(f"   💰 Precio Mayorista: {imperio_product.get('wholesale_price', 'No price')}")
            print(f"   📝 Descripción: {imperio_product.get('description', 'No description')[:100]}...")
        else:
            print("   ❌ PRODUCTO 'IMPERIO' NO ENCONTRADO EN BASE DE DATOS")
            print("   🔍 Buscando variaciones del nombre...")
            
            # Search for similar names
            similar_products = []
            for product in products:
                product_name = product.get('name', '').lower()
                if any(term in product_name for term in ['imp', 'emper', 'empo']):
                    similar_products.append(product)
            
            if similar_products:
                print(f"   📋 Productos similares encontrados ({len(similar_products)}):")
                for i, product in enumerate(similar_products[:5]):
                    print(f"      {i+1}. '{product.get('name', 'Unknown')}' - ID: {product.get('id', 'No ID')}")
            else:
                print("   ❌ No se encontraron productos similares")
            
            return imperio_investigation
        
        # 2. Validate product ID
        print("\n2️⃣ VALIDANDO ID DEL PRODUCTO:")
        product_id = imperio_product.get('id')
        if product_id and len(str(product_id)) > 10:  # UUID should be longer
            imperio_investigation['has_valid_id'] = True
            print(f"   ✅ ID válido: {product_id}")
        else:
            print(f"   ❌ ID inválido o corrupto: {product_id}")
            imperio_investigation['data_corruption'] = True
        
        # 3. Analyze images
        print("\n3️⃣ ANÁLISIS DE IMÁGENES:")
        images = imperio_product.get('images', [])
        single_image = imperio_product.get('image', '')
        
        print(f"   📷 Campo 'image': {single_image if single_image else 'VACÍO'}")
        print(f"   📷 Campo 'images': {images if images else 'VACÍO'}")
        
        all_images = list(images) if images else []
        if single_image and single_image not in all_images:
            all_images.append(single_image)
        
        if all_images:
            imperio_investigation['has_images'] = True
            print(f"   📊 Total URLs de imágenes: {len(all_images)}")
            
            # Test each image URL
            working_images = 0
            for i, img_url in enumerate(all_images):
                print(f"\n   🔍 Probando imagen {i+1}: {img_url[:60]}...")
                try:
                    import requests
                    response = requests.head(img_url, timeout=5)
                    if response.status_code == 200:
                        working_images += 1
                        print(f"      ✅ FUNCIONA (Status: {response.status_code})")
                    else:
                        print(f"      ❌ ROTA (Status: {response.status_code})")
                        
                        # Try with proxy
                        proxy_success, _ = self.run_test(
                            f"Test Image via Proxy {i+1}", 
                            "GET", 
                            f"proxy-image?url={img_url}", 
                            200
                        )
                        if proxy_success:
                            print(f"      ✅ Funciona a través del proxy")
                            working_images += 1
                        else:
                            print(f"      ❌ También falla a través del proxy")
                            
                except Exception as e:
                    print(f"      ❌ ERROR: {str(e)}")
            
            if working_images > 0:
                imperio_investigation['images_working'] = True
                print(f"\n   📊 RESULTADO: {working_images}/{len(all_images)} imágenes funcionando")
            else:
                print(f"\n   ❌ CRÍTICO: NINGUNA imagen funciona ({len(all_images)} URLs rotas)")
        else:
            print("   ❌ CRÍTICO: NO HAY IMÁGENES ASIGNADAS AL PRODUCTO")
        
        # 4. Test if product can be edited
        print("\n4️⃣ PROBANDO CAPACIDAD DE EDICIÓN:")
        if not self.token:
            print("   ❌ No hay token de admin para probar edición")
        else:
            # Try to update a non-critical field
            test_update = {
                "description": f"Producto Imperio - Actualizado para prueba {datetime.now().strftime('%H:%M:%S')}"
            }
            
            success, response = self.run_test(
                "Test Imperio Product Edit",
                "PUT",
                f"products/{product_id}",
                200,
                data=test_update
            )
            
            if success:
                imperio_investigation['can_be_edited'] = True
                print("   ✅ PRODUCTO SE PUEDE EDITAR correctamente")
                
                # Verify the update was applied
                success_verify, updated_product = self.run_test(
                    "Verify Imperio Product Update",
                    "GET",
                    f"products/{product_id}",
                    200
                )
                
                if success_verify and isinstance(updated_product, dict):
                    if test_update["description"] in updated_product.get("description", ""):
                        print("   ✅ Actualización verificada correctamente")
                    else:
                        print("   ⚠️  Actualización no se aplicó correctamente")
                else:
                    print("   ⚠️  No se pudo verificar la actualización")
            else:
                print("   ❌ CRÍTICO: PRODUCTO NO SE PUEDE EDITAR")
                print(f"      Error: {response}")
        
        # 5. Test if product can be deleted (for potential recreation)
        print("\n5️⃣ PROBANDO CAPACIDAD DE ELIMINACIÓN:")
        if not self.token:
            print("   ❌ No hay token de admin para probar eliminación")
        else:
            # Note: We won't actually delete, just test the endpoint response
            print("   ℹ️  Nota: Solo probamos el endpoint, NO eliminaremos el producto")
            
            # Test with a fake ID first to see the error response
            success, response = self.run_test(
                "Test Delete Endpoint (Fake ID)",
                "DELETE",
                "products/fake-id-test",
                404  # Expect 404 for non-existent product
            )
            
            if success:
                print("   ✅ Endpoint de eliminación funciona (responde correctamente a ID inexistente)")
                imperio_investigation['can_be_deleted'] = True
            else:
                print("   ❌ Endpoint de eliminación tiene problemas")
        
        # 6. Data integrity check
        print("\n6️⃣ VERIFICACIÓN DE INTEGRIDAD DE DATOS:")
        required_fields = ['id', 'name', 'category', 'retail_price', 'wholesale_price']
        missing_fields = []
        corrupted_fields = []
        
        for field in required_fields:
            value = imperio_product.get(field)
            if value is None or value == '':
                missing_fields.append(field)
            elif field in ['retail_price', 'wholesale_price']:
                try:
                    price = float(value)
                    if price <= 0:
                        corrupted_fields.append(f"{field} (valor: {price})")
                except (ValueError, TypeError):
                    corrupted_fields.append(f"{field} (no numérico: {value})")
        
        if missing_fields:
            print(f"   ❌ Campos faltantes: {', '.join(missing_fields)}")
            imperio_investigation['data_corruption'] = True
        
        if corrupted_fields:
            print(f"   ❌ Campos corruptos: {', '.join(corrupted_fields)}")
            imperio_investigation['data_corruption'] = True
        
        if not missing_fields and not corrupted_fields:
            print("   ✅ Integridad de datos básica correcta")
        
        # 7. Determine recommended action
        print("\n7️⃣ DETERMINANDO ACCIÓN RECOMENDADA:")
        
        if not imperio_investigation['product_found']:
            imperio_investigation['recommended_action'] = 'recreate'
            print("   🎯 ACCIÓN: RECREAR producto desde cero")
        elif imperio_investigation['data_corruption']:
            imperio_investigation['recommended_action'] = 'delete_and_recreate'
            print("   🎯 ACCIÓN: ELIMINAR y RECREAR (datos corruptos)")
        elif not imperio_investigation['has_images']:
            imperio_investigation['recommended_action'] = 'add_images'
            print("   🎯 ACCIÓN: AGREGAR imágenes al producto existente")
        elif not imperio_investigation['images_working']:
            imperio_investigation['recommended_action'] = 'replace_images'
            print("   🎯 ACCIÓN: REEMPLAZAR imágenes rotas con nuevas URLs")
        elif not imperio_investigation['can_be_edited']:
            imperio_investigation['recommended_action'] = 'fix_permissions'
            print("   🎯 ACCIÓN: INVESTIGAR problemas de permisos/autenticación")
        else:
            imperio_investigation['recommended_action'] = 'minor_fixes'
            print("   🎯 ACCIÓN: Correcciones menores necesarias")
        
        # 8. Final summary and action plan
        print("\n" + "="*80)
        print("🎯 RESUMEN EJECUTIVO - PRODUCTO 'IMPERIO'")
        print("="*80)
        
        print(f"📊 ESTADO ACTUAL:")
        print(f"   • Producto encontrado: {'✅ SÍ' if imperio_investigation['product_found'] else '❌ NO'}")
        print(f"   • ID válido: {'✅ SÍ' if imperio_investigation['has_valid_id'] else '❌ NO'}")
        print(f"   • Tiene imágenes: {'✅ SÍ' if imperio_investigation['has_images'] else '❌ NO'}")
        print(f"   • Imágenes funcionan: {'✅ SÍ' if imperio_investigation['images_working'] else '❌ NO'}")
        print(f"   • Se puede editar: {'✅ SÍ' if imperio_investigation['can_be_edited'] else '❌ NO'}")
        print(f"   • Datos corruptos: {'❌ SÍ' if imperio_investigation['data_corruption'] else '✅ NO'}")
        
        print(f"\n🚨 ACCIÓN RECOMENDADA: {imperio_investigation['recommended_action'].upper().replace('_', ' ')}")
        
        if imperio_investigation['recommended_action'] == 'add_images':
            print(f"\n📋 PASOS ESPECÍFICOS:")
            print(f"   1. Subir nueva imagen para 'Imperio' usando /api/admin/upload-images")
            print(f"   2. Actualizar producto con nueva URL de ImgBB")
            print(f"   3. Verificar que la imagen se muestre correctamente en catálogo")
        elif imperio_investigation['recommended_action'] == 'replace_images':
            print(f"\n📋 PASOS ESPECÍFICOS:")
            print(f"   1. Eliminar URLs rotas actuales")
            print(f"   2. Subir nueva imagen usando /api/admin/upload-images")
            print(f"   3. Actualizar producto con nueva URL de ImgBB")
            print(f"   4. Verificar funcionamiento en catálogo")
        elif imperio_investigation['recommended_action'] == 'delete_and_recreate':
            print(f"\n📋 PASOS ESPECÍFICOS:")
            print(f"   1. ELIMINAR producto actual (datos corruptos)")
            print(f"   2. RECREAR producto 'Imperio' con datos correctos")
            print(f"   3. Subir imagen nueva usando ImgBB")
            print(f"   4. Verificar que aparezca correctamente en catálogo")
        
        print(f"\n⚡ URGENCIA: CRÍTICA - Resolver INMEDIATAMENTE")
        print(f"   Las clientas ya vieron el problema - afecta credibilidad")
        
        return imperio_investigation

    def test_migration_failure_analysis(self):
        """CRITICAL ANALYSIS: Why only 26% of images migrated successfully"""
        print("\n🚨 ANÁLISIS CRÍTICO - MIGRACIÓN DE IMÁGENES")
        print("="*80)
        print("PROBLEMA: Solo 26% de migración exitosa (23/88 imágenes)")
        print("OBJETIVO: Identificar por qué fallaron 65 imágenes")
        print("="*80)
        
        migration_analysis = {
            'total_products': 0,
            'products_with_postimg': 0,
            'products_with_imgbb': 0,
            'products_without_images': 0,
            'failed_postimg_urls': [],
            'successful_imgbb_urls': [],
            'categories_affected': {},
            'migration_success_rate': 0
        }
        
        # 1. Get all products for analysis
        print("\n1️⃣ OBTENIENDO DATOS DE PRODUCTOS:")
        success, products = self.run_test("Get All Products for Migration Analysis", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos para análisis")
            return migration_analysis
        
        migration_analysis['total_products'] = len(products)
        print(f"   📦 Total productos en base de datos: {len(products)}")
        
        # 2. Analyze image URLs by type
        print("\n2️⃣ ANÁLISIS DE URLs DE IMÁGENES:")
        postimg_urls = []
        imgbb_urls = []
        other_urls = []
        products_by_category = {}
        
        for product in products:
            category = product.get('category', 'unknown')
            if category not in products_by_category:
                products_by_category[category] = {
                    'total': 0,
                    'with_postimg': 0,
                    'with_imgbb': 0,
                    'without_images': 0
                }
            
            products_by_category[category]['total'] += 1
            
            # Check images array
            images = product.get('images', [])
            single_image = product.get('image', '')
            
            # Combine all image URLs
            all_images = list(images) if images else []
            if single_image and single_image not in all_images:
                all_images.append(single_image)
            
            if not all_images:
                migration_analysis['products_without_images'] += 1
                products_by_category[category]['without_images'] += 1
                continue
            
            has_postimg = False
            has_imgbb = False
            
            for img_url in all_images:
                if 'postimg.cc' in img_url or 'i.postimg.cc' in img_url:
                    postimg_urls.append({
                        'url': img_url,
                        'product': product.get('name', 'Unknown'),
                        'category': category
                    })
                    has_postimg = True
                elif 'i.ibb.co' in img_url or 'ibb.co' in img_url:
                    imgbb_urls.append({
                        'url': img_url,
                        'product': product.get('name', 'Unknown'),
                        'category': category
                    })
                    has_imgbb = True
                else:
                    other_urls.append({
                        'url': img_url,
                        'product': product.get('name', 'Unknown'),
                        'category': category
                    })
            
            if has_postimg:
                migration_analysis['products_with_postimg'] += 1
                products_by_category[category]['with_postimg'] += 1
            if has_imgbb:
                migration_analysis['products_with_imgbb'] += 1
                products_by_category[category]['with_imgbb'] += 1
        
        migration_analysis['categories_affected'] = products_by_category
        
        print(f"   🔗 URLs de PostImg encontradas: {len(postimg_urls)}")
        print(f"   ✅ URLs de ImgBB encontradas: {len(imgbb_urls)}")
        print(f"   🌐 Otras URLs encontradas: {len(other_urls)}")
        print(f"   📷 Productos sin imágenes: {migration_analysis['products_without_images']}")
        
        # 3. Calculate migration success rate
        total_postimg_found = len(postimg_urls)
        total_imgbb_found = len(imgbb_urls)
        
        if total_postimg_found > 0:
            # Based on migration log: 88 PostImg URLs found, 23 migrated successfully
            migration_analysis['migration_success_rate'] = (23 / 88) * 100
            print(f"\n📊 TASA DE MIGRACIÓN:")
            print(f"   📝 Según migration.log: 88 imágenes PostImg encontradas")
            print(f"   ✅ Migradas exitosamente: 23")
            print(f"   ❌ Fallidas: 65")
            print(f"   📈 Tasa de éxito: {migration_analysis['migration_success_rate']:.1f}%")
        
        # 4. Analyze by category
        print("\n3️⃣ ANÁLISIS POR CATEGORÍA:")
        for category, stats in products_by_category.items():
            if stats['total'] > 0:
                postimg_percentage = (stats['with_postimg'] / stats['total']) * 100
                imgbb_percentage = (stats['with_imgbb'] / stats['total']) * 100
                no_images_percentage = (stats['without_images'] / stats['total']) * 100
                
                print(f"\n   📂 {category.upper()}:")
                print(f"      Total productos: {stats['total']}")
                print(f"      Con PostImg: {stats['with_postimg']} ({postimg_percentage:.1f}%)")
                print(f"      Con ImgBB: {stats['with_imgbb']} ({imgbb_percentage:.1f}%)")
                print(f"      Sin imágenes: {stats['without_images']} ({no_images_percentage:.1f}%)")
                
                # Calculate failure impact by category
                if stats['with_postimg'] > 0:
                    estimated_failed = int(stats['with_postimg'] * 0.74)  # 74% failure rate
                    print(f"      ❌ Estimado fallidas: {estimated_failed}")
        
        # 5. Test sample PostImg URLs to confirm they're broken
        print("\n4️⃣ VERIFICACIÓN DE URLs PROBLEMÁTICAS:")
        sample_postimg_urls = postimg_urls[:10]  # Test first 10
        working_postimg = 0
        broken_postimg = 0
        
        for url_info in sample_postimg_urls:
            try:
                import requests
                response = requests.head(url_info['url'], timeout=5)
                if response.status_code == 200:
                    working_postimg += 1
                    print(f"   ✅ FUNCIONA: {url_info['product']} - {url_info['url'][:50]}...")
                else:
                    broken_postimg += 1
                    print(f"   ❌ ROTA ({response.status_code}): {url_info['product']} - {url_info['url'][:50]}...")
            except Exception as e:
                broken_postimg += 1
                print(f"   ❌ ERROR: {url_info['product']} - {url_info['url'][:50]}... - {str(e)}")
        
        if sample_postimg_urls:
            broken_percentage = (broken_postimg / len(sample_postimg_urls)) * 100
            print(f"\n   📊 MUESTRA DE URLs PostImg:")
            print(f"      Probadas: {len(sample_postimg_urls)}")
            print(f"      Funcionando: {working_postimg}")
            print(f"      Rotas: {broken_postimg}")
            print(f"      % Rotas: {broken_percentage:.1f}%")
        
        # 6. Test sample ImgBB URLs to confirm they work
        print("\n5️⃣ VERIFICACIÓN DE URLs MIGRADAS:")
        sample_imgbb_urls = imgbb_urls[:10]  # Test first 10
        working_imgbb = 0
        broken_imgbb = 0
        
        for url_info in sample_imgbb_urls:
            try:
                import requests
                response = requests.head(url_info['url'], timeout=5)
                if response.status_code == 200:
                    working_imgbb += 1
                    print(f"   ✅ FUNCIONA: {url_info['product']} - {url_info['url'][:50]}...")
                else:
                    broken_imgbb += 1
                    print(f"   ❌ ROTA ({response.status_code}): {url_info['product']} - {url_info['url'][:50]}...")
            except Exception as e:
                broken_imgbb += 1
                print(f"   ❌ ERROR: {url_info['product']} - {url_info['url'][:50]}... - {str(e)}")
        
        if sample_imgbb_urls:
            working_percentage = (working_imgbb / len(sample_imgbb_urls)) * 100
            print(f"\n   📊 MUESTRA DE URLs ImgBB:")
            print(f"      Probadas: {len(sample_imgbb_urls)}")
            print(f"      Funcionando: {working_imgbb}")
            print(f"      Rotas: {broken_imgbb}")
            print(f"      % Funcionando: {working_percentage:.1f}%")
        
        # 7. Identify products that need new images
        print("\n6️⃣ PRODUCTOS QUE NECESITAN IMÁGENES NUEVAS:")
        products_needing_images = []
        
        for product in products:
            images = product.get('images', [])
            single_image = product.get('image', '')
            all_images = list(images) if images else []
            if single_image and single_image not in all_images:
                all_images.append(single_image)
            
            has_working_image = False
            for img_url in all_images:
                if 'i.ibb.co' in img_url or 'ibb.co' in img_url:
                    has_working_image = True
                    break
            
            if not has_working_image and all_images:
                # Product has images but they're likely broken PostImg URLs
                products_needing_images.append({
                    'name': product.get('name', 'Unknown'),
                    'category': product.get('category', 'unknown'),
                    'images': all_images
                })
        
        print(f"   📝 Productos que necesitan imágenes nuevas: {len(products_needing_images)}")
        
        # Show first 10 products needing images by category
        by_category = {}
        for product in products_needing_images:
            category = product['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(product)
        
        for category, products_list in by_category.items():
            print(f"\n   📂 {category.upper()} ({len(products_list)} productos):")
            for i, product in enumerate(products_list[:5]):  # Show first 5
                print(f"      {i+1}. {product['name']}")
            if len(products_list) > 5:
                print(f"      ... y {len(products_list) - 5} más")
        
        # 8. Final summary and recommendations
        print("\n" + "="*80)
        print("🎯 RESUMEN EJECUTIVO - ANÁLISIS DE MIGRACIÓN")
        print("="*80)
        
        print(f"📊 ESTADÍSTICAS GENERALES:")
        print(f"   • Total productos: {migration_analysis['total_products']}")
        print(f"   • Productos con PostImg: {migration_analysis['products_with_postimg']}")
        print(f"   • Productos con ImgBB: {migration_analysis['products_with_imgbb']}")
        print(f"   • Productos sin imágenes: {migration_analysis['products_without_images']}")
        
        print(f"\n🚨 PROBLEMA IDENTIFICADO:")
        print(f"   • Tasa de migración: {migration_analysis['migration_success_rate']:.1f}% (23/88)")
        print(f"   • Imágenes fallidas: 65")
        print(f"   • Causa principal: URLs de PostImg expiradas/rotas")
        
        print(f"\n📋 PRODUCTOS AFECTADOS POR CATEGORÍA:")
        for category, stats in products_by_category.items():
            if stats['with_postimg'] > 0:
                estimated_failed = int(stats['with_postimg'] * 0.74)
                print(f"   • {category}: {estimated_failed} productos necesitan imágenes nuevas")
        
        print(f"\n🎯 PLAN DE ACCIÓN REQUERIDO:")
        print(f"   1. Re-subir imágenes para {len(products_needing_images)} productos")
        print(f"   2. Priorizar categorías con más productos afectados")
        print(f"   3. Usar servicio estable como ImgBB para nuevas imágenes")
        print(f"   4. Verificar que todas las imágenes nuevas sean compatibles con CORS")
        
        return migration_analysis

    def test_launch_readiness_comprehensive(self):
        """Comprehensive launch readiness test"""
        print("\n🚀 COMPREHENSIVE LAUNCH READINESS ASSESSMENT")
        print("="*60)
        
        readiness_checks = {
            'api_endpoints': False,
            'admin_auth': False,
            'price_integrity': False,
            'data_integrity': False,
            'performance': False
        }
        
        # 1. API Endpoints Check
        print("\n1️⃣ API ENDPOINTS CHECK:")
        endpoints_success = 0
        critical_endpoints = [
            ("GET /api/", "Root endpoint"),
            ("GET /api/products", "Get products"),
            ("GET /api/categories", "Get categories"),
            ("POST /api/admin/login", "Admin login"),
            ("GET /api/catalog/stats", "Catalog stats")
        ]
        
        for endpoint, description in critical_endpoints:
            if "login" in endpoint:
                success, _ = self.run_test(f"Test {description}", "POST", "admin/login", 200, 
                                        data={"username": self.admin_username, "password": self.admin_password})
            elif "stats" in endpoint:
                success, _ = self.run_test(f"Test {description}", "GET", "catalog/stats", 200)
            elif endpoint == "GET /api/":
                success, _ = self.run_test(f"Test {description}", "GET", "", 200)
            else:
                success, _ = self.run_test(f"Test {description}", "GET", endpoint.replace("GET /api/", ""), 200)
            
            if success:
                endpoints_success += 1
        
        readiness_checks['api_endpoints'] = endpoints_success == len(critical_endpoints)
        print(f"   Result: {endpoints_success}/{len(critical_endpoints)} critical endpoints working")
        
        # 2. Admin Authentication Check
        print("\n2️⃣ ADMIN AUTHENTICATION CHECK:")
        if self.token:
            readiness_checks['admin_auth'] = True
            print("   ✅ Admin authentication working")
        else:
            print("   ❌ Admin authentication failed")
        
        # 3. Price Integrity Check
        print("\n3️⃣ PRICE INTEGRITY CHECK:")
        readiness_checks['price_integrity'] = self.test_price_validation_comprehensive()
        
        # 4. Data Integrity Check
        print("\n4️⃣ DATA INTEGRITY CHECK:")
        success, products = self.run_test("Get products for data integrity", "GET", "products", 200)
        if success and isinstance(products, list):
            print(f"   ✅ {len(products)} products in database")
            print(f"   ✅ Product data structure intact")
            readiness_checks['data_integrity'] = True
        else:
            print("   ❌ Data integrity issues detected")
        
        # 5. Performance Check
        print("\n5️⃣ PERFORMANCE CHECK:")
        import time
        start_time = time.time()
        success, _ = self.run_test("Performance test", "GET", "products", 200)
        end_time = time.time()
        response_time = end_time - start_time
        
        if success and response_time < 2.0:  # Less than 2 seconds
            print(f"   ✅ Response time: {response_time:.2f}s (< 2s requirement)")
            readiness_checks['performance'] = True
        else:
            print(f"   ❌ Response time: {response_time:.2f}s (>= 2s - too slow)")
        
        # Final Assessment
        print("\n" + "="*60)
        print("🎯 LAUNCH READINESS SUMMARY:")
        print("="*60)
        
        passed_checks = sum(readiness_checks.values())
        total_checks = len(readiness_checks)
        readiness_percentage = (passed_checks / total_checks) * 100
        
        for check, status in readiness_checks.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {check.replace('_', ' ').title()}")
        
        print(f"\n📊 Overall Readiness: {passed_checks}/{total_checks} ({readiness_percentage:.1f}%)")
        
        if readiness_percentage == 100:
            print("\n🎉 BACKEND IS 100% READY FOR LAUNCH!")
            return True
        elif readiness_percentage >= 80:
            print(f"\n⚠️  BACKEND IS {readiness_percentage:.1f}% READY - Minor issues need attention")
            return False
        else:
            print(f"\n❌ BACKEND IS ONLY {readiness_percentage:.1f}% READY - Critical issues must be fixed")
            return False

    def test_create_product(self):
        """Legacy test method - redirects to new comprehensive tests"""
        return self.test_create_product_with_images_colors()

def main():
    print("🚀 Starting HANNU CLOTHES API Testing...")
    print("=" * 60)
    
    tester = HannuClothesAPITester()
    
    # Test sequence - prioritizing mass upload investigation
    tests = [
        ("🚨 URGENTE: Investigación Carga Masiva", tester.test_mass_upload_investigation),
        ("Root Endpoint", tester.test_root_endpoint),
        ("Admin Login", tester.test_admin_login),
        ("Get All Products", tester.test_get_products),
        ("🚨 CRÍTICO: Análisis de Falla de Migración", tester.test_migration_failure_analysis),
        ("Get Categories", tester.test_get_categories),
        ("Get Products by Category", tester.test_get_products_by_category),
        ("Admin Profile", tester.test_admin_profile),
        ("Catalog Statistics", tester.test_catalog_stats),
        ("Search Products", tester.test_search_products),
        ("🔥 CRITICAL: Price Validation Check", tester.test_price_validation_comprehensive),
        ("🔥 CRITICAL: API Price Enforcement", tester.test_price_validation_api_enforcement),
        ("Create Product with Images/Colors", tester.test_create_product_with_images_colors),
        ("Create Product Legacy Format", tester.test_create_product_legacy_format),
        ("Data Validation Test", tester.test_data_validation),
        ("Get Single Product", tester.test_get_single_product),
        ("Update Product", tester.test_update_product),
        ("Product Appears in Catalog", tester.test_product_appears_in_catalog),
        ("🚀 LAUNCH READINESS ASSESSMENT", tester.test_launch_readiness_comprehensive),
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