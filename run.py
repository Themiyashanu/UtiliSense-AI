"""
Run Flask application.
Usage: python run.py
"""
import os
from pathlib import Path

# Ensure project root is in path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
