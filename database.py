import sqlite3
from models.userModel import User
import json

def init_db():
    conn = sqlite3.connect('spotify_version_control.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            user_data TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_user(user):
    conn = sqlite3.connect('spotify_version_control.db')
    c = conn.cursor()
    
    # Convert user data to JSON string
    user_data = json.dumps(user.to_dict())
    
    # Insert or update user data
    c.execute('''
        INSERT OR REPLACE INTO users (id, name, user_data)
        VALUES (?, ?, ?)
    ''', (user.id, user.name, user_data))
    
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('spotify_version_control.db')
    c = conn.cursor()
    
    c.execute('SELECT user_data FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        user_data = json.loads(result[0])
        return User.from_dict(user_data)
    return None 