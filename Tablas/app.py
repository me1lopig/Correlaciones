import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Tipos de Suelo - Metro Sur", layout="wide")

# Título con estilo
st.markdown("""
<div style="background-color: #4472C4; color: white; padding: 15px; text-align: center; border-radius: 5px; margin-bottom: 20px;">
    <h2 style="color: white; margin: 0;">PARÁMETROS GEOTÉCNICOS METRO SUR MADRID</h2>
</div>
""", unsafe_allow_html=True)

# Datos embebidos en el código
data = [
    ["Rellenos antrópicos", "18", "0", "28", "800-1.000", "0,35", "2.000"],
    ["Rellenso seleccionados compactados", "21", "20", "34", "10.000", "0,28", "8.000"],
    ["Aluviales", "20", "0", "32", "1.000-1.500", "0,32", "5.000"],
    ["Arenas Cuaternarias", "20", "0-5", "34", "3.000-6.000", "0,30", "8.000"],
    ["Arenas de miga", "20", "5-10", "35", "5.500-7.500", "0,30", "12.000-20.000"],
    ["Arenas Tosquizas", "20,5", "10-15", "33", "8.000-10.000", "0,30", "15.000-20.000"],
    ["Toscos Arenosos", "20,8", "20-25", "32,5", "13.000", "0,30", "25.000-35.000"],
    ["Toscos", "21", "30-40", "30", "15.000-18.000", "0,30", "30.000-40.000"],
    ["Toscos de alta plasticidad", "20,6", "40-80", "28", "20.000", "0,28", "40.000"],
    ["Peñuelas verdes y grises", "20", "50-60", "28", "20.000", "0,28", "35.000-50.000"],
    ["Peñuelas verdes o grises con yesos", "21", "50-80", "30", "25.000", "0,27", "40.000-55.000"],
    ["Peñuelas reblandecidas con yesos (redepositadas)", "20", "0-10", "28", "1.000", "0,35", "5.000"],
    ["Arenas micáceas en Mioceno", "21", "5-10", "34", "5.000", "0,30", "10.000"],
    ["Sepiolitas", "16", "20", "28", "30.000-50.000", "0,28", "20.000"],
    ["Caliches niveles litificados", "22", "150", "32", "60.000", "0,25", "80.000-100.000"],
    ["Yesos", "23", "70-100", "28", "40.000", "0,26", "6.000"]
]

columns = ["Tipo de suelo", "Peso específico aparente", "Cohesión", "Ángulo de rozamiento", "Módulo de deformación", "Coef poisson", "Coeficiente de balasto kh"]
units = ["UNIDADES", "kN/m³", "kN/m²", "º", "T/m²", "--", "T/m³"]

# Crear tabla HTML personalizada
html_table = """
<style>
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial, sans-serif;
        font-size: 14px;
        margin-top: 10px;
    }
    .custom-table th {
        background-color: #4472C4;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        border: 1px solid #ddd;
    }
    .custom-table .units-row {
        background-color: #B4C7E7;
        font-weight: bold;
        color: black;
    }
    .custom-table .data-row {
        background-color: #D9E1F2;
        color: black;
    }
    .custom-table td {
        padding: 10px;
        border: 1px solid #ddd;
        text-align: left;
    }
</style>

<table class="custom-table">
    <thead>
        <tr>
"""

# Agregar encabezados
for col in columns:
    html_table += "            <th>" + col + "</th>\n"

html_table += """        </tr>
    </thead>
    <tbody>
        <tr class="units-row">
"""

# Agregar fila de unidades
for unit in units:
    html_table += "            <td>" + unit + "</td>\n"

html_table += "        </tr>\n"

# Agregar filas de datos
for row in data:
    html_table += '        <tr class="data-row">\n'
    for cell in row:
        html_table += "            <td>" + str(cell) + "</td>\n"
    html_table += "        </tr>\n"

html_table += """    </tbody>
</table>
"""

st.markdown(html_table, unsafe_allow_html=True)

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
