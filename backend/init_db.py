"""
Database Initialization Script
Creates the SQLite database with required tables
"""

import sqlite3
import os

def init_database():
    """Initialize the database with required tables"""
    
    # Create database directory if it doesn't exist
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    db_path = os.path.join(db_dir, 'security.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            algorithm TEXT NOT NULL,
            encrypted_text TEXT NOT NULL,
            key_used TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT 0,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')
    
    # Create Attack Logs table (for educational tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attack_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            attack_type TEXT NOT NULL,
            target_message_id INTEGER,
            success BOOLEAN,
            attempts INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (target_message_id) REFERENCES messages(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized successfully at: {db_path}")
    print("📊 Tables created:")
    print("   - users")
    print("   - messages")
    print("   - attack_logs")

if __name__ == "__main__":
    init_database()
