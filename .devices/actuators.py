"""
Actuator implementations for the Smart Home system.
"""
from typing import Dict, Any
from .base import Actuator


class LightActuator(Actuator):
    """Light actuator that can turn lights on/off."""
    
    def __init__(self, device_id: str, name: str, enabled: bool = True,
                 initial_state: bool = False, command_queue=None):
        super().__init__(device_id, name, enabled, command_queue)
        self._state = initial_state
        
    def _on_state_change(self, old_state: bool, new_state: bool):
        """Handle light state change."""
        status = "ON" if new_state else "OFF"
        self.logger.info(f"💡 {self.name} turned {status}")
        
    def _execute_command(self, command: Dict[str, Any]):
        """Execute light command."""
        if 'action' in command:
            if command['action'] == 'turn_on':
                self.set_state(True)
            elif command['action'] == 'turn_off':
                self.set_state(False)
            elif command['action'] == 'toggle':
                current = self.get_state()
                self.set_state(not current)
        elif 'state' in command:
            self.set_state(bool(command['state']))
            
    def is_on(self) -> bool:
        """Check if light is on."""
        return self.get_state()


class HeaterActuator(Actuator):
    """Heater actuator that can turn heating on/off."""
    
    def __init__(self, device_id: str, name: str, enabled: bool = True,
                 initial_state: bool = False, target_temperature: float = 20.0,
                 command_queue=None):
        super().__init__(device_id, name, enabled, command_queue)
        self._state = initial_state
        self.target_temperature = target_temperature
        
    def _on_state_change(self, old_state: bool, new_state: bool):
        """Handle heater state change."""
        status = "ON" if new_state else "OFF"
        self.logger.info(f"🔥 {self.name} turned {status} (target: {self.target_temperature}°C)")
        
    def _execute_command(self, command: Dict[str, Any]):
        """Execute heater command."""
        if 'action' in command:
            if command['action'] == 'turn_on':
                self.set_state(True)
            elif command['action'] == 'turn_off':
                self.set_state(False)
            elif command['action'] == 'toggle':
                current = self.get_state()
                self.set_state(not current)
        elif 'state' in command:
            self.set_state(bool(command['state']))
            
        if 'target_temperature' in command:
            self.target_temperature = float(command['target_temperature'])
            
    def is_on(self) -> bool:
        """Check if heater is on."""
        return self.get_state()


class AlarmActuator(Actuator):
    """Alarm actuator for security system."""
    
    def __init__(self, device_id: str, name: str, enabled: bool = True,
                 initial_state: bool = False, command_queue=None):
        super().__init__(device_id, name, enabled, command_queue)
        self._state = initial_state
        
    def _on_state_change(self, old_state: bool, new_state: bool):
        """Handle alarm state change."""
        if new_state:
            self.logger.warning(f"🚨 {self.name} ACTIVATED!")
        else:
            self.logger.info(f"🔕 {self.name} deactivated")
            
    def _execute_command(self, command: Dict[str, Any]):
        """Execute alarm command."""
        if 'action' in command:
            if command['action'] == 'activate':
                self.set_state(True)
            elif command['action'] == 'deactivate':
                self.set_state(False)
            elif command['action'] == 'toggle':
                current = self.get_state()
                self.set_state(not current)
        elif 'state' in command:
            self.set_state(bool(command['state']))
            
    def is_active(self) -> bool:
        """Check if alarm is active."""
        return self.get_state()


