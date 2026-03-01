import os
import time
import threading
import uuid

class DictionaryAttack:
    """
    Handles Dictionary Attacks using wordlists provided by the user.
    """
    _sessions = {}
    _lock = threading.Lock()

    @classmethod
    def create_session(cls, target, wordlist=None, file_path=None):
        """Initialize a dictionary attack session (supports array or file_path)."""
        session_id = str(uuid.uuid4())
        
        # Determine total passwords for progress tracking
        total_count = 0
        if wordlist:
            total_count = len(wordlist)
        elif file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for _ in f:
                        total_count += 1
            except Exception:
                total_count = 0

        with cls._lock:
            cls._sessions[session_id] = {
                'id': session_id,
                'target': target.lower(),
                'wordlist': wordlist,
                'file_path': file_path,
                'attempts': 0,
                'total': total_count,
                'found': False,
                'done': False,
                'paused': False,
                'start_time': time.time(),
                'paused_accumulated': 0,
                'pause_start': None,
                'elapsed': 0.0,
                'logs': [],
                'result_password': None
            }

        # Start background thread
        thread = threading.Thread(target=cls._run, args=(session_id,))
        thread.daemon = True
        thread.start()

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
                s['done'] = True
                s['paused'] = False

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
        """Background thread execution for dictionary attack."""
        with cls._lock:
            s = cls._sessions.get(session_id)
        if not s: return

        cls._log(s, "🚀 Starting Dictionary Attack...")
        
        # Determine source
        if s.get('wordlist'):
            cls._log(s, f"📋 Wordlist: Loaded {len(s['wordlist'])} entries from user upload.")
            source_desc = "user upload"
        elif s.get('file_path') and os.path.exists(s['file_path']):
            cls._log(s, f"📂 Wordlist: {os.path.basename(s['file_path'])}")
            source_desc = f"file ({os.path.basename(s['file_path'])})"
        else:
            cls._log(s, "❌ ERROR: No wordlist data provided or file missing.")
            s['done'] = True
            return

        cls._log(s, f"🎯 Target Password: {s['target']}")
        target = s['target']

        def get_words_stream():
            if s.get('wordlist'):
                for w in s['wordlist']:
                    yield w
            elif s.get('file_path'):
                try:
                    with open(s['file_path'], 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            yield line.strip()
                except Exception as e:
                    cls._log(s, f"⚠️ Error reading wordlist file: {str(e)}")
                    return

        try:
            for password in get_words_stream():
                # Check for stop/pause
                while s['paused'] and not s['done']:
                    time.sleep(0.5)
                
                if s['done']:
                    cls._log(s, f"\n🛑 Attack stopped after {s['attempts']} attempts.")
                    return

                if not password: continue

                s['attempts'] += 1
                s['elapsed'] = round(time.time() - s['start_time'] - s['paused_accumulated'], 1)

                # Periodic logging for feedback
                if s['attempts'] % 1000 == 0 or s['attempts'] <= 5:
                    cls._log(s, f"Testing: {password} (Attempt {s['attempts']})")

                # Smooth UI for fast attacks
                if s['attempts'] < 100:
                    time.sleep(0.01)

                if password.lower() == target:
                    s['found'] = True
                    cls._log(s, f"\n🎯 MATCH FOUND! Current password matching '{target}'")
                    cls._log(s, f"🔓 Results: '{password}' found in {s['elapsed']}s")
                    s['done'] = True
                    s['result_password'] = password
                    return

        except Exception as e:
            cls._log(s, f"⚠️ Background thread error: {str(e)}")

        s['done'] = True
        if not s['found']:
            cls._log(s, f"\n🛑 Dictionary exhausted ({source_desc}). No match found.")

    @staticmethod
    def check_password_strength(password):
        score = 0
        feedback = []

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
