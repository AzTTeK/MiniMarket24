"""
DEMAND-24 — Script de Poblado de Base de Datos

Carga las 33 familias de productos del dataset Corporacion Favorita (Tienda #1)
y genera predicciones semanales basadas en datos historicos reales del CSV.

Uso:
    python scripts/populate_demo_db.py

Requisitos:
    - data/raw/train.csv debe existir
    - .env configurado con DATABASE_URL
"""

import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar raiz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logica_negocio.database.models.base import Base
from logica_negocio.database.models.sku import Sku
from logica_negocio.database.models.prediction import Prediction
from logica_negocio.config.settings import settings


# Tienda seleccionada para el minimarket (Quito, Tipo D, Cluster 13)
STORE_NUMBER = 1

# Numero de semanas historicas y proyectadas para el grafico
HISTORICAL_WEEKS = 8
PROJECTED_WEEKS = 3

# Traduccion de familias a nombres legibles
FAMILY_TRANSLATIONS = {
    "AUTOMOTIVE": "Automotriz",
    "BABY CARE": "Cuidado de Bebe",
    "BEAUTY": "Belleza",
    "BEVERAGES": "Bebidas",
    "BOOKS": "Libros",
    "BREAD/BAKERY": "Panaderia",
    "CELEBRATION": "Celebracion",
    "CLEANING": "Limpieza",
    "DAIRY": "Lacteos",
    "DELI": "Delicatessen",
    "EGGS": "Huevos",
    "FROZEN FOODS": "Congelados",
    "GROCERY I": "Abarrotes I",
    "GROCERY II": "Abarrotes II",
    "HARDWARE": "Ferreteria",
    "HOME AND KITCHEN I": "Hogar y Cocina I",
    "HOME AND KITCHEN II": "Hogar y Cocina II",
    "HOME APPLIANCES": "Electrodomesticos",
    "HOME CARE": "Cuidado del Hogar",
    "LADIESWEAR": "Ropa Dama",
    "LAWN AND GARDEN": "Jardin",
    "LINGERIE": "Lenceria",
    "LIQUOR,WINE,BEER": "Licores y Vinos",
    "MAGAZINES": "Revistas",
    "MEATS": "Carnes",
    "PERSONAL CARE": "Cuidado Personal",
    "PET SUPPLIES": "Mascotas",
    "PLAYERS AND ELECTRONICS": "Electronicos",
    "POULTRY": "Aves",
    "PREPARED FOODS": "Comida Preparada",
    "PRODUCE": "Frutas y Verduras",
    "SCHOOL AND OFFICE SUPPLIES": "Escolar y Oficina",
    "SEAFOOD": "Mariscos",
}

# Seed para reproducibilidad (Regla VI)
RANDOM_SEED = 42


def load_store_weekly_data(train_path: str) -> pd.DataFrame:
    """
    Carga y agrega datos del CSV a nivel semanal para la tienda seleccionada.

    Returns:
        DataFrame con columnas: family, week_start, weekly_sales
    """
    print(f"  Cargando datos de {train_path}...")
    df = pd.read_csv(
        train_path,
        usecols=["date", "store_nbr", "family", "sales"],
        parse_dates=["date"],
    )

    # Filtrar solo la tienda seleccionada
    df = df[df["store_nbr"] == STORE_NUMBER].copy()
    print(f"  Registros para Tienda #{STORE_NUMBER}: {len(df):,}")

    # Agregar a semanal (lunes como inicio de semana)
    df["week_start"] = df["date"].dt.to_period("W-SUN").dt.start_time.dt.date
    weekly = (
        df.groupby(["family", "week_start"])["sales"]
        .sum()
        .reset_index()
        .rename(columns={"sales": "weekly_sales"})
    )

    print(f"  Registros semanales generados: {len(weekly):,}")
    return weekly


