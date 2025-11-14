# Vercel serverless function entry point
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app

# Vercel will automatically use the 'app' object
# No need for a custom handler
