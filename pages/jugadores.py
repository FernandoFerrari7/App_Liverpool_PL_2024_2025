import os
import pandas as pd
import streamlit as st
from scrapers.filtrar_eventos_por_jugador import filtrar_y_limpiar_eventos_jugador
from visualizations.generar_heatmap import generar_heatmap
from visualizations.generar_campograma_pases import generar_campograma_pases
from visualizations.generar_campograma_tiros import generar_campograma_tiros
from visualizations.generar_radar_chart import generate_radar_chart
import io
from fpdf import FPDF
import tempfile
import webbrowser
import base64
from PIL import Image

def obtener_jugadores_liverpool(input_folder, equipo="Liverpool"):
    jugadores = set()
    for archivo in os.listdir(input_folder):
        if archivo.endswith(".csv"):
            file_path = os.path.join(input_folder, archivo)
            try:
                df = pd.read_csv(file_path)
                if "player" in df.columns and "team" in df.columns:
                    jugadores.update(df[df["team"] == equipo]["player"].dropna().unique())
            except Exception as e:
                print(f"Error procesando {archivo}: {e}")
    return sorted(jugadores)

def calcular_estadisticas_por_jugador(df, jugador_seleccionado, equipo="Liverpool"):
    acciones_defensivas = len(df[(df['player'] == jugador_seleccionado) &
                                 (df['type'].isin(['Clearance', 'Tackle', 'BallRecovery', 'Interception']))])
    acciones_ofensivas = len(df[(df['player'] == jugador_seleccionado) &
                                 (df['type'].isin(['Pass', 'Goal', 'MissedShots', 'SavedShot', 'ShotOnPost']))])
    total_pases = len(df[(df['player'] == jugador_seleccionado) & (df['type'] == 'Pass')])
    pases_exitosos = len(df[(df['player'] == jugador_seleccionado) &
                            (df['type'] == 'Pass') &
                            (df['outcome_type'] == 'Successful')])
    porcentaje_pases_exitosos = round((pases_exitosos / total_pases * 100) if total_pases > 0 else 0, 2)
    pases_clasificados = len(df[(df['player'] == jugador_seleccionado) &
                                 (df['type'] == 'Pass') &
                                 (df['qualifiers'].str.contains('KeyPass|IntentionalAssist', na=False))])
    missed_shots = len(df[(df['player'] == jugador_seleccionado) & (df['type'] == 'MissedShots')])
    saved_shots = len(df[(df['player'] == jugador_seleccionado) & (df['type'] == 'SavedShot')])
    goals = len(df[(df['player'] == jugador_seleccionado) & (df['type'] == 'Goal')])

    return {
        "acciones_defensivas": acciones_defensivas,
        "acciones_ofensivas": acciones_ofensivas,
        "porcentaje_pases_exitosos": porcentaje_pases_exitosos,
        "pases_clasificados": pases_clasificados,
        "missed_shots": missed_shots,
        "saved_shots": saved_shots,
        "goals": goals,
    }

