import streamlit as st
from PIL import Image, ImageOps
import time
from login import check_password, logout

# Configuración de la página
st.set_page_config(page_title="Análisis Liverpool PL 2024-2025", layout="wide")

# Ocultar completamente el menú de navegación superior y otros elementos de Streamlit
hide_st_style = """
<style>
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    div[data-testid="stToolbar"] {visibility: hidden !important;}
    div[data-testid="stDecoration"] {visibility: hidden !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important;}
    
    /* Ocultar solo los elementos de navegación nativos de Streamlit, no el menú personalizado */
    div.stPathFinder {display: none !important;}
    
    /* Eliminar el botón de colapso de sidebar */
    button[kind="headerButton"] {
        display: none !important;
    }
    
    /* Ocultar enlaces del sidebar nativo pero mantener el resto del sidebar */
    section[data-testid="stSidebar"] > div:first-child > div:first-child > ul {
        display: none !important;
    }
    
    /* Asegurar que no hay padding extra en la parte superior */
    #root > div:nth-child(1) > div > div > div > div:nth-child(1) {
        padding-top: 0rem !important;
    }
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Diccionario de páginas
PAGINAS = {
    "Inicio": "inicio",
    "Estadísticas de Equipo": "pages.equipo",
    "Estadísticas por Jugador": "pages.jugadores",
}

# Eliminar fondo blanco de la imagen
def eliminar_fondo(logo_path):
    """Elimina el fondo blanco de una imagen."""
    try:
        image = Image.open(logo_path).convert("RGBA")
        datas = image.getdata()
        new_data = [
            (255, 255, 255, 0) if item[:3] == (255, 255, 255) else item for item in datas
        ]
        image.putdata(new_data)
        return image
    except Exception as e:
        st.warning(f"Error al procesar la imagen: {e}")
        return None

# Cargar la página seleccionada
def cargar_pagina(pagina):
    """Carga la página seleccionada desde el diccionario PAGINAS."""
    if pagina in PAGINAS:
        modulo = __import__(PAGINAS[pagina], fromlist=["main"])
        modulo.main()
    else:
        st.error("Página no encontrada. Por favor, selecciona otra opción.")

def main():
    """Función principal de la aplicación."""

    # Crear una fila con columnas para el título y el logo
    col1, col2 = st.columns([0.7, 0.3])

    with col1:
        st.markdown(
            "<h1 style='font-size: 48px; color: #c8102e; margin-top: 0px;'>Liverpool FC Premier League 2024-2025</h1>",
            unsafe_allow_html=True
        )

    with col2:
        try:
            logo_path = "./images/logo_liverpool_3.png"
            logo = eliminar_fondo(logo_path)
            if logo:
                st.image(logo, width=150)
        except FileNotFoundError as e:
            st.warning(f"⚠️ {e}")

    # Verificación de contraseña
    if check_password():
        # Menú de navegación (con control de duplicados)
        if "pagina_actual" not in st.session_state:
            st.session_state["pagina_actual"] = "Inicio"

        pagina = st.sidebar.selectbox(
            "Selecciona una página:",
            list(PAGINAS.keys()),
            index=list(PAGINAS.keys()).index(st.session_state["pagina_actual"]),
        )

        # Guardar la página seleccionada en sesión
        st.session_state["pagina_actual"] = pagina

        # Cargar la página seleccionada
        if pagina == "Inicio":
            st.markdown("<h2 style='margin-bottom: 20px;'>Análisis y Estadísticas de Equipo e Informe individual</h2>", unsafe_allow_html=True)

            # Mostrar la imagen del plantel sin fondo
            try:
                plantel_path = "./images/plantel_1.webp"
                plantel = eliminar_fondo(plantel_path)
                if plantel:
                    # Mejorar calidad y tamaño
                    high_quality_image = plantel.resize((600, 400), Image.LANCZOS)
                    st.image(high_quality_image, width=900)  # Ajustar el ancho deseado
            except FileNotFoundError as e:
                st.warning(f"⚠️ No se encontró la imagen del plantel: {e}")

        else:
            cargar_pagina(pagina)

        # Botón de cierre de sesión
        if st.sidebar.button("Cerrar Sesión"):
            logout()

if __name__ == "__main__":
    main()