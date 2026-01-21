import json
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any

from hub import SmartHub
from services import LoggerService
from web.app import SmartHomeWebApp


class SmartHomeApplication:
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = self._load_config(config_path)
        self.hub: SmartHub = None
        self.logger_service: LoggerService = None
        self.web_app: SmartHomeWebApp = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)
            
    def initialize(self):
        print("Initializing Smart Home Hub...")
        
        self.logger_service = LoggerService(self.config)
        self.logger_service.start()
        
        self.hub = SmartHub(self.config)
        
        self.web_app = SmartHomeWebApp(self.hub, self.config)
        
        print("Initialization complete.")
        
    def start(self):
        print("Starting Smart Home Hub...")
        
        self.hub.start()
        
        import threading
        web_thread = threading.Thread(
            target=self.web_app.run,
            daemon=True
        )
        web_thread.start()
        
        time.sleep(1)
        
        flask_config = self.config.get('flask', {})
        host = flask_config.get('host', '127.0.0.1')
        port = flask_config.get('port', 5000)
        
        print(f"\n{'='*60}")
        print("Smart Home Hub is running!")
        print(f"Web Dashboard: http://{host}:{port}")
        print(f"{'='*60}\n")
        print("Press Ctrl+C to stop the system.\n")
        
    def stop(self):
        print("\nShutting down Smart Home Hub...")
        
        if self.hub:
            self.hub.stop()
            
        if self.logger_service:
            self.logger_service.stop()
            
        print("Shutdown complete.")
        
    def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.initialize()
            self.start()
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            
    def _signal_handler(self, signum, frame):
        self.stop()
        sys.exit(0)


def main():
    app = SmartHomeApplication()
    app.run()


if __name__ == '__main__':
    main()


