import os
import pandas as pd
import matplotlib.pyplot as plt
import io

# Lista de subtipos considerados como "pases clasificados"
TIPOS_PASES_IMPORTANTES = [
    "IntentionalAssist", "IntentionalGoalAssist", "KeyPass", "ShotAssist", "BigChanceCreated"
]

def calcular_metricas_pases(carpeta_partidos, min_participacion=0.7):
    """
    Calcula métricas de pases por jugador, filtrando solo aquellos que han participado
    en al menos un porcentaje mínimo de partidos.
    
    Args:
        carpeta_partidos: Ruta a la carpeta con los archivos CSV de los partidos
        min_participacion: Porcentaje mínimo de partidos en los que debe participar (0.7 = 70%)
    
    Returns:
        DataFrame con las métricas de pases por jugador
    """
    # Obtener lista de archivos de partidos
    archivos_partidos = [f for f in os.listdir(carpeta_partidos) if f.endswith('.csv')]
    total_partidos = len(archivos_partidos)
    min_partidos_requeridos = int(total_partidos * min_participacion)
    
    # Diccionario para contar participación en partidos
    participacion_jugadores = {}
    
    # Lista para almacenar los datos de cada partido
    all_data = []
    
    # Procesar cada archivo de partido
    for archivo in archivos_partidos:
        file_path = os.path.join(carpeta_partidos, archivo)
        data = pd.read_csv(file_path)
        all_data.append(data)
        
        # Contar participación de jugadores en este partido
        jugadores_partido = data[data['team'] == 'Liverpool']['player'].unique()
        for jugador in jugadores_partido:
            if jugador not in participacion_jugadores:
                participacion_jugadores[jugador] = 0
            participacion_jugadores[jugador] += 1
    
    # Combinar todos los datos
    all_data = pd.concat(all_data, ignore_index=True)
    liverpool_pases = all_data[(all_data['type'] == 'Pass') & (all_data['team'] == 'Liverpool')]

    # Procesar los pases clasificados según los tipos importantes
    liverpool_pases['pases_clasificados'] = liverpool_pases['qualifiers'].apply(
        lambda x: any(tipo in str(x) for tipo in TIPOS_PASES_IMPORTANTES)
    )

    # Calcular métricas por jugador
    metricas = (
        liverpool_pases.groupby('player')
        .agg(
            total_pases=('type', 'count'),
            pases_exitosos=('outcome_type', lambda x: (x == 'Successful').sum()),
            pases_clasificados=('pases_clasificados', 'sum')
        )
    )
    metricas['porcentaje_exitoso'] = (metricas['pases_exitosos'] / metricas['total_pases']) * 100
    metricas = metricas.reset_index()
    
    # Añadir datos de participación
    metricas['partidos_jugados'] = metricas['player'].apply(lambda x: participacion_jugadores.get(x, 0))
    
    # Filtrar solo los jugadores que cumplen con el mínimo de participación
    metricas_filtradas = metricas[metricas['partidos_jugados'] >= min_partidos_requeridos]
    
    return metricas_filtradas

def graficar_dispersion_pases(metricas_df):
    """
    Genera un gráfico de dispersión ajustado para evitar solapamientos de etiquetas.
    """
    fig, ax = plt.subplots(figsize=(6, 4))  # Tamaño ajustado
    ax.scatter(
        metricas_df['pases_clasificados'], metricas_df['porcentaje_exitoso'],
        color='red', alpha=0.7, s=30
    )

    # Agregar etiquetas con un pequeño offset dinámico
    for i, player in enumerate(metricas_df['player']):
        ax.text(
            metricas_df['pases_clasificados'].iloc[i], 
            metricas_df['porcentaje_exitoso'].iloc[i] + 0.5,  # Offset hacia arriba
            player, fontsize=6, ha='center', va='bottom', color='black',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle="round,pad=0.1")
        )

    # Configurar los ejes
    ax.set_xlabel('Pases Clasificados', fontsize=8)
    ax.set_ylabel('% Pases Exitosos', fontsize=8)
    ax.tick_params(axis='both', labelsize=7)  # Reducir tamaño de las etiquetas de los ejes

    # Mejorar espaciado
    plt.tight_layout()

    # Guardar la figura en un buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100)
    plt.close(fig)
    buffer.seek(0)
    return buffer