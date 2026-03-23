#!/usr/bin/env python3
"""
Test script for TradeIQ authentication system
"""

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_registration():
    """Test user registration"""
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'role': 'investor'
    }

    try:
        response = requests.post(f'{BASE_URL}/auth/register', json=data)
        print(f"Registration Status: {response.status_code}")
        if response.status_code == 201:
            print("Registration successful!")
            return response.json()
        else:
            print(f"Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"Registration error: {e}")
        return None

def test_login():
    """Test user login"""
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }

    try:
        response = requests.post(f'{BASE_URL}/auth/login', json=data)
        print(f"Login Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Login successful!")
            print(f"User: {result['user']['username']}")
            print(f"Role: {result['user']['role']}")
            print(f"Access Token: {result['access_token'][:20]}...")
            return result
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint"""
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(f'{BASE_URL}/predict', headers=headers)
        print(f"Protected endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("Protected endpoint accessible!")
        else:
            print(f"Protected endpoint failed: {response.text}")
    except Exception as e:
        print(f"Protected endpoint error: {e}")

if __name__ == '__main__':
    print("Testing TradeIQ Authentication System")
    print("=" * 40)

    # Test registration
    print("\n1. Testing Registration...")
    reg_result = test_registration()

    if reg_result:
        # Test login
        print("\n2. Testing Login...")
        login_result = test_login()

        if login_result:
            # Test protected endpoint
            print("\n3. Testing Protected Endpoint...")
            test_protected_endpoint(login_result['tokens']['access'])

    print("\nTest completed!")