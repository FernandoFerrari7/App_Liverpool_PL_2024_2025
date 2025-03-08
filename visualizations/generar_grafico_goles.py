import os
import pandas as pd
import matplotlib.pyplot as plt
import io

def calcular_goles_por_jugador(carpeta_partidos):
    all_data = []
    for archivo in os.listdir(carpeta_partidos):
        if archivo.endswith('.csv'):
            file_path = os.path.join(carpeta_partidos, archivo)
            data = pd.read_csv(file_path)
            all_data.append(data)

    all_data = pd.concat(all_data, ignore_index=True)
    goles_liverpool = all_data[
        (all_data['type'] == 'Goal') & (all_data['team'] == 'Liverpool')
    ]

    goles_por_jugador = goles_liverpool['player'].value_counts().reset_index()
    goles_por_jugador.columns = ['player', 'goles']
    return goles_por_jugador

def graficar_goles_torta(goles_df):
    """
    Genera un gráfico de torta con colores en tonalidades de rojo y lo guarda en un buffer.
    """
    # Englobar jugadores con un solo gol en 'Otros'
    goles_df.loc[goles_df['goles'] == 1, 'player'] = 'Otros'
    goles_torta = goles_df.groupby('player')['goles'].sum().reset_index()

    # Definir una paleta de colores en tonalidades de rojo
    colores_rojos = ['#FF6F61', '#E63946', '#D72638', '#BA1B1D', '#8B0000', '#FF3B3F']

    # Ajustar la cantidad de colores a los jugadores
    colores = colores_rojos[:len(goles_torta)]

    # Crear el gráfico de torta
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(
        goles_torta['goles'], labels=goles_torta['player'], autopct='%1.1f%%',
        startangle=140, colors=colores, textprops={'fontsize': 8}
    )

    # Guardar la figura en un buffer
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100)
    plt.close(fig)
    buffer.seek(0)
    return buffer