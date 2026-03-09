"""
Main Flask Application
Cyber Security Learning Platform Backend
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import sqlite3
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

from auth.auth_handler import AuthHandler
from crypto_algorithms.caesar import CaesarCipher
from crypto_algorithms.hill import HillCipher
from crypto_algorithms.playfair import PlayfairCipher
from crypto_algorithms.steganography import img_stego, audio_stego, video_stego
from attacks.mitm import MITMAttack
from attacks.dictionary import DictionaryAttack
from attacks.bruteforce import BruteForceAttack
from auth.rate_limiter import RateLimiter

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize auth handler and rate limiter
auth_handler = AuthHandler()
login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=900)

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'security.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def verify_token_middleware(token):
    """Verify JWT token"""
    if not token:
        return None
    
    payload = auth_handler.verify_token(token)
    return payload

# ==================== STATIC FILES ====================

@app.route('/')
def index():
    """Serve login page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)

# ==================== AUTHENTICATION ====================

@app.route('/api/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    success, message, user_id = auth_handler.register_user(username, password)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'user_id': user_id
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': message
        }), 400

@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username:
        return jsonify({'success': False, 'message': 'Username is required'}), 400

    # Check rate limit
    allowed, remaining, retry_after = login_rate_limiter.check_rate_limit(username)
    if not allowed:
        return jsonify({
            'success': False, 
            'message': f'Too many failed attempts. Please try again in {retry_after // 60} minutes and {retry_after % 60} seconds.',
            'retry_after': retry_after
        }), 429
    
    success, message, token, user_id = auth_handler.login_user(username, password)
    
    if success:
        # Reset attempts on success
        login_rate_limiter.reset_attempts(username)
        return jsonify({
            'success': True,
            'message': message,
            'token': token,
            'user_id': user_id,
            'username': username
        }), 200
    else:
        # Record failed attempt
        login_rate_limiter.record_failed_attempt(username)
        # Recalculate remaining for the message
        _, remaining, _ = login_rate_limiter.check_rate_limit(username)
        
        return jsonify({
            'success': False,
            'message': f'{message}. {remaining} attempts remaining before block.',
            'remaining_attempts': remaining
        }), 401

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users for messaging dropdown"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    payload = verify_token_middleware(token)
    if not payload:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    users = auth_handler.get_all_users()
    
    # Filter out current user
    current_user_id = payload['user_id']
    users = [u for u in users if u['id'] != current_user_id]
    
    return jsonify({
        'success': True,
        'users': users
    }), 200

# ==================== ENCRYPTION ====================

