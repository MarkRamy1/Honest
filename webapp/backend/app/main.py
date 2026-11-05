from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.seed import seed_database
from app.api.routes import health, auth, catalog, reviews, agent, vlm, embed, extension


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed baseline data (skip during isolated pytest runs)
    if settings.APP_ENV != "testing":
        try:
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as db:
                seed_database(db)
            logger.info(f"Honest AI Backend initialized successfully on {settings.HOST}:{settings.PORT}")
        except Exception as e:
            logger.error(f"Error during database startup initialization: {e}")
    yield
    # Shutdown logic if any
    logger.info("Honest AI Backend shutting down.")


app = FastAPI(
    title="Honest AI Shopping Research & Forensic Platform",
    description="Multimodal vision forensics, generative reality previews, and evidence-based shopping intelligence.",
    version="4.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(vlm.router, prefix="/api")
app.include_router(embed.router, prefix="/api")
app.include_router(extension.router, prefix="/api")

# Also include at root for complete URL backward compatibility
app.include_router(health.router)
app.include_router(embed.router)
app.include_router(extension.router)


@app.get("/")
def root_index():
    return {
        "app": settings.APP_NAME,
        "version": "4.0.0",
        "status": "online",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }
