import re
from typing import List, Tuple, Pattern, Callable


class PatternManager:
    """Administra todos los patrones de extracción para procesamiento de PDFs"""

    @staticmethod
    def get_extraction_patterns() -> List[Tuple[str, Pattern, Callable]]:
        """
        Obtiene los patrones de extracción autodetectores ordenados por prioridad.
        """
        return [
            # PATRÓN 1: Formato completo con orden, dni, nombre, códigos y puntaje
            (
                "formato_completo",
                re.compile(
                    r"^\s*(\d+)\s+(\d{6,9})\s+(.+?)\s+([A-E])\s+(\d{2})\s+(\d{2})\s+([A-Z])\s+([\-—–]?\d{1,4}(?:[,.]\d{2,5})?)\s+(?:\d+\s+)?(?:\d+\s+)?(INGRESO|NO INGRESO|AUSENTE|ANULADO)$",
                    re.IGNORECASE,
                ),
                lambda m: (m.group(2), m.group(3), m.group(8), m.group(9)),
            ),
            # PATRÓN 2: DNI al inicio con nombre y condición al final
            (
                "dni_inicio",
                re.compile(
                    r"^\s*(?:\d+\s+)?(\d{6,9})\s+(.+?)\s*(?:([\-—–]?\d{1,4}(?:[,.]\d{2,5})*(?:\.\d{2,5})?|\b(?:AUSENTE|ANULADO)\b)\s*)?(?:\s+\d+)?(?:\s+\d+)?\s*(INGRESO|NO INGRESO|AUSENTE|ANULADO)$",
                    re.IGNORECASE,
                ),
                lambda m: (
                    m.group(1),
                    m.group(2),
                    m.group(3) or "",
                    m.group(4),
                ),
            ),
            # PATRÓN 3: Formato con múltiples códigos intermedios
            (
                "codigos_intermedios",
                re.compile(
                    r"^\s*\d+\s+(?:\d+\s+)?(?:[A-Z0-9]+\s+)?(\d{6,9})\s+(.+?)\s+(?:[A-Z0-9]{1,5}\s+)?[A-E]\s+([\-—–]?\d{1,4}[,.]\d{2,5})\s+(INGRESO|NO INGRESO|AUSENTE|ANULADO)$",
                    re.IGNORECASE,
                ),
                lambda m: (m.group(1), m.group(2), m.group(3), m.group(4)),
            ),
            # PATRÓN 4: Orden y puntaje al inicio, DNI después
            (
                "puntaje_inicio",
                re.compile(
                    r"^\s*(\d+)\s+([\-—–]?\d{1,4}[,.]\d{2,5})\s+(\d{6,9})\s+(.+?)\s+(?:\d+)\s+(?:\d+)\s+(INGRESO|NO INGRESO|AUSENTE|ANULADO)$",
                    re.IGNORECASE,
                ),
                lambda m: (m.group(3), m.group(4), m.group(2), m.group(5)),
            ),
            # PATRÓN 5: Solo DNI, nombre y condición (ausentes/anulados)
            (
                "simple_ausente",
                re.compile(
                    r"^\s*(?:\d+\s+)?(\d{6,9})\s+(.+?)(?:\s+[\-—–]?0\.0+)?\s+(AUSENTE|ANULADO)$",
                    re.IGNORECASE,
                ),
                lambda m: (m.group(1), m.group(2), m.group(3), m.group(3)),
            ),
            # PATRÓN 6: Formato flexible con puntaje decimal
            (
                "puntaje_decimal",
                re.compile(
                    r"^\s*(?:\d+\s+)?(\d{6,9})\s+(.+?)\s+([\-—–]?\d{1,4}[,.]\d{1,5})\s+(INGRESO|NO INGRESO)$",
                    re.IGNORECASE,
                ),
                lambda m: (m.group(1), m.group(2), m.group(3), m.group(4)),
            ),
            # PATRÓN 7: Formato con puntaje entero
            (
                "puntaje_entero",
                re.compile(
                    r"^\s*(?:\d+\s+)?(\d{6,9})\s+(.+?)\s+([\-—–]?\d{1,4})\s+(INGRESO|NO INGRESO)$",
                    re.IGNORECASE,
                ),
                lambda m: (m.group(1), m.group(2), m.group(3), m.group(4)),
            ),
        ]

    @staticmethod
    def extract_year_period(text: str) -> Tuple[str, str]:
        """
        Extrae Año y Periodo de manera completa.
        """
        text_upper = text.upper()
        patterns = [
            # EXAMEN DE ADMISION 2016 - II
            (
                r"EXAMEN DE ADMISI[ÓO]N\s*(20\d{2})\s*[\-—–]?\s*(I{1,3}|IV|V|VI|VII|VIII|IX|X)",
                lambda m: (m.group(1), m.group(2)),
            ),
            # ADMISION 2016
            (
                r"(?:ADMISI[ÓO]N|INGRESO|RESULTADOS|PROCESO DE ADMISI[ÓO]N)\s*[:\-]?\s*(20\d{2})\s*[\-—–]?\s*(I{1,3}|IV|V|VI|VII|VIII|IX|X)?",
                lambda m: (m.group(1), m.group(2) or ""),
            ),
            (
                r"(20\d{2})[\s\-—–]+(I{1,3}|IV|V|VI|VII|VIII|IX|X)",
                lambda m: (m.group(1), m.group(2)),
            ),
            (r"ADMISI[ÓO]N\s+(20\d{2})", lambda m: (m.group(1), "")),
            # Repartición de resultados 2023-II
            (
                r"REPORTE DE RESULTADOS DE INGRESO\s*(20\d{2})\s*[\-—–]?\s*(I{1,3}|IV|V|VI|VII|VIII|IX|X)",
                lambda m: (m.group(1), m.group(2)),
            ),
            # CICLO II - 2017 (captura periodo y luego año)
            (
                r"CICLO\s*(I{1,3}|IV|V|VI|VII|VIII|IX|X)\s*[\-—–]?\s*(20\d{2})",
                lambda m: (m.group(2), m.group(1)),
            ),
            # 2017 - CICLO II (captura año y luego periodo)
            (
                r"(20\d{2})\s*[\-—–]?\s*CICLO\s*(I{1,3}|IV|V|VI|VII|VIII|IX|X)",
                lambda m: (m.group(1), m.group(2)),
            ),
        ]

        for pattern, extractor in patterns:
            if match := re.search(pattern, text_upper):
                year, period = extractor(match)
                if year and len(year) == 2:
                    year = "20" + year
                return year, period

        return "", ""