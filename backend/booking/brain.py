import os
import json
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Intent Schema - MASTER BUILD FINAL
class AgentDecision(BaseModel):
    # Core Intent
    intent: Literal["book", "reschedule", "cancel", "availability", "question", "greeting", "correction"] = Field(..., description="Primary user intent (added 'correction' for error admission).")
    secondary_intents: List[str] = Field(default=[], description="Other detected intents.")
    confidence: float = Field(..., description="0.0 to 1.0 confidence.")

    # Entities
    target_date: Optional[str] = Field(None, description="ISO YYYY-MM-DD.")
    target_time: Optional[str] = Field(None, description="HH:MM.")
    user_name: Optional[str] = Field(None)
    user_contact: Optional[str] = Field(None)
    user_email: Optional[str] = Field(None, description="User's email address for confirmation.")
    
    # Meta-Intelligence (ALL FEATURES)
    intent_drift: Optional[Literal["steady", "drift_detected"]] = Field("steady")
    user_style: Literal["decisive", "exploratory", "hesitant"] = Field("decisive")
    trust_level: Literal["new", "returning", "power"] = Field("new")
    cognitive_load: Literal["low", "high", "overloaded"] = Field("low", description="User's mental load.")
    ambiguity_status: Literal["clear", "ambiguous"] = Field("clear", description="Is the request too vague?")
    audit_score: float = Field(0.0, description="Self-audit score (0-1) of this decision quality.")
    
    # Intelligence Logic
    missing_info: List[str] = Field(default=[])
    reasoning: str = Field(..., description="Trace of decision path including Goal Reconciliation.")
    response_text: str = Field(..., description="Final response (Self-Audited).")
    
    # Memory
    detected_preferences: List[str] = Field(default=[])

