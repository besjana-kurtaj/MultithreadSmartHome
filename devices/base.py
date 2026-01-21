import threading
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from queue import Queue


class Device(ABC):
    
    def __init__(self, device_id: str, name: str, enabled: bool = True):
        self.device_id = device_id
        self.name = name
        self.enabled = enabled
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def start(self):
        if not self.enabled:
            self.logger.warning(f"{self.name} is disabled, not starting")
            return
            
        if self._running:
            self.logger.warning(f"{self.name} is already running")
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.logger.info(f"{self.name} started")
        
    def stop(self):
        with self._lock:
            self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self.logger.info(f"{self.name} stopped")
        
    def is_running(self) -> bool:
        with self._lock:
            return self._running
            
    @abstractmethod
    def _run(self):
        pass


class Sensor(Device):
    
    def __init__(self, device_id: str, name: str, update_interval: float, 
                 enabled: bool = True, data_queue: Optional[Queue] = None):
        super().__init__(device_id, name, enabled)
        self.update_interval = update_interval
        self.data_queue = data_queue or Queue()
        self._current_value: Any = None
        
    def get_current_value(self) -> Any:
        with self._lock:
            return self._current_value
            
    def _send_data(self, data: Dict[str, Any]):
        if self.data_queue:
            data['sensor_id'] = self.device_id
            data['sensor_name'] = self.name
            data['timestamp'] = time.time()
            self.data_queue.put(data)
            
    @abstractmethod
    def _read_sensor(self) -> Any:
        pass
        
    def _run(self):
        while self.is_running():
            try:
                value = self._read_sensor()
                with self._lock:
                    self._current_value = value
                self._send_data({'value': value})
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Error in {self.name}: {e}", exc_info=True)
                time.sleep(self.update_interval)


class Actuator(Device):
    
    def __init__(self, device_id: str, name: str, enabled: bool = True, 
                 command_queue: Optional[Queue] = None):
        super().__init__(device_id, name, enabled)
        self.command_queue = command_queue or Queue()
        self._state: Any = None
        
    def get_state(self) -> Any:
        with self._lock:
            return self._state
            
    def set_state(self, new_state: Any):
        with self._lock:
            old_state = self._state
            self._state = new_state
            if old_state != new_state:
                self.logger.info(f"{self.name} state changed: {old_state} -> {new_state}")
                self._on_state_change(old_state, new_state)
                
    @abstractmethod
    def _on_state_change(self, old_state: Any, new_state: Any):
        pass
        
    @abstractmethod
    def _execute_command(self, command: Dict[str, Any]):
        pass
        
    def _run(self):
        while self.is_running():
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get(timeout=0.1)
                    self._execute_command(command)
                else:
                    time.sleep(0.1)
            except Exception as e:
                if self.is_running():
                    self.logger.error(f"Error in {self.name}: {e}", exc_info=True)
                time.sleep(0.1)

