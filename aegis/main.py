from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aegis.core.config import settings
from aegis.core.database import engine, Base, SessionLocal
from aegis.security.auth import hash_password
from aegis.models.moderator import ModeratorOfficer
from aegis.api.escrow import router as escrow_router
from aegis.api.moderation import router as moderation_router

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Seed initial moderator account for evaluators
    db = SessionLocal()
    try:
        if not db.query(ModeratorOfficer).filter(ModeratorOfficer.username == "gdg_moderator").first():
            officer = ModeratorOfficer(
                username="gdg_moderator",
                hashed_password=hash_password("Aegis@SRM2026!"),
                badge_title="Lead Evaluator"
            )
            db.add(officer)
            db.commit()
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AegisMesh: Zero-Knowledge Autonomous Threat Escrow & Incident Triaging Engine.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(escrow_router, prefix=settings.API_V1_PREFIX)
app.include_router(moderation_router, prefix=settings.API_V1_PREFIX)

@app.get("/health", tags=["Infrastructure"])
def healthcheck():
    return {"status": "operational", "engine": settings.PROJECT_NAME, "zero_knowledge": True}