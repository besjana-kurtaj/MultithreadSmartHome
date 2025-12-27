Multithreaded Smart Home Hub
Overview

The Multithreaded Smart Home Hub is a simple Python project that simulates a smart home system.
It demonstrates how multiple sensors and devices can work at the same time using multithreading, while a Flask web interface is used to monitor the system in real time.

The project focuses on concurrency, system state management, and basic automation rules.

Project Goals

Simulate smart home sensors and actuators

Use multithreading to handle multiple sensors concurrently

Apply simple decision rules based on sensor data

Provide a web interface to monitor the system state

Log system events and sensor readings

System Architecture
1. Sensors (Device Layer)

Simulated sensors:

Temperature sensor

Light sensor

Motion sensor

Each sensor runs in its own thread

Sensors generate new values every 1–2 seconds

Sensor data is sent to the hub using thread-safe queues

2. Smart Home Hub

Acts as the central controller of the system

Stores the current state of the home

Processes incoming sensor data

Applies simple rules, for example:

If temperature is low → turn heating ON

If motion is detected and it is dark → turn lights ON

If motion is detected in away mode → activate alarm

3. Monitoring & Web Interface

A logging thread records system events into a log file

Flask provides a simple web page that shows:

Current sensor values

Actuator status (ON/OFF)

Technologies Used

Python 3.x

threading / ThreadPoolExecutor

queue

Flask

logging

time

How to Run

Clone the repository:

git clone https://gitlab.com/your-repository/multithreaded-smart-home-hub.git
cd multithreaded-smart-home-hub


Install dependencies:

pip install flask


Run the application:

python main.py


Open your browser and go to:

http://127.0.0.1:5000