def populate():
    """Pipeline principal de poblado de la BD."""
    print("=" * 60)
    print("DEMAND-24 — Poblado de Base de Datos con Datos Reales")
    print("=" * 60)

    np.random.seed(RANDOM_SEED)

    # Verificar que el CSV existe
    train_path = os.path.join("data", "raw", "train.csv")
    if not os.path.exists(train_path):
        print(f"ERROR: No se encontro {train_path}")
        print("Descarga el dataset desde Kaggle: Store Sales - Time Series Forecasting")
        return

    # Cargar datos semanales
    print("\n[1/4] Cargando datos del CSV...")
    weekly_data = load_store_weekly_data(train_path)

    # Conectar a BD
    print("\n[2/4] Conectando a la base de datos...")
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # Limpiar datos existentes para evitar duplicados
        print("  Limpiando datos existentes...")
        db.query(Prediction).delete()
        db.query(Sku).delete()
        db.commit()

        # Obtener familias unicas
        families = sorted(weekly_data["family"].unique())
        print(f"\n[3/4] Insertando {len(families)} productos (familias)...")

        sku_map = {}  # family -> Sku object
        for family in families:
            description = FAMILY_TRANSLATIONS.get(family, family)
            family_data = weekly_data[weekly_data["family"] == family]

            # Calcular stock simulado basado en demanda promedio semanal
            avg_weekly = family_data["weekly_sales"].mean()
            last_weeks = family_data.sort_values("week_start").tail(4)
            recent_avg = last_weeks["weekly_sales"].mean() if len(last_weeks) > 0 else avg_weekly

            # Stock entre 60% y 130% de la demanda promedio reciente
            # para generar una mezcla de estados (Normal, Revisar, Quiebre)
            stock_factor = np.random.uniform(0.6, 1.3)
            current_stock = max(1, int(recent_avg * stock_factor))

            sku = Sku(
                sku_code=family,
                description=description,
                current_stock=current_stock,
            )
            db.add(sku)
            db.flush()  # Para obtener el ID asignado
            sku_map[family] = sku
            print(f"    + {family} ({description}) — stock: {current_stock}")

        db.commit()
        print(f"  {len(sku_map)} SKUs insertados.")

        # Generar predicciones (historicas + proyectadas)
        print(f"\n[4/4] Generando predicciones ({HISTORICAL_WEEKS} historicas + {PROJECTED_WEEKS} proyectadas)...")

        predictions_count = 0
        today = date.today()
        # Calcular lunes de esta semana
        current_monday = today - timedelta(days=today.weekday())

        for family, sku in sku_map.items():
            family_data = weekly_data[weekly_data["family"] == family].sort_values("week_start")

            if len(family_data) < HISTORICAL_WEEKS:
                print(f"    ! {family}: datos insuficientes ({len(family_data)} semanas), saltando")
                continue

            # Tomar las ultimas semanas de datos reales para las historicas
            recent_data = family_data.tail(HISTORICAL_WEEKS + 4)  # extra para tendencia
            recent_sales = recent_data["weekly_sales"].values

            # Calcular MAPE simulado basado en variabilidad real de la serie
            cv = np.std(recent_sales) / max(np.mean(recent_sales), 1) * 100
            simulated_mape = round(min(max(cv * 0.5, 5.0), 35.0), 2)

            # Calcular tendencia para proyeccion
            if len(recent_sales) >= 4:
                trend = (np.mean(recent_sales[-2:]) - np.mean(recent_sales[-4:-2])) / max(np.mean(recent_sales[-4:-2]), 1)
            else:
                trend = 0.0

            last_n_sales = recent_sales[-HISTORICAL_WEEKS:]
            avg_recent = np.mean(last_n_sales)

            for week_offset in range(-HISTORICAL_WEEKS + 1, PROJECTED_WEEKS + 1):
                week_start = current_monday + timedelta(weeks=week_offset)

                if week_offset <= 0:
                    # Semana historica: usar datos reales del CSV
                    idx = HISTORICAL_WEEKS - 1 + week_offset
                    if 0 <= idx < len(last_n_sales):
                        demand = float(last_n_sales[idx])
                    else:
                        demand = float(avg_recent)
                else:
                    # Semana futura: proyectar con tendencia + ruido
                    growth = 1.0 + trend * week_offset * 0.3
                    noise = np.random.normal(1.0, 0.05)
                    demand = float(avg_recent * growth * noise)

                demand = max(0, round(demand, 2))

                # Calcular intervalo de confianza (90%)
                margin = demand * (simulated_mape / 100) * 1.645
                lower_bound = max(0, round(demand - margin, 2))
                upper_bound = round(demand + margin, 2)

                # Nivel de confianza basado en MAPE
                if simulated_mape <= 15:
                    confidence = 0.90
                elif simulated_mape <= 25:
                    confidence = 0.75
                else:
                    confidence = 0.60

                prediction = Prediction(
                    sku_id=sku.id,
                    week_start=week_start,
                    predicted_demand=demand,
                    confidence_level=confidence,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    mape=simulated_mape,
                )
                db.add(prediction)
                predictions_count += 1

        db.commit()
        print(f"  {predictions_count} predicciones insertadas.")

        # Resumen final
        print("\n" + "=" * 60)
        print("POBLADO COMPLETADO")
        print("=" * 60)
        print(f"  SKUs:          {len(sku_map)}")
        print(f"  Predicciones:  {predictions_count}")
        print(f"  Base de datos: {settings.DATABASE_URL}")
        print(f"  Tienda:        #{STORE_NUMBER} (Quito)")
        print("\nPuedes iniciar la API con:")
        print("  uvicorn logica_negocio.main:app --reload")
        print("\nY verificar el dashboard en:")
        print("  http://localhost:8000/api/v1/dashboard/summary")

    except Exception as err:
        print(f"\nERROR: {err}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate()
