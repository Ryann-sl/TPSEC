"""
Brute Force Attack Simulation
Attempts to crack encryption by trying all possible keys
"""

import time
import string
import itertools
import json
import uuid

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
        
        log("🎯 Caesar Cipher Brute Force Simulation")
        log(f"🔍 Ciphertext: {ciphertext}")
        log("🎲 Key Space Analysis: The Caesar cipher only has 25 useful keys.")
        log("🚀 Starting attack: Trying shifts 1 to 25...\n")
        
        # Try shifts 1 to 25 (Shift 0/26 is the original text)
        for shift in range(1, 26):
            time.sleep(0.05)
            
            # Decrypt with this shift
            decrypted = ""
            for char in ciphertext:
                if char.isalpha():
                    ascii_offset = ord('A') if char.isupper() else ord('a')
                    # Shift left for decryption
                    char_val = ord(char)
                    base_val = char_val - ascii_offset
                    shifted = (base_val - int(shift)) % 26
                    decrypted += chr(shifted + ascii_offset)
                else:
                    decrypted += char
            
            results.append({
                'shift': shift,
                'text': decrypted
            })
            
            log(f"Attempt {shift:2d}: Results in '{decrypted}'")
        
        log(f"\n✅ SYSTEM CHECK: 25 attempts completed.")
        log("💡 OBSERVATION: One of the 25 results above MUST be the original message.")
        
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
        
    sessions: dict[str, dict[str, bool]] = {}

    @classmethod
    def get_session(cls, session_id):
        return cls.sessions.get(session_id)

    @classmethod
    def stop_session(cls, session_id):
        if session_id in cls.sessions:
            cls.sessions[session_id]['stopped'] = True

    @classmethod
    def pause_session(cls, session_id):
        if session_id in cls.sessions:
            cls.sessions[session_id]['paused'] = True

    @classmethod
    def resume_session(cls, session_id):
        if session_id in cls.sessions:
            cls.sessions[session_id]['paused'] = False

    @classmethod
    def crack_password(cls, password, mode=3, session_id=None):
        """
        Brute force a raw password by determining its length and guessing.
        """
        if not session_id:
            session_id = str(uuid.uuid4())
            
        cls.sessions[session_id] = {
            'paused': False,
            'stopped': False
        }
        
        def log_event(message, event_type="log", extra=None):
            payload = {'type': event_type, 'message': message, 'timestamp': time.time()}
            if extra:
                payload.update(extra)
            return f"data: {json.dumps(payload)}\n\n"
                
        yield log_event("🎯 Raw Password Brute Force Simulation", extra={'session_id': session_id})
        yield log_event(f"🔍 Target Password: [HIDDEN]")
        
        mode = int(mode)
        yield log_event(f"⚙️ Selected Mode: {mode}")
        
        # Determine charset and length based on mode
        if mode == 3:
            chars = "234"
            length = 3
            yield log_event("📝 Restriction: 3 characters long, using only '2', '3', '4'")
        elif mode == 5:
            chars = string.digits
            length = 5
            yield log_event("� Restriction: 5 characters long, using only digits (0-9)")
        elif mode == 6:
            chars = string.ascii_letters + string.digits + "+*!@#$%^&()-_=[]{}|;:,.<>?/"
            length = 6
            yield log_event("📝 Restriction: 6 characters long, using all alphanumeric and special characters")
        else:
            # Fallback to authentic brute force if mode is invalid
            length = len(password)
            chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
            yield log_event(f"⚠️ Invalid mode. Falling back to length {length} with full charset.")
            
        if len(password) != length:
             yield log_event(f"⚠️ Note: The target password is {len(password)} chars, but we are enforcing a length of {length} chars.")
        
        yield log_event(f"🎲 Step 2: Guessing combinations of length {length}...")
        yield log_event(f"Charset size is {len(chars)}. Possible combinations: {len(chars)**length}")
        
        start_time = time.time()
        elapsed_time: float = 0.0
        attempts = 0
        found = False
        
        for guess_tuple in itertools.product(chars, repeat=length):
            # Check session state
            session = cls.sessions.get(session_id)
            if not session:
                break
                
            if session['stopped']:
                yield log_event("🛑 Attack stopped by user.")
                break
                
            if session['paused']:
                yield log_event("⏸️ Attack paused...")
                while session['paused'] and not session['stopped']:
                    time.sleep(0.5)
                if session['stopped']:
                    yield log_event("🛑 Attack stopped by user.")
                    break
                yield log_event("▶️ Attack resumed!")
                # reset start time to account for pause
                start_time = time.time() - float(elapsed_time)
            
            guess = "".join(guess_tuple)
            attempts += 1
            
            # Keep the console active by logging the first 1,000 and every 100,000 attempts
            if attempts <= 1000:
                yield log_event(f"Attempt {attempts}: '{guess}'")
            elif attempts % 100000 == 0:
                yield log_event(f"Attempt {attempts:,}: '{guess}'")
                
            if guess == password:
                found = True
                yield log_event(f"✅ CRACKED! Found the password: '{guess}'")
                yield log_event(f"Total attempts needed: {attempts}")
                elapsed_time = float(time.time() - start_time)
                yield log_event({'attempts': attempts, 'time': elapsed_time}, "done")
                break
                
            # Update elapsed time
            elapsed_time = float(time.time() - start_time)
                
        if not found and not cls.sessions.get(session_id, {}).get('stopped'):
            yield log_event("❌ Could not crack the password within combination limits.")
            yield log_event({'attempts': attempts, 'time': elapsed_time}, "done")
            
        # Cleanup session
        cls.sessions.pop(session_id, None)
    
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
