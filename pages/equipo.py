import pandas as pd
import os
import streamlit as st
from visualizations.generar_ranking_defensivo import generar_ranking_defensivo, graficar_ranking_defensivo
from visualizations.generar_dispersion_pases import calcular_metricas_pases, graficar_dispersion_pases
from visualizations.generar_grafico_goles import calcular_goles_por_jugador, graficar_goles_torta

# Ruta de la carpeta de fotos de jugadores
fotos_dir = "./images/fotos_jugadores"

def obtener_foto_jugador(nombre):
    """Retorna la ruta de la foto del jugador si existe, o None si no se encuentra."""
    nombre_archivo = f"{nombre}.jpg"
    ruta_imagen = os.path.join(fotos_dir, nombre_archivo)
    return ruta_imagen if os.path.exists(ruta_imagen) else None

def mostrar_jugador_con_foto(jugador, valor, ancho_foto=60):
    """Muestra el jugador con su foto en la misma fila usando columnas en Streamlit."""
    col1, col2 = st.columns([1, 3])  # La imagen ocupará 1 parte, el texto 3 partes
    foto_jugador = obtener_foto_jugador(jugador)

    if foto_jugador:
        col1.image(foto_jugador, width=ancho_foto)

    col2.metric(jugador, valor)

def main():
    st.title("Análisis Global del Equipo")

    carpeta_partidos = "./data/partidos_liverpool"
    if not os.path.exists(carpeta_partidos) or not os.listdir(carpeta_partidos):
        st.error("No se encontraron datos de partidos. Asegúrate de ejecutar el scraping primero.")
        return

    # Inicializar estados de visibilidad para cada gráfico
    if "show_defensive_chart" not in st.session_state:
        st.session_state["show_defensive_chart"] = False
    if "show_dispersion_chart" not in st.session_state:
        st.session_state["show_dispersion_chart"] = False
    if "show_goles_chart" not in st.session_state:
        st.session_state["show_goles_chart"] = False

    # **1. Acciones Defensivas**
    ranking_defensivo = generar_ranking_defensivo(carpeta_partidos)
    if not ranking_defensivo.empty:
        st.markdown("<h3 style='color: red;'>Top 3 Jugadores en Acciones Defensivas</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        for i, col in enumerate([col1, col2, col3]):
            with col:
                mostrar_jugador_con_foto(ranking_defensivo.iloc[i]['player'], ranking_defensivo.iloc[i]['defensive_actions'])

        # Botón para mostrar/ocultar gráfico
        if st.button("Gráfico de Acciones Defensivas"):
            st.session_state["show_defensive_chart"] = not st.session_state["show_defensive_chart"]

        if st.session_state["show_defensive_chart"]:
            st.image(graficar_ranking_defensivo(ranking_defensivo), width=800)

    # **2. Métricas de Pases**
    metricas_pases = calcular_metricas_pases(carpeta_partidos, min_participacion=0.7)
    if not metricas_pases.empty:
        col1, col2 = st.columns(2)

        # **Porcentaje de Pases Exitosos**
        with col1:
            st.markdown("<h3 style='color: red;'>Top 3 en Porcentaje de Pases Exitosos</h3>", unsafe_allow_html=True)
            top_3_exitosos = metricas_pases.sort_values(by='porcentaje_exitoso', ascending=False).head(3)
            for i in range(min(3, len(top_3_exitosos))):
                mostrar_jugador_con_foto(
                    top_3_exitosos.iloc[i]['player'],
                    f"{top_3_exitosos.iloc[i]['porcentaje_exitoso']:.2f}%"
                )

        # **Pases Clasificados**
        with col2:
            st.markdown("<h3 style='color: red;'>Top 3 en Pases Clasificados</h3>", unsafe_allow_html=True)
            top_3_clasificados = metricas_pases.sort_values(by='pases_clasificados', ascending=False).head(3)
            for i in range(min(3, len(top_3_clasificados))):
                mostrar_jugador_con_foto(
                    top_3_clasificados.iloc[i]['player'],
                    top_3_clasificados.iloc[i]['pases_clasificados']
                )

        # Botón para mostrar/ocultar gráfico
        if st.button("Gráfico de Pases"):
            st.session_state["show_dispersion_chart"] = not st.session_state["show_dispersion_chart"]

        if st.session_state["show_dispersion_chart"]:
            st.image(graficar_dispersion_pases(metricas_pases), width=800)

    # **3. Goles**
    goles_df = calcular_goles_por_jugador(carpeta_partidos)
    if not goles_df.empty:
        st.markdown("<h3 style='color: red;'>Top 3 Goleadores</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        for i, col in enumerate([col1, col2, col3]):
            with col:
                if i < len(goles_df):
                    mostrar_jugador_con_foto(goles_df.iloc[i]['player'], goles_df.iloc[i]['goles'])

        # Botón para mostrar/ocultar gráfico
        if st.button("Gráfico de Goles"):
            st.session_state["show_goles_chart"] = not st.session_state["show_goles_chart"]

        if st.session_state["show_goles_chart"]:
            st.image(graficar_goles_torta(goles_df), width=800)

if __name__ == "__main__":
    main()
