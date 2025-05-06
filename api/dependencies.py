from fastapi import Depends
from database.db_connection import create_connection

def get_db():
    db = create_connection()
    try:
        yield db
    finally:
        db.close()