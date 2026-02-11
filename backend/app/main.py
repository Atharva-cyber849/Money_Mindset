"""
FastAPI Main Application
Money Mindset Backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.database import Base, engine
from app.api.v1 import auth, users, transactions, budgets, goals, simulations, personality, analytics, progress  # ai_tutor temporarily disabled

# Import all models to register them with SQLAlchemy
from app.models import user, finance
from app.models import personality as personality_models

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["goals"])
# app.include_router(ai_tutor.router, prefix="/api/v1/ai-tutor", tags=["ai-tutor"])  # Temporarily disabled
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["simulations"])
app.include_router(personality.router, prefix="/api/v1/personality", tags=["personality"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["progress"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
