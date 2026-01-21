import random
import time
from typing import Dict, Any
from .base import Sensor


class TemperatureSensor(Sensor):
    
    def __init__(self, device_id: str, name: str, update_interval: float,
                 initial_value: float = 20.0, min_value: float = 15.0,
                 max_value: float = 25.0, variation_range: float = 2.0,
                 enabled: bool = True, data_queue=None):
        super().__init__(device_id, name, update_interval, enabled, data_queue)
        self.current_temp = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.variation_range = variation_range
        self._current_value = initial_value
        
    def _read_sensor(self) -> float:
        change = random.uniform(-self.variation_range, self.variation_range)
        self.current_temp = max(self.min_value, 
                               min(self.max_value, self.current_temp + change))
        return round(self.current_temp, 2)
        
    def simulate_heating_effect(self, heater_on: bool):
        if heater_on:
            self.current_temp = min(self.max_value, 
                                   self.current_temp + 0.1)
        else:
            self.current_temp = max(self.min_value, 
                                   self.current_temp - 0.05)


class LightSensor(Sensor):
    
    def __init__(self, device_id: str, name: str, update_interval: float,
                 initial_value: float = 50.0, min_value: float = 0.0,
                 max_value: float = 100.0, variation_range: float = 10.0,
                 enabled: bool = True, data_queue=None):
        super().__init__(device_id, name, update_interval, enabled, data_queue)
        self.current_level = initial_value
        self.min_value = min_value
        self.max_value = max_value
        self.variation_range = variation_range
        self._current_value = initial_value
        
    def _read_sensor(self) -> float:
        change = random.uniform(-self.variation_range, self.variation_range)
        self.current_level = max(self.min_value,
                                min(self.max_value, self.current_level + change))
        return round(self.current_level, 2)
        
    def simulate_light_effect(self, light_on: bool):
        if light_on:
            self.current_level = min(self.max_value,
                                   self.current_level + 20.0)
        else:
            self.current_level = max(self.min_value,
                                   self.current_level - 5.0)


class MotionSensor(Sensor):
    
    def __init__(self, device_id: str, name: str, update_interval: float,
                 motion_probability: float = 0.3, enabled: bool = True,
                 data_queue=None):
        super().__init__(device_id, name, update_interval, enabled, data_queue)
        self.motion_probability = motion_probability
        self._current_value = False
        self._motion_detected = False
        
    def _read_sensor(self) -> bool:
        self._motion_detected = random.random() < self.motion_probability
        return self._motion_detected
        
    def get_motion_detected(self) -> bool:
        return self._motion_detected

