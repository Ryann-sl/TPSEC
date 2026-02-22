"""
Brute Force Attack Simulation
Attempts to crack encryption by trying all possible keys
"""

import time
import string

class BruteForceAttack:
    """Simulate brute force attack on encrypted messages"""
    
    @staticmethod
    def crack_caesar(ciphertext, max_attempts=26, logs_callback=None):
        """
        Brute force Caesar cipher
        
        Args:
            ciphertext (str): Encrypted text
            max_attempts (int): Maximum shifts to try (default 26)
            logs_callback (function): Optional logging callback
            
        Returns:
            dict: Attack results with all possible decryptions
        """
        logs = []
        results = []
        
        def log(message):
            logs.append({
                'timestamp': time.time(),
                'message': message
            })
            if logs_callback:
                logs_callback(message)
        
        log("🎯 Brute Force Attack on Caesar Cipher")
        log(f"🔍 Ciphertext: {ciphertext}")
        log(f"🎲 Trying all {max_attempts} possible shifts...\n")
        
        # Try all possible shifts
        for shift in range(max_attempts):
            time.sleep(0.05)
            
            # Decrypt with this shift
            decrypted = ""
            for char in ciphertext:
                if char.isalpha():
                    ascii_offset = ord('A') if char.isupper() else ord('a')
                    shifted = (ord(char) - ascii_offset - shift) % 26
                    decrypted += chr(shifted + ascii_offset)
                else:
                    decrypted += char
            
            results.append({
                'shift': shift,
                'text': decrypted
            })
            
            log(f"Shift {shift:2d}: {decrypted}")
        
        # Also check if it's just reversed text
        reversed_text = ciphertext[::-1]
        log(f"\n🔄 Checking Reverse Text: {reversed_text}")
        results.append({
            'shift': 'REVERSE',
            'text': reversed_text
        })
        
        # Check if it's Base64
        try:
            import base64
            # Add padding if needed
            padded = ciphertext + '=' * (-len(ciphertext) % 4)
            b64_decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
            if b64_decoded and b64_decoded.isprintable() and len(b64_decoded) > 0:
                 log(f"\n📦 Checking Base64: {b64_decoded}")
                 results.append({
                    'shift': 'BASE64',
                    'text': b64_decoded
                })
        except Exception:
            pass
        
        log(f"\n✅ Tried all {max_attempts} possibilities!")
        log("💡 Analyze results to find meaningful plaintext")
        log("\n🛡️  DEFENSE: Caesar cipher is NOT secure!")
        log("   - Use modern encryption (AES, RSA)")
        log("   - Increase key space complexity")
        
        return {
            'success': True,
            'algorithm': 'caesar',
            'attempts': max_attempts,
            'results': results,
            'logs': logs,
            'defense_recommendation': 'Use modern encryption algorithms with large key spaces'
        }
    
    @staticmethod
    def estimate_time(key_space, attempts_per_second=1000000):
        """
        Estimate time to brute force given key space
        
        Args:
            key_space (int): Number of possible keys
            attempts_per_second (int): Attack speed
            
        Returns:
            dict: Time estimates
        """
        seconds = key_space / attempts_per_second
        
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        years = days / 365.25
        
        # Determine best unit
        if years > 1:
            time_str = f"{years:.2e} years"
        elif days > 1:
            time_str = f"{days:.2f} days"
        elif hours > 1:
            time_str = f"{hours:.2f} hours"
        elif minutes > 1:
            time_str = f"{minutes:.2f} minutes"
        else:
            time_str = f"{seconds:.2f} seconds"
        
        return {
            'key_space': key_space,
            'attempts_per_second': attempts_per_second,
            'estimated_time': time_str,
            'seconds': seconds,
            'feasible': seconds < 86400  # Less than 1 day
        }
    
    @staticmethod
    def analyze_key_spaces():
        """
        Analyze different encryption key spaces
        
        Returns:
            dict: Analysis of various algorithms
        """
        return {
            'caesar': {
                'name': 'Caesar Cipher',
                'key_space': 26,
                'estimate': BruteForceAttack.estimate_time(26),
                'security': 'VERY WEAK - Crackable instantly'
            },
            'playfair': {
                'name': 'Playfair Cipher',
                'key_space': 26**25,  # Approximate
                'estimate': BruteForceAttack.estimate_time(26**10),  # Simplified
                'security': 'WEAK - Vulnerable to frequency analysis'
            },
            'des': {
                'name': 'DES (56-bit)',
                'key_space': 2**56,
                'estimate': BruteForceAttack.estimate_time(2**56),
                'security': 'WEAK - Broken in 1999'
            },
            'aes128': {
                'name': 'AES-128',
                'key_space': 2**128,
                'estimate': BruteForceAttack.estimate_time(2**128),
                'security': 'STRONG - Currently secure'
            },
            'aes256': {
                'name': 'AES-256',
                'key_space': 2**256,
                'estimate': BruteForceAttack.estimate_time(2**256),
                'security': 'VERY STRONG - Extremely secure'
            }
        }
    
    @staticmethod
    def explain_brute_force():
        """Return educational explanation"""
        return {
            'title': 'Brute Force Attack',
            'description': 'An attack that tries every possible key until the correct one is found.',
            'how_it_works': [
                '1. Generate all possible keys',
                '2. Try each key systematically',
                '3. Check if decryption produces meaningful text',
                '4. Continue until correct key is found'
            ],
            'effectiveness': [
                'Always works given enough time',
                'Time depends on key space size',
                'Modern encryption has huge key spaces',
                'Caesar cipher: 26 keys (instant)',
                'AES-256: 2^256 keys (impossible)'
            ],
            'defenses': [
                'Use algorithms with large key spaces',
                'Use sufficiently long keys (128+ bits)',
                'Implement rate limiting',
                'Use account lockout policies',
                'Monitor for suspicious activity',
                'Use modern encryption (AES, not Caesar)'
            ],
            'key_space_comparison': BruteForceAttack.analyze_key_spaces()
        }
