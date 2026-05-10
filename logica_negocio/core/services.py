"""
DEMAND-24 — Capa de Servicios (Service Layer)

Orquestador entre los endpoints REST y los modulos internos.
Toda logica de negocio pasa por aqui — los endpoints son "tontos".

Cumple con:
- Regla I: SoC — API no toca ML directo
- Decision #12: Backend accede ML solo via DemandPredictor
- Decision #18: Sesion BD inyectada desde capa superior
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from logica_negocio.api.schemas.api_schemas import (
    ChartPoint,
    DashboardSummary,
    KPISummary,
    ProductSummary,
)
from logica_negocio.database.repositories import (
    AlertRepository,
    ModelVersionRepository,
    PredictionRepository,
    SkuRepository,
)
from logica_negocio.database.schemas import (
    AlertRead,
    ModelVersionRead,
    PredictionRead,
    SkuCreate,
    SkuRead,
)

logger = logging.getLogger(__name__)

# Traduccion de familias del CSV a nombres legibles en espanol
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


class DemandService:
    """
    Capa de servicios que orquesta las operaciones del sistema DEMAND-24.

    Responsabilidades:
    - Consultar SKUs, predicciones, modelos via repositories
    - Disparar entrenamiento via DemandPredictor (lazy import)
    - Gestionar alertas via AlertEngine
    - Generar resumen de dashboard para el frontend
    - NUNCA accede a ML internals directamente

    Usage:
        service = DemandService(db_session)
        skus = service.get_all_skus()
    """

    def __init__(self, db: Session):
        self._db = db
        self._sku_repo = SkuRepository(db)
        self._prediction_repo = PredictionRepository(db)
        self._model_version_repo = ModelVersionRepository(db)
        self._alert_repo = AlertRepository(db)

    # ── SKU Operations ──────────────────────────────────────────

    def get_all_skus(self) -> List[SkuRead]:
        """Lista todos los SKUs registrados."""
        return self._sku_repo.get_all()

    def get_sku_by_id(self, sku_id: int) -> Optional[SkuRead]:
        """Obtiene un SKU por su ID."""
        return self._sku_repo.get_by_id(sku_id)

    def create_sku(self, sku_data: SkuCreate) -> SkuRead:
        """Crea un nuevo SKU."""
        return self._sku_repo.create(sku_data)

    # ── Prediction Operations ───────────────────────────────────

    def get_predictions_by_sku(self, sku_id: int) -> List[PredictionRead]:
        """Obtiene todas las predicciones de un SKU."""
        return self._prediction_repo.get_all_by_sku(sku_id)

    def get_all_predictions(self) -> List[PredictionRead]:
        """Obtiene todas las predicciones del sistema."""
        return self._prediction_repo.get_all()

    # ── Model Operations ────────────────────────────────────────

    def get_latest_model(self) -> Optional[ModelVersionRead]:
        """Obtiene la version mas reciente del modelo."""
        return self._model_version_repo.get_latest()

    def get_all_models(self) -> List[ModelVersionRead]:
        """Lista todas las versiones de modelo."""
        return self._model_version_repo.get_all()

    # ── Training Orchestration ──────────────────────────────────

    def trigger_training(self) -> Dict[str, Any]:
        """
        Dispara el pipeline completo de entrenamiento del modelo y genera predicciones.
        """
        logger.info("Iniciando pipeline de entrenamiento via DemandService")

        # Lazy import para evitar acoplamiento circular (Decision #12)
        from modulo_analitico.predictor import DemandPredictor

        predictor = DemandPredictor()

        try:
            logger.info("Etapa 1/5: Cargando datos...")
            predictor.load_data()

            logger.info("Etapa 2/5: Preparando datos (agregacion + features)...")
            predictor.prepare_data()

            logger.info("Etapa 3/5: Entrenando modelo...")
            training_results = predictor.train()

            from datetime import datetime
            version_name = f"v1.0-demo-{datetime.now().strftime('%Y%m%d-%H%M')}"
            
            logger.info("Etapa 4/5: Persistiendo resultados en BD (%s)...", version_name)
            predictor.save_training_results_to_db(
                model_version=version_name,
                db_session=self._db
            )
            
            logger.info("Etapa 5/5: Generando y persistiendo predicciones futuras...")
            predictions_df = predictor.predict(weeks_ahead=4, with_confidence_intervals=True)
            
            # Mapear familia y tienda al sku_id real de la BD
            all_skus = self._sku_repo.get_all()
            sku_map = {sku.description: sku.id for sku in all_skus}
                
            predictions_df["sku_id"] = predictions_df.apply(
                lambda row: sku_map.get(f"{str(row['family']).strip()} en Tienda {int(row['store_nbr'])}"),
                axis=1
            )
            
            logger.info(f"Se emparejaron {predictions_df['sku_id'].notna().sum()} SKUs de {len(predictions_df)} predicciones.")
            
            # Limpiar y preparar formato para DB
            predictions_df = predictions_df.dropna(subset=["sku_id"]).copy()
            if not predictions_df.empty:
                predictions_df["sku_id"] = predictions_df["sku_id"].astype(int)
                
                global_mape = predictor._metrics.get("mape_mean", 20.0)
                predictions_df["mape"] = global_mape
                
                predictions_df.rename(columns={
                    "prediction": "predicted_demand",
                    "ci_lower": "lower_bound",
                    "ci_upper": "upper_bound"
                }, inplace=True)
                
                # La BD espera un float entre 0 y 1, pero predictor devuelve "HIGH" / "LOW"
                if "confidence_level" in predictions_df.columns:
                    predictions_df["confidence_level"] = predictions_df["confidence_level"].map({"HIGH": 0.9, "LOW": 0.5}).fillna(0.7)
                
                # Limpiar predicciones viejas para evitar UNIQUE constraint error al re-sincronizar
                from sqlalchemy import text
                self._db.execute(text("DELETE FROM prediction"))
                self._db.commit()
                
                predictor.save_predictions_to_db(predictions_df, self._db)
                logger.info(f"Guardadas {len(predictions_df)} predicciones exitosamente.")

        except FileNotFoundError as err:
            logger.error("Dataset no encontrado: %s", err)
            raise RuntimeError(
                "No se encontro el dataset de entrenamiento. "
                "Verifica que los archivos CSV esten en data/raw/"
            ) from err
        except Exception as err:
            logger.error("Error en pipeline de entrenamiento: %s", err)
            raise RuntimeError(
                f"Error durante el entrenamiento: {str(err)}"
            ) from err

        logger.info("Pipeline de entrenamiento completado exitosamente")
        return training_results

    # ── Alert Operations ────────────────────────────────────────

    def get_active_alerts(self) -> List[AlertRead]:
        """Obtiene alertas activas (no atendidas)."""
        return self._alert_repo.get_active()

    def get_all_alerts(self) -> List[AlertRead]:
        """Obtiene todas las alertas."""
        return self._alert_repo.get_all()

    def get_alerts_by_sku(self, sku_id: int) -> List[AlertRead]:
        """Obtiene alertas de un SKU especifico."""
        return self._alert_repo.get_by_sku(sku_id)

    def acknowledge_alert(self, alert_id: int) -> Optional[AlertRead]:
        """Marca una alerta como atendida."""
        return self._alert_repo.acknowledge(alert_id)

    def check_stock_alerts(self, stock_levels: Dict[int, int]) -> List[AlertRead]:
        """
        Ejecuta el motor de alertas para detectar quiebres de stock.

        Args:
            stock_levels: {sku_id: stock_actual}
        """
        from logica_negocio.core.alert_engine import AlertEngine

        engine = AlertEngine(self._db)
        return engine.check_stock_alerts(stock_levels)

    # ── Dashboard Operations ────────────────────────────────────

    def get_dashboard_summary(self) -> DashboardSummary:
        """
        Genera el resumen completo del dashboard.

        Combina datos de SKUs, predicciones y alertas para producir:
        - KPIs principales (total SKUs, precision, quiebres, revision)
        - Lista de productos con stock, demanda estimada, estado
        - Datos de graficos (historico + proyeccion) por producto

        Returns:
            DashboardSummary con todos los datos necesarios para el frontend.
        """
        all_skus = self._sku_repo.get_all()

        if not all_skus:
            return DashboardSummary(
                kpis=KPISummary(
                    total_skus=0, model_accuracy=0.0,
                    breakdowns=0, under_review=0,
                ),
                products=[],
                chart_data={"all": []},
            )

        # Obtener predicciones agrupadas por SKU
        predictions_by_sku: Dict[int, List[PredictionRead]] = defaultdict(list)
        all_predictions = self._prediction_repo.get_all()
        for pred in all_predictions:
            predictions_by_sku[pred.sku_id].append(pred)

        # Construir productos con estados
        products: List[ProductSummary] = []
        chart_data_all_actual: Dict[str, float] = defaultdict(float)
        chart_data_all_projected: Dict[str, float] = defaultdict(float)
        chart_data_by_product: Dict[str, List[ChartPoint]] = {}
        breakdowns = 0
        under_review = 0
        mape_values = []

        for sku in all_skus:
            sku_preds = predictions_by_sku.get(sku.id, [])
            sku_preds_sorted = sorted(sku_preds, key=lambda p: p.week_start)

            # Calcular demanda estimada (ultima prediccion disponible)
            latest_demand = 0
            mape_value = None
            if sku_preds_sorted:
                latest_demand = int(float(sku_preds_sorted[-1].predicted_demand))
                mape_value = float(sku_preds_sorted[-1].mape) if sku_preds_sorted[-1].mape else None

            if mape_value is not None:
                mape_values.append(mape_value)

            stock = sku.current_stock or 0

            # Determinar estado
            if latest_demand > 0 and stock < latest_demand * 0.8:
                status = "Quiebre"
                breakdowns += 1
            elif latest_demand > 0 and stock < latest_demand * 1.1:
                status = "Revisar"
                under_review += 1
            else:
                status = "Normal"

            # Determinar confianza basada en MAPE ajustado al nuevo estandar
            if mape_value is None:
                confidence = "Media"
            elif mape_value <= 35.0:
                confidence = "Alta"
            elif mape_value <= 50.0:
                confidence = "Media"
            else:
                confidence = "Baja"

            # Extraer familia desde la descripcion ("AUTOMOTIVE en Tienda 1" -> "AUTOMOTIVE")
            family = sku.description.split(" en Tienda")[0] if " en Tienda" in (sku.description or "") else sku.sku_code
            product_name = FAMILY_TRANSLATIONS.get(family, family)

            products.append(ProductSummary(
                sku_id=sku.id,
                code=sku.sku_code,
                product=product_name,
                stock=stock,
                demand=latest_demand,
                status=status,
                confidence=confidence,
            ))

            # Construir chart data por producto
            product_chart = self._build_chart_points(sku_preds_sorted)
            chart_data_by_product[product_name] = product_chart

            # Acumular para grafico consolidado "all"
            for point in product_chart:
                if point.actual is not None:
                    chart_data_all_actual[point.name] += point.actual
                if point.projected is not None:
                    chart_data_all_projected[point.name] += point.projected

        # Construir chart consolidado
        all_week_names = []
        if products and chart_data_by_product:
            first_product_chart = list(chart_data_by_product.values())[0]
            all_week_names = [p.name for p in first_product_chart]

        chart_all: List[ChartPoint] = []
        for week_name in all_week_names:
            actual_val = chart_data_all_actual.get(week_name)
            projected_val = chart_data_all_projected.get(week_name)
            base_val = actual_val or projected_val or 0
            chart_all.append(ChartPoint(
                name=week_name,
                actual=round(actual_val, 1) if actual_val else None,
                projected=round(projected_val, 1) if projected_val else None,
                range=[round(base_val * 0.9, 1), round(base_val * 1.1, 1)] if base_val > 0 else None,
            ))

        chart_data_by_product["all"] = chart_all

        # Calcular precision del modelo (100 - MAPE promedio)
        avg_mape = sum(mape_values) / len(mape_values) if mape_values else 20.0
        model_accuracy = round(max(0, 100.0 - avg_mape), 1)

        return DashboardSummary(
            kpis=KPISummary(
                total_skus=len(all_skus),
                model_accuracy=model_accuracy,
                breakdowns=breakdowns,
                under_review=under_review,
            ),
            products=products,
            chart_data=chart_data_by_product,
        )

    def _build_chart_points(
        self, predictions: List[PredictionRead]
    ) -> List[ChartPoint]:
        """
        Construye puntos del grafico asumiendo que todos los registros en 'prediction'
        son semanas futuras proyectadas por el modelo de IA.
        """
        if not predictions:
            return []

        chart_points: List[ChartPoint] = []

        for i, pred in enumerate(predictions):
            offset = i + 1
            week_label = f"S+{offset}"
            demand = round(float(pred.predicted_demand), 1)
            lower = round(float(pred.lower_bound), 1) if pred.lower_bound else round(demand * 0.9, 1)
            upper = round(float(pred.upper_bound), 1) if pred.upper_bound else round(demand * 1.1, 1)

            # Usamos el primer punto como ancla visual conectora (S0)
            if i == 0:
                chart_points.append(ChartPoint(
                    name="S0",
                    actual=demand,
                    projected=demand,
                    range=[lower, upper],
                ))
            else:
                chart_points.append(ChartPoint(
                    name=week_label,
                    actual=None,
                    projected=demand,
                    range=[lower, upper],
                ))

        return chart_points

