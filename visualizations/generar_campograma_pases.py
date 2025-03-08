import matplotlib.pyplot as plt
from mplsoccer import Pitch

def generar_campograma_pases(df_jugador, figsize=(9, 7)):
    """
    Genera un campograma de pases para un jugador específico.

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