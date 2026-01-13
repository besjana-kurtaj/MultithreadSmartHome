"""
Modul për sensorët e Smart Home
Çdo sensor ekzekutohet në thread-in e vet dhe gjeneron vlera çdo 1-2 sekonda
"""
import threading
import time
import random
from queue import Queue


class Sensor(threading.Thread):
    """Klasa bazë për sensorë"""
    
    def __init__(self, name, update_interval=2, queue=None):
        super().__init__(daemon=True)
        self.name = name
        self.update_interval = update_interval
        self.queue = queue
        self.running = False
        self.current_value = None
        
    def read_value(self):
        """Metodë abstrakte që duhet të implementohet në nënklasat"""
        raise NotImplementedError
        
    def run(self):
        """Thread kryesor që lexon vlerat periodikisht"""
        self.running = True
        while self.running:
            value = self.read_value()
            self.current_value = value
            if self.queue:
                self.queue.put({
                    'sensor': self.name,
                    'value': value,
                    'timestamp': time.time()
                })
            time.sleep(self.update_interval)
    
    def stop(self):
        """Ndalo sensorin"""
        self.running = False


class TemperatureSensor(Sensor):
    """Sensor i temperaturës dhe lagështisë"""
    
    def __init__(self, queue=None):
        super().__init__("Temperature", update_interval=2, queue=queue)
        self.temperature = 20.0  # Temperatura fillestare (°C)
        self.humidity = 50.0  # Lagështia fillestare (%)
        
    def read_value(self):
        """Gjeneron vlera të reja të temperaturës dhe lagështisë"""
        # Simulim: temperatura ndryshon gradualisht
        self.temperature += random.uniform(-0.5, 0.5)
        self.temperature = max(15.0, min(30.0, self.temperature))
        
        self.humidity += random.uniform(-2, 2)
        self.humidity = max(30.0, min(70.0, self.humidity))
        
        return {
            'temperature': round(self.temperature, 1),
            'humidity': round(self.humidity, 1)
        }


class LightSensor(Sensor):
    """Sensor i dritës (nivel i dritës në ambient)"""
    
    def __init__(self, queue=None):
        super().__init__("Light", update_interval=1.5, queue=queue)
        self.light_level = 50.0  # Nivel fillestar (0-100)
        
    def read_value(self):
        """Gjeneron vlera të reja të nivelit të dritës"""
        # Simulim: dritë ndryshon gradualisht
        self.light_level += random.uniform(-5, 5)
        self.light_level = max(0.0, min(100.0, self.light_level))
        
        return {
            'light_level': round(self.light_level, 1),
            'is_dark': self.light_level < 30.0  # Errësirë nëse < 30
        }


class MotionSensor(Sensor):
    """Sensor i lëvizjes"""
    
    def __init__(self, queue=None):
        super().__init__("Motion", update_interval=1, queue=queue)
        self.motion_detected = False
        
    def read_value(self):
        """Gjeneron vlera të reja të lëvizjes"""
        # Simulim: lëvizje e rastësishme
        # 20% shans për të zbuluar lëvizje
        if random.random() < 0.2:
            self.motion_detected = True
        else:
            # Lëvizja mbetet për 2-3 sekonda
            if random.random() < 0.3:
                self.motion_detected = False
                
        return {
            'motion_detected': self.motion_detected
        }
