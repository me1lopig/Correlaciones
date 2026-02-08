import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT

# Configuración de la página
st.set_page_config(page_title="Geotech Calc: Módulo de Elasticidad", layout="wide")

# ==========================================
# 1. LÓGICA DE CÁLCULO
# ==========================================
def calcular_modulo_elasticidad(N_spt: int):
    resultados = []
    
    # Webb (1974)
    resultados.append({"Autor": "Webb (1974)", "Aplicación": "Arenas arcillosas", 
                       "E (MPa)": 0.5 * (N_spt + 15), "Fórmula": "0.5 · (N + 15)"})
    
    # Denver (1982)
    resultados.append({"Autor": "Denver (1982)", "Aplicación": "Arenas (General)", 
                       "E (MPa)": 7 * (N_spt ** 0.5), "Fórmula": "7 · √N"})

    # Meigh y Nixon (1961)
    resultados.append({"Autor": "Meigh y Nixon (1961)", "Aplicación": "Limos y arenas limosas", 
                       "E (MPa)": 0.5 * N_spt, "Fórmula": "0.5 · N"})
    resultados.append({"Autor": "Meigh y Nixon (1961)", "Aplicación": "Arenas finas", 
                       "E (MPa)": 0.8 * N_spt, "Fórmula": "0.8 · N"})

    # Bowles (1996) - Arenas
    resultados.append({"Autor": "Bowles (1996)", "Aplicación": "Arenas (NC)", 
                       "E (MPa)": 0.5 * (N_spt + 15), "Fórmula": "0.5 · (N + 15)"})

    # Begemann (1974)
    if N_spt <= 15:
        val_beg = 1.18 * (N_spt + 6)
        form_beg = "1.18 · (N + 6)"
    else:
        val_beg = 1.18 * (N_spt + 6) + 4.0
        form_beg = "1.18 · (N + 6) + 4.0"
    resultados.append({"Autor": "Begemann (1974)", "Aplicación": "Gravas y Arenas", 
                       "E (MPa)": val_beg, "Fórmula": form_beg})

    # Bowles (1996) Gravas
    if N_spt <= 15:
        val_bg = 0.6 * (N_spt + 6)
        form_bg = "0.6 · (N + 6)"
    else:
        val_bg = 0.6 * (N_spt + 6) + 2.0
        form_bg = "0.6 · (N + 6) + 2.0"
    resultados.append({"Autor": "Bowles (1996)", "Aplicación": "Gravas", 
                       "E (MPa)": val_bg, "Fórmula": form_bg})

    # Schmertmann (1970)
    resultados.append({"Autor": "Schmertmann (1970)", "Aplicación": "Arenas", 
                       "E (MPa)": 0.8 * N_spt, "Fórmula": "0.8 · N"})
    
    # D'Appolonia (1970)
    resultados.append({"Autor": "D'Appolonia et al.", "Aplicación": "Arenas (NC)", 
                       "E (MPa)": 22.5 + 0.9 * N_spt, "Fórmula": "22.5 + 0.9 · N"})

    return pd.DataFrame(resultados)

# ==========================================
# 2. GENERADOR DE INFORME WORD
# ==========================================
def generar_docx(n_val, df_final, df_stats, fig_plotly):
    doc = Document()
    
    # Estilo base
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)

    # --- TÍTULO ---
    titulo = doc.add_heading('Informe de Estimación Geotécnica', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    p_fecha = doc.add_paragraph(f'Fecha: {pd.Timestamp.now().strftime("%d/%m/%Y")}')
    p_fecha.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph('---')

    # --- 1. DATOS DE ENTRADA ---
    doc.add_heading('1. Datos de Entrada', level=1)
    doc.add_paragraph(f'Valor N (SPT) de diseño: {n_val} golpes/pie')

    # --- 2. MÉTODOS SELECCIONADOS ---
    doc.add_heading('2. Métodos de Cálculo Seleccionados', level=1)
    
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    table.autofit = True 
    
    # Encabezados
    hdr_cells = table.rows[0].cells
    headers = ['Autor', 'Aplicación', 'Fórmula', 'E (MPa)']
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        paragraph = hdr_cells[i].paragraphs[0]
        paragraph.runs[0].bold = True
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER 
        hdr_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        
    # Filas
    for index, row in df_final.iterrows():
        row_cells = table.add_row().cells
        row_cells[0].text = str(row['Autor'])
        row_cells[1].text = str(row['Aplicación'])
        row_cells[2].text = str(row['Fórmula'])
        row_cells[3].text = f"{row['E (MPa)']:.2f}"
        
        # Centrar resultado
        row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[3].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    # --- 3. ANÁLISIS ESTADÍSTICO ---
    doc.add_heading('3. Análisis Estadístico de Resultados', level=1)
    
    if df_stats is not None:
        doc.add_paragraph('Resumen estadístico basado en los métodos seleccionados:')
        
        stat_table = doc.add_table(rows=1, cols=5)
        stat_table.style = 'Table Grid'
        stat_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        stat_table.autofit = True 
        
        # Encabezados Estadísticos
        sh_cells = stat_table.rows[0].cells
        s_headers = ['Mínimo', 'Máximo', 'Promedio', 'Mediana', 'Desv. Típica']
        
        for i, h in enumerate(s_headers):
            sh_cells[i].text = h
            p = sh_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER 
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(10) 
            sh_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        
        # Valores Estadísticos
        vals_cells = stat_table.add_row().cells
        valores = [
            f"{df_stats.iloc[0]['Mínimo']:.2f}",
            f"{df_stats.iloc[0]['Máximo']:.2f}",
            f"{df_stats.iloc[0]['Promedio']:.2f}",
            f"{df_stats.iloc[0]['Mediana']:.2f}",
            f"{df_stats.iloc[0]['Desv. Típica']:.2f}"
        ]
        
        for i, val in enumerate(valores):
            vals_cells[i].text = val
            p = vals_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].font.size = Pt(10)
            vals_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    else:
        doc.add_paragraph('No procede el cálculo de métricas estadísticas (solo 1 método seleccionado).')

    # --- 4. GRÁFICA ---
    doc.add_heading('4. Gráfica Comparativa', level=1)
    try:
        img_bytes = fig_plotly.to_image(format="png", width=800, height=500, scale=2)
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_img.add_run()
        run.add_picture(BytesIO(img_bytes), width=Inches(6.0))
    except Exception:
        doc.add_paragraph("[Gráfica no disponible. Requiere librería 'kaleido']")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==========================================
