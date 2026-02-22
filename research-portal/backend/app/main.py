from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes import upload, extraction


app = FastAPI(title="Research Portal API")


# -----------------------------
# CORS Middleware (IMPORTANT for frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Include API Routers
# -----------------------------
app.include_router(upload.router)
app.include_router(extraction.router)


# -----------------------------
# Serve output files (Excel download)
# -----------------------------
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Research Portal Running",
        "docs": "/docs"
    }
