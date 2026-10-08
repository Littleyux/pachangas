import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dev_user:dev_password@localhost:5432/pachangas_db")

def get_db_connection():
    # RealDictCursor hace que los resultados devuelvan diccionarios (JSON) en lugar de tuplas
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn