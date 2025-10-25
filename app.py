import streamlit as st
import streamlit.components.v1 as components
import base64
from pathlib import Path

from components.gallery_component import create_gallery_html
from extractor.extractor import PDFExtractor
from utils.exceptions import PDFProcessingError
import polars as pl
import pandas as pd


st.set_page_config(
    page_title="Extractor de PDFs de Admisión",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("Extractor de PDFs de Admisión")
st.write(
    "Bienvenido al **Extractor de Admisión v2025**. Este sistema analiza la **primera página** de los PDF de admisión y extrae automáticamente los datos de todas las paginas del PDF según los **5 patrones adaptados por el sistema**."
)

st.divider()

def img_to_base64(img_path: str) -> str:
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError:
        st.warning(f"Imagen no encontrada: {img_path}")
        return ""

@st.dialog("Patrones soportados por el sistema")
def mostrar_patrones():
    tipos = ["Tipo I", "Tipo II", "Tipo III", "Tipo IV", "Tipo V"]
    imagenes = [
        "images/tipo_I.png",
        "images/tipo_II.png",
        "images/tipo_III.png",
        "images/tipo_IV.png",
        "images/tipo_V.png",
    ]

    st.write("A continuación se muestran los **5 tipos de patrones** reconocidos por el sistema:")
    st.info("Solo se procesarán correctamente los PDF cuya primera página coincida con uno de los patrones.")

    html_content = create_gallery_html(tipos, imagenes, img_to_base64)
    components.html(html_content, height=700, scrolling=False)

st.markdown("Antes de procesar un PDF, revisa los patrones compatibles:")

if st.button("Ver patrones válidos", icon=':material/file_open:'):
    mostrar_patrones()

st.divider()

st.subheader("Cargar archivo PDF para procesar")

uploaded_file = st.file_uploader("Selecciona tu archivo de admisión", type=["pdf"])

if uploaded_file:
    st.success(f"Archivo cargado correctamente: `{uploaded_file.name}`", icon=':material/check_circle:')

    if st.button("Procesar PDF", icon=':material/play_arrow:'):
        try:
            pdf_bytes = uploaded_file.read()
            
            progress_bar = st.progress(0, text="Iniciando procesamiento...")
            status_text = st.empty()
            
            def update_progress(current, total, records):
                percentage = int((current / total) * 100)
                progress_bar.progress(percentage, text=f"Procesando página {current}/{total}")
                status_text.info(f"Registros acumulados: **{records}**")
            
            with st.spinner("Inicializando extractor..."):
                extractor = PDFExtractor(pdf_bytes)
            
            extractor.process_pdf(progress_callback=update_progress)
            
            progress_bar.progress(100, text="Procesamiento completado")
            
            year = extractor.year if extractor.year else "desconocido"
            period = extractor.period if extractor.period else "desconocido"
            
            with st.spinner("Generando archivo Excel..."):
                excel_buffer = extractor.export_to_excel()
            
            progress_bar.empty()
            status_text.empty()
            
            st.success(
                f"Procesamiento completado exitosamente\n\n"
                f"**Registros extraídos:** {len(extractor.data)}\n\n"
                f"**Año:** {year} | **Periodo:** {period}",
                icon=':material/check_circle:'
            )
            
            filename = extractor.get_filename()
            
            st.download_button(
                label="Descargar resultado en Excel",
                data=excel_buffer,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            with st.expander("Vista previa de los datos extraídos", expanded=False):
                excel_buffer.seek(0) 
                df_preview = pd.read_excel(excel_buffer, engine='openpyxl')
                
                st.dataframe(df_preview.head(20), use_container_width=True)
        
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total registros", len(df_preview))
                
                with col2:
                    ingresos = (df_preview['CONDICION'] == 'INGRESO').sum()
                    st.metric("Ingresos", ingresos)
                
                with col3:
                    no_ingresos = (df_preview['CONDICION'] == 'NO INGRESO').sum()
                    st.metric("No Ingresos", no_ingresos)
                
                with col4:
                    ausentes = df_preview['CONDICION'].isin(['AUSENTE', 'ANULADO']).sum()
                    st.metric("Ausentes/Anulados", ausentes)

        except PDFProcessingError as e:
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
            st.error(f"Error de procesamiento: {e}", icon=':material/error:')
            
        except Exception as e:
            if 'progress_bar' in locals():
                progress_bar.empty()
            if 'status_text' in locals():
                status_text.empty()
            st.error(f"{e}", icon=':material/error:')

else:
    st.info("Sube un archivo PDF para comenzar el análisis.", icon=':material/upload:')

st.divider()

st.write('Desarrollado por Anderson Talla')