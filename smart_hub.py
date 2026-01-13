"""
Smart Home Hub - Moduli kryesor që menaxhon sensorët, aktorët dhe rregullat
"""
import threading
import time
import logging
from queue import Queue
from sensors import TemperatureSensor, LightSensor, MotionSensor
from actuators import LightActuator, HeatingActuator, AlarmActuator


class SmartHub:
    """Klasa kryesore për Smart Home Hub"""
    
    def __init__(self):
        # Queue për komunikim midis sensorëve dhe hub-it
        self.sensor_queue = Queue()
        
        # Inicializo sensorët
        self.temperature_sensor = TemperatureSensor(queue=self.sensor_queue)
        self.light_sensor = LightSensor(queue=self.sensor_queue)
        self.motion_sensor = MotionSensor(queue=self.sensor_queue)
        
        # Inicializo aktorët
        self.light_actuator = LightActuator()
        self.heating_actuator = HeatingActuator()
        self.alarm_actuator = AlarmActuator()
        
        # Gjendja e sistemit
        self.away_mode = False  # Nëse shtëpia është në "away mode"
        self.running = False
        
        # Thread për përpunimin e të dhënave
        self.processor_thread = None
        
        # Setup logging
        logging.basicConfig(
            filename='smart_home.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Të dhëna aktuale nga sensorët
        self.current_data = {
            'temperature': None,
            'humidity': None,
            'light_level': None,
            'is_dark': None,
            'motion_detected': None
        }
        
    def start(self):
        """Nis të gjithë sensorët dhe thread-in e përpunimit"""
        self.running = True
        
        # Nis sensorët
        self.temperature_sensor.start()
        self.light_sensor.start()
        self.motion_sensor.start()
        
        # Nis thread-in e përpunimit
        self.processor_thread = threading.Thread(target=self._process_sensor_data, daemon=True)
        self.processor_thread.start()
        
        self.logger.info("Smart Home Hub u nis me sukses")
        
    def stop(self):
        """Ndalo të gjithë sensorët"""
        self.running = False
        
        self.temperature_sensor.stop()
        self.light_sensor.stop()
        self.motion_sensor.stop()
        
        self.logger.info("Smart Home Hub u ndal")
        
    def _process_sensor_data(self):
        """Përpunon të dhënat nga sensorët dhe zbaton rregullat"""
        while self.running:
            try:
                # Merr të dhëna nga queue (me timeout për të shmangur blocking)
                try:
                    data = self.sensor_queue.get(timeout=1)
                    sensor_name = data['sensor']
                    value = data['value']
                    
                    # Përditëso të dhënat aktuale
                    if sensor_name == "Temperature":
                        self.current_data['temperature'] = value['temperature']
                        self.current_data['humidity'] = value['humidity']
                        self._apply_temperature_rules(value)
                        
                    elif sensor_name == "Light":
                        self.current_data['light_level'] = value['light_level']
                        self.current_data['is_dark'] = value['is_dark']
                        self._apply_light_rules(value)
                        
                    elif sensor_name == "Motion":
                        self.current_data['motion_detected'] = value['motion_detected']
                        self._apply_motion_rules(value)
                        
                    self.logger.info(f"Sensor {sensor_name}: {value}")
                    
                except:
                    pass  # Timeout - vazhdo loop
                    
            except Exception as e:
                self.logger.error(f"Gabim në përpunimin e të dhënave: {e}")
                
    def _apply_temperature_rules(self, temp_data):
        """Zbaton rregullat bazuar në temperaturën"""
        temp = temp_data['temperature']
        
        # Rregull: Nëse temperatura < 18°C, ndiz ngrohjen
        if temp < 18.0 and not self.heating_actuator.is_on():
            self.heating_actuator.turn_on()
            self.logger.info(f"Ngrohja u ndez (temperatura: {temp}°C)")
            
        # Rregull: Nëse temperatura > 25°C, fik ngrohjen
        elif temp > 25.0 and self.heating_actuator.is_on():
            self.heating_actuator.turn_off()
            self.logger.info(f"Ngrohja u fik (temperatura: {temp}°C)")
            
    def _apply_light_rules(self, light_data):
        """Zbaton rregullat bazuar në dritën"""
        is_dark = light_data['is_dark']
        motion = self.current_data.get('motion_detected', False)
        
        # Rregull: Nëse është errësirë dhe ka lëvizje, ndiz dritat
        if is_dark and motion and not self.light_actuator.is_on():
            self.light_actuator.set_brightness(80)
            self.logger.info("Dritat u ndezën automatikisht (errësirë + lëvizje)")
            
        # Rregull: Nëse nuk është errësirë, fik dritat
        elif not is_dark and self.light_actuator.is_on():
            self.light_actuator.turn_off()
            self.logger.info("Dritat u fikën (nuk është errësirë)")
            
    def _apply_motion_rules(self, motion_data):
        """Zbaton rregullat bazuar në lëvizjen"""
        motion_detected = motion_data['motion_detected']
        
        # Rregull: Nëse ka lëvizje dhe shtëpia është në "away mode", aktivizo alarm
        if motion_detected and self.away_mode and not self.alarm_actuator.is_on():
            self.alarm_actuator.trigger()
            self.logger.warning("ALARM: Lëvizje e zbuluar në away mode!")
            
    def set_away_mode(self, enabled):
        """Vendos ose çaktivizon away mode"""
        self.away_mode = enabled
        if enabled:
            self.logger.info("Away mode u aktivizua")
        else:
            self.logger.info("Away mode u çaktivizua")
            if self.alarm_actuator.is_on():
                self.alarm_actuator.reset()
                
    def get_status(self):
        """Kthen gjendjen aktuale të sistemit"""
        return {
            'sensors': {
                'temperature': self.current_data.get('temperature'),
                'humidity': self.current_data.get('humidity'),
                'light_level': self.current_data.get('light_level'),
                'is_dark': self.current_data.get('is_dark'),
                'motion_detected': self.current_data.get('motion_detected')
            },
            'actuators': {
                'light': self.light_actuator.get_info(),
                'heating': self.heating_actuator.get_info(),
                'alarm': self.alarm_actuator.get_info()
            },
            'away_mode': self.away_mode
        }
