import sys
import os

# Make sure the project root (parent of /api) is importable so `main.py` is found
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import app  # noqa: E402

# Vercel's Python runtime looks for a variable named `app` (ASGI) in this file.
