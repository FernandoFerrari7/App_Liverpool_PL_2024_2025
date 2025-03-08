import os
import pandas as pd

def filtrar_y_limpiar_eventos_jugador(input_folder, output_folder, player_name):
    """
    Filtra eventos de un jugador específico desde múltiples archivos CSV y limpia los datos.

    Parámetros:
    - input_folder (str): Ruta de la carpeta con los archivos CSV de los partidos.
    - output_folder (str): Ruta de la carpeta donde se guardarán los datos filtrados.
    - player_name (str): Nombre del jugador a filtrar.

    Retorna:
    - str: Ruta del archivo CSV generado con los datos del jugador.
    """
    # Verificar que la carpeta de entrada exista
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"La carpeta {input_folder} no existe. Verifica la ubicación.")

    # Crear la carpeta de salida si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Generar nombre del archivo de salida
    sanitized_name = player_name.lower().replace(" ", "_")  # Normalizar el nombre para el archivo
    output_file_path = os.path.join(output_folder, f'{sanitized_name}_eventos.csv')

    # Obtener la lista de archivos CSV
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

    # Verificar si hay archivos CSV en la carpeta de entrada
    if not csv_files:
        raise FileNotFoundError("No se encontraron archivos CSV en la carpeta especificada.")

    # Inicializar un DataFrame para almacenar los datos filtrados
    filtered_data = pd.DataFrame()

    # Procesar cada archivo CSV
    for csv_file in csv_files:
        file_path = os.path.join(input_folder, csv_file)
        try:
            df = pd.read_csv(file_path)
            # Filtrar por player (en lugar de player_name)
            filtered_df = df[df['player'].str.contains(player_name, case=False, na=False)]
            # Concatenar los datos filtrados
            filtered_data = pd.concat([filtered_data, filtered_df], ignore_index=True)
        except Exception as e:
            print(f"Error procesando el archivo {csv_file}: {e}")

    # Limpiar los datos filtrados
    if not filtered_data.empty:
        # Eliminar columnas completamente vacías
        filtered_data = filtered_data.dropna(axis=1, how='all')

        # Rellenar valores faltantes con lógica específica
        filtered_data['second'] = filtered_data['second'].fillna(0)
        filtered_data['end_x'] = filtered_data['end_x'].fillna(filtered_data['x'])
        filtered_data['end_y'] = filtered_data['end_y'].fillna(filtered_data['y'])

        # Guardar los datos filtrados y limpios en un archivo CSV
        filtered_data.to_csv(output_file_path, index=False)
        print(f"Archivo limpio y filtrado guardado en: {output_file_path}")
        return output_file_path
    else:
        print(f"No se encontraron eventos para el jugador {player_name}.")
        return None