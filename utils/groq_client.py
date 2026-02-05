"""
Groq API client utilities for ultra-fast LLM inference
"""
import json
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model configurations for different tasks
MODELS = {
    "scam_detection": "llama-3.3-70b-versatile",      # Best for reasoning
    "response_generation": "llama-3.3-70b-versatile",  # Natural language
    "intelligence_extraction": "llama-3.1-8b-instant", # Fast extraction
    "decision_making": "mixtral-8x7b-32768"           # Large context
}


def call_groq(prompt: str, model: str, temperature: float = 0.7, json_mode: bool = False) -> str:
    """
    Call Groq API with error handling
    
    Args:
        prompt: The prompt to send to the model
        model: Model name from MODELS dict
        temperature: Sampling temperature (0.0-1.0)
        json_mode: Whether to request JSON response format
        
    Returns:
        Model response as string, or None if error
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        
        response = groq_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=2048,
            response_format={"type": "json_object"} if json_mode else {"type": "text"}
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Groq API error: {str(e)}")
        return None


def call_groq_json(prompt: str, model: str, temperature: float = 0.7) -> dict:
    """
    Call Groq and parse JSON response
    
    Args:
        prompt: The prompt to send to the model
        model: Model name from MODELS dict
        temperature: Sampling temperature (0.0-1.0)
        
    Returns:
        Parsed JSON dict, or None if error
    """
    response = call_groq(prompt, model, temperature, json_mode=True)
    if response:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON response")
            return None
    return None
