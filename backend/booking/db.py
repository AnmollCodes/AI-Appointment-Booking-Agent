import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "bookings.db"

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    con = connect()
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          contact TEXT NOT NULL,
          service TEXT NOT NULL,
          start_iso TEXT NOT NULL,
          end_iso TEXT NOT NULL,
          status TEXT NOT NULL
        )
        """
    )
    # Preferences table for memory functionality
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS preferences (
           contact TEXT PRIMARY KEY,
           data TEXT NOT NULL
        )
        """
    )
    con.commit()
    con.close()

# --- Appointments ---
def insert_appointment(appt: dict):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO appointments (id, name, contact, service, start_iso, end_iso, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (appt["id"], appt["name"], appt["contact"], appt["service"], appt["start_iso"], appt["end_iso"], appt["status"]),
    )
    con.commit()
    con.close()

def get_appointments_between(start_iso: str, end_iso: str) -> list[dict]:
    con = connect()
    cur = con.cursor()
    cur.execute(
        "SELECT id, name, contact, service, start_iso, end_iso, status FROM appointments WHERE start_iso < ? AND end_iso > ? AND status = 'booked'",
        (end_iso, start_iso),
    )
    rows = cur.fetchall()
    con.close()
    return [
        {"id": r[0], "name": r[1], "contact": r[2], "service": r[3], "start_iso": r[4], "end_iso": r[5], "status": r[6]}
        for r in rows
    ]

def get_appointment(appt_id: str):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "SELECT id, name, contact, service, start_iso, end_iso, status FROM appointments WHERE id = ?",
        (appt_id,),
    )
    row = cur.fetchone()
    con.close()
    if not row:
        return None
    return {"id": row[0], "name": row[1], "contact": row[2], "service": row[3], "start_iso": row[4], "end_iso": row[5], "status": row[6]}

def update_appointment_time(appt_id: str, start_iso: str, end_iso: str):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "UPDATE appointments SET start_iso = ?, end_iso = ? WHERE id = ?",
        (start_iso, end_iso, appt_id),
    )
    con.commit()
    con.close()

def cancel_appointment(appt_id: str):
    con = connect()
    cur = con.cursor()
    cur.execute(
        "UPDATE appointments SET status = 'cancelled' WHERE id = ?",
        (appt_id,),
    )
    con.commit()
    con.commit()
    con.close()

def get_active_appointments_by_email(email: str) -> list[dict]:
    con = connect()
    cur = con.cursor()
    # Normalize check? For now simple robust check
    cur.execute(
        "SELECT id, name, contact, service, start_iso, end_iso, status FROM appointments WHERE contact = ? AND status = 'booked' ORDER BY start_iso ASC",
        (email,),
    )
    rows = cur.fetchall()
    con.close()
    return [
        {"id": r[0], "name": r[1], "contact": r[2], "service": r[3], "start_iso": r[4], "end_iso": r[5], "status": r[6]}
        for r in rows
    ]

def get_all_user_appointments(email: str) -> list[dict]:
    """Get ALL appointments (past/present/cancelled) for a user to show history."""
    con = connect()
    cur = con.cursor()
    cur.execute(
        "SELECT id, name, contact, service, start_iso, end_iso, status FROM appointments WHERE contact = ? ORDER BY start_iso DESC",
        (email,),
    )
    rows = cur.fetchall()
    con.close()
    return [
        {"id": r[0], "name": r[1], "contact": r[2], "service": r[3], "start_iso": r[4], "end_iso": r[5], "status": r[6]}
        for r in rows
    ]

# --- Preferences / Memory ---
def get_user_preferences(contact: str) -> dict:
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT data FROM preferences WHERE contact = ?", (contact,))
    row = cur.fetchone()
    con.close()
    if row:
        return json.loads(row[0])
    return {}

def update_user_preferences(contact: str, new_data: dict):
    current = get_user_preferences(contact)
    current.update(new_data)
    con = connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO preferences (contact, data) VALUES (?, ?)", (contact, json.dumps(current)))
    con.commit()
    con.close()

def get_all_appointments():
    con = connect()
    cur = con.cursor()
    cur.execute("SELECT id, name, contact, service, start_iso, end_iso, status FROM appointments ORDER BY start_iso DESC")
    rows = cur.fetchall()
    con.close()
    return [
        {"id": r[0], "name": r[1], "contact": r[2], "service": r[3], "start_iso": r[4], "end_iso": r[5], "status": r[6]}
        for r in rows
    ]
