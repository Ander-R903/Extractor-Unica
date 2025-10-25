# Extractor de PDFs de Admisión UNSLG

Sistema automatizado para procesamiento y extracción de datos de archivos PDF de admisión universitaria.

## Demo

Prueba el sistema en vivo: **https://extractor-unica.streamlit.app/**

## Características

- Reconocimiento automático de 5 patrones diferentes de PDF
- Extracción masiva de datos de todas las páginas
- Exportación directa a Excel con nomenclatura estandarizada
- Interfaz intuitiva con progreso en tiempo real
- Validación robusta y manejo de errores

## Estructura del Proyecto
```

├── app.py                      # Aplicación principal
├── components/                 # Componentes de UI
│   └── gallery_component.py
├── extractor/                  # Motor de extracción
│   ├── extractor.py
│   └── metadata_parser.py
├── file_handler/               # Gestión de archivos
│   ├── file_handler.py
│   └── clean_file.py
└── utils/                      # Utilidades
    ├── patterns.py
    ├── text_cleaner.py
    ├── exceptions.py
    └── mapeo.py
```

## Instalación
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Uso

1. Acceder a la aplicación
2. Revisar los patrones soportados
3. Cargar el PDF de admisión
4. Procesar y descargar el Excel resultante

## Patrones Soportados

El sistema reconoce 5 tipos de formatos en la primera página:
- Tipo I al V con diferentes estructuras de tabla y layout

## Salida

Archivo Excel con formato: `ADMISION_{AÑO}_{PERIODO}.xlsx`

**Campos extraídos:**
- Datos del postulante
- Condición (INGRESO / NO INGRESO / AUSENTE / ANULADO)
- Información académica
- Metadata del proceso

## Tecnologías

- Streamlit
- Polars / Pandas
- OpenPyXL

## Autor

**Anderson Talla** - Versión 2025