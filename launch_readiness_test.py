import requests
import time
import json
import concurrent.futures
from datetime import datetime

class LaunchReadinessTest:
    def __init__(self, base_url="https://fashion-admin-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.admin_username = "admin"
        self.admin_password = "admin123"
        
    def authenticate(self):
        """Get admin token for protected endpoints"""
        try:
            response = requests.post(
                f"{self.api_url}/admin/login",
                json={"username": self.admin_username, "password": self.admin_password},
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json()['access_token']
                print("✅ Admin authentication successful")
                return True
            else:
                print(f"❌ Admin authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_performance_get_products(self):
        """Test GET /api/products performance - should be < 2s"""
        print("\n🚀 Testing GET /api/products performance...")
        
        start_time = time.time()
        try:
            response = requests.get(f"{self.api_url}/products", timeout=10)
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"   Response time: {response_time:.2f}s")
            
            if response.status_code == 200:
                products = response.json()
                print(f"   Products returned: {len(products)}")
                
                if response_time < 2.0:
                    print("   ✅ Performance test PASSED - Response time < 2s")
                    return True
                else:
                    print("   ❌ Performance test FAILED - Response time >= 2s")
                    return False
            else:
                print(f"   ❌ Request failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Performance test error: {str(e)}")
            return False
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        print("\n🔄 Testing concurrent request handling...")
        
        def make_request():
            try:
                response = requests.get(f"{self.api_url}/products", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Test with 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            end_time = time.time()
        
        successful_requests = sum(results)
        total_time = end_time - start_time
        
        print(f"   Successful requests: {successful_requests}/5")
        print(f"   Total time: {total_time:.2f}s")
        
        if successful_requests == 5:
            print("   ✅ Concurrent requests test PASSED")
            return True
        else:
            print("   ❌ Concurrent requests test FAILED")
            return False
    
    def test_data_integrity(self):
        """Test data integrity of existing products"""
        print("\n🔍 Testing data integrity...")
        
        try:
            response = requests.get(f"{self.api_url}/products", timeout=10)
            if response.status_code != 200:
                print("   ❌ Could not fetch products for integrity check")
                return False
            
            products = response.json()
            print(f"   Analyzing {len(products)} products...")
            
            issues = []
            valid_categories = ["vestidos", "enterizos", "conjuntos", "blusas", "tops", "faldas", "pantalones"]
            
            for i, product in enumerate(products):
                # Check required fields
                if not product.get('name'):
                    issues.append(f"Product {i+1}: Missing name")
                
                if not product.get('id'):
                    issues.append(f"Product {i+1}: Missing ID")
                
                # Check category validity
                if product.get('category') not in valid_categories:
                    issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Invalid category '{product.get('category')}'")
                
                # Check price validity
                retail_price = product.get('retail_price')
                wholesale_price = product.get('wholesale_price')
                
                if not isinstance(retail_price, (int, float)) or retail_price <= 0:
                    issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Invalid retail price")
                
                if not isinstance(wholesale_price, (int, float)) or wholesale_price <= 0:
                    issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Invalid wholesale price")
                
                if isinstance(retail_price, (int, float)) and isinstance(wholesale_price, (int, float)):
                    if wholesale_price >= retail_price:
                        issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Wholesale price >= retail price")
                
                # Check arrays integrity
                images = product.get('images', [])
                colors = product.get('colors', [])
                
                if not isinstance(images, list):
                    issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Images is not an array")
                
                if not isinstance(colors, list):
                    issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Colors is not an array")
                
                # Check for empty strings in arrays
                if isinstance(images, list):
                    for img in images:
                        if not img or not img.strip():
                            issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Empty image URL in array")
                            break
                
                if isinstance(colors, list):
                    for color in colors:
                        if not color or not color.strip():
                            issues.append(f"Product {i+1} ({product.get('name', 'Unknown')}): Empty color in array")
                            break
            
            if issues:
                print(f"   ❌ Data integrity issues found ({len(issues)} issues):")
                for issue in issues[:10]:  # Show first 10 issues
                    print(f"      - {issue}")
                if len(issues) > 10:
                    print(f"      ... and {len(issues) - 10} more issues")
                return False
            else:
                print("   ✅ Data integrity check PASSED - All products have valid data")
                return True
                
        except Exception as e:
            print(f"   ❌ Data integrity test error: {str(e)}")
            return False
    
    def test_category_distribution(self):
        """Test category distribution and verify 'blusas' category exists"""
        print("\n📊 Testing category distribution...")
        
        try:
            # Test categories endpoint
            response = requests.get(f"{self.api_url}/categories", timeout=10)
            if response.status_code != 200:
                print("   ❌ Could not fetch categories")
                return False
            
            categories = response.json()
            category_names = [cat.get('id') for cat in categories]
            
            print(f"   Available categories: {category_names}")
            
            if 'blusas' in category_names:
                print("   ✅ 'blusas' category found in categories list")
            else:
                print("   ❌ 'blusas' category NOT found in categories list")
                return False
            
            # Test products by category
            response = requests.get(f"{self.api_url}/products", timeout=10)
            if response.status_code != 200:
                print("   ❌ Could not fetch products for category analysis")
                return False
            
            products = response.json()
            category_counts = {}
            
            for product in products:
                category = product.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
            
            print("   Product distribution by category:")
            for category, count in sorted(category_counts.items()):
                print(f"      {category}: {count} products")
            
            total_products = len(products)
            print(f"   Total products: {total_products}")
            
            # Verify we have the expected number of products (around 63+ as mentioned)
            if total_products >= 60:
                print(f"   ✅ Product count check PASSED - {total_products} products (expected 60+)")
                return True
            else:
                print(f"   ❌ Product count check FAILED - Only {total_products} products (expected 60+)")
                return False
                
        except Exception as e:
            print(f"   ❌ Category distribution test error: {str(e)}")
            return False
    
    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n👤 Testing admin functionality...")
        
        if not self.token:
            print("   ❌ No admin token available")
            return False
        
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            # Test admin profile
            response = requests.get(f"{self.api_url}/admin/me", headers=headers, timeout=10)
            if response.status_code != 200:
                print("   ❌ Admin profile endpoint failed")
                return False
            
            profile = response.json()
            print(f"   Admin profile: {profile.get('username')} ({profile.get('email')})")
            
            # Test catalog stats
            response = requests.get(f"{self.api_url}/catalog/stats", headers=headers, timeout=10)
            if response.status_code != 200:
                print("   ❌ Catalog stats endpoint failed")
                return False
            
            stats = response.json()
            print(f"   Catalog stats: {stats.get('total_products')} total products")
            print(f"   Categories breakdown: {stats.get('products_by_category', {})}")
            
            # Test low stock endpoint
            response = requests.get(f"{self.api_url}/catalog/low-stock", headers=headers, timeout=10)
            if response.status_code != 200:
                print("   ❌ Low stock endpoint failed")
                return False
            
            low_stock = response.json()
            print(f"   Low stock products: {len(low_stock)} items")
            
            print("   ✅ Admin functionality test PASSED")
            return True
            
        except Exception as e:
            print(f"   ❌ Admin functionality test error: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test search functionality"""
        print("\n🔍 Testing search functionality...")
        
        search_terms = ["vestido", "negro", "blanco", "enterizo"]
        
        for term in search_terms:
            try:
                response = requests.get(f"{self.api_url}/catalog/search?query={term}", timeout=10)
                if response.status_code != 200:
                    print(f"   ❌ Search for '{term}' failed")
                    return False
                
                results = response.json()
                print(f"   Search '{term}': {len(results)} results")
                
            except Exception as e:
                print(f"   ❌ Search test error for '{term}': {str(e)}")
                return False
        
        print("   ✅ Search functionality test PASSED")
        return True
    
    def run_all_tests(self):
        """Run all launch readiness tests"""
        print("🚀 HANNU CLOTHES - LAUNCH READINESS TESTING")
        print("=" * 60)
        
        tests = [
            ("Authentication", self.authenticate),
            ("Performance - GET Products", self.test_performance_get_products),
            ("Concurrent Requests", self.test_concurrent_requests),
            ("Data Integrity", self.test_data_integrity),
            ("Category Distribution", self.test_category_distribution),
            ("Admin Functionality", self.test_admin_functionality),
            ("Search Functionality", self.test_search_functionality),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {str(e)}")
        
        print("\n" + "="*60)
        print("📊 LAUNCH READINESS RESULTS")
        print("="*60)
        print(f"✅ Tests passed: {passed}/{total}")
        print(f"❌ Tests failed: {total - passed}/{total}")
        print(f"📈 Success rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 BACKEND IS READY FOR LAUNCH!")
            print("   All critical systems are working correctly.")
            return True
        else:
            print(f"\n⚠️  LAUNCH READINESS ISSUES DETECTED")
            print(f"   {total - passed} critical issues need to be resolved before launch.")
            return False

if __name__ == "__main__":
    tester = LaunchReadinessTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)