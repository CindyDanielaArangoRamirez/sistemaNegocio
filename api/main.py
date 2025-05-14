# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import router as api_v1_router

app = FastAPI(
    title="Ferretería API - Sistema de Gestión",
    description="API para gestionar productos, ventas y otros aspectos de la ferretería.",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
async def root_redirect_to_docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/docs")