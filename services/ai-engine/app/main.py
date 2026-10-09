"""Main application entry point for QUANTA AI Engine."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as api_v1_router


app = FastAPI(
    title="QUANTA AI Decision Engine",
    description=(
        "Autonomous Corporate Treasury & Capital Allocation Decision Intelligence Service. "
        "Deterministic Search, Constraint Satisfaction, Bayesian Risk Inference, and Multi-Agent Optimization."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend and integration testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestrators and load balancers."""
    return {
        "status": "healthy",
        "service": "quanta-ai-engine",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }


# Mount API V1 routes
app.include_router(api_v1_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
