# Aura Aesthetics - Smart Booking Agent

## Overview
Aura Aesthetics is a premium, AI-powered appointment booking solution designed for high-end service businesses. It features a conversational AI agent capable of managing specific availability, handling rescheduling, and answering service-related questions.

## Key Features
- **Smart Booking Agent**: Powered by LLMs, it understands context, negotiates times, and answers questions about services.
- **Service Awareness**: Pre-configured with services like "Glow Consultation", "Deep Hydration Facial", and "Laser Precision Therapy".
- **Dynamic Scheduling**: Automatically checks specific durations (e.g., 60m for Facials vs 30m for Consultations).
- **Admin Dashboard**: A built-in, glass-morphic dashboard to view and manage all bookings in real-time.
- **Rescheduling & Cancellation**: The agent can look up bookings by email to modify them.

## Tech Stack
- **Frontend**: React + Vite + Three.js (for premium 3D aesthetics) + Framer Motion.
- **Backend**: FastAPI + SQLite + OpenAI/OpenRouter.

## How to Run

### 1. Backend
```bash
cd backend
# Install dependencies (fastapi, uvicorn, openai, python-dateutil, python-dotenv)
python main.py  # or uvicorn main:app --reload
```
*Ensure you have a valid optional `OPENROUTER_API_KEY` in `.env` if using the real LLM usage.

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## Admin Access
- Click the small "Lock" icon in the top-right corner of the chat interface to open the Admin Dashboard.
- From there, you can view all upcoming appointments and cancel them if necessary.

## Customization
- Edit `backend/booking/rules.py` to change Business Name, Hours, and Services.
