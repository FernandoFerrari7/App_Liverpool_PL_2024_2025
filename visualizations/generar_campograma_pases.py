import matplotlib.pyplot as plt
from mplsoccer import Pitch
import functools

# Diccionario para caché de campogramas de pases
PASES_CACHE = {}

# Decorador para caché
def cache_campograma_pases(func):
    @functools.wraps(func)
    def wrapper(df_jugador, figsize=(9, 7), *args, **kwargs):
        # Crear una clave única para el caché basada en el jugador y tamaño de figura
        player_name = df_jugador['player'].iloc[0] if 'player' in df_jugador.columns and not df_jugador.empty else "unknown"
        cache_key = f"{player_name}_pases_{figsize[0]}x{figsize[1]}"
        
        # Si ya existe en caché, devolver el gráfico almacenado
        if cache_key in PASES_CACHE:
            return PASES_CACHE[cache_key]
        
        # Si no está en caché, generar el gráfico
        fig = func(df_jugador, figsize, *args, **kwargs)
        
        # Almacenar en caché
        PASES_CACHE[cache_key] = fig
        
        return fig
    return wrapper

@cache_campograma_pases
def generar_campograma_pases(df_jugador, figsize=(9, 7)):
    """
    Genera un campograma de pases para un jugador específico.
    Utiliza caché para mejorar el rendimiento en entornos con recursos limitados.

    Parámetros:
    - df_jugador (DataFrame): DataFrame filtrado con los eventos del jugador, debe contener:
      ['x', 'y', 'end_x', 'end_y', 'type', 'outcome_type'].
    - figsize (tuple): Tamaño de la figura Matplotlib.

    Retorna:
    - fig: Objeto de la figura Matplotlib con el campograma de pases.
    """
    # Filtrar solo eventos de tipo 'Pass'
    df_pases = df_jugador[df_jugador['type'] == 'Pass']

    # Crear máscaras para pases completados e incompletos
    mask_complete = df_pases['outcome_type'] == 'Successful'
    mask_incomplete = df_pases['outcome_type'] == 'Unsuccessful'

    # Configurar el campo con fondo negro y líneas blancas
    pitch = Pitch(pitch_type='opta', pitch_color='black', line_color='white')
    fig, ax = pitch.draw(figsize=figsize)
    fig.set_facecolor('black')  # Fondo del gráfico negro

    # Graficar los pases completados (flechas amarillas)
    pitch.arrows(df_pases[mask_complete]['x'], df_pases[mask_complete]['y'],
                 df_pases[mask_complete]['end_x'], df_pases[mask_complete]['end_y'],
                 width=2, headwidth=10, headlength=10, color='#ffcc00', ax=ax, label='Completed Passes')

    # Graficar los pases no completados (flechas rojas)
    pitch.arrows(df_pases[mask_incomplete]['x'], df_pases[mask_incomplete]['y'],
                 df_pases[mask_incomplete]['end_x'], df_pases[mask_incomplete]['end_y'],
                 width=2, headwidth=10, headlength=10, color='#ff6666', ax=ax, label='Unsuccessful Passes')

    # Configurar la leyenda con colores claros
    ax.legend(facecolor='black', handlelength=5, edgecolor='None', fontsize=15, loc='upper left', labelcolor='white')

    return fig

# Función para limpiar el caché si es necesario
def clear_pases_cache():
    global PASES_CACHE
    PASES_CACHE = {}