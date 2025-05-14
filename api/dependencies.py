# api/dependencies.py
import sqlite3
from database.db_connection import create_connection

def get_db_session_dependency():
    db = None
    try:
        db = create_connection()
        if db is None:
            raise ConnectionError("Failed to create database connection.")
        yield db
    finally:
        if db:
            db.close()

# from fastapi import HTTPException, Security, status
# from fastapi.security import APIKeyHeader
# API_KEY_NAME = "X-API-KEY"
# api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
# async def verify_api_key(api_key: str = Security(api_key_header_auth)):
#     if api_key == "TU_API_KEY_SECRETA_AQUI":
#         return api_key
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Invalid or missing API Key"
#         )