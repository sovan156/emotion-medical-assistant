from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, chat, voice, report, emotion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Emotion-Aware Medical Communication Assistant. Educational purposes only.",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(report.router, prefix="/api")
app.include_router(emotion.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "disclaimer": "Educational purposes only. Not a replacement for medical advice."
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/ollama/status")
async def ollama_status():
    """Check if Ollama and Gemma are ready."""
    from app.services.ollama_service import ollama_service

    server_running = ollama_service.is_available()
    model_ready = ollama_service.is_model_available() if server_running else False

    return {
        "ollama_server": "running" if server_running else "not running",
        "model": ollama_service.model,
        "model_status": "ready" if model_ready else "not found",
        "instructions": (
            "Run 'ollama serve' to start server. "
            "Run 'ollama pull gemma:2b' to download model."
            if not server_running else "All good!"
        )
    }
