import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora Geotécnica de Cc", layout="wide", page_icon="🌍")

st.title("🌍 Estimador del Índice de Compresión (Cc)")
st.markdown("Herramienta optimizada: Correlaciones empíricas basadas exclusivamente en el **Límite Líquido (LL)** y el **Índice de Plasticidad (IP)**.")

# --- BARRA LATERAL: ENTRADA DE DATOS ---
st.sidebar.header("📋 Parámetros de Entrada")
st.sidebar.markdown("Ingresa los límites de Atterberg de tu ensayo de laboratorio.")

# Captura estricta de LL e IP
LL = st.sidebar.number_input("Límite Líquido (LL) [%]", value=None, min_value=0.0)
IP = st.sidebar.number_input("Índice de Plasticidad (IP) [%]", value=None, min_value=0.0)

# --- LÓGICA DE SELECCIÓN DE FÓRMULAS ---
resultados = []
info_formulas = []

# GRUPO 1: Basadas exclusivamente en Límite Líquido (LL)
if LL is not None:
    resultados.extend([
        {"Variable": "LL", "Autor": "Terzaghi & Peck (1967)", "Cc": 0.009 * (LL - 10)},
        {"Variable": "LL", "Autor": "Skempton (1944)", "Cc": 0.007 * (LL - 10)},
        {"Variable": "LL", "Autor": "Mayne (1980)", "Cc": (LL - 13) / 109},
        {"Variable": "LL", "Autor": "Tsuchida (1991) a", "Cc": 0.009 * (LL - 8)},
        {"Variable": "LL", "Autor": "Tsuchida (1991) b", "Cc": 0.009 * LL},
        {"Variable": "LL", "Autor": "Azzouz et al. (1976) a", "Cc": 0.007 * (LL - 7)},
        {"Variable": "LL", "Autor": "Azzouz et al. (1976) b", "Cc": 0.006 * (LL - 9)},
        {"Variable": "LL", "Autor": "Cozzolino (1961)", "Cc": 0.0046 * (LL - 9)},
        {"Variable": "LL", "Autor": "Yamagutshi (1959)", "Cc": 0.013 * (LL - 13.5)},
        {"Variable": "LL", "Autor": "Shouka (1964)", "Cc": 0.017 * (LL - 20)},
        {"Variable": "LL", "Autor": "Nishant Dayal et al. (2006)", "Cc": 0.0037 * (LL + 25.5)},
        {"Variable": "LL", "Autor": "Yoon et al. (2004) a", "Cc": 0.012 * (LL + 16.4)},
        {"Variable": "LL", "Autor": "Yoon et al. (2004) b", "Cc": 0.011 * (LL - 6.36)},
        {"Variable": "LL", "Autor": "Yoon et al. (2004) c", "Cc": 0.01 * (LL - 10.9)}
    ])
    info_formulas.extend([
        {"Autor": "Terzaghi & Peck (1967)", "Ecuación": "Cc = 0.009(LL-10)"},
        {"Autor": "Skempton (1944)", "Ecuación": "Cc = 0.007(LL-10)"},
        {"Autor": "Mayne (1980)", "Ecuación": "Cc = (LL-13)/109"},
        {"Autor": "Tsuchida (1991) a", "Ecuación": "Cc = 0.009(LL-8)"},
        {"Autor": "Tsuchida (1991) b", "Ecuación": "Cc = 0.009(LL)"},
        {"Autor": "Azzouz et al. (1976) a", "Ecuación": "Cc = 0.007(LL-7)"},
        {"Autor": "Azzouz et al. (1976) b", "Ecuación": "Cc = 0.006(LL-9)"},
        {"Autor": "Cozzolino (1961)", "Ecuación": "Cc = 0.0046(LL-9)"},
        {"Autor": "Yamagutshi (1959)", "Ecuación": "Cc = 0.013(LL-13.5)"},
        {"Autor": "Shouka (1964)", "Ecuación": "Cc = 0.017(LL-20)"},
        {"Autor": "Nishant Dayal et al. (2006)", "Ecuación": "Cc = 0.0037(LL+25.5)"},
        {"Autor": "Yoon et al. (2004) a", "Ecuación": "Cc = 0.012(LL+16.4)"},
        {"Autor": "Yoon et al. (2004) b", "Ecuación": "Cc = 0.011(LL-6.36)"},
        {"Autor": "Yoon et al. (2004) c", "Ecuación": "Cc = 0.01(LL-10.9)"}
    ])