@app.route('/api/encrypt/caesar', methods=['POST'])
def encrypt_caesar():
    """Encrypt with Caesar cipher"""
    data = request.get_json()
    
    try:
        plaintext = data.get('plaintext', '')
        shift = data.get('shift', 3)
        direction = data.get('direction', 'right')
        
        # Ensure shift is integer
        try:
            shift = int(shift)
        except:
            shift = 3
            
        encrypted = CaesarCipher.encrypt(plaintext, shift, direction)
        
        return jsonify({
            'success': True,
            'encrypted': encrypted,
            'algorithm': 'caesar',
            'key': shift,
            'direction': direction
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/decrypt/caesar', methods=['POST'])
def decrypt_caesar():
    """Decrypt with Caesar cipher"""
    data = request.get_json()
    
    try:
        ciphertext = data.get('ciphertext', '')
        shift = int(data.get('shift', 3))
        direction = data.get('direction', 'right')
        
        decrypted = CaesarCipher.decrypt(ciphertext, shift, direction)
        
        return jsonify({
            'success': True,
            'decrypted': decrypted,
            'algorithm': 'caesar',
            'direction': direction
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/encrypt/hill', methods=['POST'])
def encrypt_hill():
    """Encrypt with Hill cipher"""
    data = request.get_json()
    
    try:
        plaintext = data.get('plaintext', '')
        key = data.get('key', 'HILL')
        
        encrypted = HillCipher.encrypt(plaintext, key)
        
        return jsonify({
            'success': True,
            'encrypted': encrypted,
            'algorithm': 'hill',
            'key': key
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/decrypt/hill', methods=['POST'])
def decrypt_hill():
    """Decrypt with Hill cipher"""
    data = request.get_json()
    
    try:
        ciphertext = data.get('ciphertext', '')
        key = data.get('key', 'HILL')
        
        decrypted = HillCipher.decrypt(ciphertext, key)
        
        return jsonify({
            'success': True,
            'decrypted': decrypted,
            'algorithm': 'hill'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/encrypt/playfair', methods=['POST'])
def encrypt_playfair():
    """Encrypt with Playfair cipher"""
    data = request.get_json()
    
    try:
        plaintext = data.get('plaintext', '')
        key = data.get('key', 'SECRET')
        
        encrypted = PlayfairCipher.encrypt(plaintext, key)
        
        return jsonify({
            'success': True,
            'encrypted': encrypted,
            'algorithm': 'playfair',
            'key': key
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/decrypt/playfair', methods=['POST'])
def decrypt_playfair():
    """Decrypt with Playfair cipher"""
    data = request.get_json()
    
    try:
        ciphertext = data.get('ciphertext', '')
        key = data.get('key', 'SECRET')
        
        decrypted = PlayfairCipher.decrypt(ciphertext, key)
        
        return jsonify({
            'success': True,
            'decrypted': decrypted,
            'algorithm': 'playfair'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# ==================== MESSAGING ====================

@app.route('/api/playfair/matrix', methods=['GET'])
def get_playfair_matrix():
    """Return the 5x5 Playfair key matrix for a given keyword"""
    keyword = request.args.get('keyword', 'SECRET')
    try:
        matrix = PlayfairCipher.prepare_key(keyword)
        return jsonify({'success': True, 'matrix': matrix, 'keyword': keyword}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send encrypted message"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    payload = verify_token_middleware(token)
    if not payload:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    try:
        sender_id = payload['user_id']
        receiver_id = data.get('receiver_id')
        algorithm = data.get('algorithm')
        encrypted_text = data.get('encrypted_text')
        key_used = data.get('key_used', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (sender_id, receiver_id, algorithm, encrypted_text, key_used)
            VALUES (?, ?, ?, ?, ?)
        ''', (sender_id, receiver_id, algorithm, encrypted_text, str(key_used)))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully',
            'message_id': message_id
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/messages/inbox', methods=['GET'])
def get_inbox():
    """Get inbox messages"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    payload = verify_token_middleware(token)
    if not payload:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    user_id = payload['user_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.*, u.username as sender_username
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.receiver_id = ?
            ORDER BY m.timestamp DESC
        ''', (user_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        messages_list = []
        for msg in messages:
            messages_list.append({
                'id': msg['id'],
                'sender_id': msg['sender_id'],
                'sender_username': msg['sender_username'],
                'algorithm': msg['algorithm'],
                'encrypted_text': msg['encrypted_text'],
                'key_used': msg['key_used'],
                'timestamp': msg['timestamp'],
                'is_read': bool(msg['is_read'])
            })
        
        return jsonify({
            'success': True,
            'messages': messages_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/messages/<int:message_id>/read', methods=['PUT'])
def mark_message_read(message_id):
    """Mark message as read"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    payload = verify_token_middleware(token)
    if not payload:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE messages SET is_read = 1
            WHERE id = ? AND receiver_id = ?
        ''', (message_id, payload['user_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Message marked as read'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# ==================== ATTACKS ====================

@app.route('/api/attack/mitm', methods=['POST'])
def attack_mitm():
    """Simulate MITM attack"""
    data = request.get_json()
    
    try:
        message = data.get('encrypted_message', '')
        modified_message = data.get('modified_message')
        
        result = MITMAttack.simulate_interception(message, modified_message)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/attack/dictionary/start', methods=['POST'])
def attack_dictionary_start():
    """Start a dictionary attack session using a user-provided wordlist and case mode"""
    data = request.get_json()
    try:
        target_password = data.get('password', '').strip()
        case_id = data.get('case_id')
        wordlist = data.get('wordlist')

        if not target_password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400
        
        if case_id != 'case1':
            return jsonify({'success': False, 'message': 'please use bruteforce'}), 400

        if not wordlist or not isinstance(wordlist, list):
            return jsonify({'success': False, 'message': 'Please implement a file (Wordlist required)'}), 400

        # Create session using the provided wordlist
        session_id = DictionaryAttack.create_session(target_password, wordlist=wordlist)
        
        # We can still track the case_id in logs if needed, but the wordlist is primary
        session = DictionaryAttack.get_session(session_id)
        if session and case_id:
            DictionaryAttack._log(session, f"📁 Attack Mode selected: {case_id.upper()}")

        return jsonify({'success': True, 'session_id': session_id}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Backend error: {str(e)}'}), 500


@app.route('/api/attack/dictionary/poll/<session_id>', methods=['GET'])
def attack_dictionary_poll(session_id):
    """Poll the current state of a dictionary attack session"""
    session = DictionaryAttack.get_session(session_id)
    if not session:
        return jsonify({'success': False, 'message': 'Session not found'}), 404

    return jsonify({
        'success': True,
        'attempts': session['attempts'],
        'total': session['total'],
        'found': session['found'],
        'paused': session['paused'],
        'done': session['done'],
        'elapsed': session['elapsed'],
        'logs': session['logs']
    }), 200


@app.route('/api/attack/dictionary/stop/<session_id>', methods=['POST'])
def attack_dictionary_stop(session_id):

    DictionaryAttack.stop_session(session_id)
    return jsonify({'success': True, 'message': 'Stop signal sent'}), 200


@app.route('/api/attack/dictionary/pause/<session_id>', methods=['POST'])
def attack_dictionary_pause(session_id):
    """Pause a running dictionary attack session"""
    DictionaryAttack.pause_session(session_id)
    return jsonify({'success': True, 'message': 'Attack paused'}), 200


@app.route('/api/attack/dictionary/resume/<session_id>', methods=['POST'])
def attack_dictionary_resume(session_id):
    """Resume a paused dictionary attack session"""
    DictionaryAttack.resume_session(session_id)
    return jsonify({'success': True, 'message': 'Attack resumed'}), 200

@app.route('/api/attack/bruteforce', methods=['POST'])
def attack_bruteforce():
    """Simulate brute force attack"""
    data = request.get_json()
    
    try:
        ciphertext = data.get('ciphertext', '')
        password = data.get('password', ciphertext)
        algorithm = data.get('algorithm', 'caesar')
        
        # We now use the raw password guessing regardless of if the UI still says 'caesar'
        if algorithm == 'caesar' or algorithm == 'password_guess' or algorithm == 'raw':
            import uuid
            session_id = str(uuid.uuid4())
            mode = data.get('mode', 3)
            generator = BruteForceAttack.crack_password(password, mode=mode, session_id=session_id)
            response = Response(generator, mimetype='text/event-stream')
            response.headers['Cache-Control'] = 'no-cache'
            response.headers['X-Accel-Buffering'] = 'no'
            response.headers['X-Session-ID'] = session_id
            return response
        else:
            return jsonify({
                'success': False,
                'message': f'Brute force not implemented for {algorithm}'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/attack/bruteforce/stop/<session_id>', methods=['POST'])
def attack_bruteforce_stop(session_id):
    BruteForceAttack.stop_session(session_id)
    return jsonify({'success': True, 'message': 'Stop signal sent'}), 200

@app.route('/api/attack/bruteforce/pause/<session_id>', methods=['POST'])
def attack_bruteforce_pause(session_id):
    BruteForceAttack.pause_session(session_id)
    return jsonify({'success': True, 'message': 'Attack paused'}), 200

@app.route('/api/attack/bruteforce/resume/<session_id>', methods=['POST'])
def attack_bruteforce_resume(session_id):
    BruteForceAttack.resume_session(session_id)
    return jsonify({'success': True, 'message': 'Attack resumed'}), 200

@app.route('/api/password/strength', methods=['POST'])
def check_password_strength():
    """Check password strength"""
    data = request.get_json()
    
    try:
        password = data.get('password', '')
        
        result = DictionaryAttack.check_password_strength(password)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

# ==================== EDUCATIONAL CONTENT ====================

@app.route('/api/info/mitm', methods=['GET'])
def info_mitm():
    """Get MITM attack information"""
    return jsonify(MITMAttack.explain_mitm()), 200

@app.route('/api/info/dictionary', methods=['GET'])
def info_dictionary():
    """Get dictionary attack information"""
    return jsonify(DictionaryAttack.explain_dictionary_attack()), 200

@app.route('/api/info/bruteforce', methods=['GET'])
def info_bruteforce():
    """Get brute force attack information"""
    return jsonify(BruteForceAttack.explain_brute_force()), 200

# ==================== STEGANOGRAPHY ====================

from crypto_algorithms.steganography import img_stego, audio_stego, video_stego
from attacks.mitm import MITMAttack
# ... (existing imports)

# ==================== STEGANOGRAPHY ====================

@app.route('/api/steganography/encode', methods=['POST'])
def steganography_encode():
    """Encode message in image using steganography"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token_middleware(token)
        if not payload:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        message = request.form.get('message', '')
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            file.save(temp_file.name)
            result = img_stego.encode_message(temp_file.name, message)
        os.unlink(temp_file.name)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/steganography/decode', methods=['POST'])
def steganography_decode():
    """Decode message from image"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token_middleware(token)
        if not payload:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            file.save(temp_file.name)
            result = img_stego.decode_message(temp_file.name)
        os.unlink(temp_file.name)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/steganography/audio/encode', methods=['POST'])
def steganography_audio_encode():
    """Encode message in audio (WAV)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token_middleware(token)
        if not payload:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        message = request.form.get('message', '')
        
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            file.save(temp_file.name)
            result = audio_stego.encode_message(temp_file.name, message)
        os.unlink(temp_file.name)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/steganography/audio/decode', methods=['POST'])
def steganography_audio_decode():
    """Decode message from audio"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token_middleware(token)
        if not payload:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            file.save(temp_file.name)
            result = audio_stego.decode_message(temp_file.name)
        os.unlink(temp_file.name)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/steganography/video/encode', methods=['POST'])
def steganography_video_encode():
    """Encode message in video (AVI/MP4)"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token_middleware(token)
        if not payload:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        message = request.form.get('message', '')
        
        import tempfile
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            file.save(temp_file.name)
            result = video_stego.encode_message(temp_file.name, message)
        os.unlink(temp_file.name)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/steganography/video/decode', methods=['POST'])
def steganography_video_decode():
    """Decode message from video"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_token_middleware(token)
        if not payload:
            return jsonify({'error': 'Invalid or missing token'}), 401
        
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        import tempfile
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            file.save(temp_file.name)
            result = video_stego.decode_message(temp_file.name)
        os.unlink(temp_file.name)
        return jsonify(result), (200 if result['success'] else 400)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("Starting Cyber Security Learning Platform...")
    print("Server running at: http://localhost:5000")
    print("Authentication: JWT + bcrypt")
    print("Algorithms: Caesar, Hill, Playfair")
    print("Steganography: LSB Image Steganography")
    print("Attacks: MITM, Dictionary, Brute Force")
    print("\nReady to learn cybersecurity!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
