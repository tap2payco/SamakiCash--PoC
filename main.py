# SamakiCash Backend - Entry Point
# This file exists for deployment compatibility
# The actual app is in app/main.py

from app.main import app

# Export the app for uvicorn
__all__ = ["app"]
