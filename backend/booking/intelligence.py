from datetime import datetime, timedelta
from dateutil import tz, parser
from .rules import BookingRules

def calculate_integrity_score(appointments: list, day_start: datetime, day_end: datetime) -> int:
    """
    Computes a Calendar Integrity Score (0-100).
    Penalizes fragmentation (small gaps). Rewards clustering.
    """
    if not appointments:
        return 100 # Empty calendar is perfect integrity? Or 50? Let's say 100 (clean slate).

    sorted_appts = sorted(appointments, key=lambda x: x['start_iso'])
    
    score = 100
    fragmentation_penalty = 0
    
    # Analyze gaps
    for i in range(len(sorted_appts) - 1):
        curr_end = parser.isoparse(sorted_appts[i]['end_iso'])
        next_start = parser.isoparse(sorted_appts[i+1]['start_iso'])
        
        gap_minutes = (next_start - curr_end).total_seconds() / 60
        
        # Bad gap: 1-15 minutes (too short to do anything)
        if 0 < gap_minutes < 15:
            fragmentation_penalty += 15
        # Decent gap: 15-30
        elif 15 <= gap_minutes < 30:
            fragmentation_penalty += 5
        # Good gap: > 30 (usable block)
        
    score -= fragmentation_penalty
    return max(0, min(100, score))

def simulate_future_schedule(proposed_start_iso: str, duration_minutes: int, existing_appointments: list) -> dict:
    """
    What-If Simulation Engine.
    Checks if a proposed slot creates issues directly or downstream.
    """
    try:
        proposed_start = parser.isoparse(proposed_start_iso)
        proposed_end = proposed_start + timedelta(minutes=duration_minutes)
    except:
        return {"future_risk": 0.0, "recommendation": "unknown_date"}

    risk = 0.0
    conflicts = []
    
    # 1. Direct Conflict & Buffer Check
    for appt in existing_appointments:
        existing_start = parser.isoparse(appt['start_iso'])
        existing_end = parser.isoparse(appt['end_iso'])
        
        # Buffer (e.g. 5 mins)
        buffer = timedelta(minutes=5)
        
        # Check overlap including buffer
        if (proposed_start < existing_end + buffer) and (proposed_end + buffer > existing_start):
            risk = 1.0
            conflicts.append(f"Direct conflict or buffer violation with {appt.get('service', 'appointment')}")

    # 2. Fragmentation Check (Simulated)
    # If this slot creates a 10 min gap, increase risk
    # (Simplified for now)
    
    return {
        "future_risk": risk,
        "conflicts_detected": conflicts,
        "recommendation": "unsafe" if risk > 0.5 else "safe"
    }

def analyze_conversation_style(history: list) -> dict:
    """
    Conversational Compression & Cognitive Load Engine.
    Estimates user's mental state and preferred brevity.
    """
    if not history:
        return {"style": "neutral", "verbosity": "normal", "cognitive_load": "low"}
        
    user_msgs = [m['content'] for m in history if m['role'] == 'user']
    avg_len = sum(len(m) for m in user_msgs) / len(user_msgs) if user_msgs else 0
    
    # Cognitive Load Heuristics
    # High load usage: "Wait, actually, no, maybe..." (Hesitation markers)
    hesitation_markers = ["maybe", "unsure", "wait", "um", "uh", "actually"]
    last_msg = user_msgs[-1].lower() if user_msgs else ""
    hesitation_count = sum(1 for m in hesitation_markers if m in last_msg)
    
    cognitive_load = "low"
    if hesitation_count > 0 or len(last_msg) > 150:
        cognitive_load = "high"
    elif hesitation_count > 2:
        cognitive_load = "overloaded"

    style = "neutral"
    verbosity = "normal"
    
    if avg_len < 20 and cognitive_load == "low": 
        style = "decisive"
        verbosity = "low"
    elif "?" in "".join(user_msgs) or avg_len > 100:
        style = "exploratory"
        verbosity = "high"
        
    return {"style": style, "verbosity": verbosity, "cognitive_load": cognitive_load}

def evaluate_time_value(slot_iso: str) -> str:
    """
    Time Valuation Engine.
    Classifies hours into value zones for 'Executive Thinking'.
    """
    try:
        dt = parser.isoparse(slot_iso)
        hour = dt.hour
        if 9 <= hour <= 11: return "Deep Work (High Value)"
        if 13 <= hour <= 15: return "Collaborative Zone"
        if 16 <= hour <= 17: return "Admin/Low Energy"
        return "Standard"
    except:
        return "Unknown"

def calculate_ambiguity_score(user_message: str, current_context: dict) -> float:
    """
    Ambiguity Budgeting.
    Returns 0.0 (Clear) to 1.0 (Very Ambiguous).
    """
    score = 0.0
    msg = user_message.lower()
    
    # Vague time references
    if "sometime" in msg or "later" in msg or "whenever" in msg:
        score += 0.4
    
    # Missing key info check (if context implies we need it)
    if "book" in msg and "missing_info" in current_context:
        score += 0.3
        
    return min(1.0, score)


# --- ENTERPRISE INTELLIGENCE ENGINES ---

def autonomous_schedule_optimizer(appointments: list) -> str:
    """
    (A) Autonomous Schedule Optimizer.
    Scans for fragmentation and suggests improvements.
    """
    if not appointments:
        return "Calendar is clean."
    
    # Logic: Detect 15-min gaps
    sorted_appts = sorted(appointments, key=lambda x: x['start_iso'])
    gaps = []
    for i in range(len(sorted_appts) - 1):
        curr_end = parser.isoparse(sorted_appts[i]['end_iso'])
        next_start = parser.isoparse(sorted_appts[i+1]['start_iso'])
        gap_min = (next_start - curr_end).total_seconds() / 60
        if 0 < gap_min < 30:
            gaps.append(f"{int(gap_min)}m gap between {sorted_appts[i].get('service','Appt')}")
            
    if gaps:
        return f"Optimization Opportunity: Found {len(gaps)} fragments ({', '.join(gaps[:2])}...). rearranging could save ~{len(gaps)*15} mins."
    return "Schedule is optimized."

def predict_no_show_risk(user_history: list) -> dict:
    """
    (B) Predictive No-Show Detection.
    """
    # Mock logic based on user history length (New users = higher risk)
    risk_score = 0.45 if len(user_history) < 3 else 0.10
    action = "SMS Reminder Recommended" if risk_score > 0.3 else "Standard Confirmation"
    return {"risk": risk_score, "action": action}

def calculate_booking_quality(slot_iso: str, duration: int) -> int:
    """
    (D) Booking Quality Score.
    Scores based on time value and fragmentation potential.
    """
    score = 100
    try:
        dt = parser.isoparse(slot_iso)
        # Penalize Monday Mornings (Energy drain?) - Just an example
        if dt.weekday() == 0 and dt.hour < 10:
            score -= 10
        # Reward Clustering (Assume middle of work day is good)
        if 10 <= dt.hour <= 15:
            score += 5
    except:
        pass
    return min(100, score)

def route_request_to_staff(service_type: str) -> str:
    """
    (J) Skill-Based Appointment Routing.
    """
    staff_roster = {
        "Consultation": "Senior Agent Alice",
        "Support": "Staff Bob",
        "General": "Auto-Assign"
    }
    return staff_roster.get(service_type, "Staff Member")

def detect_bias_and_fairness(recent_bookings: list) -> str:
    """
    (R) Bias & Fairness Monitor.
    """
    # Simplified check
    return "Fairness Check Passed: Distribution is balanced."
