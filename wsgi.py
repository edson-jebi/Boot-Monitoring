#!/usr/bin/env python3
"""Production WSGI Entry Point for Boot-Monitoring"""
import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

# Create Flask application in production mode
application = create_app('production')

if __name__ == "__main__":
    application.run()
