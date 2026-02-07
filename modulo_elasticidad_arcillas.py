import streamlit as st
from docx import Document
import io
import pandas as pd
import math

# ---------------------------------------------------------
# CAPA DE LÓGICA (MOTOR DE CÁLCULO)
# ---------------------------------------------------------
def calcular_modulo_elasticidad(Nspt=None, IP=None, Cu=None):
    """
    Calcula el módulo de elasticidad (E) replicando EXACTAMENTE las fórmulas
    del archivo Excel 'E_arcillas.xlsx'.
    
    Inputs:
    - Nspt: Golpeo SPT (adimensional)
    - IP: Índice de Plasticidad (%) -> C2 en Excel
    - Cu: Cohesión sin drenaje (kPa) -> C4 en Excel
    """
    resultados = {}
    formulas_usadas = {}

    def valor_valido(valor):
        return valor is not None and valor >= 0

    # -----------------------------------------------------
    # 1. FÓRMULAS DE STROUD (1974) - Basadas en Nspt e IP
    # -----------------------------------------------------
    if valor_valido(Nspt) and valor_valido(IP):
        # Stroud 1974 - Límite Superior
        # Fórmula Excel: =C3*(-0,0081*C2^3+1,732*C2^2-127*C2+3703)/1000
        factor_sup = -0.0081 * IP**3 + 1.732 * IP**2 - 127 * IP + 3703
        E_sup = Nspt * factor_sup / 1000
        
        nom = 'Stroud, 1974 (Límite Superior)'
        resultados[nom] = E_sup
        formulas_usadas[nom] = {
            'formula': 'E = Nspt × Polinomio_Sup(IP) / 1000',
            'desc': 'Polinomio cúbico basado en IP'
        }

        # Stroud 1974 - Límite Inferior
        # Fórmula Excel: =C3*(-0,0031*C2^3+0,8591*C2^2-72,041*C2+2410)/1000
        factor_inf = -0.0031 * IP**3 + 0.8591 * IP**2 - 72.041 * IP + 2410
        E_inf = Nspt * factor_inf / 1000
        
        nom = 'Stroud, 1974 (Límite Inferior)'
        resultados[nom] = E_inf
        formulas_usadas[nom] = {
            'formula': 'E = Nspt × Polinomio_Inf(IP) / 1000',
            'desc': 'Polinomio cúbico basado en IP'
        }

    # -----------------------------------------------------
    # 2. STROUD Y BUTTLER - Basadas en Nspt
    # -----------------------------------------------------
    if valor_valido(Nspt):
        # Arcillas media plasticidad
        # Fórmula Excel: =5*C3*98,1/1000
        E_media = 5 * Nspt * 98.1 / 1000
        resultados['Stroud y Buttler (Arcillas media plasticidad)'] = E_media
        formulas_usadas['Stroud y Buttler (Arcillas media plasticidad)'] = {'formula': 'E = 5 × Nspt × 0.0981', 'desc': 'Conversión kg/cm² -> MPa'}

        # Arcillas baja plasticidad
        # Fórmula Excel: =6*C3*98,1/1000
        E_baja = 6 * Nspt * 98.1 / 1000
        resultados['Stroud y Buttler (Arcillas baja plasticidad)'] = E_baja
        formulas_usadas['Stroud y Buttler (Arcillas baja plasticidad)'] = {'formula': 'E = 6 × Nspt × 0.0981', 'desc': 'Conversión kg/cm² -> MPa'}

    # -----------------------------------------------------
    # 3. CTE-DB-SE-C (Tabla F.2) - Basadas en Cu (C4) e IP
    # -----------------------------------------------------
    if valor_valido(Cu) and valor_valido(IP):
        # Seleccionamos el grupo de fórmulas según el rango de IP
        
        # Grupo IP < 30
        if IP < 30:
            # OCR < 3
            resultados['CTE Tabla F.2 (IP<30, OCR<3)'] = (800 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (IP<30, OCR<3)'] = {'formula': 'E = 800 × Cu', 'desc': 'Arcilla baja plasticidad, poco consolidada'}
            
            # 3 < OCR < 5
            resultados['CTE Tabla F.2 (IP<30, 3<OCR<5)'] = (600 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (IP<30, 3<OCR<5)'] = {'formula': 'E = 600 × Cu', 'desc': 'Arcilla baja plasticidad, consol. media'}
            
            # OCR > 5
            resultados['CTE Tabla F.2 (IP<30, OCR>5)'] = (300 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (IP<30, OCR>5)'] = {'formula': 'E = 300 × Cu', 'desc': 'Arcilla baja plasticidad, muy consolidada'}

        # Grupo 30 < IP < 50
        elif 30 <= IP <= 50:
            # OCR < 3
            resultados['CTE Tabla F.2 (30<IP<50, OCR<3)'] = (350 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (30<IP<50, OCR<3)'] = {'formula': 'E = 350 × Cu', 'desc': 'Arcilla media plasticidad, poco consolidada'}
            
            # 3 < OCR < 5
            resultados['CTE Tabla F.2 (30<IP<50, 3<OCR<5)'] = (250 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (30<IP<50, 3<OCR<5)'] = {'formula': 'E = 250 × Cu', 'desc': 'Arcilla media plasticidad, consol. media'}
            
            # OCR > 5
            resultados['CTE Tabla F.2 (30<IP<50, OCR>5)'] = (130 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (30<IP<50, OCR>5)'] = {'formula': 'E = 130 × Cu', 'desc': 'Arcilla media plasticidad, muy consolidada'}

        # Grupo IP > 50
        else:
            # OCR < 3
            resultados['CTE Tabla F.2 (IP>50, OCR<3)'] = (150 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (IP>50, OCR<3)'] = {'formula': 'E = 150 × Cu', 'desc': 'Arcilla alta plasticidad, poco consolidada'}
            
            # 3 < OCR < 5
            resultados['CTE Tabla F.2 (IP>50, 3<OCR<5)'] = (100 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (IP>50, 3<OCR<5)'] = {'formula': 'E = 100 × Cu', 'desc': 'Arcilla alta plasticidad, consol. media'}
            
            # OCR > 5
            resultados['CTE Tabla F.2 (IP>50, OCR>5)'] = (50 * Cu) / 1000
            formulas_usadas['CTE Tabla F.2 (IP>50, OCR>5)'] = {'formula': 'E = 50 × Cu', 'desc': 'Arcilla alta plasticidad, muy consolidada'}

    return resultados, formulas_usadas

# ---------------------------------------------------------
# CAPA DE REPORTES (GENERACIÓN WORD)
# ---------------------------------------------------------
def generar_informe(Nspt, IP, Cu, resultados, formulas_usadas):
    doc = Document()
    doc.add_heading('Informe de Cálculo: Módulo de Elasticidad (Arcillas)', level=1)

    doc.add_heading('Datos de Entrada', level=2)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Parámetro'
    hdr_cells[1].text = 'Valor'
    
    datos = []
    if Nspt is not None: datos.append(("Número de golpes (Nspt)", Nspt))
    if IP is not None: datos.append(("Índice de Plasticidad (IP)", f"{IP}%"))
    if Cu is not None: datos.append(("Cohesión sin Drenaje (Cu)", f"{Cu} kPa"))

    for parametro, valor in datos:
        row_cells = table.add_row().cells
        row_cells[0].text = parametro
        row_cells[1].text = str(valor)

    doc.add_heading('Resultados Calculados', level=2)
    doc.add_paragraph("Nota: Todos los resultados se expresan en MPa.")
    
    # Agrupar por tipo para el reporte
    metodos_stroud = {k:v for k,v in resultados.items() if 'Stroud' in k}
    metodos_cte = {k:v for k,v in resultados.items() if 'CTE' in k}

    if metodos_stroud:
        doc.add_heading('Correlaciones de Stroud y Buttler', level=3)
        for metodo, valor in metodos_stroud.items():
            p = doc.add_paragraph()
            p.add_run(f"{metodo}: ").bold = True
            p.add_run(f"{valor:.2f} MPa")
            doc.add_paragraph(f"   Fórmula base: {formulas_usadas[metodo]['formula']}")

    if metodos_cte:
        doc.add_heading('Correlaciones CTE (Código Técnico)', level=3)
        doc.add_paragraph(f"Resultados filtrados para IP = {IP}%")
        for metodo, valor in metodos_cte.items():
            p = doc.add_paragraph()
            p.add_run(f"{metodo}: ").bold = True
            p.add_run(f"{valor:.2f} MPa")
            doc.add_paragraph(f"   Fórmula base: {formulas_usadas[metodo]['formula']}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# CAPA DE INTERFAZ (STREAMLIT)
# ---------------------------------------------------------
def main():
    st.set_page_config(page_title="E - Arcillas (Avanzado)", layout="wide")
    st.title("Calculadora de Módulo de Elasticidad (E) - Arcillas")
    st.markdown("Implementación exacta de **Stroud (1974)** y **CTE DB-SE-C**.")

    if 'data_arcillas_adv' not in st.session_state:
        st.session_state.data_arcillas_adv = {
            "Símbolo": ["Nspt", "IP", "Cu"],
            "Descripción": ["Golpeo SPT", "Índice de Plasticidad", "Cohesión sin drenaje"],
            "Valor": [None, None, None],
            "Unidad": ["-", "%", "kPa"]
        }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Entrada de Datos")
        df = pd.DataFrame(st.session_state.data_arcillas_adv)
        
        edited_df = st.data_editor(
            df,
            num_rows="fixed",
            hide_index=True,
            column_config={
                "Símbolo": st.column_config.TextColumn("Símbolo", disabled=True),
                "Descripción": st.column_config.TextColumn("Descripción", disabled=True),
                "Unidad": st.column_config.TextColumn("Unidad", disabled=True),
                "Valor": st.column_config.NumberColumn("Valor", min_value=0, required=True)
            },
            key="editor_arcillas_adv"
        )
        
        st.info("Para obtener resultados del CTE, es obligatorio rellenar **IP** y **Cu**.")

        if st.button("Calcular E", type="primary"):
            try:
                def get_val(sym):
                    val = edited_df.loc[edited_df["Símbolo"] == sym, "Valor"].values[0]
                    return float(val) if val is not None and val != "" else None

                Nspt = get_val("Nspt")
                IP = get_val("IP")
                Cu = get_val("Cu")
                
            except (ValueError, TypeError):
                Nspt, IP, Cu = None, None, None

            # Validar mínimos para calcular algo
            if Nspt is not None or (Cu is not None and IP is not None):
                resultados, formulas_usadas = calcular_modulo_elasticidad(Nspt, IP, Cu)
                
                st.success("Cálculo completado.")
                st.subheader("Resultados (MPa):")
                
                # Mostrar resultados ordenados
                metodos_stroud = {k:v for k,v in resultados.items() if 'Stroud' in k}
                metodos_cte = {k:v for k,v in resultados.items() if 'CTE' in k}

                if metodos_stroud:
                    st.markdown("##### 🔹 Método Stroud & Buttler (Basado en Nspt)")
                    for m, v in metodos_stroud.items():
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"**{m}** \n<span style='color:grey; font-size:0.9em'>{formulas_usadas[m]['formula']}</span>", unsafe_allow_html=True)
                        c2.markdown(f"**{v:.2f} MPa**")
                        st.divider()

                if metodos_cte:
                    st.markdown("##### 🔸 Método CTE DB-SE-C (Basado en Cu)")
                    st.caption(f"Fórmulas seleccionadas automáticamente para IP = {IP}%")
                    for m, v in metodos_cte.items():
                        c1, c2 = st.columns([3, 1])
                        c1.markdown(f"**{m}** \n<span style='color:grey; font-size:0.9em'>{formulas_usadas[m]['desc']}</span>", unsafe_allow_html=True)
                        c2.markdown(f"**{v:.2f} MPa**")
                        st.divider()

                informe = generar_informe(Nspt, IP, Cu, resultados, formulas_usadas)
                st.download_button(
                    label="📄 Descargar Informe Word",
                    data=informe,
                    file_name="informe_arcillas_completo.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.error("Por favor, introduce al menos (Nspt y IP) o (Cu y IP).")

    with col2:
        with st.expander("🔎 Explicación de las Fórmulas", expanded=True):
            st.markdown("### 1. Stroud (1974)")
            st.markdown("""
            Utiliza polinomios de 3º grado ajustados a curvas empíricas.
            * **Límite Superior:** $E = N_{spt} \\cdot f_{sup}(IP)$
            * **Límite Inferior:** $E = N_{spt} \\cdot f_{inf}(IP)$
            """)
            
            st.markdown("### 2. CTE DB-SE-C")
            st.markdown("""
            El Código Técnico establece relaciones $E = K \\cdot C_u$ según la plasticidad y la sobreconsolidación (OCR).
            
            **Tu IP actual:** """ + (f"**{IP}%**" if 'IP' in locals() and IP else "No definido"))
            
            if 'IP' in locals() and IP:
                if IP < 30:
                    st.table(pd.DataFrame({"OCR": ["< 3", "3 - 5", "> 5"], "Fórmula": ["800 Cu", "600 Cu", "300 Cu"]}))
                elif IP <= 50:
                    st.table(pd.DataFrame({"OCR": ["< 3", "3 - 5", "> 5"], "Fórmula": ["350 Cu", "250 Cu", "130 Cu"]}))
                else:
                    st.table(pd.DataFrame({"OCR": ["< 3", "3 - 5", "> 5"], "Fórmula": ["150 Cu", "100 Cu", "50 Cu"]}))

if __name__ == "__main__":
    main()