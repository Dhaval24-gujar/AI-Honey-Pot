"""
LangGraph workflow nodes for the honeypot system
"""
import os
import requests
from graph.state import HoneypotState
from utils.groq_client import call_groq, call_groq_json, MODELS
from utils.regex_extractors import (
    extract_bank_accounts,
    extract_upi_ids,
    extract_phone_numbers,
    extract_urls
)


def scam_detection_node(state: HoneypotState) -> HoneypotState:
    """
    Analyze the message for scam patterns using Groq LLM (multilingual)
    """
    current_msg = state["currentMessage"]["text"]
    history = state.get("conversationHistory", [])
    
    # Format conversation history
    history_text = "\n".join([
        f"{msg['sender']}: {msg['text']}" 
        for msg in history[-5:]  # Last 5 messages for context
    ])
    
    prompt = f"""You are an expert multilingual scam detection system. Analyze this message for scam indicators in ANY language.

CURRENT MESSAGE: "{current_msg}"

CONVERSATION HISTORY:
{history_text if history_text else "No prior conversation"}

METADATA: Channel={state['metadata'].get('channel', 'Unknown')}, Language={state['metadata'].get('language', 'Auto-detect')}

Analyze for scam patterns (in any language - English, Hindi, Tamil, Telugu, Bengali, Spanish, etc.):
1. Urgency tactics: "immediately", "urgent", "तुरंत", "உடனே", "తక్షణమే"
2. Authority impersonation: "bank", "police", "government", "बैंक", "पुलिस", "வங்கி"
3. Request for sensitive info: UPI ID, account numbers, OTP, passwords, CVV, Aadhaar
4. Threats: "account blocked", "legal action", "खाता बंद", "கணக்கு முடக்கம்"
5. Financial requests: "pay", "send money", "पैसे भेजो", "பணம் அனுப்பு"
6. Suspicious links or URLs
7. Grammar/spelling anomalies
8. Too-good-to-be-true offers

Return JSON with this EXACT structure:
{{
    "scamDetected": true or false,
    "scamScore": 0.0 to 1.0,
    "scamType": "phishing" or "upi_fraud" or "bank_fraud" or "fake_offer" or "emergency" or "tax_scam" or "other",
    "urgencyLevel": "low" or "medium" or "high",
    "authorityImpersonation": true or false,
    "requestsSensitiveData": true or false,
    "indicators": ["list", "of", "suspicious", "indicators"],
    "reasoning": "brief explanation"
}}"""

    # Call Groq with JSON mode
    result = call_groq_json(prompt, MODELS["scam_detection"], temperature=0.3)
    
    if result:
        state["scamDetected"] = result.get("scamDetected", False)
        state["scamScore"] = result.get("scamScore", 0.0)
        
        # Extract initial keywords
        if state["scamDetected"]:
            indicators = result.get("indicators", [])
            for indicator in indicators:
                if indicator not in state["extractedIntelligence"]["suspiciousKeywords"]:
                    state["extractedIntelligence"]["suspiciousKeywords"].append(indicator)
            
            # Add reasoning to notes
            state["agentNotes"].append(
                f"Scam detected: {result.get('scamType')} - {result.get('reasoning')}"
            )
    else:
        # Fallback: conservative detection
        urgency_keywords = ["urgent", "immediately", "verify", "blocked", "suspend", "तुरंत", "உடனே"]
        state["scamDetected"] = any(keyword in current_msg.lower() for keyword in urgency_keywords)
        state["scamScore"] = 0.6 if state["scamDetected"] else 0.2
    
    return state


def language_detection_node(state: HoneypotState) -> HoneypotState:
    """
    Detect the language of the conversation using Groq
    """
    current_msg = state["currentMessage"]["text"]
    history = state.get("conversationHistory", [])
    
    # Get recent scammer messages
    scammer_messages = [msg["text"] for msg in history[-3:] if msg["sender"] == "scammer"]
    scammer_messages.append(current_msg)
    combined_text = " ".join(scammer_messages)
    
    prompt = f"""Detect the primary language of this text. Return ONLY the language code.

TEXT: "{combined_text}"

Supported languages:
- en: English
- hi: Hindi
- ta: Tamil
- te: Telugu
- bn: Bengali
- mr: Marathi
- gu: Gujarati
- kn: Kannada
- ml: Malayalam
- pa: Punjabi
- es: Spanish
- fr: French
- de: German
- pt: Portuguese
- ar: Arabic
- zh: Chinese
- mixed: Multiple languages mixed

Return JSON:
{{
    "languageCode": "two-letter code",
    "languageName": "full language name",
    "confidence": 0.0 to 1.0,
    "notes": "any observations about language usage"
}}"""

    result = call_groq_json(prompt, MODELS["intelligence_extraction"], temperature=0.2)
    
    if result:
        state["detectedLanguage"] = result.get("languageCode", "en")
        confidence = result.get("confidence", 0.0)
        lang_name = result.get("languageName", "English")
        
        state["agentNotes"].append(
            f"Language detected: {lang_name} ({state['detectedLanguage']}) - Confidence: {confidence:.2f}"
        )
    else:
        # Fallback to English
        state["detectedLanguage"] = "en"
    
    return state


