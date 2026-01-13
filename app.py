"""
Flask aplikacion për UI web të Smart Home Hub
"""
from flask import Flask, render_template, jsonify, request
from smart_hub import SmartHub
import threading

app = Flask(__name__)
hub = SmartHub()

# Nis hub-in në thread të veçantë
hub_thread = None

def start_hub():
    """Nis Smart Hub në thread të veçantë"""
    hub.start()
    # Mbaj thread-in aktiv
    while True:
        threading.Event().wait(1)

@app.route('/')
def index():
    """Faqja kryesore"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """API endpoint për gjendjen aktuale"""
    return jsonify(hub.get_status())

@app.route('/api/away_mode', methods=['POST'])
def set_away_mode():
    """API endpoint për vendosjen e away mode"""
    data = request.json
    enabled = data.get('enabled', False)
    hub.set_away_mode(enabled)
    return jsonify({'success': True, 'away_mode': enabled})

@app.route('/api/light', methods=['POST'])
def control_light():
    """API endpoint për kontrollin manual të dritave"""
    data = request.json
    action = data.get('action')
    
    if action == 'on':
        brightness = data.get('brightness', 80)
        hub.light_actuator.set_brightness(brightness)
    elif action == 'off':
        hub.light_actuator.turn_off()
        
    return jsonify({'success': True})

@app.route('/api/heating', methods=['POST'])
def control_heating():
    """API endpoint për kontrollin manual të ngrohjes"""
    data = request.json
    action = data.get('action')
    
    if action == 'on':
        hub.heating_actuator.turn_on()
    elif action == 'off':
        hub.heating_actuator.turn_off()
    elif action == 'set_temp':
        temp = data.get('temperature', 22.0)
        hub.heating_actuator.set_target_temperature(temp)
        
    return jsonify({'success': True})

if __name__ == '__main__':
    # Nis hub-in në thread të veçantë
    hub_thread = threading.Thread(target=start_hub, daemon=True)
    hub_thread.start()
    
    # Nis Flask serverin
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
