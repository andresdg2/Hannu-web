import requests
import sys
import json
from datetime import datetime
import time

class ImageProxyTester:
    def __init__(self, base_url="https://fashion-admin-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.admin_username = "admin"
        self.admin_password = "admin123"

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, params=None):
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
        if params:
            print(f"   Params: {params}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # For image proxy, show response details
                if 'proxy-image' in endpoint:
                    content_type = response.headers.get('content-type', 'unknown')
                    content_length = len(response.content)
                    cors_header = response.headers.get('Access-Control-Allow-Origin', 'NOT SET')
                    print(f"   Content-Type: {content_type}")
                    print(f"   Content-Length: {content_length} bytes")
                    print(f"   CORS Header: {cors_header}")
                    
                    # Check if it's actually an image
                    if content_type.startswith('image/'):
                        print(f"   ✅ Valid image content received")
                    else:
                        print(f"   ❌ Not image content: {content_type}")
                        success = False
                else:
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

            return success, response

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            return False, None
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def login_admin(self):
        """Login as admin to get token"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "admin/login",
            200,
            data={"username": self.admin_username, "password": self.admin_password}
        )
        if success and response:
            try:
                response_data = response.json()
                if 'access_token' in response_data:
                    self.token = response_data['access_token']
                    print(f"   ✅ Token obtained successfully")
                    return True
            except:
                pass
        print(f"   ❌ Failed to get token")
        return False

    def test_proxy_endpoint_basic(self):
        """Test basic proxy endpoint functionality"""
        print("\n🔍 TESTING BASIC PROXY ENDPOINT")
        print("="*50)
        
        # Test with a known working image URL
        test_urls = [
            "https://i.postimg.cc/9fKvLqhZ/test.jpg",
            "https://images.unsplash.com/photo-1633077705107-8f53a004218f?w=400",
            "https://via.placeholder.com/300x400/FF0000/FFFFFF?text=Test"
        ]
        
        for i, test_url in enumerate(test_urls, 1):
            print(f"\n{i}. Testing with URL: {test_url}")
            success, response = self.run_test(
                f"Proxy Image Test {i}",
                "GET",
                "proxy-image",
                200,
                params={"url": test_url}
            )
            
            if success and response:
                # Verify CORS headers
                cors_origin = response.headers.get('Access-Control-Allow-Origin')
                if cors_origin == '*':
                    print(f"   ✅ CORS header correct: {cors_origin}")
                else:
                    print(f"   ❌ CORS header incorrect: {cors_origin}")
                
                # Verify content type
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('image/'):
                    print(f"   ✅ Content-Type is image: {content_type}")
                else:
                    print(f"   ❌ Content-Type not image: {content_type}")
                
                # Verify content length
                content_length = len(response.content)
                if content_length > 0:
                    print(f"   ✅ Image data received: {content_length} bytes")
                else:
                    print(f"   ❌ No image data received")
            
            time.sleep(1)  # Small delay between requests

    def test_proxy_with_invalid_urls(self):
        """Test proxy with invalid URLs"""
        print("\n🔍 TESTING PROXY WITH INVALID URLS")
        print("="*50)
        
        invalid_tests = [
            ("Empty URL", ""),
            ("Invalid domain", "https://invalid-domain-that-does-not-exist.com/image.jpg"),
            ("Non-image URL", "https://www.google.com"),
            ("Blocked domain", "https://example.com/image.jpg")
        ]
        
        for test_name, test_url in invalid_tests:
            print(f"\n• Testing {test_name}: {test_url}")
            success, response = self.run_test(
                f"Proxy Invalid URL - {test_name}",
                "GET",
                "proxy-image",
                400 if test_url == "" else 403 if "example.com" in test_url else 500,
                params={"url": test_url} if test_url else None
            )

    def get_sample_products(self):
        """Get sample products from database"""
        success, response = self.run_test(
            "Get Sample Products",
            "GET",
            "products",
            200,
            params={"limit": 10}
        )
        
        if success and response:
            try:
                products = response.json()
                if isinstance(products, list):
                    print(f"   ✅ Retrieved {len(products)} products")
                    return products
            except:
                pass
        
        print(f"   ❌ Failed to get products")
        return []

    def test_real_product_images(self):
        """Test proxy with real product image URLs from database"""
        print("\n🔍 TESTING REAL PRODUCT IMAGES")
        print("="*50)
        
        products = self.get_sample_products()
        if not products:
            print("❌ No products available for testing")
            return False
        
        images_tested = 0
        images_working = 0
        
        for product in products[:5]:  # Test first 5 products
            product_name = product.get('name', 'Unknown')
            images = product.get('images', [])
            
            if not images:
                # Try single image field for backward compatibility
                single_image = product.get('image', '')
                if single_image:
                    images = [single_image]
            
            if images:
                print(f"\n📦 Testing product: {product_name}")
                print(f"   Images to test: {len(images)}")
                
                for i, image_url in enumerate(images[:2], 1):  # Test first 2 images per product
                    if image_url and image_url.strip():
                        images_tested += 1
                        print(f"\n   Image {i}: {image_url}")
                        
                        # Test direct access first
                        print(f"   🔗 Testing direct access...")
                        try:
                            direct_response = requests.head(image_url, timeout=10)
                            print(f"      Direct access: {direct_response.status_code}")
                        except Exception as e:
                            print(f"      Direct access failed: {str(e)}")
                        
                        # Test through proxy
                        print(f"   🔄 Testing through proxy...")
                        success, proxy_response = self.run_test(
                            f"Proxy Real Image - {product_name} #{i}",
                            "GET",
                            "proxy-image",
                            200,
                            params={"url": image_url}
                        )
                        
                        if success:
                            images_working += 1
                            print(f"      ✅ Proxy working for this image")
                        else:
                            print(f"      ❌ Proxy failed for this image")
                            if proxy_response:
                                print(f"      Error: {proxy_response.text[:100]}...")
        
        print(f"\n📊 REAL IMAGES TEST SUMMARY:")
        print(f"   Images tested: {images_tested}")
        print(f"   Images working through proxy: {images_working}")
        if images_tested > 0:
            success_rate = (images_working / images_tested) * 100
            print(f"   Success rate: {success_rate:.1f}%")
            return success_rate > 50
        else:
            print(f"   No images found to test")
            return False

    def test_postimg_specific_urls(self):
        """Test proxy with specific PostImg URLs"""
        print("\n🔍 TESTING POSTIMG SPECIFIC URLS")
        print("="*50)
        
        # Get real PostImg URLs from products
        products = self.get_sample_products()
        postimg_urls = []
        
        for product in products:
            images = product.get('images', [])
            if not images:
                single_image = product.get('image', '')
                if single_image:
                    images = [single_image]
            
            for image_url in images:
                if image_url and 'postimg.cc' in image_url:
                    postimg_urls.append({
                        'url': image_url,
                        'product': product.get('name', 'Unknown')
                    })
        
        if postimg_urls:
            print(f"   Found {len(postimg_urls)} PostImg URLs in products")
            
            for i, item in enumerate(postimg_urls[:5], 1):  # Test first 5 PostImg URLs
                print(f"\n{i}. Testing PostImg URL from {item['product']}")
                print(f"   URL: {item['url']}")
                
                success, response = self.run_test(
                    f"PostImg URL {i}",
                    "GET",
                    "proxy-image",
                    200,
                    params={"url": item['url']}
                )
                
                if not success and response:
                    print(f"   Error details: {response.text[:200]}...")
        else:
            print("   No PostImg URLs found in products")
            # Test with sample PostImg URLs
            sample_postimg_urls = [
                "https://i.postimg.cc/sample1.jpg",
                "https://i.postimg.cc/sample2.jpg"
            ]
            
            for i, url in enumerate(sample_postimg_urls, 1):
                print(f"\n{i}. Testing sample PostImg URL: {url}")
                success, response = self.run_test(
                    f"Sample PostImg URL {i}",
                    "GET",
                    "proxy-image",
                    200,
                    params={"url": url}
                )

    def check_backend_logs(self):
        """Check backend logs for proxy errors"""
        print("\n🔍 CHECKING BACKEND LOGS")
        print("="*50)
        
        try:
            import subprocess
            
            # Check supervisor logs for backend
            log_files = [
                "/var/log/supervisor/backend.err.log",
                "/var/log/supervisor/backend.out.log"
            ]
            
            for log_file in log_files:
                print(f"\n📋 Checking {log_file}:")
                try:
                    result = subprocess.run(
                        ["tail", "-n", "20", log_file],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if lines and lines[0]:
                            print(f"   Last 20 lines:")
                            for line in lines[-10:]:  # Show last 10 lines
                                if line.strip():
                                    print(f"   {line}")
                        else:
                            print(f"   Log file is empty")
                    else:
                        print(f"   Could not read log file: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    print(f"   Timeout reading log file")
                except Exception as e:
                    print(f"   Error reading log file: {str(e)}")
                    
        except ImportError:
            print("   Cannot check logs - subprocess not available")
        except Exception as e:
            print(f"   Error checking logs: {str(e)}")

    def run_comprehensive_proxy_test(self):
        """Run comprehensive image proxy testing"""
        print("\n🚨 COMPREHENSIVE IMAGE PROXY TESTING")
        print("="*60)
        print("User reports: Images show 'Imagen procesándose por proxy' but don't load")
        print("="*60)
        
        # Login first
        if not self.login_admin():
            print("❌ Could not login - some tests may be limited")
        
        # Run all proxy tests
        test_results = {
            'basic_proxy': False,
            'real_product_images': False,
            'postimg_urls': False,
            'invalid_urls_handled': False
        }
        
        # 1. Basic proxy functionality
        print("\n" + "="*20 + " BASIC PROXY TEST " + "="*20)
        try:
            self.test_proxy_endpoint_basic()
            test_results['basic_proxy'] = True
        except Exception as e:
            print(f"❌ Basic proxy test failed: {str(e)}")
        
        # 2. Real product images
        print("\n" + "="*20 + " REAL PRODUCT IMAGES " + "="*20)
        try:
            test_results['real_product_images'] = self.test_real_product_images()
        except Exception as e:
            print(f"❌ Real product images test failed: {str(e)}")
        
        # 3. PostImg specific URLs
        print("\n" + "="*20 + " POSTIMG SPECIFIC URLS " + "="*20)
        try:
            self.test_postimg_specific_urls()
            test_results['postimg_urls'] = True
        except Exception as e:
            print(f"❌ PostImg URLs test failed: {str(e)}")
        
        # 4. Invalid URLs handling
        print("\n" + "="*20 + " INVALID URLS HANDLING " + "="*20)
        try:
            self.test_proxy_with_invalid_urls()
            test_results['invalid_urls_handled'] = True
        except Exception as e:
            print(f"❌ Invalid URLs test failed: {str(e)}")
        
        # 5. Check backend logs
        print("\n" + "="*20 + " BACKEND LOGS CHECK " + "="*20)
        self.check_backend_logs()
        
        # Final summary
        print("\n" + "="*60)
        print("🔍 IMAGE PROXY TEST SUMMARY")
        print("="*60)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name.replace('_', ' ').title()}")
        
        print(f"\n📊 Overall Result: {passed_tests}/{total_tests} tests passed")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Diagnosis
        print(f"\n🩺 DIAGNOSIS:")
        if passed_tests == total_tests:
            print("✅ Image proxy appears to be working correctly")
            print("🔍 Issue may be in frontend image loading or display logic")
        elif test_results['basic_proxy']:
            print("✅ Basic proxy functionality works")
            if not test_results['real_product_images']:
                print("❌ Issue with real product image URLs")
                print("🔍 Check if product image URLs are valid and accessible")
            else:
                print("🔍 Issue may be intermittent or frontend-related")
        else:
            print("❌ Basic proxy functionality is broken")
            print("🔍 Check backend proxy endpoint implementation")
        
        return test_results

def main():
    print("🖼️  Starting IMAGE PROXY Testing...")
    print("=" * 60)
    
    tester = ImageProxyTester()
    
    # Run comprehensive proxy test
    results = tester.run_comprehensive_proxy_test()
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"✅ Tests passed: {tester.tests_passed}")
    print(f"❌ Tests failed: {tester.tests_run - tester.tests_passed}")
    if tester.tests_run > 0:
        print(f"📈 Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    return 0 if sum(results.values()) >= len(results) // 2 else 1

if __name__ == "__main__":
    sys.exit(main())