import logging
import threading
import time
from queue import Queue
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class LoggerService:
    
    def __init__(self, config: Dict[str, Any], log_queue: Optional[Queue] = None):
        self.config = config
        self.log_queue = log_queue or Queue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        
        self._setup_logging()
        
    def _setup_logging(self):
        log_config = self.config.get('logging', {})
        log_file = log_config.get('log_file', 'logs/smart_home.log')
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))
        
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logger service initialized")
        
    def start(self):
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._log_loop, daemon=True)
        self._thread.start()
        self.logger.info("Logger service started")
        
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self.logger.info("Logger service stopped")
        
    def _log_loop(self):
        while self._running:
            try:
                if not self.log_queue.empty():
                    log_entry = self.log_queue.get(timeout=0.1)
                    self._write_log_entry(log_entry)
                else:
                    time.sleep(0.1)
            except Exception as e:
                if self._running:
                    self.logger.error(f"Error in logger service: {e}")
                time.sleep(0.1)
                
    def _write_log_entry(self, entry: Dict[str, Any]):
        timestamp = entry.get('timestamp', datetime.now().isoformat())
        level = entry.get('level', 'INFO')
        message = entry.get('message', '')
        source = entry.get('source', 'system')
        
        log_message = f"[{source}] {message}"
        
        if level == 'ERROR':
            self.logger.error(log_message)
        elif level == 'WARNING':
            self.logger.warning(log_message)
        elif level == 'DEBUG':
            self.logger.debug(log_message)
        else:
            self.logger.info(log_message)
            
    def log_event(self, message: str, level: str = 'INFO', source: str = 'system'):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'source': source
        }
        self.log_queue.put(entry)


