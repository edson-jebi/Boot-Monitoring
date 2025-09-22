"""
Main application routes - Refactored with scalable architecture.
Using controller pattern for better separation of concerns.
"""
from app.controllers import MainController, RevPiController
from app.services import ServiceFactory
from config import get_config

# Initialize service factory
config = get_config()
service_factory = ServiceFactory(config)

# Initialize controllers
main_controller = MainController('main', service_factory)
revpi_controller = RevPiController('revpi', service_factory)

# Export blueprints for registration
main_bp = main_controller.blueprint
revpi_bp = revpi_controller.blueprint

# Register RevPi routes under main blueprint for backward compatibility
main_bp.add_url_rule('/revpi-control', 'revpi_control', revpi_controller.revpi_control, methods=['GET'])
main_bp.add_url_rule('/revpi-status', 'revpi_status', revpi_controller.revpi_status, methods=['GET'])
main_bp.add_url_rule('/revpi-toggle', 'revpi_toggle', revpi_controller.revpi_toggle, methods=['POST'])
