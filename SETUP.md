# Quick Setup Guide

## Prerequisites

1. **Get a Groq API Key**
   - Visit [https://console.groq.com](https://console.groq.com)
   - Sign up for a free account
   - Navigate to API Keys section
   - Create a new API key
   - Copy the key (starts with `gsk_`)

## Setup Steps

### 1. Configure Environment Variables

Edit the `.env` file in `e:\AI-Honey-Pot\.env`:

```bash
# Replace with your actual Groq API key
GROQ_API_KEY=gsk_your_actual_key_here

# Choose your own API key for the honeypot (any string)
API_KEY=my-secret-honeypot-key-123

# GUVI endpoint (already configured)
GUVI_ENDPOINT=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

### 2. Verify Installation

Check that all dependencies are installed:

```bash
python -m pip list | findstr "langgraph groq fastapi"
```

You should see:
- langgraph (0.2.0)
- groq (0.4.2)
- fastapi (0.109.0)

### 3. Start the Server

```bash
cd e:\AI-Honey-Pot
python main.py
```

You should see:
```
🚀 Starting Honeypot Scam Detection API...
   Groq API configured: True
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test the Health Endpoint

Open a new terminal and run:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "active_sessions": 0,
  "groq_configured": true
}
```

### 5. Run Test Scenarios

```bash
python tests/test_scenarios.py
```

This will simulate scam conversations and verify the system works.

### 6. Test with a Custom Message

```bash
curl -X POST http://localhost:8000/api/honeypot ^
  -H "x-api-key: my-secret-honeypot-key-123" ^
  -H "Content-Type: application/json" ^
  -d "{\"sessionId\": \"test-1\", \"message\": {\"sender\": \"scammer\", \"text\": \"Your bank account will be blocked. Verify immediately.\", \"timestamp\": 1234567890000}, \"conversationHistory\": [], \"metadata\": {\"channel\": \"SMS\"}}"
```

## Troubleshooting

### Issue: "Groq API configured: False"

**Solution:** Check that your `.env` file has the correct `GROQ_API_KEY`

### Issue: "Invalid API key" error

**Solution:** Make sure you're using the correct `x-api-key` header value from your `.env` file

### Issue: "Module not found" errors

**Solution:** Reinstall dependencies:
```bash
python -m pip install -r requirements.txt
```

### Issue: Port 8000 already in use

**Solution:** Change the port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use 8001 instead
```

## Docker Deployment (Optional)

### Build the image:
```bash
docker build -t honeypot-api .
```

### Run the container:
```bash
docker run -p 8000:8000 --env-file .env honeypot-api
```

## Next Steps

1. ✅ Configure your Groq API key
2. ✅ Start the server
3. ✅ Run the test scenarios
4. ✅ Test with real scam messages
5. ✅ Monitor the extracted intelligence
6. ✅ Review session details via `/sessions/{session_id}` endpoint

## API Usage Example

### Send a scam message:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/honeypot",
    headers={
        "x-api-key": "my-secret-honeypot-key-123",
        "Content-Type": "application/json"
    },
    json={
        "sessionId": "session-123",
        "message": {
            "sender": "scammer",
            "text": "Urgent! Your account will be suspended. Call 9876543210 now!",
            "timestamp": 1234567890000
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English"
        }
    }
)

print(response.json())
# Output: {"status": "success", "reply": "Oh no! What happened? Why is my account being suspended?"}
```

### Get session intelligence:

```python
session_response = requests.get(
    "http://localhost:8000/sessions/session-123",
    headers={"x-api-key": "my-secret-honeypot-key-123"}
)

print(session_response.json()["extractedIntelligence"])
# Output: {"phoneNumbers": ["+919876543210"], "upiIds": [], ...}
```

## Support

For issues or questions:
1. Check the [README.md](README.md) for detailed documentation
2. Review the [walkthrough.md](walkthrough.md) for implementation details
3. Check the logs in the terminal for error messages