# GRUPO 2: Basadas exclusivamente en Índice de Plasticidad (IP)
if IP is not None:
    resultados.extend([
        {"Variable": "IP", "Autor": "Nacci et al. (1975)", "Cc": 0.02 + 0.014 * IP},
        {"Variable": "IP", "Autor": "Nakase et al. (1988)", "Cc": 0.046 + 0.0104 * IP},
        {"Variable": "IP", "Autor": "Nishant Dayal et al. (2006)", "Cc": 0.0042 * IP + 0.165},
        {"Variable": "IP", "Autor": "Yoon et al. (2004) IP", "Cc": 0.165 + 0.014 * IP}
    ])
    info_formulas.extend([
        {"Autor": "Nacci et al. (1975)", "Ecuación": "Cc = 0.02 + 0.014(IP)"},
        {"Autor": "Nakase et al. (1988)", "Ecuación": "Cc = 0.046 + 0.0104(IP)"},
        {"Autor": "Nishant Dayal et al. (2006)", "Ecuación": "Cc = 0.0042(IP) + 0.165"},
        {"Autor": "Yoon et al. (2004)", "Ecuación": "Cc = 0.165 + 0.014(IP)"}
    ])

# --- INTERFAZ PRINCIPAL (TABS) ---
if not resultados:
    st.info("👈 Por favor, ingresa el valor de LL o IP en la barra lateral para calcular los resultados.")
else:
    # Preparamos el DataFrame e incluimos la columna de control booleana
    df_res = pd.DataFrame(resultados)
    df_res['Cc'] = df_res['Cc'].round(4)
    df_res.insert(0, "Incluir", True) # Esta columna generará los checkboxes
    
    df_info = pd.DataFrame(info_formulas)

    tab1, tab2, tab3 = st.tabs(["📊 Resultados y Estadísticas", "📦 Análisis de Anomalías", "📚 Fórmulas Aplicadas"])

    with tab1:
        st.subheader("Panel de Control y Cálculos")
        
        # Dividimos la pantalla: Izquierda para la tabla interactiva, Derecha para métricas y gráfico
        col_tabla, col_grafico = st.columns([1, 1.5])
        
        with col_tabla:
            st.markdown("#### Selección de Métodos")
            st.markdown("Desmarca la casilla para **excluir** una fórmula del análisis final.")
            
            # st.data_editor permite editar el dataframe en vivo
            df_editado = st.data_editor(
                df_res,
                column_config={
                    "Incluir": st.column_config.CheckboxColumn(
                        "Incluir", 
                        help="Selecciona o deselecciona para recalcular estadísticas.",
                        default=True
                    )
                },
                disabled=["Variable", "Autor", "Cc"], # Evita que el usuario borre los nombres o valores
                hide_index=True,
                use_container_width=True,
                height=500
            )
            
        # IMPORTANTE: Filtramos en vivo los datos basándonos en las cajas marcadas
        df_validos = df_editado[(df_editado['Incluir'] == True) & (df_editado['Cc'] > 0)]
        
        with col_grafico:
            st.markdown("#### Estadísticas de la Estimación")
            
            if not df_validos.empty:
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                col_m1.metric("Fórmulas Activas", len(df_validos))
                col_m2.metric("Mediana de Cc", round(df_validos['Cc'].median(), 3))
                col_m3.metric("Promedio de Cc", round(df_validos['Cc'].mean(), 3))
                col_m4.metric("Desviación Est.", round(df_validos['Cc'].std(), 3))

                # Gráfico interactivo que se actualiza al desmarcar
                fig_bar = px.bar(
                    df_validos.sort_values(by="Cc"), 
                    x="Cc", 
                    y="Autor", 
                    color="Variable", 
                    orientation="h",
                    text="Cc",
                    color_discrete_map={"LL": "#1f77b4", "IP": "#ff7f0e"}
                )
                fig_bar.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=400)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.warning("⚠️ Has excluido todos los métodos. Por favor, marca al menos una casilla en la tabla.")
            
    with tab2:
        st.subheader("Detección de Valores Atípicos (Boxplot)")
        st.markdown("Este gráfico se actualiza dinámicamente según las selecciones que realices en la pestaña anterior.")
        
        if not df_validos.empty:
            fig_box = px.box(
                df_validos, 
                x="Variable", 
                y="Cc", 
                color="Variable",
                points="all",
                hover_data=["Autor"],
                color_discrete_map={"LL": "#1f77b4", "IP": "#ff7f0e"}
            )
            
            fig_box.update_traces(
                boxmean=True,               
                pointpos=0,                 
                jitter=0,                 
                marker=dict(size=8, line=dict(width=1.5, color='DarkSlateGrey'))
            )
            
            for i, row in df_validos.iterrows():
                fig_box.add_annotation(
                    x=row["Variable"],
                    y=row["Cc"],
                    text=row["Autor"],
                    showarrow=False,
                    xanchor="left",
                    xshift=15, 
                    font=dict(size=10, color="#333333")
                )
            
            fig_box.update_layout(
                height=700, 
                yaxis_title="Índice de Compresión (Cc)", 
                xaxis_title="Parámetro Base",
                showlegend=False
            )
            
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("Gráfico no disponible. Selecciona al menos un método.")
        
    with tab3:
        st.subheader("Base Teórica de las Ecuaciones")
        st.table(df_info)