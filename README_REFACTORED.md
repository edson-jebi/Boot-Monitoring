# JEBI Web Application - RevPi Control System

A professional Flask-based web application for controlling RevPi (Revolution Pi) devices with real-time status monitoring and comprehensive logging.

## 🌟 Features

### Core Functionality
- **Secure Authentication**: SHA-256 password hashing with session management
- **RevPi Device Control**: Toggle devices ON/OFF with piTest commands
- **Real-time Status Monitoring**: Live device status updates every 3 seconds
- **Command Execution**: Execute custom piTest commands
- **Simulation Mode**: Automatic fallback for development without hardware

### Technical Features
- **Service Layer Architecture**: Clean separation of business logic
- **Comprehensive Logging**: Structured logging with different levels
- **Error Handling**: Robust error handling with user-friendly messages
- **Configuration Validation**: Automatic validation of application settings
- **RESTful API**: JSON APIs for device control and status
- **Responsive UI**: Mobile-friendly interface with Bradken branding

### Security Features
- **Session Management**: Configurable session timeout
- **Authentication Required**: All operations require login
- **Input Validation**: Comprehensive request validation
- **Security Headers**: XSS protection, content-type options, frame options
- **Audit Logging**: All device operations are logged with user context

## 🏗️ Architecture

### Project Structure
```
jebi-web-temp/
├── app/
│   ├── __init__.py          # Application factory
│   ├── auth/                # Authentication module
│   ├── dto/                 # Data Transfer Objects
│   ├── models/              # Database models
│   ├── routes/              # Route handlers
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions and validators
│   ├── error_handlers.py    # Centralized error handling
│   └── logging_config.py    # Logging configuration
├── templates/               # Jinja2 templates
├── static/                  # CSS, images, and static files
├── config.py                # Configuration management
├── web.py                   # Application entry point
└── requirements.txt         # Python dependencies
```

### Service Layer
- **RevPiService**: Handles all RevPi device interactions
- **CommandService**: Manages system command execution
- **Configuration Validation**: Ensures proper application setup

### Data Transfer Objects (DTOs)
- **ApiResponse**: Standardized API response format
- **RevPiDeviceStatus**: Device status information
- **RevPiToggleRequest**: Device control requests

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- piTest command (for RevPi hardware) - optional for development

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd jebi-web-temp
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

5. **Run the application**
   ```bash
   python web.py
   ```

6. **Access the application**
   - Open browser to `http://localhost:5000`
   - Default credentials: `bradken` / `adminBradken25`

## ⚙️ Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key (change in production)
- `DEBUG`: Enable/disable debug mode (default: False)
- `PORT`: Application port (default: 5000)
- `HOST`: Host address (default: 0.0.0.0)
- `DATABASE_PATH`: SQLite database file path
- `SESSION_TIMEOUT`: Session timeout in seconds (default: 3600)
- `COMMAND_TIMEOUT`: Command execution timeout (default: 10)

### RevPi Device Configuration
Edit `config.py` to modify the `config_map_revpi` dictionary:

```python
config_map_revpi = {
    'RelayProcessor': "Relay Processor",
    'RelayScreen': "Relay Screen", 
    'LedProcessor': "LED Processor",
    'LedScreen': "LED Screen",
    # Add more devices as needed
}
```

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export DEBUG=true
python web.py
```

### Code Quality Tools
```bash
# Code formatting
black app/ config.py web.py

# Linting
flake8 app/ config.py web.py

# Type checking
mypy app/ config.py web.py
```

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🌐 API Documentation

### Authentication
All API endpoints require authentication via session cookies.

### Device Control
- **POST** `/revpi-toggle`
  ```json
  {
    "device": "RelayProcessor",
    "action": "on"  // or "off"
  }
  ```

### Device Status
- **GET** `/revpi-status`
  ```json
  {
    "RelayProcessor": {
      "status": "ON",
      "value": 0,
      "is_simulated": false
    }
  }
  ```

## 🔒 Security Considerations

### Production Deployment
1. **Change default credentials** in production
2. **Set strong SECRET_KEY** environment variable
3. **Disable debug mode** (`DEBUG=False`)
4. **Use HTTPS** in production
5. **Configure firewall** to restrict access
6. **Regular security updates** of dependencies

### Authentication
- Sessions expire after configured timeout
- All device operations require authentication
- Failed login attempts are logged

## 📊 Logging

### Log Levels
- **INFO**: Normal operations and system events
- **WARNING**: Potential issues and security events
- **ERROR**: Error conditions and failures
- **DEBUG**: Detailed debugging information

### Log Files
- Logs are written to `logs/` directory
- Automatic log rotation to prevent disk space issues
- Structured logging with timestamps and user context

## 🚀 Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 web:app
```

### Using Waitress (Windows-friendly)
```bash
waitress-serve --host=0.0.0.0 --port=5000 web:app
```

### Systemd Service Example
```ini
[Unit]
Description=JEBI Web Application
After=network.target

[Service]
User=pi
WorkingDirectory=/path/to/jebi-web-temp
Environment=PATH=/path/to/jebi-web-temp/venv/bin
ExecStart=/path/to/jebi-web-temp/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 web:app
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🐛 Troubleshooting

### Common Issues

1. **piTest command not found**
   - Application automatically switches to simulation mode
   - Install RevPi tools for hardware control

2. **Permission denied for database**
   - Ensure write permissions for database file and directory
   - Check SQLite database path configuration

3. **Port already in use**
   - Change PORT environment variable
   - Kill existing processes using the port

4. **Session timeout issues**
   - Adjust SESSION_TIMEOUT in configuration
   - Check browser cookie settings

## 📝 License

This project is proprietary software for Bradken operations.

## 🤝 Contributing

1. Follow the established architecture patterns
2. Add appropriate logging and error handling
3. Update documentation for new features
4. Ensure backward compatibility
5. Test both simulation and hardware modes

## 📞 Support

For technical support and questions, please contact the development team.
