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
        """Simplifed brute force simulation."""
        session_id = session_id or str(uuid.uuid4())
        cls.sessions[session_id] = {'paused': False, 'stopped': False}

        def create_message(msg, type="log", data=None):
            """Helpful function to format server messages."""
            payload = {'type': type, 'message': msg, 'timestamp': time.time()}
            if data: payload.update(data)
            return f"data: {json.dumps(payload)}\n\n"

        yield create_message("🎯 Brute Force Attack Starting...", data={'session_id': session_id})

        # --- STEP 1: Choose character set and length based on mode ---
        mode = int(mode)
        if mode == 3:
            chars, length = "234", 3
        elif mode == 5:
            chars, length = string.digits, 5
        elif mode == 6:
            chars = string.ascii_letters + string.digits + string.punctuation
            length = 6
        else:
            chars, length = string.ascii_letters + string.digits, len(password)

        yield create_message(f"🚀 Mode {mode}: Trying matches with length {length}...")

        # --- STEP 2: The Main Loop 
        start_time = time.time()
        attempts = 0

        for combination in itertools.product(chars, repeat=length):
            # Check if user clicked STOP or PAUSE
            session = cls.sessions.get(session_id)
            if not session or session.get('stopped'):
                yield create_message("🛑 Attack Stopped.")
                break

            if session.get('paused'):
                yield create_message("⏸️ Paused...")
                while session.get('paused') and not session.get('stopped'):
                    time.sleep(0.5)
                    session = cls.sessions.get(session_id)
                if not session or session.get('stopped'): break
                yield create_message("▶️ Resumed!")

            # Convert ('a','b') tuple to "ab" string
            guess = "".join(combination)
            attempts += 1

            # Log periodically so we don't slow down the computer
            if attempts <= 100 or attempts % 100000 == 0:
                yield create_message(f"Trying: {guess} (Attempt {attempts:,})")

            # Check if we found the password
            if guess == password:
                elapsed = time.time() - start_time
                yield create_message(f"✅ SUCCESS! Found '{guess}' in {attempts} tries.")
                yield create_message({'attempts': attempts, 'time': elapsed}, type="done")
                break
        else:
            yield create_message("❌ Failed: Exhausted all possibilities.", type="done")

        # Cleanup session
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
