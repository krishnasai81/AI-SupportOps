from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings

if settings.ENVIRONMENT.lower() == "production":
    jwt_secret = settings.JWT_SECRET_KEY.get_secret_value()
    if jwt_secret == "local-development-only-change-this-secret" or len(jwt_secret) < 32:
        raise RuntimeError("Set a unique JWT_SECRET_KEY of at least 32 characters in production.")
    if not settings.DATABASE_URL.startswith("postgresql+psycopg://"):
        raise RuntimeError(
            "Production requires persistent PostgreSQL. Set DATABASE_URL using postgresql+psycopg://."
        )
from app.database.connection import Base, engine
from app.database import models
from app.api.tickets import router as ticket_router
from app.api.messages import router as message_router
from app.api.knowledge import router as knowledge_router
from app.api.agent import router as agent_router
from app.api.approvals import router as approval_router
from app.api.auth import router as auth_router
from app.api.admin_users import router as admin_users_router
from app.api.vision import router as vision_router


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Role-secured multi-agent customer support platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(admin_users_router)
app.include_router(ticket_router)
app.include_router(message_router)
app.include_router(knowledge_router)
app.include_router(agent_router)
app.include_router(approval_router)
app.include_router(vision_router)


@app.get("/")
def home():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.is_file():
        return FileResponse(index_file)
    return {"message": "Welcome to AI SupportOps", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "application": settings.APP_NAME}


origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount last so API endpoints and /health take precedence. In production,
# this serves the Vite build from the same origin as the API.
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
