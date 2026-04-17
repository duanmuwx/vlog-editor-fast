"""FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.server.api.projects import router as projects_router

app = FastAPI(
    title="Vlog Editor API",
    description="AI travel vlog editing system",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
