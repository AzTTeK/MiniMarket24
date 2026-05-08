import sqlite3
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") # Usaremos anon key o service role si fuera necesario
DB_PATH = "demand24_demo.db"

def migrate():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL o SUPABASE_ANON_KEY no configurados.")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Conectar a SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Iniciando Migración a Supabase ---")

    # 1. Migrar SKUs
    print("Migrando SKUs...")
    cursor.execute("SELECT id, sku_code, description, current_stock FROM sku")
    skus = cursor.fetchall()
    
    # Mapeo de IDs antiguos a nuevos (por si acaso Supabase genera nuevos SERIALs)
    # Pero intentaremos mantener los mismos IDs para las FKs
    for s in skus:
        data = {
            "id": s[0],
            "sku_code": s[1],
            "description": s[2],
            "current_stock": s[3]
        }
        supabase.table("sku").upsert(data).execute()
    print(f"OK: {len(skus)} SKUs migrados.")

    # 2. Migrar Predicciones
    print("Migrando Predicciones...")
    cursor.execute("SELECT id, sku_id, week_start, predicted_demand, confidence_level, lower_bound, upper_bound, mape FROM prediction")
    preds = cursor.fetchall()
    
    # Insertar en bloques para mayor velocidad
    for p in preds:
        data = {
            "id": p[0],
            "sku_id": p[1],
            "week_start": p[2],
            "predicted_demand": p[3],
            "confidence_level": p[4],
            "lower_bound": p[5],
            "upper_bound": p[6],
            "mape": p[7]
        }
        supabase.table("prediction").upsert(data).execute()
    print(f"OK: {len(preds)} predicciones migradas.")

    # 3. Migrar Alertas
    print("Migrando Alertas...")
    cursor.execute("SELECT id, sku_id, prediction_id, alert_type, message, is_acknowledged FROM alert")
    alerts = cursor.fetchall()
    
    for a in alerts:
        data = {
            "id": a[0],
            "sku_id": a[1],
            "prediction_id": a[2],
            "alert_type": a[3],
            "message": a[4],
            "is_acknowledged": bool(a[5])
        }
        supabase.table("alert").upsert(data).execute()
    print(f"OK: {len(alerts)} alertas migradas.")

    conn.close()
    print("\n--- ¡Migración Completada con Éxito! ---")

if __name__ == "__main__":
    migrate()
