import streamlit as st
import time
from PIL import Image

def check_password():
    """Verifica la contraseña y maneja el estado de la sesión."""
    if "login_time" not in st.session_state:
        st.session_state.login_time = None

    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        # Verificar si han pasado más de 30 minutos desde el último login
        if st.session_state.login_time and time.time() - st.session_state.login_time > 1800:
            st.session_state.password_correct = False
            st.session_state.login_time = None

    if not st.session_state.password_correct:
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if password == "admin":
                st.session_state.password_correct = True
                st.session_state.login_time = time.time()
                st.rerun()
            else:
                st.error("😕 Contraseña incorrecta")
        return False
    return True

def logout():
    """Cierra la sesión del usuario."""
    st.session_state.password_correct = False
    st.session_state.login_time = None
    st.rerun()

# Aplicación principal
def main():
    # Encabezado con título y logo alineado
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown(
            "<h1 style='font-size: 42px; color: #c8102e; text-align: left;'>Liverpool FC Premier League 2024-2025</h1>",
            unsafe_allow_html=True
        )
    with col2:
        try:
            logo_path = "./images/liverpool_3.png"
            logo = Image.open(logo_path)
            st.image(logo, width=180)  # Tamaño del logo
        except Exception:
            st.warning("⚠️ Logo no encontrado")

    # Verificación de contraseña
    if check_password():
        st.success("Bienvenido al análisis deportivo!")

        # Contenido protegido
        st.write("Aquí va el contenido principal de tu aplicación...")

        # Botón de cierre de sesión
        if st.button("Cerrar Sesión"):
            logout()

if __name__ == "__main__":
    main()





