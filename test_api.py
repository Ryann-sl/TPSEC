import requests
import json

base_url = 'http://localhost:5000/api'

def test_caesar(direction):
    payload = {
        'plaintext': 'ABC',
        'shift': 3,
        'direction': direction
    }
    response = requests.post(f"{base_url}/encrypt/caesar", json=payload)
    print(f"Direction {direction}: Status {response.status_code}, Response: {response.json()}")

try:
    print("Testing Caesar API...")
    r_right = requests.post(f"{base_url}/encrypt/caesar", json={'plaintext': 'ABC', 'shift': 3, 'direction': 'right'})
    print(f"Right: {r_right.json().get('encrypted')} (Expect DEF)")
    
    r_left = requests.post(f"{base_url}/encrypt/caesar", json={'plaintext': 'ABC', 'shift': 3, 'direction': 'left'})
    print(f"Left: {r_left.json().get('encrypted')} (Expect XYZ)")
except Exception as e:
    print(f"Error: {e}")
