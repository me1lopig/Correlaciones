import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

def main():
    st.set_page_config(page_title="Portal de Correlaciones Geotécnicas", layout="wide")

    params = st.experimental_get_query_params()
    app = params.get("app", ["portal"])[0]

    if app == "portal":
        show_portal()
    elif app == "cc":
        try:
            import Cc_streamlit_1
            Cc_streamlit_1.main()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Índice de Compresión (Cc).")
    elif app == "angulo_rozamiento":
        try:
            import angulo_rozamiento_streamlit
            angulo_rozamiento_streamlit.main()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Ángulo de Rozamiento (φ).")
    elif app == "modulo_elasticidad":
        try:
            import modulo_elasticidad_arenas_streamlit
            modulo_elasticidad_arenas_streamlit.main()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Módulo de Elasticidad (E).")

def show_portal():
    st.title("Portal de Correlaciones Geotécnicas")
    st.markdown("Selecciona una de las siguientes aplicaciones para calcular diferentes parámetros geotécnicos:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <style>
            .app-container {{
                text-align: center;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 10px;
                margin: 10px;
                cursor: pointer;
                transition: transform 0.2s;
                background-color: #f9f9f9;
            }}
            .app-container:hover {{
                transform: scale(1.05);
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .app-icon {{
                font-size: 100px;
                margin-bottom: 15px;
            }}
            </style>
            <a href="?app=cc" target="_self">
                <div class="app-container">
                    <div class="app-icon">📊</div>
                    <h3>Índice de Compresión (Cc)</h3>
                    <p>Calcula el índice de compresión utilizando diferentes fórmulas empíricas.</p>
                </div>
            </a>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(
            f"""
            <a href="?app=angulo_rozamiento" target="_self">
                <div class="app-container">
                    <div class="app-icon">📉</div>
                    <h3>Ángulo de Rozamiento (φ)</h3>
                    <p>Calcula el ángulo de rozamiento utilizando diferentes correlaciones empíricas.</p>
                </div>
            </a>
            """, unsafe_allow_html=True)

    with col3:
        st.markdown(
            f"""
            <a href="?app=modulo_elasticidad" target="_self">
                <div class="app-container">
                    <div class="app-icon">🧪</div>
                    <h3>Módulo de Elasticidad (E)</h3>
                    <p>Calcula el módulo de elasticidad para arenas utilizando diferentes fórmulas empíricas.</p>
                </div>
            </a>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
