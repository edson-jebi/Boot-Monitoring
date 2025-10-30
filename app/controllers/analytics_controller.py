"""
Analytics controller for relay activation visualization.
"""
from flask import render_template, request, jsonify
from datetime import datetime, timedelta
from app.auth import login_required
from app.models import RelayActivation
from .base_controller import BaseController


class AnalyticsController(BaseController):
    """Controller for analytics and visualization routes."""

    def _register_routes(self):
        """Register analytics routes."""
        self.blueprint.add_url_rule('/analytics', 'analytics', self.analytics_page, methods=['GET'])
        self.blueprint.add_url_rule('/analytics/relay-activations', 'relay_activations_data',
                                     self.relay_activations_data, methods=['GET'])

    @login_required
    def analytics_page(self):
        """Analytics dashboard page."""
        self.log_user_action("accessed analytics dashboard")
        return render_template('analytics.html')

    @login_required
    def relay_activations_data(self):
        """
        Get relay activation data for visualization.

        Query parameters:
        - time_range: '1h', '24h', '1w', '1m' (default: '24h')
        - device_id: Filter by specific device (optional)
        """
        try:
            # Get query parameters
            time_range = request.args.get('time_range', '24h')
            device_id = request.args.get('device_id')

            # Calculate start time based on time range
            now = datetime.now()
            time_ranges = {
                '1h': timedelta(hours=1),
                '24h': timedelta(hours=24),
                '1w': timedelta(weeks=1),
                '1m': timedelta(days=30)
            }

            delta = time_ranges.get(time_range, timedelta(hours=24))
            start_time = now - delta

            # Format for SQLite
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

            # Get activation data
            relay_activation = RelayActivation()
            activations = relay_activation.get_activations(
                start_time=start_time_str,
                end_time=end_time_str,
                device_id=device_id,
                limit=2000
            )

            self.logger.info(
                f"Retrieved {len(activations)} relay activations for time_range={time_range}"
            )

            # Transform data for Chart.js
            chart_data = self._transform_for_chart(activations)

            return jsonify({
                'success': True,
                'time_range': time_range,
                'start_time': start_time_str,
                'end_time': end_time_str,
                'count': len(activations),
                'data': chart_data
            })

        except Exception as e:
            self.logger.error(f"Error getting relay activation data: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def _transform_for_chart(self, activations):
        """
        Transform activation data for Chart.js scatter plot.

        Returns data structured by component (device_id).
        """
        # Get unique components (device_ids)
        components = {}

        for activation in activations:
            device_id = activation.get('device_id')
            if not device_id:
                continue

            if device_id not in components:
                components[device_id] = {
                    'manual': [],
                    'automatic': []
                }

            # Parse timestamp
            timestamp = activation.get('timestamp')
            if not timestamp:
                continue

            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

            # Determine if manual or automatic
            is_automatic = activation.get('is_automatic', 0)
            action = activation.get('action', 'unknown')
            username = activation.get('username')

            point_data = {
                'x': dt.isoformat(),
                'component': device_id,
                'action': action,
                'username': username or 'Schedule',
                'success': activation.get('success', 1)
            }

            if is_automatic:
                components[device_id]['automatic'].append(point_data)
            else:
                components[device_id]['manual'].append(point_data)

        return {
            'components': list(components.keys()),
            'activations': components
        }
