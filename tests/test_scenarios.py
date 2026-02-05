"""
Test scenarios for the honeypot system
"""
import requests
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "http://localhost:8000/api/honeypot"
API_KEY = os.getenv("API_KEY", "your_honeypot_api_key")


def test_bank_fraud_scam():
    """
    Test bank fraud scam detection and conversation flow
    """
    print("\n" + "="*60)
    print("TEST: Bank Fraud Scam")
    print("="*60)
    
    session_id = f"test-bank-fraud-{int(time.time())}"
    
    scammer_messages = [
        "Your bank account will be suspended. Verify immediately.",
        "Click this link to verify: http://fake-bank-verify.com",
        "Enter your account number and UPI PIN to unlock",
        "Call this number now: 9876543210",
        "Pay Rs. 2000 to verify@paytm to unlock account"
    ]
    
    conversation_history = []
    
    for i, msg in enumerate(scammer_messages):
        print(f"\n{'─'*60}")
        print(f"Turn {i+1}: Scammer: {msg}")
        
        try:
            response = requests.post(
                API_URL,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "sessionId": session_id,
                    "message": {
                        "sender": "scammer",
                        "text": msg,
                        "timestamp": int(time.time() * 1000)
                    },
                    "conversationHistory": conversation_history,
                    "metadata": {
                        "channel": "SMS",
                        "language": "English",
                        "locale": "IN"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Agent: {data['reply']}")
                
                # Add to conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": int(time.time() * 1000)
                })
                conversation_history.append({
                    "sender": "user",
                    "text": data['reply'],
                    "timestamp": int(time.time() * 1000) + 1
                })
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                break
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            break
        
        time.sleep(2)  # Realistic delay
    
    print(f"\n{'='*60}")
    print("✅ Bank fraud test complete!")
    print(f"Session ID: {session_id}")
    
    # Get session details
    try:
        session_response = requests.get(
            f"http://localhost:8000/sessions/{session_id}",
            headers={"x-api-key": API_KEY}
        )
        if session_response.status_code == 200:
            session_data = session_response.json()
            print(f"\nExtracted Intelligence:")
            print(f"  - UPI IDs: {session_data['extractedIntelligence']['upiIds']}")
            print(f"  - Phone Numbers: {session_data['extractedIntelligence']['phoneNumbers']}")
            print(f"  - Phishing Links: {session_data['extractedIntelligence']['phishingLinks']}")
            print(f"  - Scam Score: {session_data['scamScore']}")
    except Exception as e:
        print(f"⚠️  Could not fetch session details: {e}")


def test_upi_fraud_scam():
    """
    Test UPI fraud scam detection
    """
    print("\n" + "="*60)
    print("TEST: UPI Fraud Scam")
    print("="*60)
    
    session_id = f"test-upi-fraud-{int(time.time())}"
    
    scammer_messages = [
        "Congratulations! You won Rs. 50,000. Send Rs. 500 processing fee to claim.",
        "Send money to winner2024@paytm immediately to claim your prize",
        "Hurry! Offer expires in 2 hours. Pay now!"
    ]
    
    conversation_history = []
    
    for i, msg in enumerate(scammer_messages):
        print(f"\n{'─'*60}")
        print(f"Turn {i+1}: Scammer: {msg}")
        
        try:
            response = requests.post(
                API_URL,
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "sessionId": session_id,
                    "message": {
                        "sender": "scammer",
                        "text": msg,
                        "timestamp": int(time.time() * 1000)
                    },
                    "conversationHistory": conversation_history,
                    "metadata": {
                        "channel": "WhatsApp",
                        "language": "English"
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Agent: {data['reply']}")
                
                conversation_history.append({
                    "sender": "scammer",
                    "text": msg,
                    "timestamp": int(time.time() * 1000)
                })
                conversation_history.append({
                    "sender": "user",
                    "text": data['reply'],
                    "timestamp": int(time.time() * 1000) + 1
                })
            else:
                print(f"❌ Error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            break
        
        time.sleep(2)
    
    print(f"\n{'='*60}")
    print("✅ UPI fraud test complete!")


def test_health_check():
    """
    Test health check endpoint
    """
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed:")
            print(f"   Status: {data['status']}")
            print(f"   Active sessions: {data['active_sessions']}")
            print(f"   Groq configured: {data['groq_configured']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")


if __name__ == "__main__":
    print("\n🧪 Starting Honeypot System Tests")
    print("Make sure the server is running on http://localhost:8000\n")
    
    # Run tests
    test_health_check()
    time.sleep(2)
    
    test_bank_fraud_scam()
    time.sleep(3)
    
    test_upi_fraud_scam()
    
    print("\n" + "="*60)
    print("🎉 All tests complete!")
    print("="*60)
