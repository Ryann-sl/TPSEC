import time
import threading

from typing import Dict, Any, Tuple

class RateLimiter:
    """
    Python implementation of the brute force defense logic.
    Tracks failed attempts and blocks identifiers (usernames/IPs) after too many failures.
    """
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 900, block_duration_seconds: int = 900):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds  # Default 15 minutes
        self.block_duration_seconds = block_duration_seconds  # Default 15 minutes
        self.login_attempts: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def check_rate_limit(self, identifier: str) -> Tuple[bool, int, int]:
        """
        Check if the identifier is allowed to attempt login.
        Returns: (allowed: bool, remaining_attempts: int, retry_after: int)
        """
        now = time.time()
        with self.lock:
            # Lazy cleanup of old entries
            self._cleanup(now)
            
            entry = self.login_attempts.get(identifier)
            
            if not entry:
                return True, self.max_attempts - 1, 0
            
            # Check if currently blocked
            blocked_until = entry.get('blocked_until')
            if blocked_until and now < blocked_until:
                retry_after = int(blocked_until - now)
                return False, 0, retry_after
            
            # Check if window expired
            if now - entry['first_attempt'] > self.window_seconds:
                del self.login_attempts[identifier]
                return True, self.max_attempts - 1, 0
            
            # Check if max attempts reached
            if entry['attempts'] >= self.max_attempts:
                entry['blocked_until'] = now + self.block_duration_seconds
                return False, 0, self.block_duration_seconds
            
            remaining = self.max_attempts - entry['attempts'] - 1
            return True, max(0, remaining), 0

    def record_failed_attempt(self, identifier: str) -> None:
        """Record a failed login attempt for the identifier."""
        now = time.time()
        with self.lock:
            entry = self.login_attempts.get(identifier)
            
            if not entry:
                self.login_attempts[identifier] = {
                    'attempts': 1,
                    'first_attempt': now,
                    'last_attempt': now,
                    'blocked_until': None
                }
            else:
                entry['attempts'] += 1
                entry['last_attempt'] = now

    def reset_attempts(self, identifier: str) -> None:
        """Reset attempts for an identifier (e.g., after successful login)."""
        with self.lock:
            if identifier in self.login_attempts:
                del self.login_attempts[identifier]

    def _cleanup(self, now: float) -> None:
        """Remove entries that haven't been touched for a while."""
        to_delete = []
        for key, entry in self.login_attempts.items():
            if now - entry['last_attempt'] > self.window_seconds * 2:
                to_delete.append(key)
        
        for key in to_delete:
            del self.login_attempts[key]
