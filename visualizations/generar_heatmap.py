import matplotlib.pyplot as plt
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
import functools

# Diccionario para caché de heatmaps
HEATMAP_CACHE = {}

# Decorador para caché
def cache_heatmap(func):
    @functools.wraps(func)
    def wrapper(df_jugador, figsize=(9, 7), *args, **kwargs):
        # Crear una clave única para el caché basada en el jugador y tamaño de figura
        player_name = df_jugador['player'].iloc[0] if 'player' in df_jugador.columns and not df_jugador.empty else "unknown"
        cache_key = f"{player_name}_heatmap_{figsize[0]}x{figsize[1]}"
        
        # Si ya existe en caché, devolver el gráfico almacenado
        if cache_key in HEATMAP_CACHE:
            return HEATMAP_CACHE[cache_key]
        
        # Si no está en caché, generar el gráfico
        try:
            fig = func(df_jugador, figsize, *args, **kwargs)
            # Almacenar en caché
            HEATMAP_CACHE[cache_key] = fig
            return fig
        except ValueError as e:
            # Si hay un error, registrarlo pero no cachear
            print(f"No se pudo generar el heatmap: {e}")
            return None
    return wrapper

@cache_heatmap
def generar_heatmap(df_jugador, figsize=(9, 7)):
    """
    Genera un heatmap para un jugador basado en las coordenadas x, y.
    Utiliza caché para mejorar el rendimiento en entornos con recursos limitados.

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

# Función para limpiar el caché si es necesario
def clear_heatmap_cache():
    global HEATMAP_CACHE
    HEATMAP_CACHE = {}