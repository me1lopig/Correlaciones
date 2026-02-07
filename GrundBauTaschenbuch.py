import streamlit as st
import pandas as pd
import io
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Ficha Geotécnica", page_icon="🏗️", layout="wide")

# --- ESTILOS CSS PROFESIONALES ---
st.markdown("""
<style>
    /* Estilo para la tabla de datos principal */
    .dataframe {
        font-size: 14px !important;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Encabezados de métricas */
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    /* Título del suelo */
    .soil-title {
        color: #2c3e50;
        font-size: 2.5em;
        font-weight: 700;
        margin-bottom: 0px;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    .category-header {
        color: #3498db;
        font-size: 1.2em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data
def load_and_process_data():
    csv_data = """Tipo de suelo,Granulometria_<0.06,Granulometria_<2.0,LL,LP,IP,Gamma_aparente,Gamma_sumergido,Humedad,E_mod,Phi,Cohesion,Phi_res,Permeabilidad
Grava,<5,<60,--,--,--,16,9.5,5,40,34,--,32,0.21
,,,--,--,--,19,10.5,2,90,42,--,35,0.011
Grava arenosa con pocos finos,<5,<60,--,--,--,21,11.5,7,40,35,--,32,0.011
,,,--,--,--,23,13.5,3,110,45,10,35,1.1e-06
Grava arenosa con finos limosos,<60,<60,20,16,4,21,11.5,9,40,35,0,32,1.1e-05
,,45,45,25,25,24,14.5,3,115,43,30,35,1.1e-08
Mezcla de gravas y arenas,20,<60,20,16,4,20,10.5,13,15,28,5,22,1.1e-08
,,50,50,25,30,22.5,13,5,40,35,--,30,1.1e-11
Arena uniforme Fina,<5,100,--,--,--,16,9.5,22,15,32,--,30,0.00021
,,,--,--,--,19,11,8,30,40,--,32,1.1e-05
Arena uniforme gruesa,<5,100,--,--,--,16,9.5,16,24,34,--,30,0.0051
,,,--,--,--,19,11,6,70,42,--,34,0.00021
Arena bien graduada,<5,60,--,--,--,18,10,11,20,33,--,32,5.1e-06
,,,--,--,--,21,12,5,60,41,--,34,2.1e-05
Arena con finos (no altera est.),8,>60,20,16,4,19,10.5,15,15,32,10,30,1.1e-05
,,45,45,25,25,22.5,13,4,50,40,0,32,1.1e-07
Arena con finos (altera est.),20,>60,20,16,4,18,9,20,5,25,50,22,1.1e-07
,,50,50,30,30,21.5,11,8,25,32,10,30,1.1e-10
Limo poco plastico,>50,>80,25,20,4,17.5,9.5,28,4,28,20,25,1.1e-05
,,35,35,28,11,21,11,15,11,35,5,30,1.1e-08
Limo de plasticidad media/alta,>80,>100,35,22,7,17,8.5,35,3,25,30,22,2.1e-06
,,50,50,25,20,20,10.5,20,7,33,10,29,1.1e-09
Arcilla de baja plasticidad,>80,100,25,15,7,19,9.5,28,2,24,60,20,1.1e-07
,,35,35,22,16,22,12,14,5,32,15,28,2.1e-09
Arcilla de plasticidad media,>90,100,40,18,16,18,8.5,38,1,20,80,10,5.1e-08
,,50,50,25,28,21,11,18,3,30,20,20,1.1e-10
Arcilla de alta plasticidad,100,100,60,20,33,16.5,7,55,0.5,17,100,6,1.1e-09
,,85,85,35,55,20,10,20,2,27,30,15,1.1e-11
Limo o arcilla orgánica,>80,100,45,30,10,15.5,5.5,60,0.5,20,70,15,1.1e-09
,,70,70,14,30,19,9,30,2,26,20,22,1.1e-11
Turba,--,--,--,--,--,10.4,0.4,800,0.3,25,15,--,1.1e-05
,,,--,--,--,13,3,100,0.8,30,5,--,1.1e-08
Fango,--,--,100,30,50,12.5,2.5,200,0.4,22,20,--,1.1e-07
,,250,250,80,170,16,6,50,1.5,28,5,--,1.1e-09"""
    
    df = pd.read_csv(io.StringIO(csv_data))
    df['Tipo de suelo'] = df['Tipo de suelo'].replace('', np.nan).ffill()
    
    # Columnas numéricas a procesar
    numeric_cols = ['LL', 'LP', 'IP', 'Gamma_aparente', 'Gamma_sumergido', 
                    'Humedad', 'E_mod', 'Phi', 'Cohesion', 'Phi_res', 'Permeabilidad']
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Función para formatear rango "min - max"
    def format_range(series):
        # Eliminamos NaNs
        vals = series.dropna().values
        if len(vals) == 0:
            return "--"
        
        vmin = np.min(vals)
        vmax = np.max(vals)
        
        # Caso especial: Permeabilidad (Notación científica)
        if series.name == 'Permeabilidad':
            # Ordenar para que siempre sea min a max (ej 1e-9 a 1e-7)
            # Nota: en geotecnia a veces se da rango inverso k_h vs k_v, pero asumiremos rango magnitud
            r_min = min(vmin, vmax)
            r_max = max(vmin, vmax)
            if r_min == r_max:
                return f"{r_min:.1e}"
            return f"{r_min:.1e} ... {r_max:.1e}"
            
        # Caso normal
        if vmin == vmax:
            return f"{vmin:g}"
        else:
            return f"{vmin:g} - {vmax:g}"

    # Agrupamos por suelo y aplicamos el formateo
    df_grouped = df.groupby('Tipo de suelo')[numeric_cols].agg(format_range).reset_index()
    
    # Recuperamos columnas de texto (Granulometría) tomando el primer valor no nulo
    df_text = df.groupby('Tipo de suelo')[['Granulometria_<0.06', 'Granulometria_<2.0']].first().reset_index()
    
    # Merge final
    df_final = pd.merge(df_text, df_grouped, on='Tipo de suelo')
    
    return df_final, df # Devolvemos la formateada y la raw

df_formatted, df_raw = load_and_process_data()

# --- SIDEBAR ---
st.sidebar.header("🔍 Filtros")
selected_soil = st.sidebar.selectbox("Seleccionar Suelo", df_formatted['Tipo de suelo'].unique())

# --- MAIN DISPLAY ---
# Filtramos la fila única
row = df_formatted[df_formatted['Tipo de suelo'] == selected_soil].iloc[0]

st.markdown(f"<div class='soil-title'>{selected_soil}</div>", unsafe_allow_html=True)
st.markdown("Valores característicos (Rango Min - Max)")

# --- VISUALIZACIÓN EN UNA SOLA FILA AGRUPADA (ESTILO DASHBOARD) ---

# Grupo 1: Identificación y Estado
st.markdown("<div class='category-header'>1. Identificación y Estado</div>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Granulometría <0.06mm", row['Granulometria_<0.06'] + "%" if "<" not in str(row['Granulometria_<0.06']) else row['Granulometria_<0.06'])
c2.metric("Límite Líquido (LL)", row['LL'], help="Porcentaje de humedad")
c3.metric("Índice Plástico (IP)", row['IP'])
c4.metric("Humedad Natural", row['Humedad'] + "%")
c5.metric("Peso Específico (γ)", row['Gamma_aparente'] + " kN/m³")

# Grupo 2: Resistencia y Deformación
st.markdown("<div class='category-header'>2. Resistencia y Deformación</div>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ángulo Fricción (φ')", row['Phi'] + "°")
c2.metric("Cohesión (c')", row['Cohesion'] + " kPa")
c3.metric("Módulo Young (E)", row['E_mod'] + " MPa")
c4.metric("Fricción Residual", row['Phi_res'] + "°")

# Grupo 3: Hidráulica
st.markdown("<div class='category-header'>3. Hidráulica</div>", unsafe_allow_html=True)
k_val = row['Permeabilidad'].replace("e", "x10^") # Formato visual bonito
st.metric("Permeabilidad (k)", k_val + " m/s")

st.divider()

# --- TABLA DE UNA SOLA FILA (SOLICITUD EXPLICITA) ---
st.subheader("📋 Ficha Resumen (Fila Única)")
st.caption("Esta tabla contiene todos los datos consolidados en una sola fila para copiar o reportar.")

# Renombramos columnas para que sean más legibles en la tabla
display_df = df_formatted[df_formatted['Tipo de suelo'] == selected_soil].copy()
display_df.columns = [
    "Suelo", "Finos (%)", "Arena (%)", "LL", "LP", "IP", 
    "γ (kN/m³)", "γ sum", "w (%)", "E (MPa)", "φ' (°)", "c' (kPa)", "φ res", "k (m/s)"
]

# Mostramos la tabla interactiva pero forzando a que no use index
st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Suelo": st.column_config.TextColumn("Tipo de Suelo", width="medium"),
        "k (m/s)": st.column_config.TextColumn("Permeabilidad", help="Escala logarítmica", width="medium"),
    }
)

# --- BOTÓN DE DESCARGA ---
csv = display_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="💾 Descargar esta Ficha (CSV)",
    data=csv,
    file_name=f'{selected_soil}_propiedades.csv',
    mime='text/csv',
)