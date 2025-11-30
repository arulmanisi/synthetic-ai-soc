import sys
import os
import json
import requests
import time

# Add project root to path to import simulator
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulator.sim_generator import generate_event

def train_model(n_events=200):
    print(f"Generating {n_events} events...")
    events = []
    for _ in range(n_events):
        events.append(generate_event())
    
    print(f"Sending {len(events)} events to training endpoint...")
    try:
        response = requests.post("http://localhost:8001/train", json=events)
        if response.status_code == 200:
            print("Training successful!")
            print(response.json())
        else:
            print(f"Training failed: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to anomaly-service at http://localhost:8001")
        print("Make sure the service is running.")

if __name__ == "__main__":
    train_model()
