from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database.connection import Base, engine
from app.database import models

from app.api.tickets import router as ticket_router
from app.api.messages import router as message_router
from app.api.knowledge import router as knowledge_router
from app.api.agent import router as agent_router
from app.api.approvals import router as approval_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Multi-Agent AI Customer Support and Ticket Resolution System",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(ticket_router)
app.include_router(message_router)
app.include_router(knowledge_router)
app.include_router(agent_router)
app.include_router(approval_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI SupportOps",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "application": settings.APP_NAME,
    }


if not settings.APPROVAL_API_KEY:
    raise RuntimeError("APPROVAL_API_KEY must be configured")


# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.APPROVAL_API_KEY.get_secret_value(),
    session_cookie="supportops_admin_session",
    same_site="lax",
    https_only=False,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)