import re
from typing import Callable, List


class TextCleaner:

    @staticmethod
    def clean_name(text: str) -> str:
        """
        Limpia caracteres no deseados.
        """
        if not isinstance(text, str):
            return ""

        text = text.strip()

        # Pipeline de limpieza
        cleaning_pipeline: List[Callable[[str], str]] = [
            lambda x: re.sub(r"^\s*\b\d+[A-Z]*\d*[A-Z]*\b\s*", "", x),
            lambda x: re.sub(r"\s*\b\d+[A-Z]*\d*[A-Z]*\b\s*$", "", x),
            lambda x: re.sub(r"\b[P]\d+[A-Z]*\b", "", x),
            lambda x: re.sub(r"\s*,", ",", x),
            lambda x: re.sub(r"\s{2,}", " ", x),
            lambda x: re.sub(r"\s+[A-E]\s+\d{2}\s+\d{2}\s+[A-Z]$", "", x),
            lambda x: re.sub(r"\s+[A-Z0-9]{1,5}\s+[A-E]$", "", x),
            lambda x: re.sub(r"\s+[A-E]$", "", x),
        ]

        for clean_func in cleaning_pipeline:
            text = clean_func(text)

        return text.strip().title()

    @staticmethod
    def clean_condition(text: str) -> str:
        """
        Limpia y normaliza condiciones.
        """
        text = str(text).upper().strip()

        conditions_map = [
            (lambda x: any(word in x for word in ["AUS", "AUSENT"]), "AUSENTE"),
            (lambda x: any(word in x for word in ["ANUL", "ANULA"]), "ANULADO"),
            (
                lambda x: any(
                    word in x for word in ["NO ING", "NO ADMIT", "NOING", "NO INGRESO"]
                ),
                "NO INGRESO",
            ),
            (
                lambda x: any(word in x for word in ["ING", "ADMIT", "INGRES"]),
                "INGRESO",
            ),
        ]

        for condition_func, result in conditions_map:
            if condition_func(text):
                return result

        return text

    @staticmethod
    def parse_score(score_text: str) -> str:
        """
        Parsea puntajes con diferentes puntajes.
        """
        score_text = str(score_text).strip().upper()

        if score_text in ["AUSENTE", "ANULADO"]:
            return score_text

        try:
            processing_pipeline = [
                lambda x: x.replace(" ", ""),
                lambda x: (
                    x.replace(",", ".") + "0" if x.endswith(",") and "." not in x else x
                ),
                lambda x: x.replace(",", "") if "." in x and "," in x else x,
                lambda x: x.replace(",", ".") if "," in x else x,
            ]

            clean_text = score_text
            for process in processing_pipeline:
                clean_text = process(clean_text)

            float(clean_text)  # Validar que es numérico
            return clean_text

        except ValueError:
            return ""