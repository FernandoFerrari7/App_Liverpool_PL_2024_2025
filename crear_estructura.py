import os

# Define la estructura de carpetas
estructura = [
    "data/equipos",
    "data/jugadores",
    "images",
    "data/raw",
    "scrapers",
    "pages",
    "visualizations"
]

# Crea las carpetas
for carpeta in estructura:
    os.makedirs(carpeta, exist_ok=True)

# Crea los archivos principales
archivos = [
    "main.py",
    "requirements.txt",
    "README.md",
    "pages/equipo.py",
    "pages/jugadores.py",
]

for archivo in archivos:
    ruta = archivo
    if not os.path.exists(ruta):
        with open(ruta, 'w') as f:
            f.write("")