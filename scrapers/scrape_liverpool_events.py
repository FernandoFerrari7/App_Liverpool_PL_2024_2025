import os
import pandas as pd
import ssl
from datetime import date
from soccerdata import WhoScored

# Configuración para evitar problemas de SSL
ssl._create_default_https_context = ssl._create_unverified_context

def scrape_liverpool_events():
    """
    Scrapea los eventos de los partidos del Liverpool en la temporada actual 
    y guarda cada partido en un archivo CSV dentro de la carpeta correspondiente.
    """
    print("[INFO] Iniciando scraping de partidos del Liverpool...")

    # Temporada actual
    temporada_actual = 2024

    # Inicializar el scraper para la Premier League
    ws = WhoScored(leagues=["ENG-Premier League"], seasons=[temporada_actual])
    equipo = "Liverpool"

    # Obtener el calendario de partidos
    calendario = ws.read_schedule()

    # Filtrar los partidos del equipo
    partidos_liverpool = calendario[
        (calendario["home_team"] == equipo) | (calendario["away_team"] == equipo)
    ]

    # Verificar si hay partidos disponibles
    if partidos_liverpool.empty:
        print(f"[INFO] No se encontraron partidos para {equipo}.")
        ws.close()
        return

    # Crear carpeta para guardar los partidos
    carpeta_destino = f"data/partidos_{equipo.lower()}"
    os.makedirs(carpeta_destino, exist_ok=True)

    # Verificar archivos existentes para evitar duplicados
    archivos_existentes = os.listdir(carpeta_destino)
    nuevos_partidos = 0
    partidos_sin_eventos = 0  # Contador de partidos consecutivos sin eventos

    for _, partido in partidos_liverpool.iterrows():
        try:
            # Identificar el ID del partido y el rival
            match_id = int(partido["game_id"])
            home_team = partido["home_team"]
            away_team = partido["away_team"]

            # Crear nombre del archivo respetando el orden local vs visitante
            filename = f"{home_team.lower()}_vs_{away_team.lower()}.csv"
            file_path = os.path.join(carpeta_destino, filename)

            # Si el archivo ya existe, pasar al siguiente partido
            if filename in archivos_existentes:
                print(f"[INFO] Partido ya procesado: {filename}")
                continue

            print(f"[INFO] Procesando partido: {home_team} vs {away_team}")

            # Obtener los eventos del partido
            eventos = ws.read_events(match_id)

            # Si hay eventos, reiniciar el contador de partidos sin eventos
            partidos_sin_eventos = 0

            # Guardar los eventos en un archivo CSV
            eventos.to_csv(file_path, index=False)
            print(f"[INFO] Archivo guardado: {file_path}")
            nuevos_partidos += 1

        except Exception as e:
            print(f"[ERROR] Error procesando el partido {match_id}: {str(e)}")
            continue

    # Resumen de la ejecución
    if nuevos_partidos == 0:
        print(f"[INFO] No se encontraron nuevos partidos para guardar.")
    else:
        print(f"[INFO] Se guardaron {nuevos_partidos} nuevos partidos.")
    
    # Cerrar el navegador del scraper
    ws.close()

# Ejecutar el script directamente
if __name__ == "__main__":
    scrape_liverpool_events()