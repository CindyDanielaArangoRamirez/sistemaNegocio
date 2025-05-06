from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import router as api_router

app = FastAPI(
    title="API Ferretería",
    description="Endpoints para sistema de gestión de ferretería",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")