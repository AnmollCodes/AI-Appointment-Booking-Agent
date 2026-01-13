import uuid
from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse, isoparse

from .rules import get_rules
from .availability import get_open_slots
from .db import insert_appointment, get_appointment, update_appointment_time, cancel_appointment, get_user_preferences, update_user_preferences, get_active_appointments_by_email, get_all_user_appointments
from .brain import Brain, AgentDecision
from .intelligence import (
    calculate_integrity_score, simulate_future_schedule,
    analyze_conversation_style, evaluate_time_value, calculate_ambiguity_score,
    autonomous_schedule_optimizer, predict_no_show_risk, route_request_to_staff, detect_bias_and_fairness, calculate_booking_quality
)
from .email_service import send_confirmation_email

brain = Brain()
sessions = {}

def handle_request(session_id: str, message: str, history: list) -> dict:
    rules = get_rules()
    now_str = datetime.now().isoformat()
    prefs = get_user_preferences(session_id)
    
    # --- PHASE 3 INTELLIGENCE PIPELINE ---
    
    # 1. Cognitive State Analysis
    convo_metrics = analyze_conversation_style(history)
    
    # 2. Calendar Health & Optimization (Autonomous Systems)
    # In prod, we'd query real DB appointments. Here passing empty or mock list for demo safety.
    optimizer_report = autonomous_schedule_optimizer([])
    integrity = calculate_integrity_score([], datetime.now(), datetime.now())
    
    # 3. Risk & Routing
    risk_data = predict_no_show_risk(history)
    staff_assignment = route_request_to_staff("General")
    
    # 4. Time Value & Context Construction
    curr_hour_val = evaluate_time_value(now_str)
    
    # Format services for context
    services_text = "\n".join([f"- {k}: {v['name']} ({v['duration']}m, ${v['price']})" for k,v in rules.services.items()])
    
    context = f"""
    Current Time: {now_str} ({curr_hour_val})
    Business: {rules.business_name}
    Hours: Mon-Fri {rules.day_start}-{rules.day_end}
    
    SERVICES:
    {services_text}
    
    User Preferences: {prefs.get('notes', 'None yet')}
    
    SYSTEM INTELLIGENCE:
    - Optimization: {optimizer_report}
    - Integrity Score: {integrity}/100
    - No-Show Risk: {risk_data['risk']*100}% ({risk_data['action']})
    - Staff Routing: Assigned to {staff_assignment}
    - Fairness Monitor: {detect_bias_and_fairness([])}
    
    USER STATE:
    - Style: {convo_metrics['style']} (Verbosity: {convo_metrics['verbosity']})
    - Load: {convo_metrics['cognitive_load']}
    """
    
    # 5. Neural Processing (Brain)
    decision: AgentDecision = brain.think(message, history, context)
    
    # 6. Ambiguity Check (Ambiguity Budgeting)
    ambiguity = calculate_ambiguity_score(message, decision.dict())
    if ambiguity > 0.8 and decision.intent == "book":
        # Force clarification if too ambiguous
        decision.response_text = "I want to make sure I get this right. Could you clarify the time you have in mind?"
        decision.intent = "question"

    # 7. Memory & Learning
    if decision.detected_preferences:
        new_notes = prefs.get('notes', '') + "; " + "; ".join(decision.detected_preferences)
        update_user_preferences(session_id, {"notes": new_notes})

    response_payload = {
        "text": decision.response_text,
        "intent": decision.intent,
        "data": None
    }
    
    # 8. Action Logic & Safety Simulation
    if decision.intent == "book" and decision.confidence > 0.8 and not decision.missing_info:
        # Detect Service
        chosen_service_key = "consultation"
        for key, srv in rules.services.items():
            if key in message.lower() or srv['name'].lower() in message.lower():
                chosen_service_key = key
        
        service_info = rules.services[chosen_service_key]
        duration = service_info['duration']

        sim_result = simulate_future_schedule(
            decision.target_date + "T" + (decision.target_time or "09:00"), 
            duration,
            [] 
        )
        
        # Calculate Booking Quality for this specific slot
        quality_score = calculate_booking_quality(decision.target_date + "T" + (decision.target_time or "09:00"), duration)
        
        if sim_result['recommendation'] == 'unsafe':
            response_payload['text'] = f"I paused this booking. Conflict detected: {', '.join(sim_result['conflicts_detected'])}. Alternative?"
        else:
            appt = book_internal(
                decision.user_name, 
                decision.user_contact, 
                service_info['name'], 
                decision.target_date + "T" + (decision.target_time or "09:00"),
                duration
            )
            
            # SEND CONFIRMATION EMAIL
            email_sent = send_confirmation_email(
                decision.user_email,
                decision.user_name,
                decision.target_date,
                decision.target_time,
                details={"quality_score": quality_score, "staff": staff_assignment, "service": service_info['name']}
            )
            
            email_note = " 📧 Confirmation email sent." if email_sent else ""
            response_payload['text'] += email_note
            
            response_payload["data"] = {
                "type": "confirmation", 
                "appointment": appt,
                "meta": {
                    "quality_score": quality_score,
                    "staff": staff_assignment,
                    "risk_assessment": risk_data
                }
            }
            
    elif decision.intent == "availability":
         target_date = decision.target_date if decision.target_date else now_str
         slots = get_open_slots(target_date, count=5)
         response_payload["data"] = {"type": "slots", "slots": slots}

    elif decision.intent == "question":
         # Check if it's about "my appointments" manually since intent might be question
         if "my appointment" in message.lower() or "my booking" in message.lower() or "history" in message.lower():
             if not decision.user_email:
                 response_payload["text"] = "I can definitely look that up. What is your email address?"
             else:
                 all_appts = get_all_user_appointments(decision.user_email)
                 if not all_appts:
                     response_payload["text"] = f"I found no booking history for {decision.user_email}."
                 else:
                     lines = []
                     for a in all_appts:
                         dt = parse(a['start_iso'])
                         lines.append(f"- {dt.strftime('%b %d, %H:%M')} ({a['service']}) [{a['status'].upper()}]")
                     response_payload["text"] = f"Here is your full booking history:\n" + "\n".join(lines)
         
    elif decision.intent == "cancel":
         if not decision.user_email:
             response_payload["text"] = "I need your email address to find your appointment."
         else:
             appts = get_active_appointments_by_email(decision.user_email)
             if not appts:
                 response_payload["text"] = f"I couldn't find any active appointments for {decision.user_email}."
             else:
                 # Cancel the first one found (Logic could be improved to ask which one)
                 to_cancel = appts[0]
                 cancel_appointment(to_cancel['id'])
                 response_payload["text"] = f"Cancelled your appointment on {to_cancel['start_iso']}."
                 # Ideally send cancellation email here
                 
    elif decision.intent == "reschedule":
        # Multi-step: Cancel + Book
        if not decision.user_email:
             response_payload["text"] = "I need your email address to find your existing appointment for rescheduling."
        else:
             appts = get_active_appointments_by_email(decision.user_email)
             if not appts:
                 response_payload["text"] = "No existing appointment found to reschedule."
             else:
                 # Cancel old
                 old_appt = appts[0]
                 cancel_appointment(old_appt['id'])
                 
                 # Book new (if date/time present)
                 if decision.target_date and decision.target_time:
                     # Reuse logic or recursive call? Recursive call is dangerous.
                     # Duplicate minimal book logic
                     # Detect Service from old appt
                     service_name = old_appt['service'] # Try to match?
                     # Fallback to consultation or existing
                     duration = 30 # Default
                     
                     new_appt = book_internal(
                        decision.user_name or old_appt['name'], 
                        decision.user_contact or old_appt['contact'],
                        service_name,
                        decision.target_date + "T" + decision.target_time,
                        duration
                     )
                     response_payload["text"] = f"Rescheduled from {old_appt['start_iso']} to {new_appt['start_iso']}."
                 else:
                     response_payload["text"] = f"Cancelled {old_appt['start_iso']}. What new time would you like?"

    return response_payload

def book_internal(name, contact, service, start_iso, duration_minutes=30):
    # Quick internal booker
    rules = get_rules()
    zone = tz.gettz(rules.timezone)
    try:
        start = isoparse(start_iso)
        if start.tzinfo is None: start = start.replace(tzinfo=zone)
    except:
        start = datetime.now(zone) 
        
    end = start + timedelta(minutes=duration_minutes)
    appt = {
        "id": str(uuid.uuid4())[:8],
        "name": name or "Guest",
        "contact": contact or "Unknown",
        "service": service,
        "start_iso": start.isoformat(),
        "end_iso": end.isoformat(),
        "status": "booked",
    }
    insert_appointment(appt)
    return appt
