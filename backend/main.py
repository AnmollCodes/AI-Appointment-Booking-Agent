from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from booking.db import init_db, get_all_appointments, cancel_appointment
from booking.agent import handle_request
from booking.availability import get_open_slots

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatIn(BaseModel):
    session_id: str = "default"
    message: str
    history: List[dict]

@app.on_event("startup")
def startup():
    init_db()

@app.post("/chat")
def chat_endpoint(payload: ChatIn):
    # The main entry point for the agent
    response = handle_request(payload.session_id, payload.message, payload.history)
    return response

@app.post("/simple_availability")
def simple_avail(payload: dict):
    # Legacy/Direct helper
    day = payload.get("day_iso")
    return {"slots": get_open_slots(day)}

@app.get("/admin/appointments")
def admin_get_appts():
    return get_all_appointments()

@app.post("/admin/cancel")
def admin_cancel(payload: dict):
    # payload { "id": "..." }
    cancel_appointment(payload.get("id"))
    return {"status": "ok"}
