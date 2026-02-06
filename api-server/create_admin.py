#!/usr/bin/env python3
"""
Script to create an admin user for the MultiDesk Address Book API
"""

import sys
from main import SessionLocal, User, get_password_hash

def create_admin(username: str, password: str, email: str = None):
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"User '{username}' already exists!")
            return False
        
        # Create admin user
        admin = User(
            username=username,
            password_hash=get_password_hash(password),
            email=email,
            role="admin"
        )
        db.add(admin)
        db.commit()
        print(f"Admin user '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <username> <password> [email]")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_admin(username, password, email)
