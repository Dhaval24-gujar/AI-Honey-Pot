# LangGraph Agentic Honeypot System

A sophisticated honeypot system using LangGraph for workflow orchestration and Groq for ultra-fast AI inference. The system detects scam messages, engages scammers with realistic AI-generated responses, extracts intelligence, and reports findings.

## Features

- 🤖 **LangGraph Workflow**: Orchestrated multi-node agent workflow
- ⚡ **Groq Integration**: Ultra-fast LLM inference (10-100x faster)
- 🎭 **Dynamic Personas**: 7 different victim personas for realistic engagement
- 🧠 **Intelligence Extraction**: Extracts bank accounts, UPI IDs, phone numbers, phishing links
- 📊 **Scam Detection**: Advanced pattern recognition with confidence scoring
- 🔄 **Adaptive Conversations**: Turn-based strategies that evolve with the conversation

## Architecture

```
Incoming Message → Scam Detection → Persona Selection → Response Generation
                                                              ↓
                    Final Payload ← Continuation Decision ← Intelligence Extraction
```

## Installation

### Prerequisites

- Python 3.11+
- Groq API key ([Get one here](https://console.groq.com))

### Setup

1. **Clone and navigate to the project:**
   ```bash
   cd e:\AI-Honey-Pot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   
   Edit `.env` file:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   API_KEY=your_honeypot_api_key
   GUVI_ENDPOINT=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
   ```

## Usage

### Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### 1. Process Message
```bash
POST /api/honeypot
Headers: x-api-key: your_honeypot_api_key
Content-Type: application/json

{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify immediately.",
    "timestamp": 1234567890000
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English"
  }
}
```

#### 2. Health Check
```bash
GET /health
```

#### 3. Get Session Details
```bash
GET /sessions/{session_id}
Headers: x-api-key: your_honeypot_api_key
```

## Testing

Run the test scenarios:

```bash
python tests/test_scenarios.py
```

This will test:
- Bank fraud scam detection
- UPI fraud scam detection
- Intelligence extraction
- Health check endpoint

## Project Structure

```
e:/AI-Honey-Pot/
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── main.py                # FastAPI server
├── Dockerfile             # Docker configuration
├── graph/
│   ├── __init__.py
│   ├── state.py           # State definitions
│   ├── nodes.py           # LangGraph nodes
│   └── workflow.py        # Graph construction
├── utils/
│   ├── __init__.py
│   ├── groq_client.py     # Groq helper functions
│   └── regex_extractors.py # Intelligence extraction
└── tests/
    └── test_scenarios.py  # Test scripts
```

## How It Works

### 1. Scam Detection
Analyzes incoming messages for scam patterns:
- Urgency tactics
- Authority impersonation
- Requests for sensitive data
- Threats and financial requests

### 2. Persona Selection
Chooses appropriate victim persona:
- `concerned_elderly`: Anxious, not tech-savvy
- `busy_professional`: Rushed, wants quick resolution
- `tech_unsavvy`: Confused by technology
- `curious_student`: Eager, naive
- And more...

### 3. Response Generation
Generates human-like responses using:
- Persona-specific traits
- Conversation strategies
- Turn-based objectives
- Natural language imperfections

### 4. Intelligence Extraction
Extracts structured data:
- Bank account numbers (masked)
- UPI IDs
- Phone numbers
- Phishing links
- Suspicious keywords

### 5. Continuation Decision
Decides whether to continue based on:
- Turn count (max 20)
- Intelligence gathered
- Scammer engagement
- Suspicion detection

### 6. Final Payload
Sends report to evaluation endpoint when conversation terminates.

## Groq Models Used

| Task | Model | Rationale |
|------|-------|-----------|
| Scam Detection | `llama-3.3-70b-versatile` | High-quality reasoning |
| Response Generation | `llama-3.3-70b-versatile` | Natural conversation |
| Intelligence Extraction | `llama-3.1-8b-instant` | Fast extraction |
| Decision Making | `mixtral-8x7b-32768` | Large context |

## Docker Deployment

```bash
# Build
docker build -t honeypot-api .

# Run
docker run -p 8000:8000 --env-file .env honeypot-api
```

## Example Conversation

```
Scammer: "Your bank account will be blocked today. Verify immediately."
Agent: "Oh no! Why is my account being blocked? I didnt do anything wrong.. what should i do?"

Scammer: "Share your account number to verify."
Agent: "Im really worried now. What kind of suspicious activity?? I dont understand these things.."

Scammer: "Send Rs 5000 to verify123@paytm"
Agent: "Okay i want to do this but im not very good with UPI.. can you send me that ID again?"

[Intelligence Extracted: UPI ID, urgency tactics, authority impersonation]
[Final payload sent to evaluation endpoint]
```

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
