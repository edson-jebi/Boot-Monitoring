"""
Main application routes - Refactored with scalable architecture.
Using controller pattern for better separation of concerns.
"""
from app.controllers import MainController, RevPiController, ServiceMonitorController, ConfigEditorController
from app.services import ServiceFactory
from config import get_config

# Initialize service factory
config = get_config()
service_factory = ServiceFactory(config)

# Initialize controllers
main_controller = MainController('main', service_factory)
revpi_controller = RevPiController('revpi', service_factory)
service_monitor_controller = ServiceMonitorController('service_monitor', service_factory)
config_editor_controller = ConfigEditorController('config_editor', service_factory)

# Export blueprints for registration
main_bp = main_controller.blueprint
revpi_bp = revpi_controller.blueprint
service_monitor_bp = service_monitor_controller.blueprint
config_editor_bp = config_editor_controller.blueprint

# Register RevPi routes under main blueprint for backward compatibility
main_bp.add_url_rule('/revpi-control', 'revpi_control', revpi_controller.revpi_control, methods=['GET'])
main_bp.add_url_rule('/revpi-status', 'revpi_status', revpi_controller.revpi_status, methods=['GET'])
main_bp.add_url_rule('/revpi-toggle', 'revpi_toggle', revpi_controller.revpi_toggle, methods=['POST'])

# Register Service Monitor routes under main blueprint
main_bp.add_url_rule('/service-monitor', 'service_monitor', service_monitor_controller.service_monitor, methods=['GET'])
main_bp.add_url_rule('/service-status', 'service_status', service_monitor_controller.service_status, methods=['GET'])
main_bp.add_url_rule('/service-control', 'service_control', service_monitor_controller.service_control, methods=['POST'])

# Register Config Editor routes under main blueprint
main_bp.add_url_rule('/config-editor', 'config_editor', config_editor_controller.config_editor, methods=['GET'])
main_bp.add_url_rule('/config-data', 'config_data', config_editor_controller.config_data, methods=['GET'])
main_bp.add_url_rule('/config-save', 'config_save', config_editor_controller.config_save, methods=['POST'])
