import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class Rule:
    
    def __init__(self, rule_id: str, name: str, condition_func, action_func, 
                 priority: int = 0):
        self.rule_id = rule_id
        self.name = name
        self.condition_func = condition_func
        self.action_func = action_func
        self.priority = priority
        self.last_triggered: Optional[datetime] = None
        
    def evaluate(self, state: Dict[str, Any]) -> bool:
        try:
            return self.condition_func(state)
        except Exception as e:
            logging.error(f"Error evaluating rule {self.name}: {e}")
            return False
            
    def execute(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            self.last_triggered = datetime.now()
            return self.action_func(state)
        except Exception as e:
            logging.error(f"Error executing rule {self.name}: {e}")
            return []


class RuleEngine:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules: List[Rule] = []
        self.logger = logging.getLogger(__name__)
        self._initialize_rules()
        
    def _initialize_rules(self):
        rules_config = self.config.get('rules', {})
        def temp_low_condition(state):
            temp = state.get('temperature', {}).get('value')
            heater = state.get('heater', {}).get('state', False)
            return temp is not None and temp < rules_config.get('temperature_threshold_low', 18.0) and not heater
            
        def temp_low_action(state):
            return [{'actuator': 'heater', 'action': 'turn_on'}]
            
        self.add_rule('temp_low', 'Temperature Low - Turn On Heater',
                     temp_low_condition, temp_low_action, priority=1)
        
        def temp_high_condition(state):
            temp = state.get('temperature', {}).get('value')
            heater = state.get('heater', {}).get('state', False)
            return temp is not None and temp > rules_config.get('temperature_threshold_high', 22.0) and heater
            
        def temp_high_action(state):
            return [{'actuator': 'heater', 'action': 'turn_off'}]
            
        self.add_rule('temp_high', 'Temperature High - Turn Off Heater',
                     temp_high_condition, temp_high_action, priority=1)
        
        def motion_light_condition(state):
            motion = state.get('motion', {}).get('value', False)
            light_level = state.get('light', {}).get('value')
            lights = state.get('light_actuator', {}).get('state', False)
            return (motion and 
                   light_level is not None and 
                   light_level < rules_config.get('light_threshold_low', 30.0) and
                   not lights)
        
        def motion_light_action(state):
            return [{'actuator': 'light', 'action': 'turn_on'}]
            
        self.add_rule('motion_light', 'Motion + Low Light - Turn On Lights',
                     motion_light_condition, motion_light_action, priority=2)
        
        def no_motion_light_condition(state):
            motion = state.get('motion', {}).get('value', False)
            lights = state.get('light_actuator', {}).get('state', False)
            return not motion and lights
        
        def no_motion_light_action(state):
            return [{'actuator': 'light', 'action': 'turn_off'}]
            
        self.add_rule('no_motion_light', 'No Motion - Turn Off Lights',
                     no_motion_light_condition, no_motion_light_action, priority=3)
        
        def security_alarm_condition(state):
            motion = state.get('motion', {}).get('value', False)
            home_occupied = rules_config.get('home_occupied', True)
            alarm = state.get('alarm', {}).get('state', False)
            return motion and not home_occupied and not alarm
        
        def security_alarm_action(state):
            return [{'actuator': 'alarm', 'action': 'activate'}]
            
        self.add_rule('security_alarm', 'Security Alert - Motion When Home Empty',
                     security_alarm_condition, security_alarm_action, priority=0)
        
    def add_rule(self, rule_id: str, name: str, condition_func, action_func,
                 priority: int = 0):
        """Add a new rule to the engine."""
        rule = Rule(rule_id, name, condition_func, action_func, priority)
        self.rules.append(rule)
        # Sort by priority (lower number = higher priority)
        self.rules.sort(key=lambda r: r.priority)
        
    def evaluate_rules(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all rules and return list of commands."""
        commands = []
        triggered_rules = []
        
        for rule in self.rules:
            if rule.evaluate(state):
                rule_commands = rule.execute(state)
                commands.extend(rule_commands)
                triggered_rules.append(rule.name)
                self.logger.info(f"Rule triggered: {rule.name}")
                
        if triggered_rules:
            self.logger.debug(f"Triggered rules: {', '.join(triggered_rules)}")
            
        return commands


