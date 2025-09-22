# JEBI Web Application - Boot Monitoring System

## 🚀 Overview

The **JEBI Web Application** is an enterprise-grade Flask-based web interface for monitoring and controlling RevPi (Revolution Pi) devices. It features a scalable architecture with real-time status monitoring, secure authentication, and a responsive user interface with Bradken corporate branding.

## ✨ Features

### 🔐 Security & Authentication
- **Secure Login System**: SHA-256 password hashing
- **Session Management**: Flask session-based authentication
- **User Credentials**: Default login `bradken` / `adminBradken25`
- **SQLite Database**: User data persistence

### 🎛️ RevPi Device Control
- **Real-time Status Monitoring**: Updates every 3 seconds
- **Toggle Controls**: On/Off switches for RevPi devices
- **Device Configuration**: Based on `config_map_revpi` mapping
- **Simulation Mode**: Development mode without hardware dependency

### 🏗️ Enterprise Architecture
- **Controller Pattern**: Separation of route handling and business logic
- **Service Layer**: Device-specific business logic abstraction
- **Factory Pattern**: Dependency injection for services
- **DTO Layer**: Clean API response structure
- **Blueprint Architecture**: Modular Flask application structure

### 🎨 User Interface
- **Responsive Design**: Mobile-friendly interface
- **Bradken Branding**: Corporate colors (#005596, #F3CB3C)
- **Real-time Updates**: JavaScript-powered status indicators
- **Navigation Tabs**: Extensible tab-based interface

## 📁 Project Structure

```
jebi-web-temp/
├── web.py                    # Application entry point
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── app/
│   ├── __init__.py          # Application factory
│   ├── controllers/         # 🆕 Route handling logic
│   │   ├── base_controller.py
│   │   ├── main_controller.py
│   │   └── revpi_controller.py
│   ├── services/            # 🆕 Business logic layer
│   │   ├── base_service.py
│   │   ├── revpi_service.py
│   │   ├── command_service.py
│   │   └── service_factory.py
│   ├── routes/              # Route definitions
│   │   ├── auth.py
│   │   └── main.py
│   ├── models/              # Database models
│   │   └── __init__.py
│   ├── auth/                # Authentication utilities
│   │   └── __init__.py
│   └── logging_config.py    # Logging configuration
├── static/                  # CSS, images, JavaScript
│   ├── core.css
│   ├── color.css
│   ├── logo.png
│   └── bradken_log.png
└── templates/               # Jinja2 HTML templates
    ├── base.html
    ├── login.html
    ├── home.html
    └── revpi_control.html
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- RevPi hardware (optional - simulation mode available)
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/edson-jebi/Boot-Monitoring.git
   cd Boot-Monitoring
   ```

2. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python web.py
   ```

5. **Access the application**:
   - Open browser to `http://localhost:5000`
   - Login with: `bradken` / `adminBradken25`

## 🎛️ Usage

### Login
1. Navigate to the login page
2. Enter credentials: `bradken` / `adminBradken25`
3. Click "Login" to access the dashboard

### RevPi Control
1. Click on "RevPi Control" tab
2. View real-time status of all devices (green = ON, red = OFF)
3. Use toggle buttons to control devices
4. Status updates automatically every 3 seconds

### Navigation
- **Home**: Overview dashboard
- **RevPi Control**: Device control interface
- **Logout**: End session securely

## ⚙️ Configuration

### Device Mapping
Edit `config.py` to modify device configuration:

```python
config_map_revpi = {
    'RelayProcessor': {'description': 'Main relay processor'},
    'RelayScreen': {'description': 'Screen relay control'},
    'LedProcessor': {'description': 'LED processor unit'},
    'LedScreen': {'description': 'LED screen controller'}
}
```

### Environment Variables
Copy `.env.example` to `.env` and configure:

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///dev_users.db
```

## 🏗️ Architecture Details

### Scalable Design
The application is designed for easy extension:

1. **Adding New Device Types**:
   ```python
   # Create new controller
   class PLCController(BaseController):
       # Implementation
   
   # Create new service
   class PLCService(DeviceServiceInterface):
       # Implementation
   
   # Register in ServiceFactory
   ```

2. **Adding New Tabs**:
   - Create controller in `app/controllers/`
   - Create service in `app/services/`
   - Add routes in `app/routes/`
   - Create template in `templates/`

### Service Layer Pattern
- **DeviceServiceInterface**: Abstract interface for all device services
- **RevPiService**: Specific implementation for RevPi devices
- **CommandService**: Shell command execution abstraction
- **ServiceFactory**: Dependency injection container

### Controller Pattern
- **BaseController**: Common functionality for all controllers
- **MainController**: Home and general routes
- **RevPiController**: RevPi-specific route handling

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python web.py
```

### Testing Without Hardware
The application includes simulation mode that activates automatically when RevPi hardware is not detected.

### Logging
Logs are configured in `app/logging_config.py` with different levels:
- **INFO**: General application flow
- **WARNING**: Configuration warnings
- **ERROR**: Application errors

## 📝 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout user

### Main Application
- `GET /` - Home dashboard
- `GET /revpi-control` - RevPi control interface

### RevPi API
- `GET /revpi-status` - Get real-time device status (JSON)
- `POST /revpi-toggle` - Toggle device state (JSON)

## 🔒 Security Features

- **Password Hashing**: SHA-256 with salt
- **Session Management**: Secure Flask sessions
- **CSRF Protection**: Built-in Flask security
- **Input Validation**: Server-side validation
- **Logging**: Comprehensive audit trail

## 🚀 Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web:app
```

### Using nginx (Reverse Proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Configuration
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=sqlite:///production.db
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- **Repository**: [Boot-Monitoring](https://github.com/edson-jebi/Boot-Monitoring)
- **Issues**: [GitHub Issues](https://github.com/edson-jebi/Boot-Monitoring/issues)

## 🎯 Roadmap

- [ ] Multi-device type support (PLC, Sensors, etc.)
- [ ] Advanced user management
- [ ] Real-time data visualization
- [ ] Alert and notification system
- [ ] Mobile application
- [ ] REST API documentation
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests

---

**Built with ❤️ for industrial automation and monitoring**
