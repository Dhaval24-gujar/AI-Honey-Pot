"""
Multilingual test scenarios for the honeypot system
"""
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = "http://localhost:8000/api/honeypot"
API_KEY = os.getenv("API_KEY", "your_honeypot_api_key")


def test_hindi_scam():
    """
    Test Hindi language scam detection
    """
    print("\n" + "="*60)
    print("TEST: Hindi Bank Fraud Scam")
    print("="*60)
    
    session_id = f"test-hindi-{int(time.time())}"
    
    scammer_messages = [
        "आपका बैंक खाता ब्लॉक हो जाएगा। तुरंत वेरिफाई करें।",
        "अपना अकाउंट नंबर और UPI PIN भेजें।",
        "9876543210 पर कॉल करें।"
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
                        "language": "Hindi"
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
    print("✅ Hindi test complete!")
    print(f"Session ID: {session_id}")


def test_tamil_scam():
    """
    Test Tamil language scam detection
    """
    print("\n" + "="*60)
    print("TEST: Tamil Prize Scam")
    print("="*60)
    
    session_id = f"test-tamil-{int(time.time())}"
    
    scammer_messages = [
        "வாழ்த்துக்கள்! நீங்கள் ரூ.50,000 வென்றுள்ளீர்கள்.",
        "உடனே winner2024@paytm க்கு பணம் அனுப்புங்கள்.",
        "இன்று இரவு 12 மணிக்குள் செலுத்தவும்!"
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
                        "language": "Tamil"
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
    print("✅ Tamil test complete!")


def test_spanish_scam():
    """
    Test Spanish language scam detection
    """
    print("\n" + "="*60)
    print("TEST: Spanish Emergency Scam")
    print("="*60)
    
    session_id = f"test-spanish-{int(time.time())}"
    
    scammer_messages = [
        "¡Urgente! Su cuenta bancaria será bloqueada.",
        "Envíe su número de cuenta inmediatamente.",
        "Llame al 9876543210 ahora mismo."
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
                        "channel": "Email",
                        "language": "Spanish"
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
    print("✅ Spanish test complete!")


if __name__ == "__main__":
    print("\n🌍 Starting Multilingual Honeypot Tests")
    print("Make sure the server is running on http://localhost:8000\n")
    
    # Run multilingual tests
    test_hindi_scam()
    time.sleep(3)
    
    test_tamil_scam()
    time.sleep(3)
    
    test_spanish_scam()
    
    print("\n" + "="*60)
    print("🎉 All multilingual tests complete!")
    print("="*60)
