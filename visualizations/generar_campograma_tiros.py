import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

def generar_campograma_tiros(df_jugador, figsize=(9, 3)):  # Ajusta el alto aquí
    """
    Genera un campograma de tiros con altura reducida para un jugador específico.

    Parámetros:
    - df_jugador (DataFrame): DataFrame filtrado con los eventos del jugador. 
      Debe contener las columnas ['x', 'y', 'type'].
    - figsize (tuple): Tamaño de la figura Matplotlib (ancho, alto).

    Retorna:
    - fig: Objeto de la figura Matplotlib con el campograma de tiros.
    """
    # Filtrar solo eventos de tiro
    shot_events = df_jugador[df_jugador['type'].isin(['MissedShots', 'Goal', 'SavedShot'])]

    if shot_events.empty:
        raise ValueError("No se encontraron eventos de tiros para este jugador.")

    # Configurar el campo en orientación vertical y usando solo la mitad
    fig, ax = plt.subplots(figsize=figsize)  # Control explícito del tamaño del gráfico
    pitch = VerticalPitch(
        pitch_type='opta', pitch_color='black',
        line_color='white', half=True
    )
    pitch.draw(ax=ax)
    fig.set_facecolor('black')

    # Crear máscaras para cada tipo de tiro
    mask_missed = shot_events['type'] == 'MissedShots'
    mask_goal = shot_events['type'] == 'Goal'
    mask_saved = shot_events['type'] == 'SavedShot'

    # Graficar los tiros fallados (círculos rojos)
    pitch.scatter(
        shot_events[mask_missed]['x'], shot_events[mask_missed]['y'],
        s=50, c='red', edgecolors='black', linewidth=1, ax=ax, label='Missed Shots'
    )

    # Graficar los goles (estrellas doradas)
    pitch.scatter(
        shot_events[mask_goal]['x'], shot_events[mask_goal]['y'],
        s=100, c='gold', edgecolors='black', linewidth=1, marker='*', ax=ax, label='Goals'
    )

    # Graficar los tiros atajados (triángulos azules)
    pitch.scatter(
        shot_events[mask_saved]['x'], shot_events[mask_saved]['y'],
        s=50, c='blue', edgecolors='black', linewidth=1, marker='^', ax=ax, label='Saved Shots'
    )

    # Configurar la leyenda más pequeña
    ax.legend(
        facecolor='black', edgecolor='white', fontsize=6, loc='lower left', labelcolor='white'
    )

    return fig