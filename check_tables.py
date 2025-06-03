from sqlalchemy import create_engine

url = "postgresql://penta_worlds_database_user:tlrQsqkboG4qHcixoBAIAOQlzYtLpMfx@dpg-...pg.render.com:5432/penta_worlds_database"
engine = create_engine(url)

try:
    with engine.connect() as conn:
        result = conn.execute("SELECT 1")
        print("✅ Připojení úspěšné!")
except Exception as e:
    print("❌ Chyba připojení:", e)