import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import os
import requests
import base64
import uuid

# API base URL
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000/api/v1")
AUTH_HEADERS = {}


def test_authentication():
    """Register a temporary user and obtain a JWT for protected endpoints."""
    print("Testing authentication...")
    username = f"smoke_{uuid.uuid4().hex[:8]}"
    user = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "StrongPass123",
    }
    try:
        register = requests.post(f"{BASE_URL}/auth/register", json=user, timeout=30)
        print(f"Register status: {register.status_code}")
        if register.status_code != 201:
            return False

        login = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": user["password"]},
            timeout=30,
        )
        print(f"Login status: {login.status_code}")
        if login.status_code != 200:
            return False

        token = login.json().get("access_token")
        if not token:
            return False
        AUTH_HEADERS.update({"Authorization": f"Bearer {token}"})
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_server_status():
    """Test server status endpoint"""
    print("\nTesting server status...")
    try:
        response = requests.get(f"{BASE_URL}/health/status")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_detection_with_mock_image():
    """Test detection endpoint with mock image data"""
    print("\nTesting detection endpoint...")
    try:
        # Create a small mock image (1x1 pixel red image)
        import numpy as np
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_image[:, :] = [255, 0, 0]  # Red image
        
        # Convert to base64
        import cv2
        _, buffer = cv2.imencode('.jpg', mock_image)
        frame_data = base64.b64encode(buffer).decode('utf-8')
        
        payload = {
            "frame_data": frame_data,
            "threshold": 0.6,
            "source": "test-camera"
        }
        
        response = requests.post(
            f"{BASE_URL}/detection/detect",
            json=payload,
            headers={**AUTH_HEADERS, "Content-Type": "application/json"},
            timeout=60,
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_detections():
    """Test getting detections history"""
    print("\nTesting get detections...")
    try:
        response = requests.get(
            f"{BASE_URL}/detection/detections",
            headers=AUTH_HEADERS,
            timeout=30,
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_statistics():
    """Test statistics endpoint"""
    print("\nTesting statistics...")
    try:
        response = requests.get(
            f"{BASE_URL}/statistics/statistics",
            headers=AUTH_HEADERS,
            timeout=30,
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 50)
    print("Behavior Monitor API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Authentication", test_authentication),
        ("Health Check", test_health_check),
        ("Server Status", test_server_status),
        ("Detection", test_detection_with_mock_image),
        ("Get Detections", test_get_detections),
        ("Statistics", test_statistics),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"Running: {test_name}")
        print('=' * 50)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

if __name__ == "__main__":
    main()
