"""
State definitions for the LangGraph honeypot system
"""
from typing import TypedDict, List, Annotated
import operator


class Message(TypedDict):
    """Individual message in the conversation"""
    sender: str  # "scammer" or "agent"
    text: str
    timestamp: int


class ExtractedIntelligence(TypedDict):
    """Structured intelligence extracted from scammer"""
    bankAccounts: List[str]
    upiIds: List[str]
    phishingLinks: List[str]
    phoneNumbers: List[str]
    suspiciousKeywords: List[str]


class HoneypotState(TypedDict):
    """Main state for the honeypot agent workflow"""
    sessionId: str
    currentMessage: Message
    conversationHistory: Annotated[List[Message], operator.add]
    metadata: dict
    scamDetected: bool
    scamScore: float  # 0.0 to 1.0
    extractedIntelligence: ExtractedIntelligence
    agentPersona: str
    conversationStrategy: str
    detectedLanguage: str  # Detected language of conversation
    totalMessagesExchanged: int
    agentNotes: Annotated[List[str], operator.add]
    agentReply: str
    shouldContinue: bool
    finalPayloadSent: bool

