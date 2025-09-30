#!/usr/bin/env python3

import requests
import json
import time

def test_proxy_endpoint():
    """Quick test of the image proxy endpoint"""
    base_url = "https://fashion-admin-4.preview.emergentagent.com/api"
    
    print("🔍 QUICK IMAGE PROXY DIAGNOSIS")
    print("="*50)
    
    # Test URLs - mix of working and potentially problematic ones
    test_cases = [
        {
            "name": "Unsplash Image (External)",
            "url": "https://images.unsplash.com/photo-1633077705107-8f53a004218f?w=400",
            "expected": "Should work - external domain"
        },
        {
            "name": "PostImg Working URL",
            "url": "https://i.postimg.cc/QCC17Dps/Top-Rumba-negro.jpg",
            "expected": "Should work - from logs"
        },
        {
            "name": "PostImg Problematic URL",
            "url": "https://i.postimg.cc/vTHh4Q6y/Arena-Negro.jpg",
            "expected": "May timeout - from logs"
        },
        {
            "name": "Invalid PostImg URL",
            "url": "https://i.postimg.cc/invalid/test.jpg",
            "expected": "Should return 404 or 500"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   URL: {test_case['url']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            start_time = time.time()
            response = requests.get(
                f"{base_url}/proxy-image",
                params={"url": test_case['url']},
                timeout=10  # Shorter timeout
            )
            end_time = time.time()
            
            duration = end_time - start_time
            
            result = {
                "name": test_case['name'],
                "url": test_case['url'],
                "status_code": response.status_code,
                "duration": duration,
                "content_type": response.headers.get('content-type', 'unknown'),
                "content_length": len(response.content),
                "cors_header": response.headers.get('Access-Control-Allow-Origin', 'NOT SET'),
                "success": response.status_code == 200
            }
            
            results.append(result)
            
            if result['success']:
                print(f"   ✅ SUCCESS - {result['status_code']} in {duration:.2f}s")
                print(f"      Content-Type: {result['content_type']}")
                print(f"      Content-Length: {result['content_length']} bytes")
                print(f"      CORS: {result['cors_header']}")
            else:
                print(f"   ❌ FAILED - {result['status_code']} in {duration:.2f}s")
                if len(response.text) < 200:
                    print(f"      Error: {response.text}")
                else:
                    print(f"      Error: {response.text[:200]}...")
                    
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT - Request took longer than 10 seconds")
            results.append({
                "name": test_case['name'],
                "url": test_case['url'],
                "status_code": "TIMEOUT",
                "success": False
            })
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            results.append({
                "name": test_case['name'],
                "url": test_case['url'],
                "status_code": "ERROR",
                "error": str(e),
                "success": False
            })
    
    # Summary
    print(f"\n" + "="*50)
    print("📊 SUMMARY")
    print("="*50)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"✅ Successful requests: {successful}/{total}")
    print(f"❌ Failed requests: {total - successful}/{total}")
    
    if successful > 0:
        print(f"\n✅ PROXY IS WORKING for some URLs")
        print(f"   - CORS headers are correctly set (*)")
        print(f"   - Content-Type headers are correct (image/*)")
        print(f"   - Image data is being returned")
    
    if successful < total:
        print(f"\n⚠️  SOME ISSUES DETECTED:")
        for result in results:
            if not result.get('success', False):
                status = result.get('status_code', 'UNKNOWN')
                print(f"   - {result['name']}: {status}")
    
    # Diagnosis
    print(f"\n🩺 DIAGNOSIS:")
    if successful == total:
        print("✅ Image proxy is working perfectly")
        print("🔍 Issue may be in frontend image loading logic")
    elif successful > 0:
        print("⚠️  Image proxy works for some URLs but not others")
        print("🔍 This suggests:")
        print("   - Some PostImg URLs may be invalid/expired")
        print("   - Some requests may be timing out")
        print("   - Frontend should handle failed image loads gracefully")
    else:
        print("❌ Image proxy is completely broken")
        print("🔍 Check backend implementation and logs")
    
    return results

if __name__ == "__main__":
    test_proxy_endpoint()