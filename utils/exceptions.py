class PDFExtractorError(Exception):
    """Excepción base para errores del extractor"""
    pass


class PDFProcessingError(PDFExtractorError):
    """Error durante el procesamiento del PDF"""
    pass


class PatternMatchError(PDFExtractorError):
    """Error cuando los patrones no coinciden"""
    pass


class MetadataExtractionError(PDFExtractorError):
    """Error durante la extracción de metadata"""
    pass