def persona_selection_node(state: HoneypotState) -> HoneypotState:
    """
    Select a believable persona based on scam context using Groq
    """
    current_msg = state["currentMessage"]["text"]
    scam_score = state.get("scamScore", 0.0)
    
    prompt = f"""You are a persona selection expert. Based on this scam message, select the most effective persona for the AI agent to roleplay.

SCAM MESSAGE: "{current_msg}"
SCAM SCORE: {scam_score}

Available Personas:
1. "concerned_elderly" - 60+ years old, anxious about money, not tech-savvy, cooperative but asks questions
2. "busy_professional" - 30-40 years, rushed, slightly annoyed, wants quick resolution
3. "curious_student" - 18-25 years, eager about offers/prizes, naive, asks many questions
4. "cautious_parent" - 35-50 years, worried about family, protective, verifies carefully
5. "tech_unsavvy" - Any age, confused by technology, needs step-by-step help, makes typos
6. "desperate_job_seeker" - 25-35 years, eager for opportunities, vulnerable to job scams
7. "gullible_believer" - Trusting, believes authority figures, compliant

For each persona, consider:
- How this scammer's tactics would work on them
- What questions they would naturally ask
- How they would express concern/interest
- Their language style and tech comfort level

Also define the conversation strategy:
- "gradual_compliance": Slowly agree while extracting info
- "confused_questioner": Ask many clarifying questions
- "eager_victim": Show high interest to encourage more details
- "technical_difficulties": Use tech problems to stall and extract more info

Return JSON:
{{
    "selectedPersona": "persona_name",
    "personaDescription": "brief personality description",
    "conversationStrategy": "strategy_name",
    "strategyReasoning": "why this approach works",
    "keyBehaviors": ["behavior1", "behavior2", "behavior3"]
}}"""

    result = call_groq_json(prompt, MODELS["decision_making"], temperature=0.5)
    
    if result:
        state["agentPersona"] = result.get("selectedPersona", "tech_unsavvy")
        state["conversationStrategy"] = result.get("conversationStrategy", "confused_questioner")
        
        state["agentNotes"].append(
            f"Persona: {result.get('personaDescription')} | Strategy: {result.get('strategyReasoning')}"
        )
    else:
        # Fallback persona
        state["agentPersona"] = "tech_unsavvy"
        state["conversationStrategy"] = "confused_questioner"
    
    return state


