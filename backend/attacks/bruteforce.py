import time, string, itertools, json, uuid
from typing import Dict

class BruteForceAttack:
    """Simulate brute force attacks for educational purposes."""
    sessions: Dict[str, Dict[str, bool]] = {}

    @classmethod
    def stop_session(cls, session_id):
        if session_id in cls.sessions: cls.sessions[session_id]['stopped'] = True

    @classmethod
    def pause_session(cls, session_id):
        if session_id in cls.sessions: cls.sessions[session_id]['paused'] = True

    @classmethod
    def resume_session(cls, session_id):
        if session_id in cls.sessions: cls.sessions[session_id]['paused'] = False

    @classmethod
    def crack_password(cls, password, mode=3, session_id=None):
        session_id = session_id or str(uuid.uuid4())
        cls.sessions[session_id] = {'paused': False, 'stopped': False}
        
        def log_evt(msg, type="log", extra=None):
            payload = {'type': type, 'message': msg, 'timestamp': time.time()}
            if extra: payload.update(extra)
            return f"data: {json.dumps(payload)}\n\n"

        yield log_evt("🎯 Password Brute Force Simulation", extra={'session_id': session_id})
        
        mode, length, chars = int(mode), 0, ""
        if mode == 3:
            chars, length = "234", 3
        elif mode == 5:
            chars, length = string.digits, 5
        elif mode == 6:
            chars, length = string.ascii_letters + string.digits + "+*!@#$%^&()-_=[]{}|;:,.<>?/", 6
        else:
            chars, length = string.ascii_letters + string.digits + string.punctuation, len(password)

        yield log_evt(f"🚀 Mode {mode}: Length {length}, Charset Size {len(chars)}")
        
        start_time = time.time()
        attempts = 0
        
        for guess_tuple in itertools.product(chars, repeat=length):
            session = cls.sessions.get(session_id)
            if not session: break
            if session.get('stopped'):
                yield log_evt("🛑 Stopped.")
                break
                
            if session.get('paused'):
                yield log_evt("⏸️ Paused...")
                while True:
                    time.sleep(0.5)
                    session = cls.sessions.get(session_id)
                    if session is None: break
                    if session.get('stopped') or not session.get('paused'): break
                
                if session is None or session.get('stopped'): break
                yield log_evt("▶️ Resumed!")
                start_time = time.time() - (float(attempts) / 1000000.0)

            guess = "".join(guess_tuple)
            attempts += 1
            
            if attempts <= 1000 or attempts % 100000 == 0:
                yield log_evt(f"Attempt {attempts:,}: '{guess}'")
                
            if guess == password:
                elapsed = time.time() - start_time
                yield log_evt(f"✅ CRACKED! '{guess}' in {attempts} attempts.")
                yield log_evt({'attempts': attempts, 'time': elapsed}, "done")
                break
        else:
            yield log_evt("❌ Failed to crack.", "done")
            
        cls.sessions.pop(session_id, None)

    @staticmethod
    def estimate_time(key_space, speed=1000000):
        s = key_space / speed
        units = [('years', 31557600), ('days', 86400), ('hours', 3600), ('minutes', 60)]
        for name, val in units:
            if s >= val: return {'estimated_time': f"{s/val:.2f} {name}", 'feasible': s < 86400}
        return {'estimated_time': f"{s:.2f} seconds", 'feasible': True}

    @staticmethod
    def analyze_key_spaces():
        return {
            'caesar': {'name': 'Caesar', 'key_space': 26, 'security': 'None'},
            'aes128': {'name': 'AES-128', 'key_space': 2**128, 'security': 'Secure'},
            'aes256': {'name': 'AES-256', 'key_space': 2**256, 'security': 'Very Secure'}
        }

    @staticmethod
    def explain_brute_force():
        return {
            'title': 'Brute Force Attack',
            'description': 'Trying every possible combination until the correct one is found.',
            'defenses': ['Long passwords', 'MFA', 'Rate limiting', 'Account lockout'],
            'key_space_comparison': BruteForceAttack.analyze_key_spaces()
        }
