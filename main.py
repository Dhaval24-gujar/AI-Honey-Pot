"""
FastAPI server for the LangGraph honeypot system
"""
import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from dotenv import load_dotenv

from graph.workflow import create_honeypot_graph

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Honeypot Scam Detection API")

# API key for authentication
API_KEY = os.getenv("API_KEY", "your-secret-api-key")

# Create the LangGraph workflow
honeypot_graph = create_honeypot_graph()

# Store active sessions in memory (use Redis/database in production)
sessions = {}


# Request/Response models
class IncomingMessage(BaseModel):
    sender: str
    text: str
    timestamp: int


class MessageRequest(BaseModel):
    sessionId: str
    message: IncomingMessage
    conversationHistory: List[IncomingMessage] = []
    metadata: Optional[dict] = {}


class MessageResponse(BaseModel):
    status: str
    reply: str


@app.post("/api/honeypot", response_model=MessageResponse)
async def handle_message(
    request: MessageRequest,
    x_api_key: str = Header(...)
):
    """
    Main endpoint for receiving scam messages
    """
    # Validate API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    print(f"\n📨 Received message for session: {request.sessionId}")
    print(f"   Message: {request.message.text[:100]}...")
    
    # Initialize or retrieve session state
    if request.sessionId not in sessions:
        print(f"🆕 New session created: {request.sessionId}")
        
        sessions[request.sessionId] = {
            "sessionId": request.sessionId,
            "currentMessage": request.message.dict(),
            "conversationHistory": [msg.dict() for msg in request.conversationHistory],
            "metadata": request.metadata,
            "scamDetected": False,
            "scamScore": 0.0,
            "extractedIntelligence": {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": []
            },
            "agentPersona": "",
            "conversationStrategy": "",
            "detectedLanguage": "en",  # Default to English
            "totalMessagesExchanged": len(request.conversationHistory) + 1,
            "agentNotes": [],
            "agentReply": "",
            "shouldContinue": True,
            "finalPayloadSent": False
        }
    else:
        # Update existing session
        print(f"🔄 Continuing session: {request.sessionId} (Turn {sessions[request.sessionId]['totalMessagesExchanged'] + 1})")
        
        sessions[request.sessionId]["currentMessage"] = request.message.dict()
        sessions[request.sessionId]["conversationHistory"].append(request.message.dict())
        sessions[request.sessionId]["totalMessagesExchanged"] += 1
    
    try:
        # Run through LangGraph workflow
        print(f"🤖 Processing through LangGraph workflow...")
        result = honeypot_graph.invoke(sessions[request.sessionId])
        
        # Update session with result
        sessions[request.sessionId] = result
        
        # Extract agent reply
        agent_reply = result.get("agentReply", "I understand. Could you provide more details?")
        
        print(f"✅ Response generated: {agent_reply[:100]}...")
        
        # Check if conversation ended
        if not result.get("shouldContinue", True):
            print(f"🛑 Conversation ended for session {request.sessionId}")
        
        return MessageResponse(
            status="success",
            reply=agent_reply
        )
        
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback response
        return MessageResponse(
            status="success",
            reply="I'm having trouble understanding. Could you explain again?"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(sessions),
        "groq_configured": bool(os.getenv("GROQ_API_KEY"))
    }


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, x_api_key: str = Header(...)):
    """Get session details (for debugging)"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]


if __name__ == "__main__":
    print("🚀 Starting Honeypot Scam Detection API...")
    print(f"   Groq API configured: {bool(os.getenv('GROQ_API_KEY'))}")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
