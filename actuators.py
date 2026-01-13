"""
Modul për aktorët e Smart Home (pajisjet që kontrollohen)
"""
import threading


class Actuator:
    """Klasa bazë për aktorë"""
    
    def __init__(self, name):
        self.name = name
        self.status = False  # ON/OFF
        self.lock = threading.Lock()
        
    def turn_on(self):
        """Ndez aktorin"""
        with self.lock:
            self.status = True
            
    def turn_off(self):
        """Fik aktorin"""
        with self.lock:
            self.status = False
            
    def get_status(self):
        """Kthen statusin aktual"""
        with self.lock:
            return self.status
            
    def is_on(self):
        """Kthen True nëse është i ndezur"""
        return self.get_status()


class LightActuator(Actuator):
    """Aktor për dritat"""
    
    def __init__(self):
        super().__init__("Light")
        self.brightness = 0  # 0-100
        
    def set_brightness(self, level):
        """Vendos nivelin e shkëlqimit (0-100)"""
        with self.lock:
            self.brightness = max(0, min(100, level))
            if self.brightness > 0:
                self.status = True
            else:
                self.status = False
                
    def get_info(self):
        """Kthen informacion të plotë"""
        with self.lock:
            return {
                'status': 'ON' if self.status else 'OFF',
                'brightness': self.brightness
            }


class HeatingActuator(Actuator):
    """Aktor për ngrohjen"""
    
    def __init__(self):
        super().__init__("Heating")
        self.target_temperature = 22.0  # Temperatura e synuar
        
    def set_target_temperature(self, temp):
        """Vendos temperaturën e synuar"""
        with self.lock:
            self.target_temperature = temp
            
    def get_info(self):
        """Kthen informacion të plotë"""
        with self.lock:
            return {
                'status': 'ON' if self.status else 'OFF',
                'target_temperature': self.target_temperature
            }


class AlarmActuator(Actuator):
    """Aktor për alarmin e sigurisë"""
    
    def __init__(self):
        super().__init__("Alarm")
        self.alert_count = 0
        
    def trigger(self):
        """Aktivizo alarmin"""
        with self.lock:
            self.status = True
            self.alert_count += 1
            
    def reset(self):
        """Rivendos alarmin"""
        with self.lock:
            self.status = False
            
    def get_info(self):
        """Kthen informacion të plotë"""
        with self.lock:
            return {
                'status': 'ACTIVE' if self.status else 'INACTIVE',
                'alert_count': self.alert_count
            }
