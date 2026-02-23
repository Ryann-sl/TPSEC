
import time
import threading

class DictionaryAttack:

    _sessions = {}
    _lock = threading.Lock()

    @classmethod
    def create_session(cls, target_password, wordlist):
        import uuid
        session_id = str(uuid.uuid4())
        session = {
            'id': session_id,
            'target_password': target_password,
            'wordlist': wordlist,
            'logs': [],
            'attempts': 0,
            'total': len(wordlist),
            'found': False,
            'stopped': False,
            'paused': False,
            'done': False,
            'start_time': time.time(),
            'paused_accumulated': 0.0,  # total seconds spent paused
            'pause_start': None,
            'elapsed': 0.0,
        }
        with cls._lock:
            cls._sessions[session_id] = session
        # Run in background thread
        t = threading.Thread(target=cls._run, args=(session_id,), daemon=True)
        t.start()
        return session_id

    @classmethod
    def get_session(cls, session_id):
        with cls._lock:
            return cls._sessions.get(session_id)

    @classmethod
    def stop_session(cls, session_id):
        with cls._lock:
            s = cls._sessions.get(session_id)
            if s:
                s['stopped'] = True
                s['paused'] = False  # unblock the loop so it can exit

    @classmethod
    def pause_session(cls, session_id):
        with cls._lock:
            s = cls._sessions.get(session_id)
            if s and not s['done']:
                s['paused'] = True
                s['pause_start'] = time.time()

    @classmethod
    def resume_session(cls, session_id):
        with cls._lock:
            s = cls._sessions.get(session_id)
            if s and s['paused']:
                if s['pause_start'] is not None:
                    s['paused_accumulated'] += time.time() - s['pause_start']
                    s['pause_start'] = None
                s['paused'] = False

    @classmethod
    def _log(cls, session, message):
        session['logs'].append({
            'timestamp': time.time(),
            'message': message
        })

    @classmethod
    def _run(cls, session_id):
        with cls._lock:
            s = cls._sessions.get(session_id)
        if not s:
            return

        cls._log(s, "🎯 Dictionary Attack Initiated")
        cls._log(s, f"� Wordlist size: {s['total']} passwords")
        cls._log(s, "⚠️  Starting attack...\n")

        target = s['target_password'].lower()

        for password in s['wordlist']:
            # Wait while paused
            while s['paused'] and not s['stopped']:
                time.sleep(0.1)

            # Check stop flag
            if s['stopped']:
                cls._log(s, f"\n🛑 Attack stopped by user after {s['attempts']} attempts.")
                s['done'] = True
                s['elapsed'] = round(time.time() - s['start_time'], 2)
                return

            s['attempts'] += 1
            s['elapsed'] = round(time.time() - s['start_time'] - s['paused_accumulated'], 2)

            cls._log(s, f"Attempt {s['attempts']}: Trying '{password}'...")

            if password.lower() == target:
                s['found'] = True
                cls._log(s, f"\n✅ SUCCESS! Password cracked: '{password}'")
                cls._log(s, f"🔓 Found in {s['attempts']} attempts — {s['elapsed']}s elapsed")
                s['done'] = True
                s['elapsed'] = round(time.time() - s['start_time'] - s['paused_accumulated'], 2)
                return

            time.sleep(0.03)  # Simulate processing delay

        cls._log(s, f"\n❌ Attack completed — password not found after {s['attempts']} attempts.")
        s['done'] = True
        s['elapsed'] = round(time.time() - s['start_time'] - s['paused_accumulated'], 2)

    @staticmethod
    def check_password_strength(password):
        score = 0
        feedback = []
        common = [
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "letmein", "trustno1", "dragon", "baseball",
            "iloveyou", "master", "sunshine", "passw0rd", "shadow",
            "admin", "root", "toor", "pass", "test", "guest", "user"
        ]

        if len(password) >= 12:
            score += 2
            feedback.append("✅ Good length (12+ characters)")
        elif len(password) >= 8:
            score += 1
            feedback.append("⚠️  Acceptable length (8-11 characters)")
        else:
            feedback.append("❌ Too short (less than 8 characters)")

        if any(c.isupper() for c in password):
            score += 1
            feedback.append("✅ Contains uppercase letters")
        else:
            feedback.append("❌ No uppercase letters")

        if any(c.islower() for c in password):
            score += 1
            feedback.append("✅ Contains lowercase letters")
        else:
            feedback.append("❌ No lowercase letters")

        if any(c.isdigit() for c in password):
            score += 1
            feedback.append("✅ Contains numbers")
        else:
            feedback.append("❌ No numbers")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
            feedback.append("✅ Contains special characters")
        else:
            feedback.append("❌ No special characters")

        if password.lower() in common:
            score = 0
            feedback.append("❌ CRITICAL: Password in common dictionary!")

        if score >= 5:
            strength = "STRONG"
        elif score >= 3:
            strength = "MEDIUM"
        else:
            strength = "WEAK"

        return {
            'strength': strength,
            'score': score,
            'max_score': 6,
            'feedback': feedback
        }

    @staticmethod
    def explain_dictionary_attack():
        return {
            'title': 'Dictionary Attack',
            'description': 'An attack that tries passwords from a wordlist file.',
            'how_it_works': [
                '1. Attacker uploads a wordlist file',
                '2. Systematically tries each password',
                '3. Stops when password is found or list exhausted',
                '4. Can be interrupted at any time'
            ],
            'why_effective': [
                'Many users choose weak, common passwords',
                'Password reuse across multiple sites',
                'Predictable password patterns',
                'Human tendency to choose memorable words'
            ],
            'defenses': [
                'Use strong, unique passwords',
                'Enable account lockout policies',
                'Implement rate limiting',
                'Use multi-factor authentication (MFA)',
                'Monitor for suspicious login attempts',
                'Use password managers'
            ]
        }
