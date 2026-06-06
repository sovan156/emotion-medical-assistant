# 🏥 Universal Emotion-Aware Medical Communication Assistant

An AI-powered healthcare communication assistant that detects a patient's emotional state and adapts medical explanations accordingly.

## What It Does

- Detects emotions like anxiety, confusion, stress, calmness from text and voice
- Adapts communication style based on detected emotion
- Explains medical reports in emotionally appropriate language
- Provides voice input support via OpenAI Whisper
- Multilingual support for English, Hindi, and Bengali

## Tech Stack

- Frontend: React.js + Vite + TailwindCSS
- Backend: Python FastAPI
- Database: MongoDB
- AI: HuggingFace Transformers + OpenAI GPT + Whisper STT
- Auth: JWT Authentication

## Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- MongoDB
- OpenAI API Key

### Backend Setup

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000

### Frontend Setup

cd frontend
npm install
npm run dev

### Visit the App

Open your browser and go to: http://localhost:5173

## Disclaimer

This system provides health information for educational purposes only.
It does not replace professional medical advice, diagnosis, or treatment.
Always consult a qualified healthcare professional.

## Team

- Sovan - Developer
- Nishant - Developer