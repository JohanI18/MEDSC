#!/usr/bin/env python3
"""
Test de conectividad a Supabase
"""

import requests
import socket
import os
from dotenv import load_dotenv

load_dotenv()

def test_connectivity():
    supabase_url = os.environ.get('SUPABASE_URL', "https://vdhbgtgbxszzheftvaga.supabase.co")
    supabase_key = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkaGJndGdieHN6emhlZnR2YWdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDQ0NDUsImV4cCI6MjA2OTk4MDQ0NX0.LdGqI_8JONJAex3Qbn407ueNE8hRzApGkQy5JY7x3eg")
    
    print(f"🌐 Testing connectivity to: {supabase_url}")
    print(f"🔑 Using API key: {supabase_key[:20]}...")
    
    # 1. Test DNS resolution
    try:
        hostname = supabase_url.replace('https://', '').replace('http://', '')
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip}")
    except Exception as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    
    # 2. Test HTTP connection
    try:
        response = requests.get(f"{supabase_url}/rest/v1/", timeout=10)
        print(f"✅ HTTP connection successful: Status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP connection failed: {e}")
        return False
    
    # 3. Test Auth endpoint
    try:
        headers = {
            'apikey': supabase_key,
            'Content-Type': 'application/json'
        }
        
        # Simple test to auth endpoint
        response = requests.get(f"{supabase_url}/auth/v1/settings", headers=headers, timeout=10)
        print(f"✅ Auth endpoint accessible: Status {response.status_code}")
        
        if response.status_code == 200:
            print("✅ All connectivity tests passed!")
            return True
        else:
            print(f"⚠️ Auth endpoint returned: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Auth endpoint test failed: {e}")
        return False

def test_recovery_email():
    """Test sending recovery email directly"""
    supabase_url = os.environ.get('SUPABASE_URL', "https://vdhbgtgbxszzheftvaga.supabase.co")
    supabase_key = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZkaGJndGdieHN6emhlZnR2YWdhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDQ0NDUsImV4cCI6MjA2OTk4MDQ0NX0.LdGqI_8JONJAex3Qbn407ueNE8hRzApGkQy5JY7x3eg")
    
    print("\n📧 Testing password recovery email...")
    
    headers = {
        'apikey': supabase_key,
        'Content-Type': 'application/json'
    }
    
    data = {
        'email': 'johan.illicachi@epn.edu.ec',
        'options': {
            'redirect_to': 'http://localhost:3000/auth/callback'
        }
    }
    
    try:
        response = requests.post(
            f'{supabase_url}/auth/v1/recover',
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📧 Recovery email response: {response.status_code}")
        print(f"📧 Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Recovery email sent successfully!")
            return True
        else:
            print(f"❌ Recovery email failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Recovery email error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SUPABASE CONNECTIVITY TEST")
    print("=" * 40)
    
    if test_connectivity():
        test_recovery_email()
    else:
        print("\n❌ Basic connectivity failed, skipping recovery email test")
        
    print("\n" + "=" * 40)
    print("Test completed!")
