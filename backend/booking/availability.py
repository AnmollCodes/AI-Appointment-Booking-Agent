from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import isoparse
from .rules import get_rules
from .db import get_appointments_between

def _hm_to_time(hm: str):
    h, m = hm.split(":")
    return int(h), int(m)

def get_open_slots(day_iso: str, count: int = 10) -> list[dict]:
    """
    Returns a list of slots with 'score' and 'reasoning'.
    """
    rules = get_rules()
    zone = tz.gettz(rules.timezone)
    
    try:
        day = isoparse(day_iso)
        if day.tzinfo is None:
             day = day.replace(tzinfo=zone)
        else:
             day = day.astimezone(zone)
    except:
        day = datetime.now(zone)

    if day.weekday() not in rules.work_days:
        return []

    sh, sm = _hm_to_time(rules.day_start)
    eh, em = _hm_to_time(rules.day_end)
    lh, lm = _hm_to_time(rules.lunch_start)
    leh, lem = _hm_to_time(rules.lunch_end)

    start_day = day.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end_day = day.replace(hour=eh, minute=em, second=0, microsecond=0)

    lunch_start = day.replace(hour=lh, minute=lm, second=0, microsecond=0)
    lunch_end = day.replace(hour=leh, minute=lem, second=0, microsecond=0)

    step = timedelta(minutes=rules.duration_minutes + rules.buffer_minutes)
    dur = timedelta(minutes=rules.duration_minutes)

    existing = get_appointments_between(start_day.isoformat(), end_day.isoformat())
    booked_ranges = [(isoparse(a["start_iso"]), isoparse(a["end_iso"])) for a in existing]

    slots = []
    t = start_day
    
    while t + dur <= end_day and len(slots) < count:
        score = 100
        reason = "Standard slot"
        
        # Lunch check
        if (t < lunch_end and (t + dur) > lunch_start):
             t = t + step
             continue

        # Overlap check
        end_t = t + dur
        overlaps = False
        for b0, b1 in booked_ranges:
            if b0.tzinfo is None: b0 = b0.replace(tzinfo=zone)
            if b1.tzinfo is None: b1 = b1.replace(tzinfo=zone)
            if t < b1 and end_t > b0:
                overlaps = True
                break
        
        if not overlaps:
            # Simple heuristic scoring
            if t.hour < 10: score += 10 # Morning preference?
            if t.hour > 16: score -= 5  # Late day fatigue
            
            slots.append({
                "start": t.isoformat(),
                "end": end_t.isoformat(),
                "score": score,
                "reason": reason
            })
        
        t = t + step

    # Return top slots
    slots.sort(key=lambda x: x["score"], reverse=True)
    return slots
