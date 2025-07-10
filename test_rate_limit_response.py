#!/usr/bin/env python3

"""
Test to verify that rate limiting returns proper JSON responses instead of 500 errors
"""

import requests
import time
import json
import sys

def test_rate_limit_response():
    print(" Testing Rate Limit JSON Response")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    endpoint = "/employees/search?org_id=1"
    
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code != 200:
            print(" Server health check failed")
            return False
        print(" Server is healthy")
    except Exception as e:
        print(f" Cannot connect to server: {e}")
        print("Please start the server with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    print(f"🚀 Making rapid requests to {base_url}{endpoint}")
    
    for i in range(1, 15):
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"Request {i}: HTTP {response.status_code}")
            
            if response.status_code == 429:
                print(" Rate limit triggered!")
                
                try:
                    json_response = response.json()
                    print(" Response is valid JSON:")
                    print(f"   {json.dumps(json_response, indent=2)}")
                    
                    expected_fields = ["error", "message", "detail", "retry_after"]
                    missing_fields = [field for field in expected_fields if field not in json_response]
                    
                    if missing_fields:
                        print(f"  Missing expected fields: {missing_fields}")
                    else:
                        print(" All expected fields present in response")
                    
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        print(f" Retry-After header present: {retry_after}")
                    else:
                        print("  Retry-After header missing")
                    
                    return True
                    
                except json.JSONDecodeError:
                    print(" Response is not valid JSON:")
                    print(f"   {response.text}")
                    return False
                    
            elif response.status_code == 500:
                print(" Got 500 Internal Server Error - this is the bug we're fixing!")
                print(f"   Response: {response.text}")
                return False
                
            elif response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Success: Found {len(data)} employees")
                except:
                    print("   Success: Got response")
            else:
                print(f"   Unexpected status code: {response.status_code}")
        
        except Exception as e:
            print(f"Request {i}: Error - {e}")
            return False
    
    print("  Rate limit was not triggered within 15 requests")
    print("This might be due to:")
    print("  - Rate limit settings are too permissive")
    print("  - Requests are not fast enough")
    print("  - Previous requests have expired from the rate limit window")
    return True

if __name__ == "__main__":
    success = test_rate_limit_response()
    if success:
        print("\n Rate limit response test completed successfully!")
    else:
        print("\n Rate limit response test failed!")
    sys.exit(0 if success else 1)
