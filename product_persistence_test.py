#!/usr/bin/env python3
"""
CRITICAL BUG TESTING: Product Disappearing Issue
==============================================

This test specifically addresses the user's reported issue:
"When I add a product from the admin panel, the product disappears immediately"

The test will:
1. Count products before creation
2. Login as admin
3. Create a new product with realistic data
4. Verify the product was created and has an ID
5. Count products after creation
6. Verify the new product appears in the product list
7. Wait and check again to ensure persistence
"""

import requests
import json
import time
from datetime import datetime

class ProductPersistenceTest:
    def __init__(self):
        self.base_url = "https://fashion-admin-4.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.admin_username = "admin"
        self.admin_password = "admin123"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers and error handling"""
        url = f"{self.api_url}/{endpoint}" if endpoint else f"{self.api_url}/"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=15)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=15)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=15)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=15)
                
            self.log(f"{method} {url} -> Status: {response.status_code}")
            
            if response.status_code != expected_status:
                self.log(f"UNEXPECTED STATUS: Expected {expected_status}, got {response.status_code}", "ERROR")
                self.log(f"Response: {response.text[:300]}", "ERROR")
                return False, None
                
            try:
                return True, response.json()
            except:
                return True, response.text
                
        except requests.exceptions.RequestException as e:
            self.log(f"REQUEST FAILED: {str(e)}", "ERROR")
            return False, None
            
    def step_1_count_initial_products(self):
        """Step 1: Count products before creating new one"""
        self.log("STEP 1: Counting initial products...")
        
        success, products = self.make_request('GET', 'products')
        if not success:
            self.log("FAILED to get initial product count", "ERROR")
            return False
            
        if not isinstance(products, list):
            self.log(f"UNEXPECTED RESPONSE: Expected list, got {type(products)}", "ERROR")
            return False
            
        self.initial_count = len(products)
        self.log(f"Initial product count: {self.initial_count}")
        
        # Log some existing product names for reference
        if products:
            self.log("Existing products (first 5):")
            for i, product in enumerate(products[:5]):
                name = product.get('name', 'Unknown')
                self.log(f"  {i+1}. {name}")
                
        return True
        
    def step_2_admin_login(self):
        """Step 2: Login as admin to get authentication token"""
        self.log("STEP 2: Logging in as admin...")
        
        login_data = {
            "username": self.admin_username,
            "password": self.admin_password
        }
        
        success, response = self.make_request('POST', 'admin/login', login_data)
        if not success:
            self.log("FAILED to login as admin", "ERROR")
            return False
            
        if not isinstance(response, dict) or 'access_token' not in response:
            self.log(f"INVALID LOGIN RESPONSE: {response}", "ERROR")
            return False
            
        self.token = response['access_token']
        self.log("Admin login successful, token obtained")
        return True
        
    def step_3_create_test_product(self):
        """Step 3: Create a new product with realistic data"""
        self.log("STEP 3: Creating test product...")
        
        # Use realistic product data similar to what a user would enter
        self.test_product_data = {
            "name": "Blusa Elegante de Prueba",
            "description": "Blusa elegante para ocasiones especiales, confeccionada en tela de alta calidad con detalles únicos.",
            "retail_price": 89000,
            "wholesale_price": 62300,  # 70% of retail price
            "category": "blusas",
            "images": [
                "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400",
                "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&crop=entropy"
            ],
            "colors": ["Blanco", "Negro", "Azul Marino"],
            "composition": "95% Algodón, 5% Elastano",
            "sizes": ["XS", "S", "M", "L", "XL"],
            "stock": {"XS": 3, "S": 8, "M": 12, "L": 10, "XL": 5},
            "specifications": "Blusa de corte recto, manga larga, cuello en V",
            "care": "Lavar a máquina en agua fría, no usar blanqueador"
        }
        
        self.log(f"Creating product: {self.test_product_data['name']}")
        self.log(f"Category: {self.test_product_data['category']}")
        self.log(f"Price: ${self.test_product_data['retail_price']:,} / ${self.test_product_data['wholesale_price']:,}")
        self.log(f"Images: {len(self.test_product_data['images'])} images")
        self.log(f"Colors: {', '.join(self.test_product_data['colors'])}")
        
        success, response = self.make_request('POST', 'products', self.test_product_data)
        if not success:
            self.log("FAILED to create product", "ERROR")
            return False
            
        if not isinstance(response, dict) or 'id' not in response:
            self.log(f"INVALID CREATE RESPONSE: {response}", "ERROR")
            return False
            
        self.created_product_id = response['id']
        self.created_product_name = response.get('name', 'Unknown')
        
        self.log(f"✅ Product created successfully!")
        self.log(f"Product ID: {self.created_product_id}")
        self.log(f"Product Name: {self.created_product_name}")
        
        # Verify the response contains expected data
        if response.get('images') == self.test_product_data['images']:
            self.log("✅ Images array preserved correctly")
        else:
            self.log(f"⚠️ Images mismatch: Expected {self.test_product_data['images']}, Got {response.get('images')}", "WARNING")
            
        if response.get('colors') == self.test_product_data['colors']:
            self.log("✅ Colors array preserved correctly")
        else:
            self.log(f"⚠️ Colors mismatch: Expected {self.test_product_data['colors']}, Got {response.get('colors')}", "WARNING")
            
        return True
        
    def step_4_verify_immediate_persistence(self):
        """Step 4: Immediately verify the product appears in the catalog"""
        self.log("STEP 4: Verifying immediate persistence...")
        
        # Get all products immediately after creation
        success, products = self.make_request('GET', 'products')
        if not success:
            self.log("FAILED to get products after creation", "ERROR")
            return False
            
        if not isinstance(products, list):
            self.log(f"UNEXPECTED RESPONSE: Expected list, got {type(products)}", "ERROR")
            return False
            
        self.immediate_count = len(products)
        self.log(f"Product count after creation: {self.immediate_count}")
        self.log(f"Count difference: {self.immediate_count - self.initial_count}")
        
        # Check if our product is in the list
        found_product = None
        for product in products:
            if product.get('id') == self.created_product_id:
                found_product = product
                break
                
        if found_product:
            self.log("✅ PRODUCT FOUND in immediate catalog check!")
            self.log(f"Found product: {found_product.get('name')}")
            self.log(f"Product category: {found_product.get('category')}")
            self.log(f"Product images: {len(found_product.get('images', []))} images")
            self.log(f"Product colors: {len(found_product.get('colors', []))} colors")
            return True
        else:
            self.log("❌ CRITICAL: PRODUCT NOT FOUND in immediate catalog check!", "ERROR")
            self.log("This confirms the user's reported bug: product disappears immediately", "ERROR")
            
            # List all product names for debugging
            self.log("Current products in catalog:")
            for i, product in enumerate(products):
                name = product.get('name', 'Unknown')
                product_id = product.get('id', 'No ID')
                self.log(f"  {i+1}. {name} (ID: {product_id[:8]}...)")
                
            return False
            
    def step_5_wait_and_recheck(self):
        """Step 5: Wait a few seconds and check again for persistence"""
        self.log("STEP 5: Waiting 5 seconds and rechecking persistence...")
        
        time.sleep(5)
        
        success, products = self.make_request('GET', 'products')
        if not success:
            self.log("FAILED to get products after wait", "ERROR")
            return False
            
        if not isinstance(products, list):
            self.log(f"UNEXPECTED RESPONSE: Expected list, got {type(products)}", "ERROR")
            return False
            
        self.final_count = len(products)
        self.log(f"Product count after 5-second wait: {self.final_count}")
        
        # Check if our product is still there
        found_product = None
        for product in products:
            if product.get('id') == self.created_product_id:
                found_product = product
                break
                
        if found_product:
            self.log("✅ PRODUCT STILL FOUND after wait - persistence confirmed!")
            return True
        else:
            self.log("❌ CRITICAL: PRODUCT DISAPPEARED after wait!", "ERROR")
            self.log("This confirms the user's bug report", "ERROR")
            return False
            
    def step_6_test_specific_product_retrieval(self):
        """Step 6: Try to get the specific product by ID"""
        self.log("STEP 6: Testing specific product retrieval by ID...")
        
        success, product = self.make_request('GET', f'products/{self.created_product_id}')
        if success:
            self.log("✅ Product can be retrieved by ID")
            self.log(f"Retrieved product: {product.get('name')}")
            return True
        else:
            self.log("❌ CRITICAL: Product cannot be retrieved by ID", "ERROR")
            return False
            
    def step_7_test_category_filtering(self):
        """Step 7: Test if product appears when filtering by category"""
        self.log("STEP 7: Testing category filtering...")
        
        category = self.test_product_data['category']
        success, products = self.make_request('GET', f'products?category={category}')
        if not success:
            self.log(f"FAILED to get products for category {category}", "ERROR")
            return False
            
        if not isinstance(products, list):
            self.log(f"UNEXPECTED RESPONSE: Expected list, got {type(products)}", "ERROR")
            return False
            
        self.log(f"Products in '{category}' category: {len(products)}")
        
        # Check if our product is in the category results
        found_in_category = False
        for product in products:
            if product.get('id') == self.created_product_id:
                found_in_category = True
                break
                
        if found_in_category:
            self.log(f"✅ Product found in '{category}' category filter")
            return True
        else:
            self.log(f"❌ Product NOT found in '{category}' category filter", "ERROR")
            return False
            
    def cleanup(self):
        """Clean up the test product"""
        self.log("CLEANUP: Removing test product...")
        
        if hasattr(self, 'created_product_id'):
            success, _ = self.make_request('DELETE', f'products/{self.created_product_id}')
            if success:
                self.log("✅ Test product cleaned up successfully")
            else:
                self.log("⚠️ Could not clean up test product", "WARNING")
                
    def run_full_test(self):
        """Run the complete product persistence test"""
        self.log("🚀 STARTING PRODUCT PERSISTENCE TEST")
        self.log("=" * 60)
        self.log("Testing user-reported bug: 'Products disappear immediately after creation'")
        self.log("=" * 60)
        
        test_steps = [
            ("Count Initial Products", self.step_1_count_initial_products),
            ("Admin Login", self.step_2_admin_login),
            ("Create Test Product", self.step_3_create_test_product),
            ("Verify Immediate Persistence", self.step_4_verify_immediate_persistence),
            ("Wait and Recheck", self.step_5_wait_and_recheck),
            ("Test Specific Product Retrieval", self.step_6_test_specific_product_retrieval),
            ("Test Category Filtering", self.step_7_test_category_filtering),
        ]
        
        results = {}
        
        for step_name, step_func in test_steps:
            self.log(f"\n{'='*20} {step_name} {'='*20}")
            try:
                result = step_func()
                results[step_name] = result
                if result:
                    self.log(f"✅ {step_name} PASSED")
                else:
                    self.log(f"❌ {step_name} FAILED", "ERROR")
                    # Continue with other tests even if one fails
            except Exception as e:
                self.log(f"❌ {step_name} FAILED with exception: {str(e)}", "ERROR")
                results[step_name] = False
                
        # Cleanup
        try:
            self.cleanup()
        except Exception as e:
            self.log(f"Cleanup failed: {str(e)}", "WARNING")
            
        # Final report
        self.log("\n" + "=" * 60)
        self.log("🎯 PRODUCT PERSISTENCE TEST RESULTS")
        self.log("=" * 60)
        
        passed_steps = sum(results.values())
        total_steps = len(results)
        
        for step_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} - {step_name}")
            
        self.log(f"\n📊 Overall Result: {passed_steps}/{total_steps} steps passed")
        
        if passed_steps == total_steps:
            self.log("🎉 ALL TESTS PASSED - Product persistence is working correctly!")
            self.log("The user's reported bug may be a frontend issue or user error.")
            return True
        else:
            self.log("❌ CRITICAL BUG CONFIRMED - Product persistence is not working!")
            self.log("The user's report is accurate - products are disappearing after creation.")
            
            # Provide specific diagnosis
            if not results.get("Verify Immediate Persistence", True):
                self.log("🔍 DIAGNOSIS: Products disappear immediately after creation")
                self.log("   This suggests a backend database issue or API problem")
                
            if results.get("Create Test Product", False) and not results.get("Test Specific Product Retrieval", True):
                self.log("🔍 DIAGNOSIS: Product creation returns success but product is not stored")
                self.log("   This suggests a database persistence issue")
                
            return False

def main():
    """Main function to run the product persistence test"""
    tester = ProductPersistenceTest()
    success = tester.run_full_test()
    
    if success:
        print("\n✅ CONCLUSION: Backend product persistence is working correctly")
        return 0
    else:
        print("\n❌ CONCLUSION: Backend product persistence has critical issues")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())