def fig_to_buffer(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
    buffer.seek(0)
    return buffer

def fig_to_base64(fig, dpi=150):
    # Convierte la figura matplotlib a una imagen base64 para HTML
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{img_str}"

def generate_pdf(jugador_seleccionado, stats, fig_radar, fig_heatmap, fig_pases, fig_tiros):
    pdf = FPDF()
    pdf.add_page()
    
    # Configuración de la página
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Título
    pdf.set_font("Arial", "B", size=16)
    pdf.cell(200, 10, txt=f"{jugador_seleccionado} - Premier League 24/25", ln=1, align='C')
    pdf.ln(10)
    
    # Estadísticas principales
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(200, 10, txt="Estadísticas del Jugador", ln=1, align='L')
    pdf.set_font("Arial", size=10)
    
    # Primera fila de estadísticas
    pdf.cell(100, 10, txt=f"Acciones Defensivas: {stats['acciones_defensivas']}", ln=0)
    pdf.cell(100, 10, txt=f"Acciones Ofensivas: {stats['acciones_ofensivas']}", ln=1)
    
    # Segunda fila de estadísticas
    pdf.cell(100, 10, txt=f"Pases Exitosos: {stats['porcentaje_pases_exitosos']}%", ln=0)
    pdf.cell(100, 10, txt=f"Pases Clasificados: {stats['pases_clasificados']}", ln=1)
    
    # Estadísticas de tiros
    pdf.ln(5)
    pdf.set_font("Arial", "B", size=12)
    pdf.cell(200, 10, txt="Resumen de Tiros", ln=1, align='L')
    pdf.set_font("Arial", size=10)
    pdf.cell(70, 10, txt=f"Missed Shots: {stats['missed_shots']}", ln=0)
    pdf.cell(70, 10, txt=f"Saved Shots: {stats['saved_shots']}", ln=0)
    pdf.cell(60, 10, txt=f"Goals: {stats['goals']}", ln=1)
    
    # Agrupar imágenes en pares
    image_pairs = [
        [('Radar Chart', fig_radar), ('Heat Map', fig_heatmap)],
        [('Mapa de Pases', fig_pases), ('Mapa de Tiros', fig_tiros)]
    ]
    
    for pair in image_pairs:
        pdf.ln(10)
        for i, (title, fig) in enumerate(pair):
            # Guardar figura temporalmente
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            fig.savefig(temp_img.name, format='png', bbox_inches='tight', dpi=300)
            
            # Título de la imagen
            pdf.set_font("Arial", "B", size=12)
            if i == 0:
                pdf.cell(95, 10, txt=title, ln=0, align='L')
            else:
                pdf.cell(95, 10, txt=title, ln=1, align='L')
            
            # Agregar imagen al PDF
            if i == 0:
                pdf.image(temp_img.name, x=10, y=pdf.get_y()+10, w=90)
            else:
                pdf.image(temp_img.name, x=110, y=pdf.get_y(), w=90)
                pdf.ln(70)  # Espacio para la siguiente fila de imágenes
            
            # Cerrar y eliminar archivo temporal
            temp_img.close()
            os.unlink(temp_img.name)
    
    # Guardar PDF y abrirlo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        webbrowser.open('file://' + tmp.name)

def print_page(jugador_seleccionado, stats, fig_radar, fig_heatmap, fig_pases, fig_tiros):
    """
    Genera una página HTML optimizada para impresión con las visualizaciones y estadísticas
    del jugador seleccionado. Todo el contenido está diseñado para caber en una sola página.
    """
    # Convertir figuras a base64 para incluirlas en HTML
    # Usar menor DPI para reducir el tamaño de las imágenes y garantizar que todo quepa en una página
    radar_img = fig_to_base64(fig_radar, dpi=120) if fig_radar else ""
    heatmap_img = fig_to_base64(fig_heatmap, dpi=120) if fig_heatmap else ""
    pases_img = fig_to_base64(fig_pases, dpi=120) if fig_pases else ""
    tiros_img = fig_to_base64(fig_tiros, dpi=120) if fig_tiros else ""
    
    # Crear HTML para impresión con ajustes de tamaño y diseño optimizados para una sola página
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{jugador_seleccionado} - Liverpool Premier League 24/25</title>
        <style>
            @media print {{
                @page {{ 
                    size: landscape; 
                    margin: 0.1cm; /* Reducir más los márgenes */
                }}
                body {{ 
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    font-size: 8pt; /* Reducir más el tamaño de texto */
                    max-height: 100vh;
                    overflow: hidden;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 2px; 
                    padding-top: 2px;
                    height: 20px;
                }}
                .content-wrapper {{
                    display: flex;
                    flex-direction: column;
                    height: 95vh;
                    max-height: 95vh;
                    overflow: hidden;
                }}
                .top-section {{
                    display: flex;
                    height: 10vh;
                    max-height: 10vh;
                    overflow: hidden;
                }}
                .stats-container {{ 
                    display: flex; 
                    justify-content: space-between; 
                    width: 100%;
                    margin: 0;
                    padding: 0;
                }}
                .stats-box {{ 
                    width: 48%; 
                    padding: 3px;
                    border: 1px solid #ddd; 
                    border-radius: 3px; 
                }}
                .stats-box p {{
                    margin: 1px 0;
                    line-height: 1.1;
                }}
                .charts-container {{
                    display: flex;
                    flex-direction: column;
                    height: 85vh;
                    max-height: 85vh;
                    width: 100%;
                    overflow: hidden;
                }}
                .charts-row {{
                    display: flex;
                    justify-content: space-between;
                    height: 42vh;
                    max-height: 42vh;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                .chart-box {{ 
                    width: 49%; 
                    text-align: center; 
                    position: relative;
                    height: 100%;
                    overflow: hidden;
                }}
                .chart-box h2 {{
                    margin: 0;
                    padding: 0;
                    font-size: 9pt;
                    height: 12px;
                }}
                .chart-img-container {{
                    height: calc(100% - 12px);
                    width: 100%;
                    position: relative;
                    overflow: hidden;
                }}
                .chart-img {{
                    max-height: 100%;
                    max-width: 100%;
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    margin: auto;
                    object-fit: contain;
                }}
                h1 {{ 
                    color: #c8102e; /* Liverpool red */
                    font-size: 12pt;
                    margin: 0;
                    padding: 0;
                }}
                h2 {{ 
                    color: #0a0a0a; 
                    margin: 0;
                    padding: 0;
                    font-size: 9pt;
                }}
            }}
            
            /* Estilos para visualización en pantalla antes de imprimir */
            body {{ 
                font-family: Arial, sans-serif; 
                margin: 10px; 
                padding: 0;
            }}
            .header {{ 
                text-align: center; 
                margin-bottom: 10px; 
            }}
            .content-wrapper {{
                display: flex;
                flex-direction: column;
            }}
            .top-section {{
                display: flex;
            }}
            .stats-container {{ 
                display: flex; 
                justify-content: space-between; 
                width: 100%;
                margin-bottom: 5px;
            }}
            .stats-box {{ 
                width: 48%; 
                padding: 5px; 
                border: 1px solid #ddd; 
                border-radius: 5px; 
            }}
            .stats-box p {{
                margin: 4px 0;
            }}
            .charts-container {{
                display: flex;
                flex-direction: column;
                width: 100%;
            }}
            .charts-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
            }}
            .chart-box {{ 
                width: 49%; 
                text-align: center; 
            }}
            .chart-box h2 {{
                margin: 3px 0;
            }}
            .chart-img-container {{
                width: 100%;
                height: 300px;
                position: relative;
            }}
            .chart-img {{
                max-width: 100%;
                max-height: 100%;
                object-fit: contain;
            }}
            h1 {{ 
                color: #c8102e; /* Liverpool red */
                margin: 5px 0;
            }}
            h2 {{ 
                color: #0a0a0a; 
                margin: 4px 0;
            }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="content-wrapper">
            <div class="header">
                <h1>{jugador_seleccionado} - Liverpool Premier League 24/25</h1>
            </div>
            
            <div class="top-section">
                <div class="stats-container">
                    <div class="stats-box">
                        <h2>Estadísticas del Jugador</h2>
                        <p>Acciones Defensivas: {stats['acciones_defensivas']}</p>
                        <p>Acciones Ofensivas: {stats['acciones_ofensivas']}</p>
                        <p>Pases Exitosos: {stats['porcentaje_pases_exitosos']}%</p>
                        <p>Pases Clasificados: {stats['pases_clasificados']}</p>
                    </div>
                    <div class="stats-box">
                        <h2>Resumen de Tiros</h2>
                        <p>Missed Shots: {stats['missed_shots']}</p>
                        <p>Saved Shots: {stats['saved_shots']}</p>
                        <p>Goals: {stats['goals']}</p>
                    </div>
                </div>
            </div>
            
            <div class="charts-container">
                <div class="charts-row">
                    <div class="chart-box">
                        <h2>Radar Chart</h2>
                        <div class="chart-img-container">
                            <img src="{radar_img}" alt="Radar Chart" class="chart-img">
                        </div>
                    </div>
                    <div class="chart-box">
                        <h2>Heat Map</h2>
                        <div class="chart-img-container">
                            <img src="{heatmap_img}" alt="Heat Map" class="chart-img">
                        </div>
                    </div>
                </div>
                
                <div class="charts-row">
                    <div class="chart-box">
                        <h2>Mapa de Pases</h2>
                        <div class="chart-img-container">
                            <img src="{pases_img}" alt="Mapa de Pases" class="chart-img">
                        </div>
                    </div>
                    <div class="chart-box">
                        <h2>Mapa de Tiros</h2>
                        <div class="chart-img-container">
                            <img src="{tiros_img}" alt="Mapa de Tiros" class="chart-img">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Crear archivo HTML temporal y abrirlo en el navegador
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as f:
        f.write(html)
        filename = f.name
    
    # Abrir el archivo HTML en una nueva pestaña del navegador
    webbrowser.open('file://' + filename)

def main():
    st.title("Análisis de Jugadores")

    input_folder = "./data/partidos_liverpool"
    output_folder = "./data/jugadores"

    if not os.path.exists(input_folder) or not os.listdir(input_folder):
        st.error("No se encontraron datos de partidos. Asegúrate de ejecutar el scraping primero.")
        return

    jugadores_disponibles = obtener_jugadores_liverpool(input_folder)
    if not jugadores_disponibles:
        st.error("No se encontraron jugadores en los archivos de datos.")
        return

    jugador_seleccionado = st.selectbox(
        "Selecciona un jugador",
        jugadores_disponibles,
        label_visibility="visible",
        key="jugador_seleccionado",
    )

    if jugador_seleccionado:
        sanitized_name = jugador_seleccionado.lower().replace(" ", "_")
        archivo_filtrado = os.path.join(output_folder, f"{sanitized_name}_eventos.csv")

        if not os.path.exists(archivo_filtrado):
            archivo_filtrado = filtrar_y_limpiar_eventos_jugador(input_folder, output_folder, jugador_seleccionado)

        if archivo_filtrado and os.path.exists(archivo_filtrado):
            df_jugador = pd.read_csv(archivo_filtrado)
            if df_jugador.empty:
                st.warning(f"No se encontraron eventos para el jugador {jugador_seleccionado}.")
                return

            stats = calcular_estadisticas_por_jugador(df_jugador, jugador_seleccionado)

            try:
                params = ['Goals', '% Pass Successful', '% Take On Successful', 'Dispossessed',
                          '% Aerial Successful', '% Tackle Successful', 'Ball Recovery',
                          'Interception', 'Clearance']
                min_range = [0] * len(params)
                max_range = [10, 100, 100, 5, 100, 100, 10, 10, 10]
                fig_radar = generate_radar_chart(df_jugador, params, min_range, max_range)
            except Exception as e:
                st.error(f"Error generando radar chart: {e}")
                fig_radar = None

            try:
                fig_heatmap = generar_heatmap(df_jugador)
            except Exception as e:
                st.error(f"Error generando heatmap: {e}")
                fig_heatmap = None

            try:
                fig_pases = generar_campograma_pases(df_jugador)
            except Exception as e:
                st.error(f"Error generando campograma de pases: {e}")
                fig_pases = None

            try:
                fig_tiros = generar_campograma_tiros(df_jugador)
            except Exception as e:
                st.error(f"Error generando campograma de tiros: {e}")
                fig_tiros = None

            # Primera fila
            col1, col2, col3 = st.columns([1, 2, 1], gap="small")

            with col1:
                st.markdown("<div style='margin-top: 60px; margin-left: 40px;'>", unsafe_allow_html=True)
                col1.metric("Acciones Defensivas", stats["acciones_defensivas"])
                col1.metric("Acciones Ofensivas", stats["acciones_ofensivas"])
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                if fig_radar is not None:
                    st.image(fig_to_buffer(fig_radar), width=350)

            with col3:
                # Añadir margen superior para alinear con el radar chart
                st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
                
                # Buscar imagen del jugador
                player_img_path = f"images/fotos_jugadores/{jugador_seleccionado}.jpg"
                if os.path.exists(player_img_path):
                    # Si existe la foto, mostrarla
                    img = Image.open(player_img_path)
                    st.image(img, width=120)  # Reducir el tamaño a 120px
                else:
                    # Si no existe, buscar alternativas de nombre
                    found = False
                    for filename in os.listdir("images/fotos_jugadores"):
                        if filename.lower().endswith(".jpg"):
                            nombre_archivo = os.path.splitext(filename)[0].lower()
                            nombre_jugador = jugador_seleccionado.lower()
                            
                            # Verificar si el nombre del archivo contiene el nombre del jugador o viceversa
                            if nombre_jugador in nombre_archivo or all(part in nombre_archivo for part in nombre_jugador.split()):
                                img = Image.open(f"images/fotos_jugadores/{filename}")
                                st.image(img, width=120)  # Reducir el tamaño a 120px
                                st.markdown(f"<div style='text-align: center; font-weight: bold; color: #c8102e;'>{jugador_seleccionado}</div>", unsafe_allow_html=True)
                                found = True
                                break
                    
                    # Si no se encontró ninguna coincidencia, mostrar un placeholder
                    if not found:
                        st.markdown("<div style='width: 120px; height: 120px; background-color: #f0f0f0; display: flex; justify-content: center; align-items: center; border-radius: 50%; margin: 0 auto;'>Sin imagen</div>", unsafe_allow_html=True)

            # Segunda fila
            col1, col2, col3 = st.columns([1.5, 1, 1.5], gap="small")

            with col1:
                if fig_heatmap is not None:
                    st.image(fig_to_buffer(fig_heatmap))

            with col2:
                # Contenedor centrado con ancho fijo
                st.markdown("""
                    <div style='
                        margin-left: 40px;
                        text-align: center;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        width: 100%;
                    '>
                """, unsafe_allow_html=True)
                
                # Estilo para las métricas
                st.markdown("""
                    <style>
                        [data-testid="stMetricValue"] {
                            text-align: center;
                            width: 100%;
                            display: flex;
                            justify-content: center;
                        }
                        [data-testid="stMetricLabel"] {
                            text-align: center;
                            width: 100%;
                            display: flex;
                            justify-content: center;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                col2.metric("% Pases Exitosos", f"{stats['porcentaje_pases_exitosos']}%")
                col2.metric("Pases Clasificados", stats["pases_clasificados"])
                st.markdown("</div>", unsafe_allow_html=True)

            with col3:
                if fig_pases is not None:
                    st.image(fig_to_buffer(fig_pases))

            # Tercera fila
            col1, col2 = st.columns([1, 1], gap="medium")

            with col1:
                if fig_tiros is not None:
                    st.image(fig_to_buffer(fig_tiros), width=400)

            with col2:
                # Añadimos espacio vertical antes del resumen de tiros
                st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
                st.markdown("#### Resumen de Tiros")
                col21, col22, col23 = st.columns(3, gap="small")
                col21.metric("Missed Shots", stats["missed_shots"])
                col22.metric("Saved Shots", stats["saved_shots"])
                col23.metric("Goals", stats["goals"])
                
                # Más espacio antes de los botones
                st.markdown("<div style='margin-top: 50px;'>", unsafe_allow_html=True)
                btn_col1, btn_col2 = st.columns(2)
                
                # Estilo personalizado para los botones
                button_style = """
                <style>
                div[data-testid="stButton"] button {
                    background-color: #ffebee;
                    color: #d32f2f;
                    border: 1px solid #d32f2f;
                    margin-top: 20px;
                }
                div[data-testid="stButton"] button:hover {
                    background-color: #ffcdd2;
                    color: #b71c1c;
                    border: 1px solid #b71c1c;
                }
                </style>
                """
                st.markdown(button_style, unsafe_allow_html=True)
                
                # Botones con sus respectivas funciones
                with btn_col1:
                    if st.button("🖨️ Imprimir", key="print_button"):
                        if all([fig_radar, fig_heatmap, fig_pases, fig_tiros]):
                            print_page(jugador_seleccionado, stats, 
                                      fig_radar, fig_heatmap, fig_pases, fig_tiros)
                        else:
                            st.error("No se pudieron generar todas las visualizaciones necesarias para imprimir")
                
                with btn_col2:
                    if st.button("📄 Generar PDF", key="pdf_button"):
                        if all([fig_radar, fig_heatmap, fig_pases, fig_tiros]):
                            generate_pdf(jugador_seleccionado, stats, 
                                      fig_radar, fig_heatmap, fig_pases, fig_tiros)
                        else:
                            st.error("No se pudieron generar todas las visualizaciones necesarias para el PDF")
                st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()