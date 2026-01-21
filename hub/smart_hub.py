import threading
import time
import logging
from queue import Queue
from typing import Dict, Any, Optional
from datetime import datetime

from devices import (
    TemperatureSensor, LightSensor, MotionSensor,
    LightActuator, HeaterActuator, AlarmActuator
)
from .rule_engine import RuleEngine


class SmartHub:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        self.sensor_data_queue = Queue()
        self.actuator_command_queues: Dict[str, Queue] = {}
        
        self.sensors: Dict[str, Any] = {}
        self.actuators: Dict[str, Any] = {}
        
        self.state: Dict[str, Any] = {}
        self._state_lock = threading.Lock()
        
        self._running = False
        self._controller_thread: Optional[threading.Thread] = None
        
        self.rule_engine = RuleEngine(config)
        
        self._initialize_devices()
        
    def _initialize_devices(self):
        sensors_config = self.config.get('sensors', {})
        actuators_config = self.config.get('actuators', {})
        
        # Initialize sensors
        if sensors_config.get('temperature', {}).get('enabled', False):
            temp_config = sensors_config['temperature']
            temp_sensor = TemperatureSensor(
                device_id='temp_01',
                name='Temperature Sensor',
                update_interval=temp_config.get('update_interval', 2.0),
                initial_value=temp_config.get('initial_value', 20.0),
                min_value=temp_config.get('min_value', 15.0),
                max_value=temp_config.get('max_value', 25.0),
                variation_range=temp_config.get('variation_range', 2.0),
                enabled=True,
                data_queue=self.sensor_data_queue
            )
            self.sensors['temperature'] = temp_sensor
            
        if sensors_config.get('light', {}).get('enabled', False):
            light_config = sensors_config['light']
            light_sensor = LightSensor(
                device_id='light_01',
                name='Light Sensor',
                update_interval=light_config.get('update_interval', 1.5),
                initial_value=light_config.get('initial_value', 50.0),
                min_value=light_config.get('min_value', 0.0),
                max_value=light_config.get('max_value', 100.0),
                variation_range=light_config.get('variation_range', 10.0),
                enabled=True,
                data_queue=self.sensor_data_queue
            )
            self.sensors['light'] = light_sensor
            
        if sensors_config.get('motion', {}).get('enabled', False):
            motion_config = sensors_config['motion']
            motion_sensor = MotionSensor(
                device_id='motion_01',
                name='Motion Sensor',
                update_interval=motion_config.get('update_interval', 3.0),
                motion_probability=motion_config.get('motion_probability', 0.3),
                enabled=True,
                data_queue=self.sensor_data_queue
            )
            self.sensors['motion'] = motion_sensor
            
        # Initialize actuators
        if actuators_config.get('light', {}).get('enabled', False):
            light_queue = Queue()
            self.actuator_command_queues['light'] = light_queue
            light_actuator = LightActuator(
                device_id='light_act_01',
                name='Light Actuator',
                enabled=True,
                initial_state=actuators_config['light'].get('initial_state', False),
                command_queue=light_queue
            )
            self.actuators['light'] = light_actuator
            
        if actuators_config.get('heater', {}).get('enabled', False):
            heater_queue = Queue()
            self.actuator_command_queues['heater'] = heater_queue
            heater_config = actuators_config['heater']
            heater_actuator = HeaterActuator(
                device_id='heater_01',
                name='Heater Actuator',
                enabled=True,
                initial_state=heater_config.get('initial_state', False),
                target_temperature=heater_config.get('target_temperature', 20.0),
                command_queue=heater_queue
            )
            self.actuators['heater'] = heater_actuator
            
        if actuators_config.get('alarm', {}).get('enabled', False):
            alarm_queue = Queue()
            self.actuator_command_queues['alarm'] = alarm_queue
            alarm_actuator = AlarmActuator(
                device_id='alarm_01',
                name='Alarm Actuator',
                enabled=True,
                initial_state=actuators_config['alarm'].get('initial_state', False),
                command_queue=alarm_queue
            )
            self.actuators['alarm'] = alarm_actuator
            
        self.logger.info(f"Initialized {len(self.sensors)} sensors and {len(self.actuators)} actuators")
        
    def start(self):
        if self._running:
            self.logger.warning("Hub is already running")
            return
            
        self.logger.info("Starting Smart Home Hub...")
        self._running = True
        
        for sensor in self.sensors.values():
            sensor.start()
            
        for actuator in self.actuators.values():
            actuator.start()
            
        self._controller_thread = threading.Thread(target=self._controller_loop, daemon=True)
        self._controller_thread.start()
        
        self.logger.info("Smart Home Hub started successfully")
        
    def stop(self):
        self.logger.info("Stopping Smart Home Hub...")
        self._running = False
        
        for sensor in self.sensors.values():
            sensor.stop()
            
        for actuator in self.actuators.values():
            actuator.stop()
            
        if self._controller_thread:
            self._controller_thread.join(timeout=5.0)
            
        self.logger.info("Smart Home Hub stopped")
        
    def _controller_loop(self):
        while self._running:
            try:
                self._process_sensor_data()
                self._update_state()
                self._evaluate_and_execute_rules()
                self._simulate_device_interactions()
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error in controller loop: {e}", exc_info=True)
                time.sleep(1.0)
                
    def _process_sensor_data(self):
        while not self.sensor_data_queue.empty():
            try:
                data = self.sensor_data_queue.get_nowait()
                sensor_id = data.get('sensor_id', '')
                sensor_name = data.get('sensor_name', '')
                value = data.get('value')
                timestamp = data.get('timestamp', time.time())
                
                sensor_type = None
                for key, sensor in self.sensors.items():
                    if sensor.device_id == sensor_id:
                        sensor_type = key
                        break
                        
                if sensor_type:
                    with self._state_lock:
                        if 'sensors' not in self.state:
                            self.state['sensors'] = {}
                        self.state['sensors'][sensor_type] = {
                            'value': value,
                            'timestamp': timestamp,
                            'sensor_id': sensor_id,
                            'sensor_name': sensor_name
                        }
                        
            except Exception as e:
                self.logger.error(f"Error processing sensor data: {e}")
                
    def _update_state(self):
        with self._state_lock:
            for sensor_type, sensor in self.sensors.items():
                if 'sensors' not in self.state:
                    self.state['sensors'] = {}
                if sensor_type not in self.state['sensors']:
                    self.state['sensors'][sensor_type] = {}
                self.state['sensors'][sensor_type]['value'] = sensor.get_current_value()
                
            self.state['actuators'] = {}
            for actuator_type, actuator in self.actuators.items():
                self.state['actuators'][actuator_type] = {
                    'state': actuator.get_state(),
                    'device_id': actuator.device_id,
                    'name': actuator.name
                }
                
            self.state['temperature'] = self.state.get('sensors', {}).get('temperature', {})
            self.state['light'] = self.state.get('sensors', {}).get('light', {})
            self.state['motion'] = self.state.get('sensors', {}).get('motion', {})
            self.state['heater'] = self.state.get('actuators', {}).get('heater', {})
            self.state['light_actuator'] = self.state.get('actuators', {}).get('light', {})
            self.state['alarm'] = self.state.get('actuators', {}).get('alarm', {})
            
    def _evaluate_and_execute_rules(self):
        with self._state_lock:
            state_copy = self.state.copy()
            
        commands = self.rule_engine.evaluate_rules(state_copy)
        
        for command in commands:
            actuator_name = command.get('actuator')
            if actuator_name in self.actuator_command_queues:
                self.actuator_command_queues[actuator_name].put(command)
                
    def _simulate_device_interactions(self):
        if 'heater' in self.actuators and 'temperature' in self.sensors:
            heater_on = self.actuators['heater'].is_on()
            if isinstance(self.sensors['temperature'], TemperatureSensor):
                self.sensors['temperature'].simulate_heating_effect(heater_on)
                
        if 'light' in self.actuators and 'light' in self.sensors:
            light_on = self.actuators['light'].is_on()
            if isinstance(self.sensors['light'], LightSensor):
                self.sensors['light'].simulate_light_effect(light_on)
                
    def get_state(self) -> Dict[str, Any]:
        with self._state_lock:
            return self.state.copy()
            
    def get_status(self) -> Dict[str, Any]:
        state = self.get_state()
        return {
            'running': self._running,
            'sensors': {
                name: {
                    'value': sensor.get_current_value(),
                    'running': sensor.is_running()
                }
                for name, sensor in self.sensors.items()
            },
            'actuators': {
                name: {
                    'state': actuator.get_state(),
                    'running': actuator.is_running()
                }
                for name, actuator in self.actuators.items()
            },
            'state': state
        }

