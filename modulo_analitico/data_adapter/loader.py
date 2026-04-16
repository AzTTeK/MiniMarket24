"""
DEMAND-24 — Carga y Validación de Datos

Responsable de cargar los CSVs del dataset Kaggle y validar su integridad.
Implementa RF-02 (Validación de Datos) con mensajes de error descriptivos.

Cumple con:
- Regla I: Inmutabilidad (todos los DataFrames se retornan como copias)
- Regla II: Código Auto-Documentado (nombres descriptivos)
- Regla IV: Early Return Pattern (validaciones al inicio)
"""

from pathlib import Path
from typing import Tuple, Optional
import pandas as pd

from ..config.ml_config import MLConfig


class DataLoader:
    """
    Carga y valida los datos del dataset Kaggle.
    
    Responsabilidades:
    - Cargar train.csv, stores.csv, holidays_events.csv, oil.csv
    - Validar esquema (columnas, tipos)
    - Detectar valores nulos críticos
    - Verificar mínimo 12 semanas por SKU (RF-02)
    """

    REQUIRED_TRAIN_COLUMNS = {
        "id": "int64",
        "date": "object",
        "store_nbr": "int64",
        "family": "object",
        "sales": "float64",
        "onpromotion": "int64",
    }

    REQUIRED_STORES_COLUMNS = {
        "store_nbr": "int64",
        "city": "object",
        "state": "object",
        "type": "object",
        "cluster": "int64",
    }

    REQUIRED_HOLIDAYS_COLUMNS = {
        "date": "object",
        "type": "object",
        "locale": "object",
        "locale_name": "object",
        "description": "object",
        "transferred": "object",
    }

    REQUIRED_OIL_COLUMNS = {
        "date": "object",
        "dcoilwtico": "object",
    }

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()

    def load_train_data(self) -> pd.DataFrame:
        """
        Carga y valida train.csv.
        
        Returns:
            DataFrame con datos de entrenamiento validados
        
        Raises:
            FileNotFoundError: Si el archivo no existe
            ValueError: Si el esquema no es correcto
        """
        train_path = self.config.DATA_RAW_DIR / "train.csv"
        
        if not train_path.exists():
            raise FileNotFoundError(
                f"train.csv no encontrado en {self.config.DATA_RAW_DIR}. "
                f"Descargar desde: https://www.kaggle.com/competitions/store-sales-time-series-forecasting"
            )

        df = pd.read_csv(train_path, parse_dates=["date"])

        self._validate_schema(df, self.REQUIRED_TRAIN_COLUMNS, "train.csv")
        self._validate_no_null_critical(df, ["date", "store_nbr", "family", "sales"])

        return df.copy()

    def load_stores_data(self) -> pd.DataFrame:
        """
        Carga y valida stores.csv.
        
        Returns:
            DataFrame con información de tiendas
        """
        stores_path = self.config.DATA_RAW_DIR / "stores.csv"
        
        if not stores_path.exists():
            raise FileNotFoundError(
                f"stores.csv no encontrado en {self.config.DATA_RAW_DIR}"
            )

        df = pd.read_csv(stores_path)
        self._validate_schema(df, self.REQUIRED_STORES_COLUMNS, "stores.csv")

        return df.copy()

    def load_holidays_data(self) -> pd.DataFrame:
        """
        Carga y valida holidays_events.csv.
        
        Returns:
            DataFrame con eventos festivos
        """
        holidays_path = self.config.DATA_RAW_DIR / "holidays_events.csv"
        
        if not holidays_path.exists():
            raise FileNotFoundError(
                f"holidays_events.csv no encontrado en {self.config.DATA_RAW_DIR}"
            )

        df = pd.read_csv(holidays_path, parse_dates=["date"])
        self._validate_schema(df, self.REQUIRED_HOLIDAYS_COLUMNS, "holidays_events.csv")

        return df.copy()

    def load_oil_data(self) -> pd.DataFrame:
        """
        Carga y valida oil.csv.
        
        Returns:
            DataFrame con precios del petróleo
        """
        oil_path = self.config.DATA_RAW_DIR / "oil.csv"
        
        if not oil_path.exists():
            raise FileNotFoundError(
                f"oil.csv no encontrado en {self.config.DATA_RAW_DIR}"
            )

        df = pd.read_csv(oil_path, parse_dates=["date"])
        self._validate_schema(df, self.REQUIRED_OIL_COLUMNS, "oil.csv")

        return df.copy()

    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Carga todos los datasets simultáneamente.
        
        Returns:
            Tuple con (train, stores, holidays, oil)
        """
        train_df = self.load_train_data()
        stores_df = self.load_stores_data()
        holidays_df = self.load_holidays_data()
        oil_df = self.load_oil_data()

        return train_df, stores_df, holidays_df, oil_df

    def validate_minimum_weeks_per_sku(
        self,
        df: pd.DataFrame,
        min_weeks: Optional[int] = None,
    ) -> Tuple[bool, str]:
        """
        Valida que cada SKU tenga al menos min_weeks de historia.
        Implementa RF-02 (Validación de Datos).
        
        Args:
            df: DataFrame con columnas date, store_nbr, family
            min_weeks: Mínimo de semanas requeridas (default: config.MIN_WEEKS_HISTORY)
        
        Returns:
            Tuple con (es_valido, mensaje)
        """
        min_weeks = min_weeks or self.config.MIN_WEEKS_HISTORY

        df_copy = df.copy()
        df_copy["week"] = df_copy["date"].dt.to_period("W-MON")

        sku_weeks = df_copy.groupby(["store_nbr", "family"])["week"].nunique()

        skus_insuficientes = sku_weeks[sku_weeks < min_weeks]

        if len(skus_insuficientes) > 0:
            mensaje = (
                f"{len(skus_insuficientes)} SKU-tienda tienen menos de {min_weeks} semanas de historia. "
                f"Mínimo encontrado: {skus_insuficientes.min()} semanas. "
                f"SKUs afectados: {skus_insuficientes.head(5).to_dict()}"
            )
            return False, mensaje

        return True, f"Todos los SKU-tienda tienen al menos {min_weeks} semanas de historia."

    def _validate_schema(
        self,
        df: pd.DataFrame,
        expected_columns: dict,
        filename: str,
    ) -> None:
        """
        Valida que el DataFrame tenga las columnas y tipos esperados.
        
        Args:
            df: DataFrame a validar
            expected_columns: Dict de {columna: tipo_esperado}
            filename: Nombre del archivo para mensajes de error
        
        Raises:
            ValueError: Si faltan columnas o los tipos no coinciden
        """
        missing_columns = set(expected_columns.keys()) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"{filename}: Faltan columnas: {missing_columns}. "
                f"Columnas encontradas: {df.columns.tolist()}"
            )

        for col, expected_type in expected_columns.items():
            actual_type = str(df[col].dtype)
            if not self._is_compatible_type(actual_type, expected_type):
                raise ValueError(
                    f"{filename}: Columna '{col}' tiene tipo {actual_type}, "
                    f"se esperaba {expected_type}"
                )

    def _is_compatible_type(self, actual: str, expected: str) -> bool:
        """Verifica si un tipo es compatible con el esperado."""
        type_compatibility = {
            "int64": ["int64", "int32", "int16", "int8"],
            "float64": ["float64", "float32", "int64", "int32"],
            "object": ["object", "string"],
        }
        return actual in type_compatibility.get(expected, [expected])

    def _validate_no_null_critical(
        self,
        df: pd.DataFrame,
        critical_columns: list[str],
    ) -> None:
        """
        Valida que no haya nulos en columnas críticas.
        
        Args:
            df: DataFrame a validar
            critical_columns: Lista de columnas que no pueden tener nulos
        
        Raises:
            ValueError: Si hay nulos en columnas críticas
        """
        for col in critical_columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                raise ValueError(
                    f"Columna crítica '{col}' tiene {null_count} valores nulos. "
                    f"Porcentaje: {(null_count / len(df) * 100):.2f}%"
                )
