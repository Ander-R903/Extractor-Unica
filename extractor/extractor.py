import pdfplumber
import io
from typing import List, Dict, Optional, Callable, Union
from pathlib import Path

from utils.text_cleaner import TextCleaner
from extractor.metadata_parser import MetadataParser
from file_handler.file_handler import FileHandler
from utils.exceptions import PDFProcessingError, PatternMatchError
from utils.patterns import PatternManager


class PDFExtractor:
    def __init__(self, pdf_source: Union[bytes, io.BytesIO, str, Path]) -> None:
        self.pdf_source = self._prepare_pdf_source(pdf_source)
        self.data: List[Dict[str, str]] = []
        self._reset_metadata()
        self.order = 1

    def _prepare_pdf_source(self, source: Union[bytes, io.BytesIO, str, Path]) -> io.BytesIO:
        if isinstance(source, bytes):
            return io.BytesIO(source)
        elif isinstance(source, io.BytesIO):
            return source
        elif isinstance(source, (str, Path)):
            with open(source, 'rb') as f:
                return io.BytesIO(f.read())
        else:
            raise ValueError(f"Tipo de fuente no soportado: {type(source)}")

    def _reset_metadata(self) -> None:
        self.modality = ""
        self.career = ""
        self.school = ""
        self.year = ""
        self.period = ""

    def extract_metadata(self, text: str) -> None:
        """
        Extrae toda la metadata de la página actual.
        """
        text_upper = text.upper()
        lines = text_upper.split("\n")

        # Extraer Año y Periodo
        self.year, self.period = PatternManager.extract_year_period(text_upper)

        # Reset metadata de página
        self.career = ""
        self.school = ""
        self.modality = ""

        # Extractores de metadata por línea
        extractors = [
            (
                lambda line: not self.modality,
                MetadataParser.extract_modality,
                "modality",
            ),
            (
                lambda line: not self.career,
                MetadataParser.extract_career,
                "career",
            ),
            (
                lambda line: not self.school and not self.career,
                MetadataParser.extract_school,
                "school",
            ),
        ]

        for line in lines:
            for condition, extractor_func, attr_name in extractors:
                if condition(line):
                    result = extractor_func(line)
                    if result:
                        setattr(self, attr_name, result)
        
        # Si solo hay escuela pero no carrera, usar escuela como carrera
        if self.school and not self.career:
            self.career = self.school
            self.school = ""

    def process_line(self, line: str) -> Optional[Dict[str, str]]:
        """
        Procesa una línea de resultados usando patrones priorizados.
        """
        line = line.strip()
        if not line:
            return None

        for pattern_name, pattern, extractor in PatternManager.get_extraction_patterns():
            if match := pattern.match(line):
                try:
                    dni, name, score, condition = extractor(match)

                    return {
                        "dni": str(dni),
                        "apellidos_nombres": TextCleaner.clean_name(name),
                        "puntaje": TextCleaner.parse_score(score),
                        "condicion": TextCleaner.clean_condition(condition),
                    }
                except Exception as e:
                    raise PatternMatchError(f"Error processing pattern {pattern_name}: {e}")

        return None

    def _add_metadata(self, record: Dict[str, str]) -> Dict[str, str]:
        """
        Agrega metadata persistente a un registro.
        """
        metadata_fields = {
            "modalidad_ingreso": self.modality,
            "carrera": self.career,  #Usar la carrera obligatorio
            "anio": str(self.year),
            "periodo": str(self.period),
            "orden_original": self.order,
        }

        return {**record, **metadata_fields}

    def process_page(self, page) -> List[Dict[str, str]]:
        """
        Procesa una página completa.
        """
        text = page.extract_text()
        if not text:
            return []

        self.extract_metadata(text)
        records = []

        for line in text.split("\n"):
            if line_result := self.process_line(line):
                complete_record = self._add_metadata(line_result)
                records.append(complete_record)
                self.order += 1

        return records

    def process_pdf(self, progress_callback: Optional[Callable[[int, int, int], None]] = None) -> None:
        """
        Procesa el PDF completo con callback de progreso opcional.
        
        Args:
            progress_callback: Función opcional que recibe (current_page, total_pages, total_records)
                             Se llama después de procesar cada página.
        """
        try:
            with pdfplumber.open(self.pdf_source) as pdf:
                total_pages = len(pdf.pages)

                for idx, page in enumerate(pdf.pages, 1):
                    records = self.process_page(page)
                    self.data.extend(records)
                    
                    if progress_callback:
                        progress_callback(idx, total_pages, len(self.data))

        except Exception as e:
            raise PDFProcessingError(f"Error processing PDF: {e}")

    def export_to_excel(self, output_path: Union[str, Path] = None) -> Union[Path, io.BytesIO]:
        """
        Exporta datos a Excel.
        """
        if not self.data:
            raise ValueError("No hay datos para exportar")

        try:
            return FileHandler.export_to_excel(
                self.data, 
                output_path,
                self.year,
                self.period
            )
        except Exception as e:
            raise PDFProcessingError(f"Error exporting to Excel: {e}")

    def get_filename(self) -> str:
        """Genera el nombre del archivo de salida."""
        return FileHandler.generate_filename(self.year, self.period)