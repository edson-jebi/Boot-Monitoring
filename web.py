#!/usr/bin/env python3
"""
JEBI Web Application Entry Point

This module serves as the main entry point for the JEBI Web Application.
It creates and configures the Flask application using the application factory pattern.

Author: Copilot (Refactored for scalability)
Date: 2025-09-22
"""

import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    app = create_app('development')
    logger.info("Starting JEBI Web Application on 0.0.0.0:5000")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    app.run(host='0.0.0.0', port=5000, debug=True)
