import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from logica_negocio.database.models.base import Base
from logica_negocio.database.models.sku import Sku
from logica_negocio.config.settings import settings
import os

def populate():
    print("Iniciando poblacion de base de datos para DEMO...")
    
    # Usar la URL de la base de datos de settings (.env)
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 1. Cargar SKUs desde train.csv (limitado para la demo)
        train_path = "data/raw/train.csv"
        if not os.path.exists(train_path):
            print(f"Error: No se encontro {train_path}")
            return

        print("Leyendo SKUs de train.csv...")
        # Leer solo una muestra para no saturar
        df = pd.read_csv(train_path, usecols=["store_nbr", "family"]).drop_duplicates().head(50)
        
        count = 0
        for _, row in df.iterrows():
            code = f"S{row['store_nbr']}-{row['family'][:3].upper()}"
            desc = f"{row['family']} en Tienda {row['store_nbr']}"
            
            # Evitar duplicados
            exists = db.query(Sku).filter(Sku.sku_code == code).first()
            if not exists:
                new_sku = Sku(
                    sku_code=code,
                    description=desc
                )
                db.add(new_sku)
                count += 1
        
        db.commit()
        print(f"{count} SKUs insertados con exito.")
        print("\nSugerencia: Ahora puedes correr la API y hacer clic en 'Re-entrenar' para generar las predicciones reales.")

    except Exception as e:
        print(f"Error durante la poblacion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()
