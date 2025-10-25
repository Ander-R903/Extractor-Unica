import re
from typing import Optional


class MetadataParser:
    """Clase de utilidad para parsear metadata del texto del PDF"""

    @staticmethod
    def extract_modality(line: str) -> str:
        """Extrae la Modalidad de Ingreso de una línea específica."""
        if match := re.match(r"MODALIDAD\s*[:\-]?\s*([^\n]+)", line.upper()):
            return match.group(1).strip().upper()
        return ""

    @staticmethod
    def extract_faculty(line: str) -> str:
        """Extrae el nombre de la Facultad de una línea específica."""
        if match := re.match(r"FACULTAD\s*[:\-]?\s*([^\n]+)", line.upper()):
            return match.group(1).strip().upper()
        return ""

    @staticmethod
    def extract_career(line: str) -> str:
        """Extrae el nombre de la Carrera de una línea específica."""
        if match := re.match(
            r"CARRERA(?: PROFESIONAL)?\s*[:\-]?\s*([^\n]+)", line.upper()
        ):
            career_name = match.group(1).strip().upper()
            return re.sub(r"^\d+\s*", "", career_name).strip()
        return ""

    @staticmethod
    def extract_school(line: str) -> str:
        """Extrae el nombre de la Escuela de una línea específica."""
        if match := re.match(
            r"ESCUELA\s*[:\-]?\s*(\d{2})?\s*([A-ZÁÉÍÓÚÑ\s\-\.]+)", line.upper()
        ):
            school_name = match.group(2).strip().upper()
            return re.sub(r"^\d+\s*", "", school_name).strip()
        return ""