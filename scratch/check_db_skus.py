from logica_negocio.config.settings import settings
from sqlalchemy import create_engine, text
import json

def main():
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text('SELECT sku_code, description FROM sku'))
            rows = [dict(row._mapping) for row in result]
            print(json.dumps(rows, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
