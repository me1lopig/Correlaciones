import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard Geotécnico", layout="wide")

st.title("📊 Análisis Estadístico de Campaña Geotécnica")

# 1. Cargar archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Leer datos (ajustar según sea csv o excel)
    df = pd.read_csv(uploaded_file)

    try:
    # Plan A: Intenta leerlo con la codificación estándar por defecto (utf-8)
        df = pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
    # Plan B: Si falla por las tildes/eñes, rebobina el archivo y usa latin-1
        uploaded_file.seek(0) 
        df = pd.read_csv(uploaded_file, encoding='latin-1')


    
    # 2. Barra lateral de filtros
    st.sidebar.header("Filtros")
    prospeccion = st.sidebar.multiselect(
        "Selecciona el Sondeo/Calicata:", 
        options=df["Descripción Muestra"].dropna().unique()
    )
    
    # Filtrar el dataframe
    if prospeccion:
        df_filtrado = df[df["Descripción Muestra"].isin(prospeccion)]
    else:
        df_filtrado = df
        
    # 3. Métricas rápidas
    st.subheader("Métricas Generales del Terreno")
    col1, col2, col3 = st.columns(3)
    
    # Convertir SPT a numérico para la media
    df_filtrado['SPT (valores centrales)'] = pd.to_numeric(df_filtrado['SPT (valores centrales)'], errors='coerce')
    
    col1.metric("SPT Medio (N30)", round(df_filtrado['SPT (valores centrales)'].mean(), 1))
    col2.metric("Suelo Predominante USCS", df_filtrado['Clasificación USCS'].mode()[0] if not df_filtrado['Clasificación USCS'].dropna().empty else "N/A")
    col3.metric("Humedad Máxima (%)", df_filtrado['W'].max() if 'W' in df_filtrado.columns else "N/A")

    # 4. Gráfica de Profundidad (Ejemplo con SPT)
    st.subheader("Perfil de Resistencia SPT vs Profundidad")
    
    fig, ax = plt.subplots(figsize=(8, 6))
    df_spt = df_filtrado.dropna(subset=['Profundidad inicial', 'SPT (valores centrales)'])
    
    sns.lineplot(data=df_spt, x='SPT (valores centrales)', y='Profundidad inicial', 
                 hue='Descripción Muestra', marker='o', sort=False, ax=ax)
    
    ax.invert_yaxis() # Invertir eje para que parezca el subsuelo
    ax.set_ylabel("Profundidad (m)")
    ax.set_xlabel("Golpeo SPT (N30)")
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Mostrar la figura en Streamlit
    st.pyplot(fig)