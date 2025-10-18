import streamlit as st


def main():
    st.set_page_config(page_title="Portal de Correlaciones Geotécnicas (en pruebas)", layout="wide")

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "portal"

    if st.session_state.current_page == "portal":
        show_portal()
    elif st.session_state.current_page == "cc":
        try:
            import Cc_streamlit_1
            Cc_streamlit_1.main()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Índice de Compresión (Cc).")
    elif st.session_state.current_page == "angulo_rozamiento":
        try:
            import angulo_rozamiento_streamlit
            angulo_rozamiento_streamlit.main()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Ángulo de Rozamiento (φ).")
    elif st.session_state.current_page == "modulo_elasticidad":
        try:
            import modulo_elasticidad_arenas_streamlit
            modulo_elasticidad_arenas_streamlit.main()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Módulo de Elasticidad (E).")


def show_portal():
    st.title("Portal de Correlaciones Geotécnicas")
    st.markdown("Selecciona una de las siguientes aplicaciones para calcular diferentes parámetros geotécnicos:")

    st.markdown(
        """
        <style>
        .app-card {
            text-align: center;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            margin: 10px;
            transition: transform 0.2s;
            background-color: #f9f9f9;
            height: 300px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            max-width: 400px;
        }
        .app-card:hover {
            transform: scale(1.05);
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .app-icon {
            display: flex;
            justify-content: center;
            margin-top: 15px;
        }
        .app-icon img {
            width: 80px;
            height: 80px;
        }
        .app-emoji {
            font-size: 80px;
        }
        .app-title {
            margin: 15px 0 10px 0;
            font-size: 1.3em;
            font-weight: bold;
            text-align: center;
        }
        .app-description {
            text-align: center;
            color: #555;
            font-size: 0.9em;
            margin-bottom: 20px;
            padding: 0 10px;
        }
        
        /* Estilo de botones verdes */
        .stButton > button {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            padding: 12px 24px !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            background-color: #45a049 !important;
            border: none !important;
        }
        .stButton > button:focus {
            background-color: #4CAF50 !important;
            color: white !important;
            border: none !important;
            box-shadow: none !important;
        }
        </style>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    # Índice de Compresión (Cc)
    with col1:
        st.markdown(
            """
            <div class="app-card">
                <div class="app-icon"><span class="app-emoji">📊</span></div>
                <div class="app-title">Índice de Compresión (Cc)</div>
                <div class="app-description">
                    Calcula el coeficiente de compresibilidad Cc utilizando diferentes correlaciones empíricas.
                </div>
            </div>
            """, unsafe_allow_html=True)
        # Subcolumnas para centrar el botón
        _, mid1, _ = st.columns([1, 2, 1])
        with mid1:
            if st.button("Abrir aplicación", key="cc_button"):
                st.session_state.current_page = "cc"
                st.rerun()

    # Ángulo de Rozamiento (φ)
    with col2:
        st.markdown(
            """
            <div class="app-card">
                <div class="app-icon">
                    <img src="https://cdn-icons-png.flaticon.com/512/4140/4140048.png" alt="Ángulo de rozamiento">
                </div>
                <div class="app-title">Ángulo de Rozamiento (φ)</div>
                <div class="app-description">
                    Calcula el ángulo de rozamiento utilizando diferentes correlaciones empíricas.
                </div>
            </div>
            """, unsafe_allow_html=True)
        _, mid2, _ = st.columns([1, 2, 1])
        with mid2:
            if st.button("Abrir aplicación", key="ar_button"):
                st.session_state.current_page = "angulo_rozamiento"
                st.rerun()

    # Módulo de Elasticidad (E)
    with col3:
        st.markdown(
            """
            <div class="app-card">
                <div class="app-icon">
                    <img src="https://cdn-icons-png.flaticon.com/512/3174/3174705.png" alt="Módulo de elasticidad">
                </div>
                <div class="app-title">Módulo de Elasticidad (E)</div>
                <div class="app-description">
                    Calcula el módulo de elasticidad para arenas utilizando diferentes fórmulas empíricas.
                </div>
            </div>
            """, unsafe_allow_html=True)
        _, mid3, _ = st.columns([1, 2, 1])
        with mid3:
            if st.button("Abrir aplicación", key="me_button"):
                st.session_state.current_page = "modulo_elasticidad"
                st.rerun()


if __name__ == "__main__":
    main()
