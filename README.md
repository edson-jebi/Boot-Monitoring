# JEBI Web Application

## Overview
A Flask-based web application for controlling JEBI hardware with secure authentication and professional UI.

## Features
- 🔐 **Secure Authentication**: SQLite-based user management with password hashing
- 🎨 **Professional UI**: Clean, responsive design using Bradken colors and branding
- 🏗️ **Modular Architecture**: Well-organized code structure following Flask best practices
- 📝 **Comprehensive Logging**: Application and security logging with rotation
- 🛡️ **Security Features**: Rate limiting, input validation, security headers
- ⚡ **Error Handling**: Graceful error handling with custom error pages

## Project Structure
```
jebi-web-temp/
├── app/                          # Application package
│   ├── __init__.py              # Application factory
│   ├── auth/                    # Authentication module
│   ├── models/                  # Database models
│   ├── routes/                  # Route blueprints
│   ├── logging_config.py        # Logging configuration
│   └── error_handlers.py        # Error handling
├── templates/                   # Jinja2 templates
├── static/                      # Static files (CSS, images)
├── logs/                        # Application logs
├── config.py                    # Configuration management
├── web.py                       # Main application entry point
├── requirements.txt             # Python dependencies
└── .env.example                # Environment variables template

## Installation

1. **Clone and setup virtual environment:**
   ```bash
   cd jebi-web-temp
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application:**
   ```bash
   python web.py
   ```

## Default Credentials
- **Username:** bradken
- **Password:** adminBradken25

## Configuration
The application uses environment-based configuration:
- **Development:** Debug enabled, verbose logging
- **Production:** Security headers, restricted logging
- **Testing:** In-memory database, testing-specific settings

## Security Features
- Password hashing with salt
- Session management with timeout
- Rate limiting for login attempts
- Input validation and sanitization
- Security headers (XSS protection, CSRF protection)
- Comprehensive audit logging

## API Endpoints
- `GET /` - Home page (requires authentication)
- `GET /auth/login` - Login page
- `POST /auth/login` - Login form submission
- `GET /auth/logout` - Logout
- `GET /execute` - Execute piTest command

## Development Notes
This application follows semi-senior developer best practices:
- Separation of concerns with blueprints
- Configuration management
- Proper error handling and logging
- Security considerations
- Code documentation
- Modular architecture

## Production Deployment
For production deployment:
1. Set `FLASK_ENV=production`
2. Generate a secure `SECRET_KEY`
3. Configure proper logging
4. Use a production WSGI server (gunicorn, uwsgi)
5. Set up SSL/HTTPS
6. Configure firewall and security groups

## Maintenance
- Logs are automatically rotated (10MB max, 5 backups)
- Database is SQLite for simplicity (consider PostgreSQL for production)
- Monitor the logs/ directory for application and security events
