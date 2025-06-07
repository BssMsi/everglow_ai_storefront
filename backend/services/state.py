from typing import Dict, Any, List, Tuple, Optional

class AgentState:
    """
    Tracks the conversation state, including history, extracted entities, user intent, and active agent.
    """
    def __init__(self, history=None, entities=None, intent=None, active_agent=None, followup_questions=None):
        self.history: List[Tuple[str, str]] = history or []  # List of (user, agent) tuples
        self.entities: Dict[str, Any] = entities or {}  # e.g., {"categories": ["serum"]}
        self.intent: Optional[str] = intent  # e.g., "search", "recommend", "review_explanation", "brand_info"
        self.active_agent: Optional[str] = active_agent  # e.g., "conversational_search"
        self.followup_questions: List[str] = followup_questions or []

    def to_dict(self):
        return {
            "history": self.history,
            "entities": self.entities,
            "intent": self.intent,
            "active_agent": self.active_agent,
            "followup_questions": self.followup_questions,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            history=d.get("history", []),
            entities=d.get("entities", {}),
            intent=d.get("intent"),
            active_agent=d.get("active_agent"),
            followup_questions=d.get("followup_questions", []),
        )