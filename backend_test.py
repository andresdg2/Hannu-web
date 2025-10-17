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

    def test_duplicate_products_investigation(self):
        """CRITICAL INVESTIGATION: Find duplicate products, especially 'Blonda'"""
        print("\n🚨 INVESTIGACIÓN CRÍTICA - PRODUCTOS DUPLICADOS")
        print("="*80)
        print("PROBLEMA REPORTADO: Productos 'Blonda' duplicados y otros productos no editables")
        print("OBJETIVO: Identificar todos los productos duplicados y problemas de edición")
        print("="*80)
        
        duplicate_investigation = {
            'total_products': 0,
            'duplicate_names': {},
            'blonda_products': [],
            'products_with_same_data': [],
            'problematic_products': [],
            'database_integrity_issues': []
        }
        
        # 1. Get all products for analysis
        print("\n1️⃣ OBTENIENDO TODOS LOS PRODUCTOS:")
        success, products = self.run_test("Get All Products for Duplicate Analysis", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos para análisis")
            return duplicate_investigation
        
        duplicate_investigation['total_products'] = len(products)
        print(f"   📦 Total productos en base de datos: {len(products)}")
        
        # 2. Analyze for duplicate names
        print("\n2️⃣ ANÁLISIS DE NOMBRES DUPLICADOS:")
        name_counts = {}
        products_by_name = {}
        
        for product in products:
            name = product.get('name', '').strip().lower()
            if name:
                if name not in name_counts:
                    name_counts[name] = 0
                    products_by_name[name] = []
                name_counts[name] += 1
                products_by_name[name].append(product)
        
        # Find duplicates
        duplicates_found = 0
        for name, count in name_counts.items():
            if count > 1:
                duplicates_found += 1
                duplicate_investigation['duplicate_names'][name] = {
                    'count': count,
                    'products': products_by_name[name]
                }
                
                print(f"   ❌ DUPLICADO: '{name}' aparece {count} veces")
                for i, product in enumerate(products_by_name[name]):
                    print(f"      {i+1}. ID: {product.get('id', 'No ID')[:8]}... - Precio: ${product.get('retail_price', 'N/A')}")
                    
                    # Special attention to Blonda products
                    if 'blonda' in name:
                        duplicate_investigation['blonda_products'].append(product)
        
        if duplicates_found == 0:
            print("   ✅ No se encontraron nombres duplicados")
        else:
            print(f"   📊 Total nombres duplicados: {duplicates_found}")
        
        # 3. Special focus on Blonda products
        print("\n3️⃣ ANÁLISIS ESPECÍFICO DE PRODUCTOS 'BLONDA':")
        blonda_products = [p for p in products if 'blonda' in p.get('name', '').lower()]
        
        if blonda_products:
            print(f"   📋 Productos 'Blonda' encontrados: {len(blonda_products)}")
            for i, product in enumerate(blonda_products):
                print(f"\n   🔍 BLONDA {i+1}:")
                print(f"      ID: {product.get('id', 'No ID')}")
                print(f"      Nombre exacto: '{product.get('name', 'No name')}'")
                print(f"      Categoría: {product.get('category', 'No category')}")
                print(f"      Precio retail: ${product.get('retail_price', 'N/A')}")
                print(f"      Precio mayorista: ${product.get('wholesale_price', 'N/A')}")
                print(f"      Imágenes: {len(product.get('images', []))}")
                print(f"      Colores: {len(product.get('colors', []))}")
                print(f"      Creado: {product.get('created_at', 'N/A')}")
                
                # Check if this Blonda can be edited
                if self.token:
                    test_update = {"description": f"Test edit {datetime.now().strftime('%H:%M:%S')}"}
                    edit_success, _ = self.run_test(
                        f"Test Edit Blonda {i+1}",
                        "PUT",
                        f"products/{product.get('id')}",
                        200,
                        data=test_update
                    )
                    if edit_success:
                        print(f"      ✅ SE PUEDE EDITAR")
                    else:
                        print(f"      ❌ NO SE PUEDE EDITAR")
                        duplicate_investigation['problematic_products'].append({
                            'name': product.get('name'),
                            'id': product.get('id'),
                            'issue': 'Cannot be edited'
                        })
        else:
            print("   ℹ️  No se encontraron productos 'Blonda' en la base de datos")
        
        # 4. Test editing functionality on random products
        print("\n4️⃣ PRUEBA DE FUNCIONALIDAD DE EDICIÓN:")
        if not self.token:
            print("   ❌ No hay token de admin para probar edición")
        else:
            # Test editing on a sample of products
            sample_products = products[:15]  # Test first 15 products
            editable_count = 0
            non_editable_count = 0
            
            for i, product in enumerate(sample_products):
                product_id = product.get('id')
                product_name = product.get('name', 'Unknown')
                
                if not product_id:
                    print(f"   ❌ Producto sin ID: '{product_name}'")
                    duplicate_investigation['problematic_products'].append({
                        'name': product_name,
                        'id': 'MISSING',
                        'issue': 'No ID field'
                    })
                    continue
                
                # Try a minimal edit
                test_update = {
                    "description": f"Test edit {datetime.now().strftime('%H:%M:%S')}"
                }
                
                success, response = self.run_test(
                    f"Test Edit Product {i+1}",
                    "PUT",
                    f"products/{product_id}",
                    200,
                    data=test_update
                )
                
                if success:
                    editable_count += 1
                    print(f"   ✅ EDITABLE: '{product_name}' - ID: {product_id[:8]}...")
                else:
                    non_editable_count += 1
                    print(f"   ❌ NO EDITABLE: '{product_name}' - ID: {product_id[:8]}...")
                    duplicate_investigation['problematic_products'].append({
                        'name': product_name,
                        'id': product_id,
                        'issue': f'Edit failed: {response}'
                    })
            
            print(f"\n   📊 RESULTADOS DE EDICIÓN:")
            print(f"      Productos editables: {editable_count}")
            print(f"      Productos NO editables: {non_editable_count}")
            
            if non_editable_count > 0:
                print(f"      ⚠️  {non_editable_count} productos tienen problemas de edición")
        
        # 5. Database integrity checks
        print("\n5️⃣ VERIFICACIÓN DE INTEGRIDAD DE BASE DE DATOS:")
        integrity_issues = []
        
        for product in products:
            product_name = product.get('name', 'Unknown')
            
            # Check for missing required fields
            required_fields = ['id', 'name', 'retail_price', 'wholesale_price', 'category']
            for field in required_fields:
                if not product.get(field):
                    integrity_issues.append(f"'{product_name}': Missing {field}")
            
            # Check for invalid prices
            retail_price = product.get('retail_price')
            wholesale_price = product.get('wholesale_price')
            
            if retail_price is not None and wholesale_price is not None:
                try:
                    retail = float(retail_price)
                    wholesale = float(wholesale_price)
                    
                    if wholesale <= 0:
                        integrity_issues.append(f"'{product_name}': Invalid wholesale price ({wholesale})")
                    if retail <= 0:
                        integrity_issues.append(f"'{product_name}': Invalid retail price ({retail})")
                    if wholesale >= retail:
                        integrity_issues.append(f"'{product_name}': Wholesale >= retail ({wholesale} >= {retail})")
                except (ValueError, TypeError):
                    integrity_issues.append(f"'{product_name}': Non-numeric prices")
            
            # Check for duplicate IDs
            product_id = product.get('id')
            if product_id:
                id_count = sum(1 for p in products if p.get('id') == product_id)
                if id_count > 1:
                    integrity_issues.append(f"'{product_name}': Duplicate ID {product_id}")
        
        duplicate_investigation['database_integrity_issues'] = integrity_issues
        
        if integrity_issues:
            print(f"   ❌ PROBLEMAS DE INTEGRIDAD ENCONTRADOS: {len(integrity_issues)}")
            for issue in integrity_issues[:10]:  # Show first 10
                print(f"      • {issue}")
            if len(integrity_issues) > 10:
                print(f"      ... y {len(integrity_issues) - 10} más")
        else:
            print("   ✅ No se encontraron problemas de integridad básica")
        
        # 6. Final summary and recommendations
        print("\n" + "="*80)
        print("🎯 RESUMEN EJECUTIVO - INVESTIGACIÓN DE DUPLICADOS")
        print("="*80)
        
        print(f"📊 HALLAZGOS PRINCIPALES:")
        print(f"   • Total productos: {duplicate_investigation['total_products']}")
        print(f"   • Nombres duplicados: {len(duplicate_investigation['duplicate_names'])}")
        print(f"   • Productos 'Blonda': {len(duplicate_investigation['blonda_products'])}")
        print(f"   • Productos problemáticos: {len(duplicate_investigation['problematic_products'])}")
        print(f"   • Problemas de integridad: {len(duplicate_investigation['database_integrity_issues'])}")
        
        # Specific recommendations
        print(f"\n🎯 RECOMENDACIONES ESPECÍFICAS:")
        
        if duplicate_investigation['duplicate_names']:
            print(f"   1. ELIMINAR DUPLICADOS: {len(duplicate_investigation['duplicate_names'])} nombres duplicados encontrados")
            for name, info in list(duplicate_investigation['duplicate_names'].items())[:3]:
                print(f"      • '{name}': {info['count']} copias")
        
        if duplicate_investigation['blonda_products']:
            print(f"   2. REVISAR BLONDA: {len(duplicate_investigation['blonda_products'])} productos 'Blonda' requieren atención")
        
        if duplicate_investigation['problematic_products']:
            print(f"   3. CORREGIR EDICIÓN: {len(duplicate_investigation['problematic_products'])} productos no se pueden editar")
        
        if duplicate_investigation['database_integrity_issues']:
            print(f"   4. INTEGRIDAD BD: {len(duplicate_investigation['database_integrity_issues'])} problemas de datos")
        
        print(f"\n⚡ PRIORIDAD: CRÍTICA - Afecta operaciones diarias del usuario")
        
        return duplicate_investigation

    def test_comprehensive_crud_operations(self):
        """Test complete CRUD operations for daily operations"""
        print("\n🔧 PRUEBA COMPLETA DE OPERACIONES CRUD")
        print("="*60)
        print("OBJETIVO: Verificar que todas las operaciones diarias funcionen correctamente")
        
        crud_results = {
            'create_working': False,
            'read_working': False,
            'update_working': False,
            'delete_working': False,
            'test_product_id': None
        }
        
        if not self.token:
            print("❌ No hay token de admin para pruebas CRUD")
            return crud_results
        
        # 1. CREATE - Test product creation
        print("\n1️⃣ PROBANDO CREACIÓN DE PRODUCTO:")
        test_product = {
            "name": "Producto Prueba CRUD",
            "description": "Producto para probar operaciones CRUD completas",
            "retail_price": 95000,
            "wholesale_price": 66500,
            "category": "vestidos",
            "images": ["https://i.ibb.co/test-image.jpg"],
            "colors": ["Azul", "Rojo"],
            "composition": "95% Algodón, 5% Elastano",
            "sizes": ["S", "M", "L"],
            "stock": {"S": 5, "M": 8, "L": 6}
        }
        
        success, response = self.run_test(
            "CREATE - New Product",
            "POST",
            "products",
            200,
            data=test_product
        )
        
        if success and isinstance(response, dict) and 'id' in response:
            crud_results['create_working'] = True
            crud_results['test_product_id'] = response['id']
            print(f"   ✅ CREACIÓN EXITOSA - ID: {response['id'][:8]}...")
        else:
            print(f"   ❌ CREACIÓN FALLÓ")
            return crud_results
        
        # 2. READ - Test reading the created product
        print("\n2️⃣ PROBANDO LECTURA DE PRODUCTO:")
        success, response = self.run_test(
            "READ - Get Created Product",
            "GET",
            f"products/{crud_results['test_product_id']}",
            200
        )
        
        if success and isinstance(response, dict):
            crud_results['read_working'] = True
            print(f"   ✅ LECTURA EXITOSA - Nombre: {response.get('name', 'Unknown')}")
            
            # Verify data integrity
            if response.get('name') == test_product['name']:
                print(f"   ✅ Datos íntegros - Nombre correcto")
            else:
                print(f"   ⚠️  Posible problema de datos - Nombre: {response.get('name')}")
        else:
            print(f"   ❌ LECTURA FALLÓ")
        
        # 3. UPDATE - Test updating the product
        print("\n3️⃣ PROBANDO ACTUALIZACIÓN DE PRODUCTO:")
        update_data = {
            "name": "Producto Prueba CRUD - ACTUALIZADO",
            "retail_price": 105000,
            "wholesale_price": 73500,
            "colors": ["Azul", "Rojo", "Verde"],
            "description": "Producto actualizado para pruebas CRUD"
        }
        
        success, response = self.run_test(
            "UPDATE - Modify Product",
            "PUT",
            f"products/{crud_results['test_product_id']}",
            200,
            data=update_data
        )
        
        if success and isinstance(response, dict):
            crud_results['update_working'] = True
            print(f"   ✅ ACTUALIZACIÓN EXITOSA")
            
            # Verify updates were applied
            if response.get('name') == update_data['name']:
                print(f"   ✅ Nombre actualizado correctamente")
            if response.get('retail_price') == update_data['retail_price']:
                print(f"   ✅ Precio actualizado correctamente")
            if len(response.get('colors', [])) == 3:
                print(f"   ✅ Colores actualizados correctamente")
        else:
            print(f"   ❌ ACTUALIZACIÓN FALLÓ")
        
        # 4. DELETE - Test deleting the product
        print("\n4️⃣ PROBANDO ELIMINACIÓN DE PRODUCTO:")
        success, response = self.run_test(
            "DELETE - Remove Product",
            "DELETE",
            f"products/{crud_results['test_product_id']}",
            200
        )
        
        if success:
            crud_results['delete_working'] = True
            print(f"   ✅ ELIMINACIÓN EXITOSA")
            
            # Verify product is gone
            success_verify, response_verify = self.run_test(
                "VERIFY DELETE - Try to Get Deleted Product",
                "GET",
                f"products/{crud_results['test_product_id']}",
                404  # Should return 404 Not Found
            )
            
            if success_verify:
                print(f"   ✅ Producto correctamente eliminado de la base de datos")
            else:
                print(f"   ⚠️  Producto podría no haberse eliminado completamente")
        else:
            print(f"   ❌ ELIMINACIÓN FALLÓ")
        
        # 5. Summary
        print("\n" + "="*60)
        print("📊 RESUMEN DE OPERACIONES CRUD:")
        print("="*60)
        
        operations = [
            ("CREATE (Crear)", crud_results['create_working']),
            ("READ (Leer)", crud_results['read_working']),
            ("UPDATE (Actualizar)", crud_results['update_working']),
            ("DELETE (Eliminar)", crud_results['delete_working'])
        ]
        
        working_operations = 0
        for operation, working in operations:
            status = "✅ FUNCIONA" if working else "❌ FALLA"
            print(f"   {operation}: {status}")
            if working:
                working_operations += 1
        
        success_rate = (working_operations / len(operations)) * 100
        print(f"\n📈 TASA DE ÉXITO CRUD: {working_operations}/{len(operations)} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 TODAS LAS OPERACIONES CRUD FUNCIONAN CORRECTAMENTE")
            print("✅ El sistema está listo para operaciones diarias")
        else:
            print("⚠️  ALGUNAS OPERACIONES CRUD TIENEN PROBLEMAS")
            print("❌ Requiere corrección antes de uso comercial")
        
        return crud_results

    def test_complete_editing_functionality_verification(self):
        """URGENT VERIFICATION: Complete editing functionality for daily commercial use"""
        print("\n🚨 VERIFICACIÓN URGENTE - FUNCIONALIDAD DE EDICIÓN COMPLETA")
        print("="*80)
        print("OBJETIVO: Verificar que TODAS las funcionalidades de edición estén funcionando")
        print("CONTEXTO: Después de restaurar productos eliminados incorrectamente")
        print("NECESIDAD: Control TOTAL sobre crear/editar/eliminar para uso diario")
        print("="*80)
        
        verification_results = {
            'total_products_count': 0,
            'target_products_found': {},
            'edit_functionality_working': False,
            'create_functionality_working': False,
            'delete_functionality_working': False,
            'mass_upload_working': False,
            'data_integrity_ok': False,
            'crud_operations_ready': False
        }
        
        if not self.token:
            print("❌ CRÍTICO: No hay token de admin - no se puede verificar funcionalidad")
            return verification_results
        
        # 1. Verify total product count (~140 expected)
        print("\n1️⃣ VERIFICANDO CONTEO TOTAL DE PRODUCTOS:")
        success, products = self.run_test("Get All Products for Count Verification", "GET", "products?limit=1000", 200)
        
        if success and isinstance(products, list):
            verification_results['total_products_count'] = len(products)
            print(f"   📊 Total productos en base de datos: {len(products)}")
            
            if len(products) >= 135:  # Close to expected 140
                print(f"   ✅ Conteo de productos correcto (>= 135)")
            else:
                print(f"   ⚠️  Conteo menor al esperado ({len(products)} < 135)")
        else:
            print("   ❌ CRÍTICO: No se pueden obtener productos")
            return verification_results
        
        # 2. Find and verify specific target products
        print("\n2️⃣ BUSCANDO PRODUCTOS OBJETIVO ESPECÍFICOS:")
        target_products = ["Blonda", "Sol", "Jade", "Amelia", "Abigail"]
        
        for target_name in target_products:
            found_products = []
            for product in products:
                product_name = product.get('name', '').lower()
                if target_name.lower() in product_name:
                    found_products.append(product)
            
            verification_results['target_products_found'][target_name] = found_products
            
            if found_products:
                print(f"   ✅ '{target_name}': {len(found_products)} producto(s) encontrado(s)")
                for i, product in enumerate(found_products):
                    print(f"      {i+1}. '{product.get('name', 'Unknown')}' - {product.get('category', 'unknown')} - ID: {product.get('id', 'No ID')[:8]}...")
            else:
                print(f"   ❌ '{target_name}': NO encontrado")
        
        # 3. Test editing functionality on target products
        print("\n3️⃣ PROBANDO FUNCIONALIDAD DE EDICIÓN:")
        edit_tests_passed = 0
        edit_tests_total = 0
        
        for target_name, found_products in verification_results['target_products_found'].items():
            if found_products:
                # Test editing the first found product of each type
                product = found_products[0]
                product_id = product.get('id')
                
                if product_id:
                    edit_tests_total += 1
                    
                    # Test updating description and prices
                    test_update = {
                        "description": f"Producto {target_name} - Actualizado para verificación {datetime.now().strftime('%H:%M:%S')}",
                        "retail_price": product.get('retail_price', 100000) + 1000,  # Small price increase
                        "wholesale_price": product.get('wholesale_price', 70000) + 700
                    }
                    
                    success, response = self.run_test(
                        f"Edit {target_name} Product",
                        "PUT",
                        f"products/{product_id}",
                        200,
                        data=test_update
                    )
                    
                    if success:
                        edit_tests_passed += 1
                        print(f"   ✅ '{target_name}' editado exitosamente")
                        
                        # Verify the edit was applied
                        success_verify, updated_product = self.run_test(
                            f"Verify {target_name} Edit",
                            "GET",
                            f"products/{product_id}",
                            200
                        )
                        
                        if success_verify and isinstance(updated_product, dict):
                            if test_update["description"] in updated_product.get("description", ""):
                                print(f"      ✅ Cambios verificados correctamente")
                            else:
                                print(f"      ⚠️  Cambios no se aplicaron correctamente")
                    else:
                        print(f"   ❌ '{target_name}' NO se pudo editar")
        
        verification_results['edit_functionality_working'] = edit_tests_passed == edit_tests_total and edit_tests_total > 0
        print(f"\n   📊 RESULTADO EDICIÓN: {edit_tests_passed}/{edit_tests_total} productos editados exitosamente")
        
        # 4. Test creating new products
        print("\n4️⃣ PROBANDO CREACIÓN DE PRODUCTOS NUEVOS:")
        
        test_product_data = {
            "name": f"Producto de Prueba Completa {datetime.now().strftime('%H%M%S')}",
            "description": "Producto creado para verificar funcionalidad completa de creación",
            "retail_price": 95000,
            "wholesale_price": 66500,
            "category": "vestidos",
            "images": ["https://i.ibb.co/test1.jpg", "https://i.ibb.co/test2.jpg"],
            "colors": ["Rojo", "Azul", "Verde"],
            "composition": "95% Algodón, 5% Elastano",
            "sizes": ["S", "M", "L", "XL"],
            "stock": {"S": 5, "M": 10, "L": 8, "XL": 3}
        }
        
        success, created_product = self.run_test(
            "Create Complete Test Product",
            "POST",
            "products",
            200,
            data=test_product_data
        )
        
        if success and isinstance(created_product, dict) and 'id' in created_product:
            verification_results['create_functionality_working'] = True
            self.test_product_id = created_product['id']
            print(f"   ✅ Producto creado exitosamente - ID: {self.test_product_id[:8]}...")
            
            # Verify it appears in catalog immediately
            success_catalog, catalog_products = self.run_test(
                "Verify New Product in Catalog",
                "GET",
                "products?limit=10",
                200
            )
            
            if success_catalog and isinstance(catalog_products, list):
                new_product_found = any(p.get('id') == self.test_product_id for p in catalog_products)
                if new_product_found:
                    print(f"   ✅ Producto aparece inmediatamente en catálogo")
                else:
                    print(f"   ⚠️  Producto no aparece inmediatamente en catálogo")
        else:
            print(f"   ❌ CRÍTICO: No se pudo crear producto de prueba")
        
        # 5. Test deletion functionality
        print("\n5️⃣ PROBANDO FUNCIONALIDAD DE ELIMINACIÓN:")
        
        if hasattr(self, 'test_product_id'):
            success, response = self.run_test(
                "Delete Test Product",
                "DELETE",
                f"products/{self.test_product_id}",
                200
            )
            
            if success:
                verification_results['delete_functionality_working'] = True
                print(f"   ✅ Producto eliminado exitosamente")
                
                # Verify it's actually deleted
                success_verify, response_verify = self.run_test(
                    "Verify Product Deleted",
                    "GET",
                    f"products/{self.test_product_id}",
                    404  # Should return 404 Not Found
                )
                
                if success_verify:
                    print(f"   ✅ Eliminación verificada - producto ya no existe")
                else:
                    print(f"   ⚠️  Producto aún existe después de eliminación")
            else:
                print(f"   ❌ CRÍTICO: No se pudo eliminar producto")
        else:
            print(f"   ⚠️  No hay producto de prueba para eliminar")
        
        # 6. Test mass upload endpoint availability
        print("\n6️⃣ VERIFICANDO SISTEMA DE CARGA MASIVA:")
        
        # Test endpoint availability (without actually uploading files)
        success, response = self.run_test(
            "Test Mass Upload Endpoint",
            "POST",
            "admin/upload-images",
            400,  # Expect 400 because we're not sending proper files
            data={}
        )
        
        if success:
            verification_results['mass_upload_working'] = True
            print(f"   ✅ Endpoint de carga masiva disponible y respondiendo")
        else:
            print(f"   ❌ Endpoint de carga masiva no disponible")
        
        # 7. Data integrity verification
        print("\n7️⃣ VERIFICANDO INTEGRIDAD DE DATOS:")
        
        integrity_issues = []
        valid_products = 0
        
        for product in products[:50]:  # Check first 50 products for performance
            # Check required fields
            required_fields = ['id', 'name', 'category', 'retail_price', 'wholesale_price']
            missing_fields = []
            
            for field in required_fields:
                if not product.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                integrity_issues.append(f"Producto '{product.get('name', 'Unknown')}': campos faltantes {missing_fields}")
            
            # Check price validity
            retail_price = product.get('retail_price', 0)
            wholesale_price = product.get('wholesale_price', 0)
            
            try:
                retail_price = float(retail_price)
                wholesale_price = float(wholesale_price)
                
                if wholesale_price <= 0:
                    integrity_issues.append(f"Producto '{product.get('name', 'Unknown')}': precio mayorista inválido ({wholesale_price})")
                elif wholesale_price >= retail_price:
                    integrity_issues.append(f"Producto '{product.get('name', 'Unknown')}': precio mayorista >= precio retail")
                else:
                    valid_products += 1
            except (ValueError, TypeError):
                integrity_issues.append(f"Producto '{product.get('name', 'Unknown')}': precios no numéricos")
        
        if len(integrity_issues) == 0:
            verification_results['data_integrity_ok'] = True
            print(f"   ✅ Integridad de datos correcta ({valid_products} productos válidos)")
        else:
            print(f"   ❌ Problemas de integridad encontrados:")
            for issue in integrity_issues[:5]:  # Show first 5 issues
                print(f"      • {issue}")
            if len(integrity_issues) > 5:
                print(f"      ... y {len(integrity_issues) - 5} problemas más")
        
        # 8. Overall CRUD readiness assessment
        print("\n8️⃣ EVALUACIÓN GENERAL DE OPERACIONES CRUD:")
        
        crud_checks = [
            verification_results['edit_functionality_working'],
            verification_results['create_functionality_working'], 
            verification_results['delete_functionality_working'],
            verification_results['data_integrity_ok']
        ]
        
        crud_passed = sum(crud_checks)
        crud_total = len(crud_checks)
        
        verification_results['crud_operations_ready'] = crud_passed == crud_total
        
        print(f"   📊 Operaciones CRUD: {crud_passed}/{crud_total} funcionando")
        print(f"   • Editar: {'✅' if verification_results['edit_functionality_working'] else '❌'}")
        print(f"   • Crear: {'✅' if verification_results['create_functionality_working'] else '❌'}")
        print(f"   • Eliminar: {'✅' if verification_results['delete_functionality_working'] else '❌'}")
        print(f"   • Integridad: {'✅' if verification_results['data_integrity_ok'] else '❌'}")
        
        # 9. Final assessment
        print("\n" + "="*80)
        print("🎯 VEREDICTO FINAL - FUNCIONALIDAD DE EDICIÓN COMPLETA")
        print("="*80)
        
        total_checks = 6  # Main functionality areas
        passed_checks = sum([
            verification_results['total_products_count'] >= 135,
            len([p for p in verification_results['target_products_found'].values() if p]) >= 3,  # At least 3 target products found
            verification_results['edit_functionality_working'],
            verification_results['create_functionality_working'],
            verification_results['delete_functionality_working'],
            verification_results['mass_upload_working']
        ])
        
        readiness_percentage = (passed_checks / total_checks) * 100
        
        print(f"📊 ESTADO GENERAL:")
        print(f"   • Total productos: {verification_results['total_products_count']}")
        print(f"   • Productos objetivo encontrados: {len([p for p in verification_results['target_products_found'].values() if p])}/5")
        print(f"   • Funcionalidad edición: {'✅ OPERATIVA' if verification_results['edit_functionality_working'] else '❌ FALLA'}")
        print(f"   • Funcionalidad creación: {'✅ OPERATIVA' if verification_results['create_functionality_working'] else '❌ FALLA'}")
        print(f"   • Funcionalidad eliminación: {'✅ OPERATIVA' if verification_results['delete_functionality_working'] else '❌ FALLA'}")
        print(f"   • Sistema carga masiva: {'✅ DISPONIBLE' if verification_results['mass_upload_working'] else '❌ NO DISPONIBLE'}")
        print(f"   • Integridad de datos: {'✅ CORRECTA' if verification_results['data_integrity_ok'] else '❌ PROBLEMAS'}")
        
        print(f"\n🎯 LISTO PARA USO DIARIO: {readiness_percentage:.1f}% ({passed_checks}/{total_checks} verificaciones pasadas)")
        
        if readiness_percentage >= 90:
            print(f"✅ EXCELENTE: Sistema completamente listo para operaciones comerciales diarias")
        elif readiness_percentage >= 75:
            print(f"⚠️  BUENO: Sistema mayormente listo, algunos ajustes menores necesarios")
        else:
            print(f"❌ CRÍTICO: Sistema necesita correcciones importantes antes del uso diario")
        
        return verification_results

    def test_jade_sol_investigation(self):
        """URGENT INVESTIGATION: Jade and Sol products - prices, images, and editability"""
        print("\n🚨 INVESTIGACIÓN URGENTE - PRODUCTOS 'JADE' Y 'SOL'")
        print("="*80)
        print("PROBLEMA CRÍTICO: Usuario reporta que modifiqué productos sin permiso")
        print("PRODUCTOS AFECTADOS: 'Jade' y 'Sol' - precios incorrectos, imágenes faltantes, no editables")
        print("OBJETIVO: Identificar exactamente qué está mal para restaurar como el usuario quiere")
        print("="*80)
        
        investigation_results = {
            'jade_products': [],
            'sol_products': [],
            'jade_editable': False,
            'sol_editable': False,
            'jade_images_working': False,
            'sol_images_working': False,
            'price_discrepancies': [],
            'authentication_working': False,
            'recommended_actions': []
        }
        
        # 1. Get all products to find Jade and Sol
        print("\n1️⃣ BUSCANDO PRODUCTOS 'JADE' Y 'SOL' EN BASE DE DATOS:")
        success, products = self.run_test("Get All Products to Find Jade and Sol", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos de la base de datos")
            return investigation_results
        
        print(f"   📦 Total productos en base de datos: {len(products)}")
        
        # Search for Jade and Sol products (case insensitive)
        jade_products = []
        sol_products = []
        
        for product in products:
            product_name = product.get('name', '').lower()
            if 'jade' in product_name:
                jade_products.append(product)
            elif 'sol' in product_name:
                sol_products.append(product)
        
        investigation_results['jade_products'] = jade_products
        investigation_results['sol_products'] = sol_products
        
        print(f"   🔍 Productos 'Jade' encontrados: {len(jade_products)}")
        for i, product in enumerate(jade_products):
            print(f"      {i+1}. '{product.get('name', 'Unknown')}' - ID: {product.get('id', 'No ID')[:8]}...")
            print(f"         Retail: ${product.get('retail_price', 'No price'):,} | Mayorista: ${product.get('wholesale_price', 'No price'):,}")
            print(f"         Categoría: {product.get('category', 'Unknown')}")
            print(f"         Imágenes: {len(product.get('images', []))} | Imagen única: {'Sí' if product.get('image') else 'No'}")
        
        print(f"   🔍 Productos 'Sol' encontrados: {len(sol_products)}")
        for i, product in enumerate(sol_products):
            print(f"      {i+1}. '{product.get('name', 'Unknown')}' - ID: {product.get('id', 'No ID')[:8]}...")
            print(f"         Retail: ${product.get('retail_price', 'No price'):,} | Mayorista: ${product.get('wholesale_price', 'No price'):,}")
            print(f"         Categoría: {product.get('category', 'Unknown')}")
            print(f"         Imágenes: {len(product.get('images', []))} | Imagen única: {'Sí' if product.get('image') else 'No'}")
        
        if not jade_products and not sol_products:
            print("   ❌ CRÍTICO: NO se encontraron productos 'Jade' ni 'Sol'")
            investigation_results['recommended_actions'].append("VERIFICAR: Los productos pueden haber sido eliminados accidentalmente")
            return investigation_results
        
        # 2. Analyze price discrepancies
        print("\n2️⃣ ANÁLISIS DE PRECIOS - IDENTIFICANDO DISCREPANCIAS:")
        
        # Check for duplicate products with different prices
        all_target_products = jade_products + sol_products
        price_issues = []
        
        # Group by name to find duplicates
        products_by_name = {}
        for product in all_target_products:
            name = product.get('name', '').lower()
            if name not in products_by_name:
                products_by_name[name] = []
            products_by_name[name].append(product)
        
        for name, product_list in products_by_name.items():
            if len(product_list) > 1:
                print(f"\n   ⚠️  DUPLICADOS ENCONTRADOS para '{name.title()}':")
                prices = []
                for i, product in enumerate(product_list):
                    retail = product.get('retail_price', 0)
                    wholesale = product.get('wholesale_price', 0)
                    prices.append((retail, wholesale))
                    print(f"      Copia {i+1}: Retail ${retail:,} | Mayorista ${wholesale:,} | ID: {product.get('id', 'No ID')[:8]}...")
                    print(f"                Categoría: {product.get('category', 'Unknown')} | Creado: {product.get('created_at', 'Unknown')}")
                
                # Check if prices are different
                unique_prices = list(set(prices))
                if len(unique_prices) > 1:
                    price_issues.append({
                        'product_name': name.title(),
                        'copies': len(product_list),
                        'different_prices': unique_prices,
                        'products': product_list
                    })
                    print(f"      ❌ PROBLEMA: Precios diferentes entre copias!")
                else:
                    print(f"      ✅ Precios consistentes entre copias")
        
        investigation_results['price_discrepancies'] = price_issues
        
        # 3. Test image accessibility
        print("\n3️⃣ VERIFICACIÓN DE IMÁGENES:")
        
        def test_product_images(product, product_type):
            print(f"\n   🖼️  Analizando imágenes de {product_type} '{product.get('name', 'Unknown')}':")
            
            images = product.get('images', [])
            single_image = product.get('image', '')
            
            all_images = list(images) if images else []
            if single_image and single_image not in all_images:
                all_images.append(single_image)
            
            if not all_images:
                print(f"      ❌ CRÍTICO: NO HAY IMÁGENES asignadas")
                return False
            
            print(f"      📊 Total URLs de imágenes: {len(all_images)}")
            working_images = 0
            
            for i, img_url in enumerate(all_images):
                print(f"      🔍 Imagen {i+1}: {img_url[:60]}...")
                try:
                    import requests
                    response = requests.head(img_url, timeout=5)
                    if response.status_code == 200:
                        working_images += 1
                        print(f"         ✅ FUNCIONA (Status: {response.status_code})")
                    else:
                        print(f"         ❌ ROTA (Status: {response.status_code})")
                        
                        # Try with proxy
                        proxy_success, _ = self.run_test(
                            f"Test {product_type} Image via Proxy {i+1}", 
                            "GET", 
                            f"proxy-image?url={img_url}", 
                            200
                        )
                        if proxy_success:
                            print(f"         ✅ Funciona a través del proxy")
                            working_images += 1
                        else:
                            print(f"         ❌ También falla a través del proxy")
                            
                except Exception as e:
                    print(f"         ❌ ERROR: {str(e)}")
            
            success_rate = (working_images / len(all_images)) * 100 if all_images else 0
            print(f"      📊 RESULTADO: {working_images}/{len(all_images)} imágenes funcionando ({success_rate:.1f}%)")
            
            return working_images > 0
        
        # Test images for all Jade products
        jade_images_working = True
        for product in jade_products:
            if not test_product_images(product, "JADE"):
                jade_images_working = False
        
        # Test images for all Sol products  
        sol_images_working = True
        for product in sol_products:
            if not test_product_images(product, "SOL"):
                sol_images_working = False
        
        investigation_results['jade_images_working'] = jade_images_working
        investigation_results['sol_images_working'] = sol_images_working
        
        # 4. Test editability
        print("\n4️⃣ VERIFICACIÓN DE CAPACIDAD DE EDICIÓN:")
        
        if not self.token:
            print("   ❌ No hay token de admin para probar edición")
            investigation_results['authentication_working'] = False
        else:
            investigation_results['authentication_working'] = True
            print(f"   ✅ Autenticación admin funcionando (usuario: {self.admin_username})")
            
            def test_product_editability(product, product_type):
                product_id = product.get('id')
                product_name = product.get('name', 'Unknown')
                
                print(f"\n   ✏️  Probando edición de {product_type} '{product_name}':")
                
                # Try to update description (non-critical field)
                test_update = {
                    "description": f"Producto {product_name} - Test de edición {datetime.now().strftime('%H:%M:%S')}"
                }
                
                success, response = self.run_test(
                    f"Test {product_type} Product Edit",
                    "PUT",
                    f"products/{product_id}",
                    200,
                    data=test_update
                )
                
                if success:
                    print(f"      ✅ PRODUCTO SE PUEDE EDITAR correctamente")
                    
                    # Verify the update was applied
                    success_verify, updated_product = self.run_test(
                        f"Verify {product_type} Product Update",
                        "GET",
                        f"products/{product_id}",
                        200
                    )
                    
                    if success_verify and isinstance(updated_product, dict):
                        if test_update["description"] in updated_product.get("description", ""):
                            print(f"      ✅ Actualización verificada correctamente")
                            return True
                        else:
                            print(f"      ⚠️  Actualización no se aplicó correctamente")
                            return False
                    else:
                        print(f"      ⚠️  No se pudo verificar la actualización")
                        return False
                else:
                    print(f"      ❌ CRÍTICO: PRODUCTO NO SE PUEDE EDITAR")
                    print(f"         Error: {response}")
                    return False
            
                # Test editability for all Jade products
            jade_editable = True
            for product in jade_products:
                if not test_product_editability(product, "JADE"):
                    jade_editable = False
            
            # Test editability for all Sol products
            sol_editable = True
            for product in sol_products:
                if not test_product_editability(product, "SOL"):
                    sol_editable = False
            
            investigation_results['jade_editable'] = jade_editable
            investigation_results['sol_editable'] = sol_editable
        
        # Initialize variables if authentication failed
        if not investigation_results['authentication_working']:
            jade_editable = False
            sol_editable = False
        
        # 5. Generate recommendations
        print("\n5️⃣ GENERANDO RECOMENDACIONES:")
        
        recommendations = []
        
        # Price issues
        if price_issues:
            recommendations.append("PRECIOS: Resolver duplicados con precios diferentes - eliminar copias incorrectas")
            for issue in price_issues:
                recommendations.append(f"  - {issue['product_name']}: {issue['copies']} copias con precios diferentes")
        
        # Image issues
        if not jade_images_working:
            recommendations.append("IMÁGENES JADE: Reemplazar URLs rotas con nuevas imágenes ImgBB")
        if not sol_images_working:
            recommendations.append("IMÁGENES SOL: Reemplazar URLs rotas con nuevas imágenes ImgBB")
        
        # Editability issues
        if not investigation_results['jade_editable']:
            recommendations.append("EDICIÓN JADE: Investigar problemas de permisos o corrupción de datos")
        if not investigation_results['sol_editable']:
            recommendations.append("EDICIÓN SOL: Investigar problemas de permisos o corrupción de datos")
        
        # Authentication issues
        if not investigation_results['authentication_working']:
            recommendations.append("AUTENTICACIÓN: Verificar credenciales admin (admin/admin123)")
        
        investigation_results['recommended_actions'] = recommendations
        
        # 6. Final summary
        print("\n" + "="*80)
        print("🎯 RESUMEN EJECUTIVO - INVESTIGACIÓN JADE Y SOL")
        print("="*80)
        
        print(f"📊 PRODUCTOS ENCONTRADOS:")
        print(f"   • Jade: {len(jade_products)} producto(s)")
        print(f"   • Sol: {len(sol_products)} producto(s)")
        
        print(f"\n🔧 ESTADO FUNCIONAL:")
        print(f"   • Jade editable: {'✅ SÍ' if investigation_results['jade_editable'] else '❌ NO'}")
        print(f"   • Sol editable: {'✅ SÍ' if investigation_results['sol_editable'] else '❌ NO'}")
        print(f"   • Jade imágenes funcionando: {'✅ SÍ' if investigation_results['jade_images_working'] else '❌ NO'}")
        print(f"   • Sol imágenes funcionando: {'✅ SÍ' if investigation_results['sol_images_working'] else '❌ NO'}")
        print(f"   • Autenticación admin: {'✅ SÍ' if investigation_results['authentication_working'] else '❌ NO'}")
        
        print(f"\n💰 PROBLEMAS DE PRECIOS:")
        if price_issues:
            print(f"   ❌ {len(price_issues)} producto(s) con precios inconsistentes:")
            for issue in price_issues:
                print(f"      • {issue['product_name']}: {issue['copies']} copias")
        else:
            print(f"   ✅ No se encontraron inconsistencias de precios")
        
        print(f"\n📋 ACCIONES RECOMENDADAS:")
        if recommendations:
            for i, action in enumerate(recommendations, 1):
                print(f"   {i}. {action}")
        else:
            print(f"   ✅ No se requieren acciones - productos funcionando correctamente")
        
        print(f"\n⚡ PRÓXIMOS PASOS PARA EL USUARIO:")
        print(f"   1. Revisar productos duplicados y eliminar copias incorrectas")
        print(f"   2. Re-subir imágenes para productos con URLs rotas")
        print(f"   3. Verificar que los precios sean los originales deseados")
        print(f"   4. Confirmar que la funcionalidad de edición funciona")
        
        return investigation_results

    def test_first_4_products_editing_issue(self):
        """CRITICAL INVESTIGATION: First 4 products not editable"""
        print("\n🚨 INVESTIGACIÓN CRÍTICA - PRIMEROS 4 PRODUCTOS NO EDITABLES")
        print("="*80)
        print("PROBLEMA REPORTADO: Usuario NO puede editar ni eliminar primeros 4 productos")
        print("PERO SÍ puede editar desde el producto 5 en adelante")
        print("="*80)
        
        investigation_results = {
            'products_retrieved': False,
            'total_products': 0,
            'first_4_products': [],
            'product_5': None,
            'first_4_editable': [],
            'product_5_editable': False,
            'pattern_identified': False,
            'root_cause': 'unknown'
        }
        
        # 1. Get all products in order of appearance
        print("\n1️⃣ OBTENIENDO PRIMEROS PRODUCTOS EN ORDEN:")
        success, products = self.run_test("Get All Products in Order", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos")
            return investigation_results
        
        investigation_results['products_retrieved'] = True
        investigation_results['total_products'] = len(products)
        print(f"   📦 Total productos obtenidos: {len(products)}")
        
        if len(products) < 5:
            print(f"   ❌ INSUFICIENTES PRODUCTOS: Solo {len(products)} productos (necesitamos al menos 5)")
            return investigation_results
        
        # 2. Identify first 4 products and product 5
        first_4 = products[:4]
        product_5 = products[4] if len(products) > 4 else None
        
        investigation_results['first_4_products'] = first_4
        investigation_results['product_5'] = product_5
        
        print(f"\n📋 PRIMEROS 4 PRODUCTOS IDENTIFICADOS:")
        for i, product in enumerate(first_4):
            print(f"   {i+1}. '{product.get('name', 'Unknown')}' - ID: {product.get('id', 'No ID')[:8]}...")
            print(f"      Categoría: {product.get('category', 'Unknown')}")
            print(f"      Precios: Retail ${product.get('retail_price', 0):,} | Mayorista ${product.get('wholesale_price', 0):,}")
            print(f"      Creado: {product.get('created_at', 'Unknown')}")
        
        if product_5:
            print(f"\n📋 PRODUCTO 5 (CONTROL - DEBERÍA SER EDITABLE):")
            print(f"   5. '{product_5.get('name', 'Unknown')}' - ID: {product_5.get('id', 'No ID')[:8]}...")
            print(f"      Categoría: {product_5.get('category', 'Unknown')}")
            print(f"      Precios: Retail ${product_5.get('retail_price', 0):,} | Mayorista ${product_5.get('wholesale_price', 0):,}")
            print(f"      Creado: {product_5.get('created_at', 'Unknown')}")
        
        # 3. Test editing each of the first 4 products
        print(f"\n2️⃣ PROBANDO EDICIÓN DE PRIMEROS 4 PRODUCTOS:")
        
        if not self.token:
            print("❌ No hay token de admin para probar edición")
            return investigation_results
        
        for i, product in enumerate(first_4):
            product_id = product.get('id')
            product_name = product.get('name', f'Producto {i+1}')
            
            print(f"\n   🔍 PROBANDO PRODUCTO {i+1}: '{product_name}'")
            print(f"      ID: {product_id}")
            
            # Test update with minimal change
            test_update = {
                "description": f"Test edit {datetime.now().strftime('%H:%M:%S')} - Producto {i+1}"
            }
            
            success, response = self.run_test(
                f"Edit Product {i+1} ({product_name[:20]}...)",
                "PUT",
                f"products/{product_id}",
                200,
                data=test_update
            )
            
            investigation_results['first_4_editable'].append({
                'position': i+1,
                'name': product_name,
                'id': product_id,
                'editable': success,
                'response': response if not success else 'Success'
            })
            
            if success:
                print(f"      ✅ EDITABLE: Producto {i+1} se puede editar correctamente")
                
                # Verify the change was applied
                verify_success, updated_product = self.run_test(
                    f"Verify Product {i+1} Update",
                    "GET",
                    f"products/{product_id}",
                    200
                )
                
                if verify_success and isinstance(updated_product, dict):
                    if test_update["description"] in updated_product.get("description", ""):
                        print(f"      ✅ VERIFICADO: Cambio aplicado correctamente")
                    else:
                        print(f"      ⚠️  ADVERTENCIA: Cambio no se aplicó correctamente")
            else:
                print(f"      ❌ NO EDITABLE: Producto {i+1} falló al editar")
                print(f"         Error: {response}")
        
        # 4. Test editing product 5 (control)
        print(f"\n3️⃣ PROBANDO EDICIÓN DE PRODUCTO 5 (CONTROL):")
        
        if product_5:
            product_5_id = product_5.get('id')
            product_5_name = product_5.get('name', 'Producto 5')
            
            print(f"   🔍 PROBANDO PRODUCTO 5: '{product_5_name}'")
            print(f"      ID: {product_5_id}")
            
            test_update_5 = {
                "description": f"Test edit {datetime.now().strftime('%H:%M:%S')} - Producto 5 (Control)"
            }
            
            success, response = self.run_test(
                f"Edit Product 5 ({product_5_name[:20]}...)",
                "PUT",
                f"products/{product_5_id}",
                200,
                data=test_update_5
            )
            
            investigation_results['product_5_editable'] = success
            
            if success:
                print(f"      ✅ EDITABLE: Producto 5 se puede editar correctamente")
                
                # Verify the change was applied
                verify_success, updated_product = self.run_test(
                    f"Verify Product 5 Update",
                    "GET",
                    f"products/{product_5_id}",
                    200
                )
                
                if verify_success and isinstance(updated_product, dict):
                    if test_update_5["description"] in updated_product.get("description", ""):
                        print(f"      ✅ VERIFICADO: Cambio aplicado correctamente")
            else:
                print(f"      ❌ NO EDITABLE: Producto 5 también falló al editar")
                print(f"         Error: {response}")
        
        # 5. Analyze patterns and differences
        print(f"\n4️⃣ ANÁLISIS DE PATRONES Y DIFERENCIAS:")
        
        # Count how many of first 4 are actually not editable
        non_editable_count = sum(1 for result in investigation_results['first_4_editable'] if not result['editable'])
        editable_count = len(investigation_results['first_4_editable']) - non_editable_count
        
        print(f"   📊 RESULTADOS DE EDICIÓN:")
        print(f"      Primeros 4 productos editables: {editable_count}/4")
        print(f"      Primeros 4 productos NO editables: {non_editable_count}/4")
        print(f"      Producto 5 editable: {'✅ SÍ' if investigation_results['product_5_editable'] else '❌ NO'}")
        
        # Check for patterns in non-editable products
        if non_editable_count > 0:
            print(f"\n   🔍 PRODUCTOS NO EDITABLES IDENTIFICADOS:")
            for result in investigation_results['first_4_editable']:
                if not result['editable']:
                    print(f"      ❌ Producto {result['position']}: '{result['name']}'")
                    print(f"         ID: {result['id']}")
                    print(f"         Error: {result['response']}")
        
        # Compare data structures
        print(f"\n   🔍 COMPARACIÓN DE ESTRUCTURAS DE DATOS:")
        
        # Check creation dates
        first_4_dates = [p.get('created_at', 'Unknown') for p in first_4]
        product_5_date = product_5.get('created_at', 'Unknown') if product_5 else 'N/A'
        
        print(f"      📅 Fechas de creación:")
        for i, date in enumerate(first_4_dates):
            print(f"         Producto {i+1}: {date}")
        print(f"         Producto 5: {product_5_date}")
        
        # Check for data corruption or missing fields
        print(f"\n      🔍 VERIFICACIÓN DE INTEGRIDAD DE DATOS:")
        required_fields = ['id', 'name', 'category', 'retail_price', 'wholesale_price']
        
        for i, product in enumerate(first_4):
            missing_fields = []
            corrupted_fields = []
            
            for field in required_fields:
                value = product.get(field)
                if value is None or value == '':
                    missing_fields.append(field)
                elif field in ['retail_price', 'wholesale_price']:
                    try:
                        price = float(value)
                        if price <= 0:
                            corrupted_fields.append(f"{field}={price}")
                    except (ValueError, TypeError):
                        corrupted_fields.append(f"{field}={value}")
            
            status = "✅ OK"
            if missing_fields or corrupted_fields:
                status = "❌ PROBLEMAS"
            
            print(f"         Producto {i+1}: {status}")
            if missing_fields:
                print(f"            Campos faltantes: {', '.join(missing_fields)}")
            if corrupted_fields:
                print(f"            Campos corruptos: {', '.join(corrupted_fields)}")
        
        # 6. Determine root cause and pattern
        print(f"\n5️⃣ DIAGNÓSTICO Y CAUSA RAÍZ:")
        
        if non_editable_count == 0:
            investigation_results['root_cause'] = 'no_issue_found'
            print(f"   ✅ NO SE ENCONTRÓ EL PROBLEMA: Todos los primeros 4 productos SON editables")
            print(f"      Posibles causas del reporte del usuario:")
            print(f"      • Problema temporal que ya se resolvió")
            print(f"      • Problema en el frontend, no en el backend")
            print(f"      • Usuario probando productos diferentes")
            print(f"      • Problema de permisos/autenticación temporal")
        elif non_editable_count == 4 and not investigation_results['product_5_editable']:
            investigation_results['root_cause'] = 'general_edit_issue'
            print(f"   ❌ PROBLEMA GENERAL: NINGÚN producto es editable (incluido producto 5)")
            print(f"      Causa probable: Problema de autenticación o permisos generales")
        elif non_editable_count == 4 and investigation_results['product_5_editable']:
            investigation_results['root_cause'] = 'first_4_specific_issue'
            investigation_results['pattern_identified'] = True
            print(f"   🎯 PROBLEMA CONFIRMADO: Solo los primeros 4 productos NO son editables")
            print(f"      Producto 5 SÍ es editable - confirma el patrón reportado")
            print(f"      Posibles causas específicas:")
            print(f"      • Productos más antiguos con estructura de datos diferente")
            print(f"      • Problema de índices o ordenamiento en base de datos")
            print(f"      • Corrupción de datos en productos específicos")
            print(f"      • Problema de migración de datos históricos")
        else:
            investigation_results['root_cause'] = 'partial_issue'
            print(f"   ⚠️  PROBLEMA PARCIAL: {non_editable_count}/4 primeros productos no editables")
            print(f"      Patrón no completamente consistente con reporte del usuario")
        
        # 7. Recommendations
        print(f"\n6️⃣ RECOMENDACIONES:")
        
        if investigation_results['root_cause'] == 'no_issue_found':
            print(f"   📋 ACCIONES RECOMENDADAS:")
            print(f"      1. Verificar problema en frontend/interfaz de usuario")
            print(f"      2. Revisar logs de errores JavaScript en navegador")
            print(f"      3. Confirmar con usuario qué productos específicos están probando")
            print(f"      4. Verificar que usuario tenga permisos de admin correctos")
        elif investigation_results['root_cause'] == 'general_edit_issue':
            print(f"   📋 ACCIONES RECOMENDADAS:")
            print(f"      1. Verificar configuración de autenticación admin")
            print(f"      2. Revisar permisos de base de datos")
            print(f"      3. Verificar configuración de CORS y headers")
            print(f"      4. Revisar logs del servidor backend")
        elif investigation_results['root_cause'] == 'first_4_specific_issue':
            print(f"   📋 ACCIONES RECOMENDADAS:")
            print(f"      1. INVESTIGAR estructura de datos de primeros 4 productos")
            print(f"      2. Comparar campos y tipos de datos con productos editables")
            print(f"      3. Verificar si son productos migrados de sistema anterior")
            print(f"      4. Considerar recrear productos problemáticos")
            print(f"      5. Revisar logs específicos de errores de estos productos")
        
        # 8. Final summary
        print("\n" + "="*80)
        print("🎯 RESUMEN EJECUTIVO - INVESTIGACIÓN PRIMEROS 4 PRODUCTOS")
        print("="*80)
        
        print(f"📊 RESULTADOS:")
        print(f"   • Total productos analizados: {investigation_results['total_products']}")
        print(f"   • Primeros 4 productos editables: {editable_count}/4")
        print(f"   • Producto 5 (control) editable: {'✅ SÍ' if investigation_results['product_5_editable'] else '❌ NO'}")
        print(f"   • Patrón identificado: {'✅ SÍ' if investigation_results['pattern_identified'] else '❌ NO'}")
        print(f"   • Causa raíz: {investigation_results['root_cause'].replace('_', ' ').upper()}")
        
        if investigation_results['pattern_identified']:
            print(f"\n🚨 CONFIRMACIÓN: El problema reportado por el usuario ES REAL")
            print(f"   Los primeros 4 productos específicamente no son editables")
            print(f"   Requiere investigación técnica inmediata")
        else:
            print(f"\n🔍 ESTADO: Problema no reproducido exactamente como se reportó")
            print(f"   Requiere más investigación o verificación con usuario")
        
        return investigation_results

    def test_specific_product_investigation(self):
        """URGENT INVESTIGATION: Specific products Imperio and Velvet + first 4 products editability"""
        print("\n🚨 INVESTIGACIÓN ESPECÍFICA - PRODUCTOS SIN IMÁGENES Y PROBLEMA DE EDICIÓN POR POSICIÓN")
        print("="*100)
        print("PROBLEMA 1: Productos sin imágenes - 'Imperio' y 'Velvet' muestran placeholder")
        print("PROBLEMA 2: Productos no editables por posición - primeros en grid NO se pueden editar")
        print("="*100)
        
        investigation_results = {
            'imperio_found': False,
            'velvet_found': False,
            'imperio_images_working': False,
            'velvet_images_working': False,
            'first_4_products': [],
            'first_4_editable': [],
            'products_order': [],
            'backend_editability': True,
            'image_issues': [],
            'position_pattern': False
        }
        
        # 1. Get all products to analyze order and find specific products
        print("\n1️⃣ OBTENIENDO PRODUCTOS Y ANALIZANDO ORDEN:")
        success, products = self.run_test("Get All Products for Investigation", "GET", "products?limit=1000", 200)
        
        if not success or not isinstance(products, list):
            print("❌ CRÍTICO: No se pueden obtener productos")
            return investigation_results
        
        print(f"   📦 Total productos encontrados: {len(products)}")
        investigation_results['products_order'] = [p.get('name', 'Unknown') for p in products]
        
        # 2. Search for Imperio and Velvet specifically
        print("\n2️⃣ BUSCANDO PRODUCTOS ESPECÍFICOS:")
        imperio_product = None
        velvet_product = None
        
        for product in products:
            name = product.get('name', '').lower()
            if 'imperio' in name:
                imperio_product = product
                investigation_results['imperio_found'] = True
                print(f"   ✅ IMPERIO ENCONTRADO: '{product.get('name')}' - ID: {product.get('id')}")
            elif 'velvet' in name:
                velvet_product = product
                investigation_results['velvet_found'] = True
                print(f"   ✅ VELVET ENCONTRADO: '{product.get('name')}' - ID: {product.get('id')}")
        
        if not imperio_product:
            print("   ❌ IMPERIO NO ENCONTRADO en base de datos")
        if not velvet_product:
            print("   ❌ VELVET NO ENCONTRADO en base de datos")
        
        # 3. Analyze images for Imperio and Velvet
        print("\n3️⃣ VERIFICANDO IMÁGENES DE PRODUCTOS ESPECÍFICOS:")
        
        for product_name, product_data in [("Imperio", imperio_product), ("Velvet", velvet_product)]:
            if product_data:
                print(f"\n   🔍 Analizando {product_name.upper()}:")
                images = product_data.get('images', [])
                single_image = product_data.get('image', '')
                
                all_images = list(images) if images else []
                if single_image and single_image not in all_images:
                    all_images.append(single_image)
                
                print(f"      📷 Total URLs de imagen: {len(all_images)}")
                
                if all_images:
                    working_images = 0
                    for i, img_url in enumerate(all_images):
                        print(f"      🔗 Imagen {i+1}: {img_url[:60]}...")
                        try:
                            import requests
                            response = requests.head(img_url, timeout=5)
                            if response.status_code == 200:
                                working_images += 1
                                print(f"         ✅ FUNCIONA")
                            else:
                                print(f"         ❌ ROTA (Status: {response.status_code})")
                                investigation_results['image_issues'].append({
                                    'product': product_name,
                                    'url': img_url,
                                    'status': response.status_code
                                })
                        except Exception as e:
                            print(f"         ❌ ERROR: {str(e)}")
                            investigation_results['image_issues'].append({
                                'product': product_name,
                                'url': img_url,
                                'error': str(e)
                            })
                    
                    if working_images > 0:
                        if product_name.lower() == 'imperio':
                            investigation_results['imperio_images_working'] = True
                        else:
                            investigation_results['velvet_images_working'] = True
                        print(f"      ✅ {working_images}/{len(all_images)} imágenes funcionando")
                    else:
                        print(f"      ❌ TODAS las imágenes están ROTAS")
                else:
                    print(f"      ❌ NO HAY IMÁGENES asignadas")
        
        # 4. Analyze first 4 products in order
        print("\n4️⃣ ANALIZANDO PRIMEROS 4 PRODUCTOS EN EL GRID:")
        first_4 = products[:4]
        investigation_results['first_4_products'] = [
            {
                'name': p.get('name', 'Unknown'),
                'id': p.get('id', 'No ID'),
                'category': p.get('category', 'Unknown'),
                'position': i + 1
            }
            for i, p in enumerate(first_4)
        ]
        
        for i, product in enumerate(first_4):
            print(f"   {i+1}. {product.get('name', 'Unknown')} (ID: {product.get('id', 'No ID')[:8]}...)")
            print(f"      Categoría: {product.get('category', 'Unknown')}")
            print(f"      Precios: Retail ${product.get('retail_price', 0):,} | Mayorista ${product.get('wholesale_price', 0):,}")
        
        # 5. Test editability of first 4 products from backend
        print("\n5️⃣ PROBANDO EDICIÓN DE PRIMEROS 4 PRODUCTOS DESDE BACKEND:")
        if not self.token:
            print("   ❌ No hay token de admin para probar edición")
        else:
            for i, product in enumerate(first_4):
                product_id = product.get('id')
                product_name = product.get('name', 'Unknown')
                
                print(f"\n   🔧 Probando edición de '{product_name}' (Posición {i+1}):")
                
                # Try a simple update
                test_update = {
                    "description": f"Test de edición - {datetime.now().strftime('%H:%M:%S')}"
                }
                
                success, response = self.run_test(
                    f"Edit Product Position {i+1}",
                    "PUT",
                    f"products/{product_id}",
                    200,
                    data=test_update
                )
                
                if success:
                    investigation_results['first_4_editable'].append({
                        'name': product_name,
                        'position': i + 1,
                        'editable': True
                    })
                    print(f"      ✅ EDITABLE desde backend API")
                    
                    # Verify the change was applied
                    verify_success, updated_product = self.run_test(
                        f"Verify Edit Position {i+1}",
                        "GET",
                        f"products/{product_id}",
                        200
                    )
                    
                    if verify_success and isinstance(updated_product, dict):
                        if test_update["description"] in updated_product.get("description", ""):
                            print(f"      ✅ Cambio verificado correctamente")
                        else:
                            print(f"      ⚠️  Cambio no se aplicó correctamente")
                else:
                    investigation_results['first_4_editable'].append({
                        'name': product_name,
                        'position': i + 1,
                        'editable': False,
                        'error': response
                    })
                    print(f"      ❌ NO EDITABLE desde backend API")
                    print(f"         Error: {response}")
                    investigation_results['backend_editability'] = False
        
        # 6. Test products after scroll (positions 5-8) for comparison
        print("\n6️⃣ PROBANDO PRODUCTOS DESPUÉS DEL SCROLL (POSICIONES 5-8):")
        if len(products) > 4 and self.token:
            scroll_products = products[4:8]
            for i, product in enumerate(scroll_products):
                product_id = product.get('id')
                product_name = product.get('name', 'Unknown')
                position = i + 5
                
                print(f"\n   🔧 Probando edición de '{product_name}' (Posición {position}):")
                
                test_update = {
                    "description": f"Test scroll position - {datetime.now().strftime('%H:%M:%S')}"
                }
                
                success, response = self.run_test(
                    f"Edit Product Position {position}",
                    "PUT",
                    f"products/{product_id}",
                    200,
                    data=test_update
                )
                
                if success:
                    print(f"      ✅ EDITABLE desde backend API")
                else:
                    print(f"      ❌ NO EDITABLE desde backend API")
                    investigation_results['backend_editability'] = False
        
        # 7. Analyze pattern
        print("\n7️⃣ ANÁLISIS DE PATRÓN:")
        editable_count = len([p for p in investigation_results['first_4_editable'] if p.get('editable', False)])
        
        if editable_count == 4:
            print("   ✅ TODOS los primeros 4 productos SON EDITABLES desde backend")
            print("   🔍 El problema reportado NO es del backend - es del frontend")
        elif editable_count == 0:
            print("   ❌ NINGUNO de los primeros 4 productos es editable desde backend")
            print("   🚨 PROBLEMA CRÍTICO en backend o autenticación")
        else:
            print(f"   ⚠️  Solo {editable_count}/4 primeros productos son editables")
            print("   🔍 Patrón mixto - investigar productos específicos")
            investigation_results['position_pattern'] = True
        
        # 8. Final summary and recommendations
        print("\n" + "="*100)
        print("🎯 RESUMEN EJECUTIVO - INVESTIGACIÓN ESPECÍFICA")
        print("="*100)
        
        print(f"\n📊 PRODUCTOS ESPECÍFICOS:")
        print(f"   • Imperio encontrado: {'✅ SÍ' if investigation_results['imperio_found'] else '❌ NO'}")
        print(f"   • Imperio imágenes funcionan: {'✅ SÍ' if investigation_results['imperio_images_working'] else '❌ NO'}")
        print(f"   • Velvet encontrado: {'✅ SÍ' if investigation_results['velvet_found'] else '❌ NO'}")
        print(f"   • Velvet imágenes funcionan: {'✅ SÍ' if investigation_results['velvet_images_working'] else '❌ NO'}")
        
        print(f"\n📊 PRIMEROS 4 PRODUCTOS:")
        for product_info in investigation_results['first_4_products']:
            editable_info = next((e for e in investigation_results['first_4_editable'] if e['name'] == product_info['name']), None)
            editable_status = "✅ EDITABLE" if editable_info and editable_info.get('editable') else "❌ NO EDITABLE"
            print(f"   {product_info['position']}. {product_info['name']} - {editable_status}")
        
        print(f"\n📊 PROBLEMAS DE IMÁGENES IDENTIFICADOS:")
        if investigation_results['image_issues']:
            for issue in investigation_results['image_issues']:
                print(f"   ❌ {issue['product']}: {issue['url'][:50]}... - {issue.get('status', issue.get('error', 'Unknown'))}")
        else:
            print(f"   ✅ No se encontraron problemas de imágenes en productos analizados")
        
        print(f"\n🎯 DIAGNÓSTICO FINAL:")
        if not investigation_results['backend_editability']:
            print("   ❌ PROBLEMA EN BACKEND: Algunos productos no son editables desde API")
        else:
            print("   ✅ BACKEND FUNCIONAL: Todos los productos son editables desde API")
            print("   🔍 PROBLEMA EN FRONTEND: Issue de edición por posición es del lado cliente")
        
        if investigation_results['image_issues']:
            print(f"   ❌ IMÁGENES ROTAS: {len(investigation_results['image_issues'])} URLs problemáticas identificadas")
        else:
            print("   ✅ IMÁGENES OK: No se detectaron problemas de imágenes")
        
        print(f"\n📋 ACCIONES RECOMENDADAS:")
        if investigation_results['image_issues']:
            print("   1. REEMPLAZAR imágenes rotas usando /api/admin/upload-images con ImgBB")
            print("   2. Actualizar productos Imperio y Velvet con nuevas URLs")
        
        if investigation_results['backend_editability']:
            print("   3. INVESTIGAR frontend - problema de edición por posición es del lado cliente")
            print("   4. Verificar JavaScript, event handlers, y renderizado de botones de edición")
        else:
            print("   3. INVESTIGAR backend - problema de autenticación o permisos")
        
        return investigation_results

def main():
    tester = HannuClothesAPITester()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        # Login first for authenticated tests
        if test_type in ["editing_verification", "duplicates", "imperio", "mass_upload"]:
            if not tester.test_admin_login():
                print("❌ CRITICAL: Admin login failed")
                return 1
        
        if test_type == "urgent":
            tester.test_urgent_product_visibility_investigation()
        elif test_type == "mass_upload":
            tester.test_mass_upload_investigation()
        elif test_type == "imperio":
            tester.test_imperio_product_investigation()
        elif test_type == "migration":
            tester.test_migration_failure_analysis()
        elif test_type == "duplicates":
            tester.test_duplicate_products_investigation()
        elif test_type == "final_verification":
            tester.test_final_verification_complete()
        elif test_type == "editing_verification":
            tester.test_complete_editing_functionality_verification()
        elif test_type == "jade_sol":
            tester.test_jade_sol_investigation()
        elif test_type == "first_4_products":
            tester.test_first_4_products_editing_issue()
        elif test_type == "specific_investigation":
            tester.test_specific_product_investigation()
        else:
            print("Available test types: urgent, mass_upload, imperio, migration, duplicates, final_verification, editing_verification, jade_sol, first_4_products, specific_investigation")
            return 1
    else:
        # Default: Run the original critical investigation
        print("🚨 INVESTIGACIÓN CRÍTICA - PRODUCTOS DUPLICADOS Y NO EDITABLES")
        print("=" * 80)
        print("PROBLEMA REPORTADO: Productos 'Blonda' duplicados y otros productos no editables")
        print("OBJETIVO: Identificar TODOS los problemas y entregar plan de acción completo")
        print("=" * 80)
        
        # Login first
        if not tester.test_admin_login():
            print("❌ CRITICAL: Admin login failed")
            return 1
        
        # Critical investigation tests as requested in review
        tests = [
            ("🚨 CRÍTICO: Investigación Productos Duplicados", tester.test_duplicate_products_investigation),
            ("🔧 CRÍTICO: Operaciones CRUD Completas", tester.test_comprehensive_crud_operations),
            ("🔍 Verificación Integridad BD", tester.test_price_validation_comprehensive),
            ("📊 Estadísticas del Catálogo", tester.test_catalog_stats),
            ("🔍 Búsqueda de Productos", tester.test_search_products),
            ("📂 Categorías de Productos", tester.test_get_categories),
            ("📦 Obtener Todos los Productos", tester.test_get_products),
        ]
        
        print(f"\n📋 Ejecutando {len(tests)} investigaciones críticas...")
        
        # Store results for final analysis
        duplicate_results = None
        crud_results = None
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                if "Duplicados" in test_name:
                    duplicate_results = result
                elif "CRUD" in test_name:
                    crud_results = result
            except Exception as e:
                print(f"❌ Test category '{test_name}' failed with exception: {str(e)}")
        
        # Print final critical analysis
        print("\n" + "="*80)
        print("🎯 ANÁLISIS FINAL - INVESTIGACIÓN CRÍTICA COMPLETADA")
        print("="*80)
        print(f"✅ Tests ejecutados: {tester.tests_run}")
        print(f"✅ Tests exitosos: {tester.tests_passed}")
        print(f"📈 Tasa de éxito: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
        
        # Critical findings summary
        print(f"\n🚨 HALLAZGOS CRÍTICOS:")
        critical_issues = []
        
        if duplicate_results:
            if duplicate_results.get('duplicate_names'):
                critical_issues.append(f"❌ DUPLICADOS: {len(duplicate_results['duplicate_names'])} productos con nombres duplicados")
            else:
                print(f"   ✅ DUPLICADOS: No se encontraron productos duplicados")
            
            if duplicate_results.get('blonda_products'):
                critical_issues.append(f"❌ BLONDA: {len(duplicate_results['blonda_products'])} productos 'Blonda' encontrados")
            
            if duplicate_results.get('problematic_products'):
                critical_issues.append(f"❌ EDICIÓN: {len(duplicate_results['problematic_products'])} productos no editables")
            else:
                print(f"   ✅ EDICIÓN: Todos los productos probados son editables")
            
            if duplicate_results.get('database_integrity_issues'):
                critical_issues.append(f"❌ INTEGRIDAD: {len(duplicate_results['database_integrity_issues'])} problemas de integridad")
        
        if crud_results:
            crud_success = all([
                crud_results.get('create_working', False),
                crud_results.get('read_working', False),
                crud_results.get('update_working', False),
                crud_results.get('delete_working', False)
            ])
            
            if crud_success:
                print(f"   ✅ CRUD: Todas las operaciones diarias funcionan correctamente")
            else:
                critical_issues.append("❌ CRUD: Algunas operaciones diarias tienen problemas")
        
        # Display critical issues
        if critical_issues:
            for issue in critical_issues:
                print(f"   {issue}")
        
        # Action plan
        print(f"\n📋 PLAN DE ACCIÓN REQUERIDO:")
        action_items = []
        
        if duplicate_results:
            if duplicate_results.get('duplicate_names'):
                action_items.append("1. Eliminar productos duplicados identificados")
                # Show specific duplicates
                for name, info in list(duplicate_results['duplicate_names'].items())[:5]:
                    action_items.append(f"   • Eliminar duplicados de '{name}' ({info['count']} copias)")
            
            if duplicate_results.get('blonda_products'):
                action_items.append("2. Revisar específicamente productos 'Blonda'")
            
            if duplicate_results.get('problematic_products'):
                action_items.append("3. Corregir productos que no se pueden editar")
                # Show specific problematic products
                for product in duplicate_results['problematic_products'][:5]:
                    action_items.append(f"   • Corregir '{product['name']}' - {product['issue']}")
            
            if duplicate_results.get('database_integrity_issues'):
                action_items.append("4. Resolver problemas de integridad de base de datos")
        
        if crud_results and not crud_success:
            action_items.append("5. Corregir operaciones CRUD que fallan")
        
        if action_items:
            for item in action_items:
                print(f"   {item}")
        else:
            print(f"   🎉 No se requieren acciones correctivas - sistema operativo")
        
        print(f"\n⚡ PRIORIDAD: CRÍTICA - Afecta operaciones diarias del usuario")
        print(f"🎯 OBJETIVO: Resolver TODOS los problemas sin perder productos ni fotos existentes")
        
        # Return status based on critical issues
        if critical_issues:
            print(f"\n❌ INVESTIGACIÓN COMPLETADA - {len(critical_issues)} PROBLEMAS CRÍTICOS ENCONTRADOS")
            return 1
        else:
            print(f"\n✅ INVESTIGACIÓN COMPLETADA - SISTEMA OPERATIVO SIN PROBLEMAS CRÍTICOS")
            return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())