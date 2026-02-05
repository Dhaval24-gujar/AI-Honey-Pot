"""
Vercel serverless function entry point
"""
from main import app

# Vercel expects a handler function
handler = app