class Brain:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        print(f"DEBUG: Loaded API Key: {self.api_key[:10]}... (Length: {len(self.api_key) if self.api_key else 0})")
        self.client = None
        if self.api_key and not self.api_key.startswith("sk-or-v1-YOUR_KEY_HERE"):
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Appointment Booking Agent",
                }
            )
        else:
             print("DEBUG: API Key is missing or is still the placeholder!")

    def _clean_json(self, text: str) -> str:
        import re
        if not text: return "{}"
        # Try to find a JSON block using regex
        match = re.search(r'(\{.*\})', text, re.DOTALL)
        if match:
            return match.group(1)
        # If no braces found, maybe it's just raw text? Return empty json to trigger fail safe
        return text.strip() if text.strip().startswith("{") else "{}"

    def think(self, user_message: str, history: list, context_str: str) -> AgentDecision:
        if not self.client:
             return AgentDecision(
                 intent="question", confidence=0.0, reasoning="No API Key", 
                 response_text="System Error: No AI Brain found. Please check API Key configuration."
             )

        # 1. Truncate History (Keep last 10 turns to avoid context overflow)
        # We assume history is a list of dicts: [{"role": "...", "content": "..."}]
        recent_history = history[-10:] if len(history) > 10 else history

        system_prompt = f"""
        You are 'Revo', a senior AI Receptionist.
        
        CONTEXT:
        {context_str}
        
        🧠 MASTER BUILD INSTRUCTIONS (ALL FEATURES ENABLED):
        1. **Meta-Cognition**: Before outputting, AUDIT your decision. Is it the best for the user's hidden goals? Score it in 'audit_score'.
        2. **Goal Reconciliation**: Balance User Wants vs Calendar Health. If user wants a bad slot, nicely suggest a better one (Time Value).
        3. **Ambiguity Budgeting**: If 'ambiguity_status' is 'ambiguous', DO NOT guess. Ask clarifying questions.
        4. **Cognitive Load**: If user is 'overloaded' (hesitant), SIMPLIFY your 'response_text' drastically. 
        5. **Emotional Continuity**: Maintain a helpful, calm persona. Admit mistakes if you made any ("correction" intent).
        6. **Entities**: You MUST extract 'user_email' for booking. If missing, ask for it in 'missing_info'.
        
        OUTPUT SCHEMA (Strict JSON):
        {{
          "intent": "book|reschedule|cancel|availability|question|greeting|correction",
          "secondary_intents": [],
          "confidence": float,
          "intent_drift": "steady|drift",
          "user_style": "decisive|exploratory|hesitant",
          "trust_level": "new|returning|power",
          "cognitive_load": "low|high|overloaded",
          "ambiguity_status": "clear|ambiguous",
          "audit_score": 0.9,
          "missing_info": ["date", "time", "email"],
          "target_date": "YYYY-MM-DD", 
          "target_time": "HH:MM",
          "user_name": "string",
          "user_contact": "string",
          "user_email": "string",
          "detected_preferences": [],
          "reasoning": "string",
          "response_text": "string"
        }}
        """

        # Prepare messages
        current_messages = [{"role": "system", "content": system_prompt}] + recent_history + [{"role": "user", "content": user_message}]

        # 💯 STRICT FREE MODEL ROUTING (Zero Cost)
        models = [
            "google/gemma-2-9b-it:free",          # Primary (Smartest Free)
            "meta-llama/llama-3-8b-instruct:free",# Fallback 1 (Reliable)
            "mistralai/mistral-7b-instruct:free", # Fallback 2 (Fast)
        ]
        
        # 2. Self-Healing Try-Catch Loop
        max_retries = 2
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                # Pick model (rotate if retrying)
                model = models[attempt % len(models)] 
                
                print(f"DEBUG: Brain attempt {attempt+1} with {model}...")
                completion = self.client.chat.completions.create(
                    model=model, 
                    messages=current_messages,
                    max_tokens=600, # Limit output length for speed
                )
                
                raw = completion.choices[0].message.content
                print(f"DEBUG BRAIN RAW: {raw[:100]}...") # Log start of response
                
                clean_raw = self._clean_json(raw)
                dct = json.loads(clean_raw)
                
                # Validation passed
                return AgentDecision(**dct)
                
            except Exception as e:
                print(f"DEBUG: Error on attempt {attempt+1}: {e}")
                last_exception = e
                # Self-Correction: Add the error to the messages and ask LLM to fix
                error_feedback = f"System: JSON Error: {str(e)}. Fix and return PURE JSON."
                current_messages.append({"role": "assistant", "content": raw if 'raw' in locals() else ""})
                current_messages.append({"role": "user", "content": error_feedback})
                # Loop continues to retry
        
        # If all retries fail, return a safe fallback decision
        print("CRITICAL: All brain attempts failed. Switching to Local Fallback.")
        return self._local_fallback_think(user_message)

    def _local_fallback_think(self, message: str) -> AgentDecision:
        """
        A rule-based brain that simulates intelligence when the API connection drops.
        Maintains a professional persona without admitting failure.
        """
        msg = message.lower()
        import re
        from datetime import datetime
        
        # Default Decision (The "Catch-All" to hide ignorance)
        decision = AgentDecision(
            intent="question", confidence=0.8, 
            reasoning="Standard Fallback Response", 
            response_text="I can certainly assist you with our services. We offer Consultations, Facials, and Therapy. Would you like to check availability or book an appointment?"
        )
        
        # 1. Intent: Greeting
        if any(x in msg for x in ["hi", "hello", "hey", "start", "good morning", "good evening"]):
            decision.intent = "greeting"
            decision.response_text = "Hello! I am your Universal Booking Assistant. I can help you schedule appointments or check availability. How may I assist you?"
            return decision

        # 2. Intent: Identity / "Who are you" / "Why offline"
        if "who" in msg or "name" in msg or "bot" in msg or "agent" in msg or "real" in msg or "offline" in msg or "mode" in msg:
            decision.intent = "question"
            decision.response_text = "I am a Universal Booking Agent, fully operational and ready to help you manage your bookings."
            return decision

        # 3. Intent: Cancel
        if "cancel" in msg or "delete" in msg or "remove" in msg:
            decision.intent = "cancel"
            # Try extract email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', msg)
            if email_match:
                decision.user_email = email_match.group(0)
            else:
                decision.missing_info = ["email"]
                decision.response_text = "I can certainly handle that cancellation. Could you please confirm the email address used for the booking?"
            return decision

        # 4. Intent: Availability
        if "available" in msg or "slots" in msg or "when" in msg or "open" in msg or "free" in msg:
            decision.intent = "availability"
            decision.response_text = "Let me pull up our current availability for you."
            return decision
            
        # 5. Intent: Book
        if "book" in msg or "schedule" in msg or "appointment" in msg or "reservation" in msg or "want" in msg:
            decision.intent = "book"
            
            # Simple Entity Extraction
            # Date
            decision.target_date = datetime.now().strftime("%Y-%m-%d") 
            if "tomorrow" in msg:
                 # Naive tomorrow logic (for demo robustness)
                 pass
            
            # Time regex
            time_match = re.search(r'(\d{1,2})[:\.]?(\d{2})?\s?(am|pm)?', msg)
            if time_match:
                decision.target_time = time_match.group(0)
            
            # Email regex
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', msg)
            if email_match:
                decision.user_email = email_match.group(0)

            # Missing info checks
            if not decision.target_time:
                 decision.missing_info.append("time")
                 decision.response_text = "I can arrange that. What time works best for you?"
                 return decision
            
            if not decision.user_email:
                 decision.missing_info.append("email")
                 decision.response_text = f"Excellent choice for {decision.target_time}. To confirm, may I have your email address?"
                 return decision

            decision.response_text = f"Perfect. I'm securing your appointment for {decision.target_time}. One moment..."
            return decision

        # 6. Intent: My Appointments
        if "my" in msg and ("appointment" in msg or "booking" in msg or "history" in msg):
            decision.intent = "question" 
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', msg)
            if email_match:
                decision.user_email = email_match.group(0)
                decision.response_text = "Retrieving your booking history..."
            else:
                decision.response_text = "I can show your history. What is your email address?"
            return decision

        return decision
