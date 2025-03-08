import matplotlib.pyplot as plt
from mplsoccer import PyPizza

def generate_radar_chart(
    data_player, params, min_range, max_range, 
    player_color="#1A78CF", 
    radar_background_color="#E0F7FA", 
    figure_background_color="#FFFFFF", 
    text_color="#000000"
):
    """
    Genera un gráfico de radar para un jugador.
    """
    def calculate_metrics(data):
        metrics = {
            'Goals': len(data[data['type'] == 'Goal']),
            '% Pass Successful': round((len(data[(data['type'] == 'Pass') & 
                                                (data['outcome_type'] == 'Successful')]) / 
                                         len(data[data['type'] == 'Pass']) 
                                         if len(data[data['type'] == 'Pass']) > 0 else 0) * 100, 2),
            '% Take On Successful': round((len(data[(data['type'] == 'TakeOn') & 
                                                    (data['outcome_type'] == 'Successful')]) / 
                                           len(data[data['type'] == 'TakeOn']) 
                                           if len(data[data['type'] == 'TakeOn']) > 0 else 0) * 100, 2),
            'Dispossessed': len(data[data['type'] == 'Dispossessed']),
            '% Aerial Successful': round((len(data[(data['type'] == 'Aerial') & 
                                                   (data['outcome_type'] == 'Successful')]) / 
                                          len(data[data['type'] == 'Aerial']) 
                                          if len(data[data['type'] == 'Aerial']) > 0 else 0) * 100, 2),
            '% Tackle Successful': round((len(data[(data['type'] == 'Tackle') & 
                                                   (data['outcome_type'] == 'Successful')]) / 
                                          len(data[data['type'] == 'Tackle']) 
                                          if len(data[data['type'] == 'Tackle']) > 0 else 0) * 100, 2),
            'Ball Recovery': len(data[data['type'] == 'BallRecovery']),
            'Interception': len(data[data['type'] == 'Interception']),
            'Clearance': len(data[data['type'] == 'Clearance']),
        }
        return metrics

    metrics_player = calculate_metrics(data_player)
    values_player = [metrics_player[param] for param in params]

    # Ajuste del tamaño para evitar desproporción
    fig_size = (7, 7)  
    baker = PyPizza(
        params=params,
        min_range=min_range,
        max_range=max_range,
        background_color=radar_background_color,
        straight_line_color="#FFFFFF",
        last_circle_color="#000000",
        last_circle_lw=2,
        other_circle_lw=0,
        other_circle_color="#FFFFFF"
    )

    fig, ax = baker.make_pizza(
        values=values_player,
        figsize=fig_size,
        kwargs_slices=dict(facecolor=player_color, edgecolor="#000000", zorder=1, linewidth=1),
        kwargs_params=dict(color=text_color, fontsize=13, zorder=5, va="center"),
        # Agregar valores visibles en negrita y más grandes
        kwargs_values=dict(color=text_color, fontsize=14, zorder=3, fontweight='bold')
    )
    fig.patch.set_facecolor(figure_background_color)
    return fig