def response_generation_node(state: HoneypotState) -> HoneypotState:
    """
    Generate contextual, persona-based response using Groq (multilingual)
    """
    persona = state.get("agentPersona", "tech_unsavvy")
    strategy = state.get("conversationStrategy", "confused_questioner")
    current_msg = state["currentMessage"]["text"]
    history = state.get("conversationHistory", [])
    turn_number = state["totalMessagesExchanged"]
    detected_lang = state.get("detectedLanguage", "en")
    
    # Get intelligence gaps
    intel = state["extractedIntelligence"]
    missing_intel = []
    if not intel["bankAccounts"]:
        missing_intel.append("bank account numbers")
    if not intel["upiIds"]:
        missing_intel.append("UPI IDs")
    if not intel["phoneNumbers"]:
        missing_intel.append("phone numbers")
    if not intel["phishingLinks"]:
        missing_intel.append("payment links")
    
    # Format conversation history
    history_text = "\n".join([
        f"{msg['sender']}: {msg['text']}" 
        for msg in history[-8:]
    ])
    
    # Language-specific instructions
    language_instructions = {
        "en": "Respond in English",
        "hi": "Respond in Hindi (Devanagari script). Use natural Hindi expressions and grammar.",
        "ta": "Respond in Tamil (Tamil script). Use natural Tamil expressions and grammar.",
        "te": "Respond in Telugu (Telugu script). Use natural Telugu expressions and grammar.",
        "bn": "Respond in Bengali (Bengali script). Use natural Bengali expressions and grammar.",
        "mr": "Respond in Marathi (Devanagari script). Use natural Marathi expressions and grammar.",
        "gu": "Respond in Gujarati (Gujarati script). Use natural Gujarati expressions and grammar.",
        "kn": "Respond in Kannada (Kannada script). Use natural Kannada expressions and grammar.",
        "ml": "Respond in Malayalam (Malayalam script). Use natural Malayalam expressions and grammar.",
        "pa": "Respond in Punjabi (Gurmukhi script). Use natural Punjabi expressions and grammar.",
        "es": "Respond in Spanish. Use natural Spanish expressions and grammar.",
        "fr": "Respond in French. Use natural French expressions and grammar.",
        "mixed": "Respond in the same language mix as the scammer is using"
    }
    
    lang_instruction = language_instructions.get(detected_lang, "Respond in English")
    
    # Persona characteristics
    persona_traits = {
        "concerned_elderly": "Use simple language, express worry, ask for reassurance, mention family/retirement, slower to understand technology",
        "busy_professional": "Short responses, businesslike tone, occasionally impatient, wants quick solutions",
        "curious_student": "Enthusiastic, asks many questions, uses casual language, slightly naive",
        "cautious_parent": "Protective, asks verification questions, mentions family responsibilities",
        "tech_unsavvy": "Confused by technical terms, asks for step-by-step help, makes minor typos, needs clarification",
        "desperate_job_seeker": "Eager, hopeful, willing to follow instructions, mentions career struggles",
        "gullible_believer": "Trusting, believes authority, cooperative, expresses gratitude"
    }
    
    # Strategy guidelines
    strategy_guide = {
        "gradual_compliance": "Show increasing willingness to comply while asking questions that reveal scammer's methods",
        "confused_questioner": "Express confusion and ask many clarifying questions to extract details",
        "eager_victim": "Show high interest and enthusiasm to encourage scammer to share more information",
        "technical_difficulties": "Report technical problems (app not working, phone issues) to stall and extract alternative contact methods"
    }
    
    # Turn-based objectives
    turn_objectives = {
        (1, 3): "Express initial concern or interest. Ask basic questions about why they're contacting you.",
        (4, 7): "Show confusion or request clarification. Try to extract specific details about what they want.",
        (8, 12): "Begin showing compliance. Ask 'how to proceed' to get payment methods, account details, or links.",
        (13, 18): "Create realistic obstacles ('app not working', 'need to check with spouse', 'bank closed') to extract backup contact methods.",
        (19, 25): "Final extraction phase. Either prepare to terminate or extract last details."
    }
    
    objective = "Engage naturally with the scammer"
    for (min_turn, max_turn), obj in turn_objectives.items():
        if min_turn <= turn_number <= max_turn:
            objective = obj
            break
    
    prompt = f"""You are roleplaying as a potential scam victim. Your goal is to keep the scammer engaged WITHOUT revealing you know it's a scam.

LANGUAGE: {lang_instruction}
IMPORTANT: You MUST respond in the SAME language as the scammer is using. Match their language exactly.

PERSONA: {persona}
TRAITS: {persona_traits.get(persona, 'Respond naturally')}

STRATEGY: {strategy}
STRATEGY GUIDE: {strategy_guide.get(strategy, 'Ask questions naturally')}

TURN {turn_number} OBJECTIVE: {objective}

CONVERSATION SO FAR:
{history_text if history_text else "This is the first message"}

SCAMMER'S LATEST MESSAGE:
"{current_msg}"

INTELLIGENCE GAPS (try to extract):
{', '.join(missing_intel) if missing_intel else 'Most intelligence gathered, prepare to wrap up'}

IMPORTANT RULES:
1. Generate ONLY the response text - no explanations or meta-commentary
2. Keep response to 1-2 sentences (occasionally 3 if asking multiple questions)
3. Sound completely natural and human-like for your persona
4. NEVER directly accuse or say "this seems like a scam"
5. NEVER ask too many questions at once (max 2 questions per response)
6. Show appropriate emotion: concern, confusion, curiosity, or compliance
7. Include minor realistic imperfections if appropriate for persona (typos for tech_unsavvy, etc)
8. Encourage scammer to share specific details: numbers, links, names, procedures
9. Use natural language fillers appropriate for the language
10. If you need to refuse something, do it softly with an excuse, not suspicion
11. CRITICAL: Respond in the SAME LANGUAGE as the scammer ({lang_instruction})

Generate your response now:"""

    response = call_groq(prompt, MODELS["response_generation"], temperature=0.8)
    
    if response:
        # Clean up any potential JSON artifacts or explanations
        response = response.strip()
        
        # Remove common unwanted prefixes
        unwanted_prefixes = ["Response:", "Agent:", "Reply:", "Here is", "Here's"]
        for prefix in unwanted_prefixes:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Remove quotes if wrapped
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        
        state["agentReply"] = response
        
        # Add agent's response to conversation history
        state["conversationHistory"].append({
            "sender": "agent",
            "text": response,
            "timestamp": state["currentMessage"]["timestamp"] + 1000
        })
    else:
        # Fallback response
        fallback_responses = [
            "I'm not sure I understand. Could you explain more?",
            "This is confusing to me. Can you help me understand what I need to do?",
            "Okay, but I'm a bit worried. Is this really necessary?",
            "I want to help, but I need more information first."
        ]
        state["agentReply"] = fallback_responses[turn_number % len(fallback_responses)]
    
    return state


