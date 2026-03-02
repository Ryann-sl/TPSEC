import sys
import os
import time

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.rate_limiter import RateLimiter

def test_rate_limiter():
    print("Testing RateLimiter...")
    limiter = RateLimiter(max_attempts=3, window_seconds=2, block_duration_seconds=2)
    
    identifier = "test_user"
    
    # 1. First attempt
    allowed, remaining, retry = limiter.check_rate_limit(identifier)
    print(f"Attempt 1: allowed={allowed}, remaining={remaining}")
    assert allowed == True
    assert remaining == 2
    limiter.record_failed_attempt(identifier)
    
    # 2. Second attempt
    allowed, remaining, retry = limiter.check_rate_limit(identifier)
    print(f"Attempt 2: allowed={allowed}, remaining={remaining}")
    assert allowed == True
    assert remaining == 1
    limiter.record_failed_attempt(identifier)
    
    # 3. Third attempt
    allowed, remaining, retry = limiter.check_rate_limit(identifier)
    print(f"Attempt 3: allowed={allowed}, remaining={remaining}")
    assert allowed == True
    assert remaining == 0
    limiter.record_failed_attempt(identifier)
    
    # 4. Fourth attempt - should be blocked
    allowed, remaining, retry = limiter.check_rate_limit(identifier)
    print(f"Attempt 4: allowed={allowed}, retry_after={retry}")
    assert allowed == False
    assert retry > 0
    
    # 5. Wait for block to expire
    print("Waiting for block to expire...")
    time.sleep(2.1)
    allowed, remaining, retry = limiter.check_rate_limit(identifier)
    print(f"Post-block: allowed={allowed}, remaining={remaining}")
    assert allowed == True
    
    # 6. Test reset
    limiter.record_failed_attempt(identifier)
    limiter.reset_attempts(identifier)
    allowed, remaining, retry = limiter.check_rate_limit(identifier)
    print(f"After reset: allowed={allowed}, remaining={remaining}")
    assert remaining == 2
    
    print("✅ RateLimiter tests passed!")

if __name__ == "__main__":
    test_rate_limiter()
