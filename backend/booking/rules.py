from dataclasses import dataclass, field
from typing import Set, Dict

@dataclass
class BookingRules:
    business_name: str = "Aura Aesthetics"
    timezone: str = "America/Chicago"
    work_days: Set[int] = field(default_factory=lambda: {0, 1, 2, 3, 4}) # Mon-Fri
    day_start: str = "09:00"
    day_end: str = "17:00"
    lunch_start: str = "12:00"
    lunch_end: str = "13:00"
    duration_minutes: int = 30 # Default slot if not specified
    buffer_minutes: int = 5
    emergency_override: bool = False 
    
    # New Business Logic
    services: Dict[str, dict] = field(default_factory=lambda: {
        "consultation": {"name": "Glow Consultation", "duration": 30, "price": 50, "desc": "Initial skin assessment and plan."},
        "facial": {"name": "Deep Hydration Facial", "duration": 60, "price": 120, "desc": "Intense moisture treatment for relaxation."},
        "laser": {"name": "Laser Precision Therapy", "duration": 45, "price": 200, "desc": "Targeted treatment for skin correction."}
    })

    def to_dict(self):
         return {
             "business_name": self.business_name,
             "timezone": self.timezone,
             "work_days": list(self.work_days),
             "day_start": self.day_start,
             "day_end": self.day_end,
             "services": self.services
         }

def get_rules() -> BookingRules:
    return BookingRules()
