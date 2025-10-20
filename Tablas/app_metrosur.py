import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Tipos de Suelo - Metro Sur", layout="wide")

# CSS personalizado para los colores de la tabla
st.markdown("""
<style>
    .stDataFrame {
        font-size: 14px;
    }
    
    .header-blue {
        background-color: #4472C4;
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Título con estilo
st.markdown('<div class="header-blue"><h2 style="color: white; margin: 0;">PARÁMETROS GEOTÉCNICOS DE LOS TIPOS DE SUELO</h2></div>', unsafe_allow_html=True)

# Datos embebidos en el código
data = [
    {"Tipo de suelo": "Rellenos antrópicos", "Peso específico aparente": "18", "Cohesión": "0", "Ángulo de rozamiento": "28", "Módulo de deformación": "800-1.000", "Coef poisson": "0,35", "Coeficiente de balasto kh": "2.000"},
    {"Tipo de suelo": "Rellenso seleccionados compactados", "Peso específico aparente": "21", "Cohesión": "20", "Ángulo de rozamiento": "34", "Módulo de deformación": "10.000", "Coef poisson": "0,28", "Coeficiente de balasto kh": "8.000"},
    {"Tipo de suelo": "Aluviales", "Peso específico aparente": "20", "Cohesión": "0", "Ángulo de rozamiento": "32", "Módulo de deformación": "1.000-1.500", "Coef poisson": "0,32", "Coeficiente de balasto kh": "5.000"},
    {"Tipo de suelo": "Arenas Cuaternarias", "Peso específico aparente": "20", "Cohesión": "0-5", "Ángulo de rozamiento": "34", "Módulo de deformación": "3.000-6.000", "Coef poisson": "0,30", "Coeficiente de balasto kh": "8.000"},
    {"Tipo de suelo": "Arenas de miga", "Peso específico aparente": "20", "Cohesión": "5-10", "Ángulo de rozamiento": "35", "Módulo de deformación": "5.500-7.500", "Coef poisson": "0,30", "Coeficiente de balasto kh": "12.000-20.000"},
    {"Tipo de suelo": "Arenas Tosquizas", "Peso específico aparente": "20,5", "Cohesión": "10-15", "Ángulo de rozamiento": "33", "Módulo de deformación": "8.000-10.000", "Coef poisson": "0,30", "Coeficiente de balasto kh": "15.000-20.000"},
    {"Tipo de suelo": "Toscos Arenosos", "Peso específico aparente": "20,8", "Cohesión": "20-25", "Ángulo de rozamiento": "32,5", "Módulo de deformación": "13.000", "Coef poisson": "0,30", "Coeficiente de balasto kh": "25.000-35.000"},
    {"Tipo de suelo": "Toscos", "Peso específico aparente": "21", "Cohesión": "30-40", "Ángulo de rozamiento": "30", "Módulo de deformación": "15.000-18.000", "Coef poisson": "0,30", "Coeficiente de balasto kh": "30.000-40.000"},
    {"Tipo de suelo": "Toscos de alta plasticidad", "Peso específico aparente": "20,6", "Cohesión": "40-80", "Ángulo de rozamiento": "28", "Módulo de deformación": "20.000", "Coef poisson": "0,28", "Coeficiente de balasto kh": "40.000"},
    {"Tipo de suelo": "Peñuelas verdes y grises", "Peso específico aparente": "20", "Cohesión": "50-60", "Ángulo de rozamiento": "28", "Módulo de deformación": "20.000", "Coef poisson": "0,28", "Coeficiente de balasto kh": "35.000-50.000"},
    {"Tipo de suelo": "Peñuelas verdes o grises con yesos", "Peso específico aparente": "21", "Cohesión": "50-80", "Ángulo de rozamiento": "30", "Módulo de deformación": "25.000", "Coef poisson": "0,27", "Coeficiente de balasto kh": "40.000-55.000"},
    {"Tipo de suelo": "Peñuelas reblandecidas con yesos (redepositadas)", "Peso específico aparente": "20", "Cohesión": "0-10", "Ángulo de rozamiento": "28", "Módulo de deformación": "1.000", "Coef poisson": "0,35", "Coeficiente de balasto kh": "5.000"},
    {"Tipo de suelo": "Arenas micáceas en Mioceno", "Peso específico aparente": "21", "Cohesión": "5-10", "Ángulo de rozamiento": "34", "Módulo de deformación": "5.000", "Coef poisson": "0,30", "Coeficiente de balasto kh": "10.000"},
    {"Tipo de suelo": "Sepiolitas", "Peso específico aparente": "16", "Cohesión": "20", "Ángulo de rozamiento": "28", "Módulo de deformación": "30.000-50.000", "Coef poisson": "0,28", "Coeficiente de balasto kh": "20.000"},
    {"Tipo de suelo": "Caliches niveles litificados", "Peso específico aparente": "22", "Cohesión": "150", "Ángulo de rozamiento": "32", "Módulo de deformación": "60.000", "Coef poisson": "0,25", "Coeficiente de balasto kh": "80.000-100.000"},
    {"Tipo de suelo": "Yesos", "Peso específico aparente": "23", "Cohesión": "70-100", "Ángulo de rozamiento": "28", "Módulo de deformación": "40.000", "Coef poisson": "0,26", "Coeficiente de balasto kh": "6.000"}
]

# Crear DataFrame con los datos
df_data = pd.DataFrame(data)

# Crear fila de unidades
df_units = pd.DataFrame([{
    "Tipo de suelo": "UNIDADES",
    "Peso específico aparente": "kN/m³",
    "Cohesión": "kN/m²",
    "Ángulo de rozamiento": "º",
    "Módulo de deformación": "T/m²",
    "Coef poisson": "--",
    "Coeficiente de balasto kh": "T/m³"
}])

# Combinar unidades y datos
df_combined = pd.concat([df_units, df_data], ignore_index=True)

# Función para aplicar colores a las filas
def highlight_rows(row):
    if row.name == 0:  # Fila de unidades
        return ["background-color: #B4C7E7; font-weight: bold; color: black"] * len(row)
    else:
        return ["background-color: #D9E1F2; color: black"] * len(row)

# Aplicar estilos
styled_df = df_combined.style.apply(highlight_rows, axis=1)

# Mostrar la tabla (usando width en lugar de use_container_width)
st.dataframe(
    styled_df,
    width=None,
    hide_index=True,
    height=600
)

# Información adicional
st.markdown("""
<div style="background-color: #E7E6E6; padding: 15px; border-radius: 5px; margin-top: 20px;">
<strong>Notas:</strong>
<ul>
<li>Los autores recomiendan que en los casos en los que aparecen dos valores, el mayor se considere para niveles profundos (>10 m) o con un mayor grado de consolidación o cementación.</li>
<li>Los valores se han tomado para el diseño de pantallas de proyectos del metro de Madrid.</li>
</ul>
</div>
""", unsafe_allow_html=True)