# 3. INTERFAZ STREAMLIT
# ==========================================

st.title("📊 Calculadora Geotécnica Profesional")
st.markdown("---")

with st.sidebar:
    st.header("Entrada de Datos")
    n_spt = st.number_input("Valor N (SPT) de diseño:", min_value=1, max_value=100, value=15)

df_base = calcular_modulo_elasticidad(n_spt)
df_base.insert(0, "Seleccionar", True)

st.subheader("1. Selección de Métodos")
st.info("Marque las casillas de los métodos que apliquen a su caso.")

col_config = {
    "Seleccionar": st.column_config.CheckboxColumn("Incluir", width="small"),
    "E (MPa)": st.column_config.NumberColumn("E (MPa)", format="%.2f")
}

df_editado = st.data_editor(
    df_base,
    column_config=col_config,
    disabled=["Autor", "Aplicación", "E (MPa)", "Fórmula"],
    hide_index=True,
    use_container_width=True
)

df_final = df_editado[df_editado["Seleccionar"] == True].drop(columns=["Seleccionar"])
num_seleccionados = len(df_final)

if num_seleccionados > 0:
    # --- GRÁFICA (CORREGIDA) ---
    st.subheader("2. Visualización Gráfica")
    
    # Crear una etiqueta compuesta para el eje Y que fuerce la separación de barras
    df_final["Etiqueta_Grafico"] = df_final["Autor"] + " - " + df_final["Aplicación"]
    
    fig = px.bar(
        df_final, 
        x="E (MPa)", 
        y="Etiqueta_Grafico",  # Usamos la etiqueta única
        color="Aplicación",    # Coloreamos por aplicación para diferenciar visualmente
        orientation='h',
        text_auto='.1f',
        title=f"Módulo de Elasticidad (N={n_spt})",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    
    # Ordenar las barras para que se vean mejor (opcional, por valor de E)
    # fig.update_layout(yaxis={'categoryorder':'total ascending'}) 
    
    # Limpiar el título del eje Y para que no diga "Etiqueta_Grafico"
    fig.update_layout(yaxis_title="")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- ESTADÍSTICAS ---
    st.subheader("3. Análisis Estadístico")
    
    df_stats = None
    
    if num_seleccionados >= 2:
        stats_data = {
            "Mínimo": [df_final["E (MPa)"].min()],
            "Máximo": [df_final["E (MPa)"].max()],
            "Promedio": [df_final["E (MPa)"].mean()],
            "Mediana": [df_final["E (MPa)"].median()],
            "Desv. Típica": [df_final["E (MPa)"].std()]
        }
        df_stats = pd.DataFrame(stats_data)
        
        st.dataframe(
            df_stats.style.format("{:.2f}").set_properties(**{'text-align': 'center'}),
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning(f"⚠️ Solo se ha seleccionado 1 método. No se pueden calcular métricas de dispersión.")

    # REPORTE
    st.markdown("---")
    st.write("📥 **Generar Informe**")
    
    docx_file = generar_docx(n_spt, df_final, df_stats, fig)
    
    st.download_button(
        label="📄 Descargar Informe Word (.docx)",
        data=docx_file,
        file_name=f"Informe_Geotecnico_N{n_spt}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

else:
    st.error("Por favor, seleccione al menos un método para continuar.")