#!/usr/bin/env python3

"""
Unit test for the rate limiter to verify it's working correctly
"""

import time
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.rate_limiter import RateLimiter

def test_rate_limiter():
    print("🧪 Testing Rate Limiter Logic")
    print("=" * 40)
    
    # Create a rate limiter with very restrictive settings for testing
    limiter = RateLimiter(limit=3, interval_sec=10)  # 3 requests per 10 seconds
    
    test_ip = "192.168.1.100"
    
    print(f" Test Configuration:")
    print(f"   Limit: 3 requests")
    print(f"   Window: 10 seconds")
    print(f"   Test IP: {test_ip}")
    print()
    
    print("🚀 Testing rapid requests...")
    allowed_count = 0
    blocked_count = 0
    
    for i in range(1, 8): 
        allowed = limiter.is_allowed(test_ip)
        status = " ALLOWED" if allowed else " BLOCKED"
        print(f"Request {i}: {status}")
        
        if allowed:
            allowed_count += 1
        else:
            blocked_count += 1
    
    print()
    print(" Results:")
    print(f"   Allowed requests: {allowed_count}")
    print(f"   Blocked requests: {blocked_count}")
    
    if allowed_count == 3 and blocked_count == 4:
        print(" Rate limiter is working CORRECTLY!")
        print("   First 3 requests allowed, remaining 4 blocked as expected")
    else:
        print(" Rate limiter is NOT working as expected!")
        print(f"   Expected: 3 allowed, 4 blocked")
        print(f"   Actual: {allowed_count} allowed, {blocked_count} blocked")
        return False
    
    print()
    print(" Testing time-based reset...")
    print("Waiting 11 seconds for rate limit window to reset...")
    
    time.sleep(11)
    
    allowed_after_wait = limiter.is_allowed(test_ip)
    if allowed_after_wait:
        print(" Rate limit reset correctly after time window")
    else:
        print(" Rate limit did NOT reset after time window")
        return False
    
    print()
    print("🎉 All rate limiter tests PASSED!")
    return True

if __name__ == "__main__":
    success = test_rate_limiter()
    sys.exit(0 if success else 1)
