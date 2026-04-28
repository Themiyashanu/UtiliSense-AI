"""
Create admin user. Run: python scripts/create_admin.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    username = input("Admin username [admin]: ") or "admin"
    password = input("Admin password [admin123]: ") or "admin123"
    u = User.query.filter_by(username=username).first()
    if u:
        u.set_password(password)
        u.is_admin = True
        db.session.commit()
        print(f"Updated {username} as admin.")
    else:
        u = User(username=username, email=f"{username}@local")
        u.set_password(password)
        u.is_admin = True
        db.session.add(u)
        db.session.commit()
        print(f"Created admin user: {username}")
