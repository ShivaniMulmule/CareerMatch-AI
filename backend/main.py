"""
CareerMatch AI — FastAPI Application Entrypoint.
"Know Your Job Fit. Before You Apply."
Full-Stack SaaS Backend providing Semantic Vector Embeddings, XGBoost Regression,
SHAP TreeExplainer, Evidence-based Skill Gap Analysis, and PDF Reporting.
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.routes.auth import router as auth_router
from backend.routes.resumes import router as resumes_router
from backend.routes.jobs import router as jobs_router
from backend.routes.analysis import router as analysis_router
from backend.routes.recommendations import router as recommendations_router
from backend.routes.reports import router as reports_router
from backend.routes.profile import router as profile_router
from backend.routes.health import router as health_router
from database.db_client import get_database, get_current_db_mode
from storage.storage_client import get_storage, get_current_storage_mode


app = FastAPI(
    title="CareerMatch AI Backend",
    description="Explainable AI-Based Resume Screening and Skill Gap Analysis System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Register Sub-Routers
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(jobs_router)
app.include_router(analysis_router)
app.include_router(recommendations_router)
app.include_router(reports_router)
app.include_router(profile_router)
app.include_router(health_router)


@app.on_event("startup")
async def startup_event():
    print("=" * 65)
    print("CAREERMATCH AI — BACKEND SERVER STARTUP")
    print("=" * 65)
    await get_database()
    get_storage()
    print(f"[+] Database Mode: {get_current_db_mode()}")
    print(f"[+] Storage Mode:  {get_current_storage_mode()}")
    print("[+] Model:         XGBRegressor + Sentence-BERT (all-MiniLM-L6-v2) + SHAP")
    print("[+] Core Principle: Zero keyword matching — dense vector semantic representations")
    print("=" * 65)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Safe error handler to prevent internal tracebacks from leaking in API responses."""
    print(f"[ERROR] Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred while processing your request.",
            "error_type": exc.__class__.__name__
        }
    )


@app.get("/")
async def root():
    return {
        "product": "CareerMatch AI",
        "tagline": "Know Your Job Fit. Before You Apply.",
        "project": "Explainable AI-Based Resume Screening and Skill Gap Analysis System",
        "documentation": "/docs",
        "health_check": "/api/health"
    }
