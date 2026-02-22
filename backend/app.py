"""
Main Flask Application
Cyber Security Learning Platform Backend
"""

from flask import Flask, request, jsonify, send_from_directory
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
from attacks.mitm import MITMAttack
from attacks.dictionary import DictionaryAttack
from attacks.bruteforce import BruteForceAttack

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize auth handler
auth_handler = AuthHandler()

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
    
    success, message, token, user_id = auth_handler.login_user(username, password)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'token': token,
            'user_id': user_id,
            'username': username
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': message
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
        shift = int(data.get('shift', 3))
        
        encrypted = CaesarCipher.encrypt(plaintext, shift)
        
        return jsonify({
            'success': True,
            'encrypted': encrypted,
            'algorithm': 'caesar',
            'key': shift
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
        
        decrypted = CaesarCipher.decrypt(ciphertext, shift)
        
        return jsonify({
            'success': True,
            'decrypted': decrypted,
            'algorithm': 'caesar'
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
        encrypted_message = data.get('encrypted_message', '')
        algorithm = data.get('algorithm', 'caesar')
        modified_message = data.get('modified_message')
        key = data.get('key')
        
        result = MITMAttack.simulate_interception(encrypted_message, algorithm, modified_message, key)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/attack/dictionary', methods=['POST'])
def attack_dictionary():
    """Simulate dictionary attack"""
    data = request.get_json()
    
    try:
        target_password = data.get('password', '')
        max_attempts = int(data.get('max_attempts', 50))
        custom_wordlist = data.get('wordlist')
        
        result = DictionaryAttack.simulate_attack(target_password, max_attempts, custom_wordlist)
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@app.route('/api/attack/bruteforce', methods=['POST'])
def attack_bruteforce():
    """Simulate brute force attack"""
    data = request.get_json()
    
    try:
        ciphertext = data.get('ciphertext', '')
        algorithm = data.get('algorithm', 'caesar')
        
        if algorithm == 'caesar':
            result = BruteForceAttack.crack_caesar(ciphertext)
        else:
            return jsonify({
                'success': False,
                'message': f'Brute force not implemented for {algorithm}'
            }), 400
        
        return jsonify({
            'success': True,
            'result': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

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

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("🚀 Starting Cyber Security Learning Platform...")
    print("📍 Server running at: http://localhost:5000")
    print("🔐 Authentication: JWT + bcrypt")
    print("📚 Algorithms: Caesar, Hill, Playfair")
    print("⚔️  Attacks: MITM, Dictionary, Brute Force")
    print("\n✅ Ready to learn cybersecurity!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
