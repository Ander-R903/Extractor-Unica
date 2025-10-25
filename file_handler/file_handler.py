import io
import pandas as pd
from typing import Dict, List, Union
from pathlib import Path
from file_handler.clean_file import DataFrameCleaner
import polars as pl


class FileHandler:
    @staticmethod
    def prepare_dataframe(data: List[Dict[str, str]]) -> pd.DataFrame:
        df = pd.DataFrame(data)

        required_cols = [
            "dni",
            "apellidos_nombres",
            "puntaje",
            "condicion",
            "anio",
            "periodo",
            "modalidad_ingreso",
            "carrera",
            "orden_original",
        ]

        # Asegurar existencia de columnas
        for col_name in required_cols:
            if col_name not in df.columns:
                df[col_name] = ""

        # Limpiar y ordenar
        df = df.sort_values(by="orden_original", ascending=True).reset_index(drop=True)

        # Limpiar valores 
        for col in df.columns:
            if col != "orden_original":
                df[col] = df[col].astype(str).replace("None", "").fillna("")

        return df

    @staticmethod
    def determine_columns(df: pd.DataFrame) -> List[str]:
        """
        Determina qué columnas incluir dinámicamente basado en contenido.
        """
        columnas_base = [
            "dni",
            "apellidos_nombres",
            "puntaje",
            "condicion",
            "anio",
            "periodo",
        ]

        columnas_opcionales = ["modalidad_ingreso", "carrera"]
        columnas_con_datos = [
            col for col in columnas_opcionales if (df[col].astype(str) != "").any()
        ]

        return columnas_base + columnas_con_datos

    @staticmethod
    def export_to_excel(
        data: List[Dict[str, str]],
        output_path: Union[str, Path] = None,
        anio: str = "",
        periodo: str = "",
    ) -> Union[Path, io.BytesIO]:
        """
        Exporta datos a Excel con columnas dinámicas.
        """
        if not data:
            raise ValueError("No hay datos para exportar")
        
        df = FileHandler.prepare_dataframe(data)
        columns = FileHandler.determine_columns(df)
        df = df[columns]

        pl_df = pl.from_pandas(df)

        pl_df = DataFrameCleaner.clean_dataframe(pl_df)

        df_clean = pl_df.to_pandas()

        if output_path is None:
            buffer = io.BytesIO()
            df_clean.to_excel(buffer, index=False, engine="openpyxl")
            buffer.seek(0)
            return buffer

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_excel(output_path, index=False, engine="openpyxl")
        return output_path


    @staticmethod
    def generate_filename(anio: str = "", periodo: str = "") -> str:
        """
        Formato : Año y periodo
        """
        return f"Resultados-UNICA-{anio or 'SIN_ANIO'}-{periodo or 'X'}.xlsx"