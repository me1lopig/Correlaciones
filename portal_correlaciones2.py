import streamlit as st

def main():
    st.set_page_config(page_title="Portal de Correlaciones Geotécnicas", layout="wide")

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "portal"

    if st.session_state.current_page == "portal":
        show_portal()
    elif st.session_state.current_page == "cc":
        try:
            import Cc_streamlit_1
            Cc_streamlit_1.main()
            if st.button("Volver al Portal"):
                st.session_state.current_page = "portal"
                st.rerun()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Índice de Compresión (Cc).")
    elif st.session_state.current_page == "angulo_rozamiento":
        try:
            import angulo_rozamiento_streamlit
            angulo_rozamiento_streamlit.main()
            if st.button("Volver al Portal"):
                st.session_state.current_page = "portal"
                st.rerun()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Ángulo de Rozamiento (φ).")
    elif st.session_state.current_page == "modulo_elasticidad":
        try:
            import modulo_elasticidad_arenas_streamlit
            modulo_elasticidad_arenas_streamlit.main()
            if st.button("Volver al Portal"):
                st.session_state.current_page = "portal"
                st.rerun()
        except ImportError:
            st.error("No se pudo cargar la aplicación de Módulo de Elasticidad (E).")

def show_portal():
    st.title("Portal de Correlaciones Geotécnicas")
    st.markdown("Selecciona una de las siguientes aplicaciones para calcular diferentes parámetros geotécnicos:")

    st.markdown(
        """
        <style>
        .app-container {
            text-align: center;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 10px;
            margin: 10px;
            cursor: pointer;
            transition: transform 0.2s;
            background-color: #f9f9f9;
            height: 250px;
        }
        .app-container:hover {
            transform: scale(1.05);
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .app-icon {
            font-size: 100px;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("", key="cc_button", use_container_width=True):
            st.session_state.current_page = "cc"
            st.rerun()
        st.markdown(
            """
            <div class="app-container">
                <div class="app-icon">📊</div>
                <h3>Índice de Compresión (Cc)</h3>
                <p>Calcula el coeficiente de compresibilidad Cc utilizando diferentes correlaciones empíricas.</p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if st.button("", key="ar_button", use_container_width=True):
            st.session_state.current_page = "angulo_rozamiento"
            st.rerun()
        st.markdown(
            """
            <div class="app-container">
                <div class="app-icon">📉</div>
                <h3>Ángulo de Rozamiento (φ)</h3>
                <p>Calcula el ángulo de rozamiento utilizando diferentes correlaciones empíricas.</p>
            </div>
            """, unsafe_allow_html=True)

    with col3:
        if st.button("", key="me_button", use_container_width=True):
            st.session_state.current_page = "modulo_elasticidad"
            st.rerun()
        st.markdown(
            """
            <div class="app-container">
                <div class="app-icon">🧪</div>
                <h3>Módulo de Elasticidad (E)</h3>
                <p>Calcula el módulo de elasticidad para arenas utilizando diferentes fórmulas empíricas.</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

