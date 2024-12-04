import sqlite3
from models.userModel import User
import json
from models.stageModel import StagedChange

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
    
    # Create staged_changes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS staged_changes (
            user_id TEXT PRIMARY KEY,
            change_data TEXT
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

def save_staged_change(user_id: str, staged_change: StagedChange) -> None:
    conn = sqlite3.connect('spotify_version_control.db')
    c = conn.cursor()
    
    # Create staged_changes table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS staged_changes (
            user_id TEXT PRIMARY KEY,
            change_data TEXT
        )
    ''')
    
    # Convert staged change to JSON string
    change_data = json.dumps(staged_change.to_dict())
    
    # Insert or update staged change
    c.execute('''
        INSERT OR REPLACE INTO staged_changes (user_id, change_data)
        VALUES (?, ?)
    ''', (user_id, change_data))
    
    conn.commit()
    conn.close()

def get_staged_change(user_id: str) -> StagedChange:
    conn = sqlite3.connect('spotify_version_control.db')
    c = conn.cursor()
    
    c.execute('SELECT change_data FROM staged_changes WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        change_data = json.loads(result[0])
        return StagedChange.from_dict(change_data)
    return None

def clear_staged_change(user_id: str) -> None:
    conn = sqlite3.connect('spotify_version_control.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM staged_changes WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()