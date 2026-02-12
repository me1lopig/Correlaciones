import streamlit as st
import pandas as pd
import io
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Propiedades de Materiales",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS AVANZADOS ---
st.markdown("""
<style>
    /* Fuente principal */
    .main {
        background-color: #fcfcfc;
    }
    
    /* Tarjetas de Métricas */
    .metric-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        height: 100%;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        border-color: #3498db;
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #2c3e50;
        font-size: 1.6rem;
        font-weight: 700;
        font-family: 'Segoe UI', monospace;
    }
    .metric-unit {
        font-size: 0.9rem;
        color: #95a5a6;
        font-weight: normal;
    }
    
    /* Título Principal */
    .soil-header {
        font-family: 'Helvetica Neue', sans-serif;
        color: #1a252f;
        font-size: 2.2rem;
        font-weight: 800;
        padding-bottom: 10px;
        border-bottom: 2px solid #3498db;
        margin-bottom: 25px;
    }
    
    /* Ajustes de Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f1f2f6;
        border-radius: 5px 5px 0 0;
        border: 1px solid #e0e0e0;
        padding-left: 20px;
        padding-right: 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: white;
        border-bottom: 2px solid #3498db;
        color: #3498db;
        font-weight: bold;
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
    
    numeric_cols = ['LL', 'LP', 'IP', 'Gamma_aparente', 'Gamma_sumergido', 
                    'Humedad', 'E_mod', 'Phi', 'Cohesion', 'Phi_res', 'Permeabilidad']
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    def format_range(series):
        vals = series.dropna().values
        if len(vals) == 0: return "--"
        vmin, vmax = np.min(vals), np.max(vals)
        
        if series.name == 'Permeabilidad':
            r_min, r_max = min(vmin, vmax), max(vmin, vmax)
            if r_min == r_max: return f"{r_min:.1e}"
            return f"{r_min:.1e} ... {r_max:.1e}"
            
        if vmin == vmax: return f"{vmin:g}"
        return f"{vmin:g} - {vmax:g}"

    df_grouped = df.groupby('Tipo de suelo')[numeric_cols].agg(format_range).reset_index()
    df_text = df.groupby('Tipo de suelo')[['Granulometria_<0.06', 'Granulometria_<2.0']].first().reset_index()
    df_final = pd.merge(df_text, df_grouped, on='Tipo de suelo')
    
    return df_final

# Función auxiliar para renderizar tarjetas HTML
def card(label, value, unit=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value} <span class="metric-unit">{unit}</span></div>
    </div>
    """, unsafe_allow_html=True)

df_formatted = load_and_process_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏝️ Tipo de suelo")
    selected_soil = st.selectbox("Seleccionar Material", df_formatted['Tipo de suelo'].unique())
    st.markdown("---")
    st.info("Base de datos referencial basada en el *Grundbau-Taschenbuch*. Los valores son indicativos para pre-dimensionamiento.")

# --- MAIN DISPLAY ---
row = df_formatted[df_formatted['Tipo de suelo'] == selected_soil].iloc[0]

# Título
st.markdown(f"<div class='soil-header'>{selected_soil}</div>", unsafe_allow_html=True)

# Tabs principales
tab1, tab2, tab3 = st.tabs(["📊 Identificación y Estado", "⚙️ Parámetros Mecánicos", "💧 Permeabilidad"])

