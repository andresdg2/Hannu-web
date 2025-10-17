#!/usr/bin/env python3
"""
Database Diagnostic Test
========================

This test will diagnose the database connection and persistence issues
by directly testing the MongoDB connection and operations.
"""

import requests
import json
import time
from datetime import datetime

class DatabaseDiagnostic:
    def __init__(self):
        self.base_url = "https://fashion-admin-6.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def login_admin(self):
        """Login as admin"""
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{self.api_url}/admin/login", json=login_data, timeout=10)
        
        if response.status_code == 200:
            self.token = response.json()['access_token']
            self.log("Admin login successful")
            return True
        else:
            self.log(f"Admin login failed: {response.status_code}", "ERROR")
            return False
            
    def test_database_operations(self):
        """Test database operations step by step"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        # Step 1: Count products before
        self.log("Step 1: Counting products before creation...")
        response = requests.get(f"{self.api_url}/products", timeout=10)
        if response.status_code == 200:
            products_before = response.json()
            count_before = len(products_before)
            self.log(f"Products before: {count_before}")
        else:
            self.log("Failed to get products before", "ERROR")
            return False
            
        # Step 2: Create a simple product
        self.log("Step 2: Creating a simple test product...")
        test_product = {
            "name": "DB Test Product",
            "description": "Testing database persistence",
            "retail_price": 50000,
            "wholesale_price": 35000,
            "category": "blusas"
        }
        
        response = requests.post(f"{self.api_url}/products", json=test_product, headers=headers, timeout=10)
        if response.status_code == 200:
            created_product = response.json()
            product_id = created_product['id']
            self.log(f"Product created with ID: {product_id}")
            self.log(f"Created product data: {json.dumps(created_product, indent=2)}")
        else:
            self.log(f"Failed to create product: {response.status_code} - {response.text}", "ERROR")
            return False
            
        # Step 3: Immediately check if product exists by ID
        self.log("Step 3: Checking if product exists by ID immediately...")
        response = requests.get(f"{self.api_url}/products/{product_id}", timeout=10)
        if response.status_code == 200:
            retrieved_product = response.json()
            self.log(f"✅ Product retrieved by ID: {retrieved_product['name']}")
        else:
            self.log(f"❌ Failed to retrieve product by ID: {response.status_code}", "ERROR")
            
        # Step 4: Check if product appears in products list
        self.log("Step 4: Checking if product appears in products list...")
        response = requests.get(f"{self.api_url}/products", timeout=10)
        if response.status_code == 200:
            products_after = response.json()
            count_after = len(products_after)
            self.log(f"Products after: {count_after}")
            self.log(f"Count difference: {count_after - count_before}")
            
            # Look for our product in the list
            found = False
            for product in products_after:
                if product.get('id') == product_id:
                    found = True
                    self.log(f"✅ Product found in list: {product['name']}")
                    break
                    
            if not found:
                self.log("❌ Product NOT found in products list!", "ERROR")
                self.log("This confirms the bug - product exists by ID but not in list", "ERROR")
                
                # Let's check if there's a pagination or limit issue
                self.log("Checking if it's a limit issue...")
                response_unlimited = requests.get(f"{self.api_url}/products?limit=1000", timeout=10)
                if response_unlimited.status_code == 200:
                    products_unlimited = response_unlimited.json()
                    self.log(f"Products with limit=1000: {len(products_unlimited)}")
                    
                    found_unlimited = False
                    for product in products_unlimited:
                        if product.get('id') == product_id:
                            found_unlimited = True
                            self.log(f"✅ Product found with higher limit: {product['name']}")
                            break
                            
                    if not found_unlimited:
                        self.log("❌ Product still not found even with higher limit", "ERROR")
        else:
            self.log(f"Failed to get products after: {response.status_code}", "ERROR")
            
        # Step 5: Wait and check again
        self.log("Step 5: Waiting 3 seconds and checking again...")
        time.sleep(3)
        
        response = requests.get(f"{self.api_url}/products", timeout=10)
        if response.status_code == 200:
            products_final = response.json()
            count_final = len(products_final)
            self.log(f"Products after wait: {count_final}")
            
            found_final = False
            for product in products_final:
                if product.get('id') == product_id:
                    found_final = True
                    self.log(f"✅ Product still found after wait: {product['name']}")
                    break
                    
            if not found_final:
                self.log("❌ Product disappeared after wait!", "ERROR")
        
        # Step 6: Check by category
        self.log("Step 6: Checking by category filter...")
        response = requests.get(f"{self.api_url}/products?category=blusas", timeout=10)
        if response.status_code == 200:
            category_products = response.json()
            self.log(f"Products in 'blusas' category: {len(category_products)}")
            
            found_in_category = False
            for product in category_products:
                if product.get('id') == product_id:
                    found_in_category = True
                    self.log(f"✅ Product found in category filter: {product['name']}")
                    break
                    
            if not found_in_category:
                self.log("❌ Product not found in category filter", "ERROR")
        
        # Step 7: Try to update the product
        self.log("Step 7: Trying to update the product...")
        update_data = {"name": "DB Test Product - Updated"}
        response = requests.put(f"{self.api_url}/products/{product_id}", json=update_data, headers=headers, timeout=10)
        if response.status_code == 200:
            self.log("✅ Product updated successfully")
        else:
            self.log(f"❌ Failed to update product: {response.status_code}", "ERROR")
            
        # Step 8: Final cleanup
        self.log("Step 8: Cleaning up test product...")
        response = requests.delete(f"{self.api_url}/products/{product_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            self.log("✅ Product deleted successfully")
        else:
            self.log(f"❌ Failed to delete product: {response.status_code}", "ERROR")
            
        return True
        
    def test_multiple_products(self):
        """Test creating multiple products to see if it's a consistency issue"""
        self.log("\n🔍 Testing multiple product creation...")
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        
        created_ids = []
        
        for i in range(3):
            self.log(f"Creating product {i+1}/3...")
            test_product = {
                "name": f"Multi Test Product {i+1}",
                "description": f"Testing multiple creation {i+1}",
                "retail_price": 50000 + (i * 1000),
                "wholesale_price": 35000 + (i * 700),
                "category": "blusas"
            }
            
            response = requests.post(f"{self.api_url}/products", json=test_product, headers=headers, timeout=10)
            if response.status_code == 200:
                product_id = response.json()['id']
                created_ids.append(product_id)
                self.log(f"✅ Product {i+1} created: {product_id}")
            else:
                self.log(f"❌ Failed to create product {i+1}", "ERROR")
                
        # Check if all products appear in the list
        self.log("Checking if all products appear in the list...")
        response = requests.get(f"{self.api_url}/products", timeout=10)
        if response.status_code == 200:
            products = response.json()
            found_count = 0
            
            for product_id in created_ids:
                found = any(p.get('id') == product_id for p in products)
                if found:
                    found_count += 1
                    self.log(f"✅ Product {product_id[:8]}... found in list")
                else:
                    self.log(f"❌ Product {product_id[:8]}... NOT found in list", "ERROR")
                    
            self.log(f"Found {found_count}/{len(created_ids)} products in list")
            
        # Cleanup
        self.log("Cleaning up multiple test products...")
        for product_id in created_ids:
            response = requests.delete(f"{self.api_url}/products/{product_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                self.log(f"✅ Cleaned up {product_id[:8]}...")
            else:
                self.log(f"❌ Failed to cleanup {product_id[:8]}...", "ERROR")
                
    def run_diagnostic(self):
        """Run the complete diagnostic"""
        self.log("🔍 STARTING DATABASE DIAGNOSTIC")
        self.log("=" * 50)
        
        if not self.login_admin():
            return False
            
        self.test_database_operations()
        self.test_multiple_products()
        
        self.log("\n" + "=" * 50)
        self.log("🎯 DIAGNOSTIC COMPLETE")
        
        return True

def main():
    diagnostic = DatabaseDiagnostic()
    diagnostic.run_diagnostic()

if __name__ == "__main__":
    main()