from flask import Flask, render_template, jsonify, request
import json
import logging
import os
from typing import Dict, Any, Optional


class SmartHomeWebApp:
    
    def __init__(self, hub, config: Dict[str, Any]):
        self.hub = hub
        self.config = config
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.app = Flask(__name__, template_folder=template_dir)
        
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        self._setup_routes()
        
    def _setup_routes(self):
        
        @self.app.route('/')
        def index():
            return render_template('index.html')
            
        @self.app.route('/api/status')
        def get_status():
            try:
                status = self.hub.get_status()
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/state')
        def get_state():
            try:
                state = self.hub.get_state()
                return jsonify(state)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/actuator/<actuator_name>', methods=['POST'])
        def control_actuator(actuator_name):
            try:
                data = request.get_json() or {}
                action = data.get('action', 'toggle')
                
                if actuator_name not in self.hub.actuator_command_queues:
                    return jsonify({'error': f'Actuator {actuator_name} not found'}), 404
                    
                command = {
                    'actuator': actuator_name,
                    'action': action
                }
                
                self.hub.actuator_command_queues[actuator_name].put(command)
                return jsonify({'success': True, 'message': f'Command sent to {actuator_name}'})
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
                
        @self.app.route('/api/config')
        def get_config():
            return jsonify(self.config)
            
    def run(self):
        flask_config = self.config.get('flask', {})
        host = flask_config.get('host', '127.0.0.1')
        port = flask_config.get('port', 5000)
        debug = flask_config.get('debug', False)
        
        import warnings
        warnings.filterwarnings('ignore', category=UserWarning)
        
        self.app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)

