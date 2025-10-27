"""
Main application routes - Refactored with scalable architecture.
Using controller pattern for better separation of concerns.
"""
from app.controllers import (
    MainController,
    RevPiController,
    ServiceMonitorController,
    ConfigEditorController,
    AnalyticsController
)
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
analytics_controller = AnalyticsController('analytics', service_factory)

# Export blueprints for registration
main_bp = main_controller.blueprint
revpi_bp = revpi_controller.blueprint
service_monitor_bp = service_monitor_controller.blueprint
config_editor_bp = config_editor_controller.blueprint
analytics_bp = analytics_controller.blueprint

# Register RevPi routes under main blueprint for backward compatibility
main_bp.add_url_rule('/revpi-control', 'revpi_control', revpi_controller.revpi_control, methods=['GET'])
main_bp.add_url_rule('/revpi-status', 'revpi_status', revpi_controller.revpi_status, methods=['GET'])
main_bp.add_url_rule('/revpi-toggle', 'revpi_toggle', revpi_controller.revpi_toggle, methods=['POST'])
main_bp.add_url_rule('/revpi-time', 'revpi_time', revpi_controller.revpi_time, methods=['GET'])
main_bp.add_url_rule('/system-time', 'system_time', revpi_controller.system_time, methods=['GET'])
main_bp.add_url_rule('/log-service-activation', 'log_service_activation', revpi_controller.log_service_activation, methods=['POST'])

# Register schedule routes
main_bp.add_url_rule('/revpi-schedule/save', 'save_schedule', revpi_controller.save_schedule, methods=['POST'])
main_bp.add_url_rule('/revpi-schedule/get/<device_id>', 'get_schedule', revpi_controller.get_schedule, methods=['GET'])
main_bp.add_url_rule('/revpi-schedule/all', 'get_all_schedules', revpi_controller.get_all_schedules, methods=['GET'])
main_bp.add_url_rule('/revpi-schedule/enable', 'enable_schedule', revpi_controller.enable_schedule, methods=['POST'])
main_bp.add_url_rule('/revpi-schedule/delete/<device_id>', 'delete_schedule', revpi_controller.delete_schedule, methods=['DELETE'])
main_bp.add_url_rule('/revpi-schedule/check', 'check_schedule', revpi_controller.check_schedule, methods=['POST'])

# Register log download route
main_bp.add_url_rule('/download-logs-by-date', 'download_logs_by_date', revpi_controller.download_logs_by_date, methods=['POST'])

# Register switchboard configuration routes
main_bp.add_url_rule('/switchboard-config', 'get_switchboard_config', revpi_controller.get_switchboard_config, methods=['GET'])
main_bp.add_url_rule('/switchboard-config/update', 'update_switchboard_config', revpi_controller.update_switchboard_config, methods=['POST'])

# Register Service Monitor routes under main blueprint
main_bp.add_url_rule('/service-monitor', 'service_monitor', service_monitor_controller.service_monitor, methods=['GET'])
main_bp.add_url_rule('/service-status', 'service_status', service_monitor_controller.service_status, methods=['GET'])
main_bp.add_url_rule('/service-control', 'service_control', service_monitor_controller.service_control, methods=['POST'])

# Register Config Editor routes under main blueprint
main_bp.add_url_rule('/config-editor', 'config_editor', config_editor_controller.config_editor, methods=['GET'])
main_bp.add_url_rule('/config-data', 'config_data', config_editor_controller.config_data, methods=['GET'])
main_bp.add_url_rule('/config-save', 'config_save', config_editor_controller.config_save, methods=['POST'])
main_bp.add_url_rule('/log-directory', 'log_directory', config_editor_controller.log_directory, methods=['GET'])
main_bp.add_url_rule('/download-log-file/<filename>', 'download_log_file', config_editor_controller.download_log_file, methods=['GET'])
main_bp.add_url_rule('/download-selected-logs', 'download_selected_logs', config_editor_controller.download_selected_logs, methods=['POST'])

# Register Analytics routes under main blueprint
main_bp.add_url_rule('/analytics', 'analytics', analytics_controller.analytics_page, methods=['GET'])
main_bp.add_url_rule('/analytics/relay-activations', 'relay_activations_data', analytics_controller.relay_activations_data, methods=['GET'])
