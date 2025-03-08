import matplotlib.pyplot as plt
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter

def generar_heatmap(df_jugador, figsize=(9, 7)):
    """
    Genera un heatmap para un jugador basado en las coordenadas x, y.

    Parámetros:
    - df_jugador (DataFrame): DataFrame con los eventos del jugador, que contiene las columnas 'x' y 'y'.
    - figsize (tuple): Tamaño de la figura Matplotlib.

    Retorna:
    - fig: Objeto de la figura Matplotlib con el heatmap.
    """
    # Verificar que las columnas 'x' y 'y' existan en el DataFrame
    if 'x' not in df_jugador.columns or 'y' not in df_jugador.columns:
        raise ValueError("El DataFrame debe contener las columnas 'x' y 'y'.")

    # Filtrar las columnas necesarias para el heatmap
    heatmap_data = df_jugador[['x', 'y']].dropna()

    # Configurar el campo
    pitch = Pitch(
        pitch_type='opta', 
        axis=False,         
        label=False,        
        pitch_color='#22312b', 
        line_color='white'
    )

    # Dibujar el campo
    fig, ax = pitch.draw(figsize=figsize)
    fig.set_facecolor('black')  # Fondo de la figura

    # Crear los datos del mapa de calor acumulado
    bin_statistic = pitch.bin_statistic(
        heatmap_data['x'], heatmap_data['y'],
        statistic='count', bins=(25, 25)
    )
    bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)

    # Dibujar el mapa de calor con transparencia
    pcm = pitch.heatmap(bin_statistic, ax=ax, cmap='hot', edgecolors='#22312b', alpha=0.7)

    # Agregar la barra de color
    cbar = fig.colorbar(pcm, ax=ax, shrink=0.6)
    cbar.outline.set_edgecolor('white')  
    cbar.ax.yaxis.set_ticks([])          
    cbar.ax.set_facecolor('#22312b')     

    return fig