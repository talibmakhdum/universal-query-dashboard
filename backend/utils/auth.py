import sqlite3
import os
import hashlib
import secrets
from typing import Dict, Any, Optional

file_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_DB_PATH = os.path.join(file_dir, 'auth.db')

def init_auth_db():
    with sqlite3.connect(AUTH_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def hash_password(password: str, salt: str) -> str:
    """Hash a password using pbkdf2_hmac and a salt."""
    return hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()

def create_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user in the database."""
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)
    
    try:
        with sqlite3.connect(AUTH_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
            """, (name, email, password_hash, salt))
            conn.commit()
            
            user_id = cursor.lastrowid
            return {
                "success": True,
                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email
                }
            }
    except sqlite3.IntegrityError:
        return {
            "success": False,
            "error": "User with this email already exists."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create user: {str(e)}"
        }

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """Authenticate a user using their email and password."""
    try:
        with sqlite3.connect(AUTH_DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                return {
                    "success": False,
                    "error": "Invalid email or password."
                }
            
            # Verify password
            salt = user["salt"]
            stored_hash = user["password_hash"]
            provided_hash = hash_password(password, salt)
            
            if provided_hash == stored_hash:
                return {
                    "success": True,
                    "user": {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"]
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid email or password."
                }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to authenticate: {str(e)}"
        }
