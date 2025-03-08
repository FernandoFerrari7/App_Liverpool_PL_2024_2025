import os
import requests
from bs4 import BeautifulSoup

# URL del Liverpool en Transfermarkt
url = "https://www.transfermarkt.es/fc-liverpool/startseite/verein/31"

# Cabecera para evitar bloqueos
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}

# Hacer la solicitud GET
response = requests.get(url, headers=headers)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Definir el directorio de imágenes
    base_dir = "images"
    fotos_dir = os.path.join(base_dir, "fotos_jugadores")

    # Crear las carpetas si no existen
    os.makedirs(fotos_dir, exist_ok=True)

    # Buscar todas las imágenes de jugadores
    player_images = soup.find_all("img", {"class": "bilderrahmen-fixed"})

    for img in player_images:
        img_url = img.get("data-src", img.get("src"))  # Intentar primero data-src, luego src
        player_name = img["alt"].strip()

        # Validar si la URL es correcta (comienza con http o https)
        if not img_url.startswith("http"):
            print(f"⚠ Imagen descartada (no es una URL válida): {player_name}")
            continue

        # Formatear el nombre del archivo
        player_filename = player_name.replace(" ", "_") + ".jpg"
        img_path = os.path.join(fotos_dir, player_filename)

        # Descargar la imagen
        img_data = requests.get(img_url, headers=headers).content
        with open(img_path, "wb") as handler:
            handler.write(img_data)

        print(f"✅ Imagen guardada: {img_path}")

else:
    print("❌ Error al acceder a la página")


