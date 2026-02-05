"""
LangGraph workflow construction
"""
from langgraph.graph import StateGraph, END
from graph.state import HoneypotState
from graph.nodes import (
    scam_detection_node,
    language_detection_node,
    persona_selection_node,
    response_generation_node,
    intelligence_extraction_node,
    continuation_decision_node,
    send_final_payload_node
)


def route_after_detection(state: HoneypotState) -> str:
    """Route based on scam detection"""
    if state["scamDetected"]:
        # Always go to language detection first
        return "language_detection"
    else:
        # Not a scam - send neutral response and end
        state["agentReply"] = "Thank you for your message. I'll look into this."
        return "end"


def route_after_language_detection(state: HoneypotState) -> str:
    """Route after language detection"""
    # Check if persona already selected (for subsequent messages)
    if state.get("agentPersona", "") == "":
        return "persona_selection"
    else:
        # Skip persona selection, go straight to response
        return "response_generation"


def route_after_decision(state: HoneypotState) -> str:
    """Route based on continuation decision"""
    if state["shouldContinue"]:
        return "end"  # Wait for next message
    else:
        return "send_final_payload"  # Terminate and report


def create_honeypot_graph():
    """
    Create the LangGraph workflow
    
    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(HoneypotState)
    
    # Add nodes
    workflow.add_node("scam_detection", scam_detection_node)
    workflow.add_node("language_detection", language_detection_node)
    workflow.add_node("persona_selection", persona_selection_node)
    workflow.add_node("response_generation", response_generation_node)
    workflow.add_node("intelligence_extraction", intelligence_extraction_node)
    workflow.add_node("continuation_decision", continuation_decision_node)
    workflow.add_node("send_final_payload", send_final_payload_node)
    
    # Set entry point
    workflow.set_entry_point("scam_detection")
    
    # Add edges
    workflow.add_conditional_edges(
        "scam_detection",
        route_after_detection,
        {
            "language_detection": "language_detection",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "language_detection",
        route_after_language_detection,
        {
            "persona_selection": "persona_selection",
            "response_generation": "response_generation"
        }
    )
    
    workflow.add_edge("persona_selection", "response_generation")
    workflow.add_edge("response_generation", "intelligence_extraction")
    workflow.add_edge("intelligence_extraction", "continuation_decision")
    
    workflow.add_conditional_edges(
        "continuation_decision",
        route_after_decision,
        {
            "end": END,
            "send_final_payload": "send_final_payload"
        }
    )
    
    workflow.add_edge("send_final_payload", END)
    
    return workflow.compile()
