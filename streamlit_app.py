
import streamlit as st
from docx import Document
import io
import pandas as pd

def calcular_Cc(LL=None, PL=None, IP=None, w=None, e=None, Gs=None, F=None):
    """
    Calcula el índice de compresión (Cc) según los datos disponibles.
    Solo aplica fórmulas para las que todos los parámetros necesarios estén disponibles.
    """
    resultados = {}
    formulas_usadas = {}

    def valor_aceptable(valor):
        return valor if valor is not None and valor >= 0 else "Valor no aceptable para los datos introducidos"

    # Fórmulas que solo requieren LL
    if LL is not None:
        cc_value = 0.009 * (LL - 10)
        resultados['Terzaghi & Peck (1967)'] = valor_aceptable(cc_value)
        formulas_usadas['Terzaghi & Peck (1967)'] = {'formula': 'Cc = 0.009 × (LL - 10)', 'parametros': ['LL']}

        cc_value = 0.007 * (LL - 7)
        resultados['Azzouz et al. (1976, arcillas remoldeadas)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, arcillas remoldeadas)'] = {'formula': 'Cc = 0.007 × (LL - 7)', 'parametros': ['LL']}

        cc_value = 0.0046 * (LL - 9)
        resultados['Azzouz et al. (1976, arcillas brasileñas)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, arcillas brasileñas)'] = {'formula': 'Cc = 0.0046 × (LL - 9)', 'parametros': ['LL']}

        cc_value = (LL - 13) / 109
        resultados['Mayne (1980)'] = valor_aceptable(cc_value)
        formulas_usadas['Mayne (1980)'] = {'formula': 'Cc = (LL - 13) / 109', 'parametros': ['LL']}

    # Fórmulas que requieren e
    if e is not None:
        cc_value = 0.3 * (e - 0.27)
        resultados['Hough (1957)'] = valor_aceptable(cc_value)
        formulas_usadas['Hough (1957)'] = {'formula': 'Cc = 0.3 × (e - 0.27)', 'parametros': ['e']}

        cc_value = 0.156 * e + 0.0107
        resultados['Azzouz et al. (1976, todas las arcillas)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, todas las arcillas)'] = {'formula': 'Cc = 0.156 × e + 0.0107', 'parametros': ['e']}

        cc_value = 0.75 * (e - 0.5)
        resultados['Azzouz et al. (1976, baja plasticidad)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, baja plasticidad)'] = {'formula': 'Cc = 0.75 × (e - 0.5)', 'parametros': ['e']}

        cc_value = 1.21 + 1.005 * (e - 1.87)
        resultados['Azzouz et al. (1976, São Paulo)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, São Paulo)'] = {'formula': 'Cc = 1.21 + 1.005 × (e - 1.87)', 'parametros': ['e']}

        cc_value = 1.15 * (e - 0.35)
        resultados['Nishida (1956)'] = valor_aceptable(cc_value)
        formulas_usadas['Nishida (1956)'] = {'formula': 'Cc = 1.15 × (e - 0.35)', 'parametros': ['e']}

    # Fórmulas que requieren w
    if w is not None:
        cc_value = 0.0115 * w
        resultados['Azzouz et al. (1976, suelos orgánicos)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, suelos orgánicos)'] = {'formula': 'Cc = 0.0115 × w', 'parametros': ['w']}

        cc_value = 0.0093 * w
        resultados['Koppula (1981, a)'] = valor_aceptable(cc_value)
        formulas_usadas['Koppula (1981, a)'] = {'formula': 'Cc = 0.0093 × w', 'parametros': ['w']}

        cc_value = 17.66e-5 * w**2 + 5.93e-3 * w - 0.135
        resultados['Azzouz et al. (1976, Chicago 2)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, Chicago 2)'] = {'formula': 'Cc = 17.66 × 10⁻⁵ × w² + 5.93 × 10⁻³ × w - 0.135', 'parametros': ['w']}

    # Fórmulas que requieren e, LL, y w
    if e is not None and LL is not None and w is not None:
        cc_value = 0.37 * (e + 0.003 * LL + 0.0004 * w - 0.34)
        resultados['Azzouz et al. (1976, 678 datos)'] = valor_aceptable(cc_value)
        formulas_usadas['Azzouz et al. (1976, 678 datos)'] = {'formula': 'Cc = 0.37 × (e + 0.003 × LL + 0.0004 × w - 0.34)', 'parametros': ['e', 'LL', 'w']}

    # Fórmulas que requieren PL y Gs (corregida según la imagen)
    if PL is not None and Gs is not None:
        cc_value = 0.005 * Gs * IP
        resultados['Wroth & Wood (1978)'] = valor_aceptable(cc_value)
        formulas_usadas['Wroth & Wood (1978)'] = {'formula': 'Cc = 0.005 × Gs × IP', 'parametros': ['Gs', 'IP']}

    # Fórmulas que requieren IP
    if IP is not None:
        cc_value = 0.046 + 0.0104 * IP
        resultados['Nakase et al. (1988)'] = valor_aceptable(cc_value)
        formulas_usadas['Nakase et al. (1988)'] = {'formula': 'Cc = 0.046 + 0.0104 × IP', 'parametros': ['IP']}

    # Fórmulas que requieren LL, IP, w, e, y F
    if LL is not None and IP is not None and w is not None and e is not None and F is not None:
        cc_value = -0.0997 + 0.009 * LL + 0.0014 * IP + 0.0036 * w + 0.1156 * e + 0.0025 * F
        resultados['Koppula (1981, b)'] = valor_aceptable(cc_value)
        formulas_usadas['Koppula (1981, b)'] = {'formula': 'Cc = -0.0997 + 0.009 × LL + 0.0014 × IP +
