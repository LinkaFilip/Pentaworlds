import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connection to database successful!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)