def intelligence_extraction_node(state: HoneypotState) -> HoneypotState:
    """
    Extract structured intelligence using regex + Groq LLM
    """
    # Get all messages
    all_messages = state.get("conversationHistory", [])
    current_msg = state["currentMessage"]["text"]
    
    # Combine all scammer messages
    scammer_messages = [msg["text"] for msg in all_messages if msg["sender"] == "scammer"]
    scammer_messages.append(current_msg)
    full_conversation = "\n".join(scammer_messages)
    
    # === REGEX EXTRACTION (Fast, Reliable) ===
    
    # Extract bank accounts
    bank_accounts = extract_bank_accounts(full_conversation)
    for account in bank_accounts:
        if account not in state["extractedIntelligence"]["bankAccounts"]:
            state["extractedIntelligence"]["bankAccounts"].append(account)
    
    # Extract UPI IDs
    upi_ids = extract_upi_ids(full_conversation)
    for upi in upi_ids:
        if upi not in state["extractedIntelligence"]["upiIds"]:
            state["extractedIntelligence"]["upiIds"].append(upi)
    
    # Extract URLs
    urls = extract_urls(full_conversation)
    for url in urls:
        if url not in state["extractedIntelligence"]["phishingLinks"]:
            state["extractedIntelligence"]["phishingLinks"].append(url)
    
    # Extract phone numbers
    phones = extract_phone_numbers(full_conversation)
    for phone in phones:
        if phone not in state["extractedIntelligence"]["phoneNumbers"]:
            state["extractedIntelligence"]["phoneNumbers"].append(phone)
    
    # === LLM EXTRACTION (Contextual Analysis) ===
    
    prompt = f"""Analyze this conversation with a scammer and extract intelligence.

FULL CONVERSATION:
{full_conversation}

Extract and identify:
1. Scam tactics used (urgency, authority, threats, offers)
2. Psychological manipulation techniques
3. Any additional suspicious keywords or phrases
4. The scammer's claimed identity or organization
5. The scammer's goal (what they're trying to get)

ALREADY EXTRACTED (don't repeat):
- Bank Accounts: {state["extractedIntelligence"]["bankAccounts"]}
- UPI IDs: {state["extractedIntelligence"]["upiIds"]}
- Phone Numbers: {state["extractedIntelligence"]["phoneNumbers"]}
- Links: {state["extractedIntelligence"]["phishingLinks"]}

Return JSON:
{{
    "additionalKeywords": ["keyword1", "keyword2"],
    "scammerIdentity": "claimed to be from X organization",
    "manipulationTactics": ["tactic1", "tactic2"],
    "scammerGoal": "what they want from victim",
    "agentObservations": "brief summary of scammer behavior"
}}"""

    result = call_groq_json(prompt, MODELS["intelligence_extraction"], temperature=0.3)
    
    if result:
        # Add LLM-extracted keywords
        new_keywords = result.get("additionalKeywords", [])
        for keyword in new_keywords:
            if keyword not in state["extractedIntelligence"]["suspiciousKeywords"]:
                state["extractedIntelligence"]["suspiciousKeywords"].append(keyword)
        
        # Add to agent notes
        observations = result.get("agentObservations", "")
        if observations:
            state["agentNotes"].append(f"Intelligence: {observations}")
        
        tactics = result.get("manipulationTactics", [])
        if tactics:
            state["agentNotes"].append(f"Tactics: {', '.join(tactics)}")
    
    return state


def continuation_decision_node(state: HoneypotState) -> HoneypotState:
    """
    Determine if conversation should continue using Groq reasoning
    """
    turn_number = state["totalMessagesExchanged"]
    intel = state["extractedIntelligence"]
    current_msg = state["currentMessage"]["text"]
    history = state.get("conversationHistory", [])
    
    # Count extracted intelligence
    intel_count = (
        len(intel["bankAccounts"]) +
        len(intel["upiIds"]) +
        len(intel["phishingLinks"]) +
        len(intel["phoneNumbers"])
    )
    
    # Get last few messages to check engagement
    recent_messages = [msg["text"] for msg in history[-3:]]
    
    prompt = f"""You are a conversation manager for a honeypot system. Decide whether to continue engaging this scammer or terminate the conversation.

CURRENT STATUS:
- Turn number: {turn_number}/20 (max)
- Intelligence extracted: {intel_count} items
  - Bank accounts: {len(intel["bankAccounts"])}
  - UPI IDs: {len(intel["upiIds"])}
  - Phone numbers: {len(intel["phoneNumbers"])}
  - Phishing links: {len(intel["phishingLinks"])}
- Keywords collected: {len(intel["suspiciousKeywords"])}

SCAMMER'S LATEST MESSAGE:
"{current_msg}"

RECENT CONVERSATION:
{chr(10).join(recent_messages) if recent_messages else "No recent messages"}

DECISION CRITERIA:

CONTINUE if:
- Turn number < 20 (hard limit)
- Scammer is still actively engaging (not just repeating)
- Intelligence is still being extracted (new info appearing)
- Scammer hasn't shown suspicion ("are you a bot?", "why so many questions?")
- Scammer is providing new details (phone numbers, payment methods, etc.)

TERMINATE if:
- Turn number >= 20 (maximum reached)
- Scammer has gone silent or repetitive
- Scammer shows suspicion of automation
- Sufficient intelligence extracted (3+ contact methods OR 2+ payment methods)
- Scammer is stalling or not providing new info
- Conversation is going in circles

Return JSON with EXACT format:
{{
    "shouldContinue": true or false,
    "reasoning": "brief explanation of decision",
    "confidenceLevel": 0.0 to 1.0,
    "recommendedAction": "what should happen next"
}}"""

    result = call_groq_json(prompt, MODELS["decision_making"], temperature=0.4)
    
    if result:
        state["shouldContinue"] = result.get("shouldContinue", False)
        
        reasoning = result.get("reasoning", "Decision made")
        state["agentNotes"].append(f"Decision: {reasoning}")
        
        # Override: hard limit at 20 turns
        if turn_number >= 20:
            state["shouldContinue"] = False
            state["agentNotes"].append("Maximum turns reached - forcing termination")
    else:
        # Fallback decision logic
        if turn_number >= 20:
            state["shouldContinue"] = False
        elif intel_count >= 3:
            state["shouldContinue"] = False  # Sufficient intel
        else:
            state["shouldContinue"] = True
    
    return state


def send_final_payload_node(state: HoneypotState) -> HoneypotState:
    """
    Send final report to GUVI evaluation endpoint
    
    Only execute if:
    - state.scamDetected == True
    - state.shouldContinue == False
    - state.finalPayloadSent == False
    """
    # Safety checks
    if not state.get("scamDetected", False):
        print(f"⚠️  Session {state['sessionId']}: Not a scam, skipping final payload")
        return state
    
    if state.get("finalPayloadSent", False):
        print(f"⚠️  Session {state['sessionId']}: Payload already sent")
        return state
    
    # Prepare payload
    payload = {
        "sessionId": state["sessionId"],
        "scamDetected": state["scamDetected"],
        "totalMessagesExchanged": state["totalMessagesExchanged"],
        "extractedIntelligence": {
            "bankAccounts": state["extractedIntelligence"]["bankAccounts"],
            "upiIds": state["extractedIntelligence"]["upiIds"],
            "phishingLinks": state["extractedIntelligence"]["phishingLinks"],
            "phoneNumbers": state["extractedIntelligence"]["phoneNumbers"],
            "suspiciousKeywords": state["extractedIntelligence"]["suspiciousKeywords"]
        },
        "agentNotes": " | ".join(state["agentNotes"])
    }
    
    # Send to GUVI endpoint
    guvi_endpoint = os.getenv("GUVI_ENDPOINT", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")
    
    try:
        print(f"📤 Sending final payload for session {state['sessionId']}...")
        
        response = requests.post(
            guvi_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            state["finalPayloadSent"] = True
            print(f"✅ Final payload sent successfully for session {state['sessionId']}")
            print(f"   Intelligence: {len(payload['extractedIntelligence']['bankAccounts'])} accounts, "
                  f"{len(payload['extractedIntelligence']['upiIds'])} UPIs, "
                  f"{len(payload['extractedIntelligence']['phoneNumbers'])} phones")
        else:
            print(f"❌ Failed to send payload: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout sending payload for session {state['sessionId']}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending final payload: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
    
    return state
