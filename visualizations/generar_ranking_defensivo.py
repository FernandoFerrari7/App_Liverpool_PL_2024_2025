import os
import pandas as pd
import matplotlib.pyplot as plt
import io

# Variables defensivas que vamos a analizar
defensive_actions = ['Clearance', 'Tackle', 'BallRecovery', 'Interception']

def generar_ranking_defensivo(carpeta_partidos):
    """
    Genera un ranking de acciones defensivas de los jugadores del Liverpool.
    """
    all_defensive_data = []

    for archivo in os.listdir(carpeta_partidos):
        if archivo.endswith('.csv'):
            file_path = os.path.join(carpeta_partidos, archivo)
            data = pd.read_csv(file_path)
            liverpool_defensive_actions = data[
                (data['type'].isin(defensive_actions)) & (data['team'] == 'Liverpool')
            ]
            all_defensive_data.append(liverpool_defensive_actions)

    all_defensive_data = pd.concat(all_defensive_data, ignore_index=True)
    ranking = all_defensive_data.groupby('player').size().reset_index(name='defensive_actions')
    ranking = ranking.sort_values(by='defensive_actions', ascending=False)
    return ranking

def graficar_ranking_defensivo(ranking):
    """
    Genera un gráfico de barras con el ranking de acciones defensivas.
    """
    fig, ax = plt.subplots(figsize=(6, 4))  # Ajusta tamaño
    ax.bar(ranking['player'], ranking['defensive_actions'], color='red', alpha=0.7)

    # Configuración del diseño
    ax.set_xticklabels(ranking['player'], rotation=45, ha='right', fontsize=8)
    ax.tick_params(axis='both', labelsize=8)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100)
    plt.close(fig)
    buffer.seek(0)
    return buffer