with tab1:
    col_metrics, col_chart = st.columns([2, 1])
    
    with col_metrics:
        st.subheader("Parámetros Físicos")
        c1, c2, c3 = st.columns(3)
        with c1: card("Peso Específico (γ)", row['Gamma_aparente'], "kN/m³")
        with c2: card("Humedad (w)", row['Humedad'], "%")
        with c3: card("Índice Plástico (IP)", row['IP'], "%")
        
        st.write("") # Espaciador
        
        c4, c5, c6 = st.columns(3)
        with c4: card("Límite Líquido", row['LL'], "%")
        with c5: card("Límite Plástico", row['LP'], "%")
        with c6: card("Finos (<0.06mm)", row['Granulometria_<0.06'], "%")

    with col_chart:
        # Gráfico estimativo de composición (Parsing simple para visualización)
        try:
            finos_str = str(row['Granulometria_<0.06']).replace('<', '').replace('>', '')
            finos_val = float(finos_str)
            gruesos_val = 100 - finos_val
            
            fig = go.Figure(data=[go.Pie(
                labels=['Finos (Limo/Arcilla)', 'Gruesos (Arena/Grava)'],
                values=[finos_val, gruesos_val],
                hole=.6,
                marker=dict(colors=['#3498db', '#ecf0f1'])
            )])
            fig.update_layout(
                showlegend=False, 
                height=250, 
                margin=dict(l=0, r=0, t=30, b=0),
                annotations=[dict(text=f'{finos_val}%', x=0.5, y=0.5, font_size=20, showarrow=False)],
                title="Contenido de Finos (aprox)"
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        except:
            st.info("Gráfico de composición no disponible para este rango.")

with tab2:
    st.subheader("Parámetros de Diseño")
    
    # Fila 1: Resistencia
    c1, c2 = st.columns(2)
    with c1: card("Ángulo de Fricción (φ')", row['Phi'], "°")
    with c2: card("Cohesión Efectiva (c')", row['Cohesion'], "kPa")
    
    st.write("")
    
    # Fila 2: Rigidez
    c3, c4 = st.columns(2)
    with c3: card("Módulo de Young (E)", row['E_mod'], "MPa")
    with c4: card("Fricción Residual", row['Phi_res'], "°")
    
    st.caption("Nota: Los valores de E corresponden a rangos típicos para condiciones de carga estática.")

with tab3:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### Permeabilidad (k)")
        st.markdown("Capacidad del suelo para transmitir agua.")
        # Formatear bonito la notación científica
        k_val = row['Permeabilidad']
        st.markdown(f"""
        <div style="font-size: 2.5rem; font-weight: bold; color: #2980b9;">
            {k_val.split('...')[0]} <span style="font-size: 1rem; color: #7f8c8d;">m/s</span>
        </div>
        """, unsafe_allow_html=True)
        if "..." in k_val:
            st.caption(f"Rango máximo hasta: {k_val.split('...')[1]}")
            
    with c2:
        st.info("💡 **Interpretación:**\n\n* **10⁻² a 10⁻⁵**: Muy permeable (Gravas/Arenas limpias)\n* **10⁻⁵ a 10⁻⁷**: Poco permeable (Arenas finas/Limos)\n* **< 10⁻⁷**: Impermeable (Arcillas)")

st.markdown("---")

# --- TABLA RESUMEN MEJORADA ---
st.subheader("📋 Datos básicos")

display_df = df_formatted[df_formatted['Tipo de suelo'] == selected_soil].copy()
display_df = display_df[['Tipo de suelo', 'Granulometria_<0.06', 'LL', 'IP', 'Gamma_aparente', 'Phi', 'Cohesion', 'E_mod']]

st.dataframe(
    display_df,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Tipo de suelo": st.column_config.TextColumn("Clasificación", width="medium"),
        "Granulometria_<0.06": st.column_config.ProgressColumn(
            "% Finos", 
            help="Porcentaje que pasa el tamiz 0.063mm",
            format="%s%%",
            min_value=0, max_value=100
        ),
        "LL": st.column_config.NumberColumn("Lim. Líquido", format="%s%%"),
        "IP": "Índice Plást.",
        "Gamma_aparente": st.column_config.NumberColumn("Peso Esp. (kN/m³)", format="%s"),
        "Phi": "Fricción (°)",
        "Cohesion": "Cohesión (kPa)",
        "E_mod": "Módulo E (MPa)"
    }
)