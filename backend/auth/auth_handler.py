"""
Authentication Handler
Manages user registration, login, and JWT token generation
"""

import bcrypt
import jwt
import sqlite3
from datetime import datetime, timedelta
import os

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "cyber_security_platform_secret_key_2026"
JWT_EXPIRATION_HOURS = 24

class AuthHandler:
    """Handles authentication operations"""
    
    def __init__(self):
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'database',
            'security.db'
        )
        self.db_path = db_path
    
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def generate_token(self, user_id, username):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return token
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register_user(self, username, password):
        """
        Register a new user
        Returns: (success: bool, message: str, user_id: int or None)
        """
        # Validate input
        if not username or not password:
            return False, "Username and password are required", None
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters", None
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters", None
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Insert into database
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return True, "User registered successfully", user_id
            
        except sqlite3.IntegrityError:
            return False, "Username already exists", None
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None
    
    def login_user(self, username, password):
        """
        Login user
        Returns: (success: bool, message: str, token: str or None, user_id: int or None)
        """
        if not username or not password:
            return False, "Username and password are required", None, None
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return False, "Invalid username or password", None, None
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                return False, "Invalid username or password", None, None
            
            # Generate token
            token = self.generate_token(user['id'], user['username'])
            
            return True, "Login successful", token, user['id']
            
        except Exception as e:
            return False, f"Login failed: {str(e)}", None, None
    
    def get_all_users(self):
        """Get all users (for messaging dropdown)"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, username FROM users ORDER BY username")
            users = cursor.fetchall()
            conn.close()
            
            return [{"id": user['id'], "username": user['username']} for user in users]
            
        except Exception as e:
            return []
