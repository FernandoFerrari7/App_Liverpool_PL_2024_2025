import os

# Directorio donde están guardadas las fotos
fotos_dir = "images/fotos_jugadores"

# Nombres correctos del dataset (orden oficial)
nombres_correctos = [
    "Alexis Mac Allister",
    "Alisson Becker",
    "Andy Robertson",
    "Caoimhín Kelleher",
    "Cody Gakpo",
    "Conor Bradley",
    "Curtis Jones",
    "Darwin Núñez",
    "Diogo Jota",
    "Dominik Szoboszlai",
    "Federico Chiesa",
    "Harvey Elliott",
    "Ibrahima Konaté",
    "Jarell Quansah",
    "Joe Gomez",
    "Kostas Tsimikas",
    "Luis Díaz",
    "Mohamed Salah",
    "Ryan Gravenberch",
    "Trent Alexander-Arnold",
    "Virgil van Dijk",
    "Vítězslav Jaroš",
    "Wataru Endo"
]

# Nombres actuales en la carpeta
archivos = os.listdir(fotos_dir)

# Extraer los nombres de los archivos sin la extensión
nombres_actuales = [archivo.replace(".jpg", "").replace("_", " ") for archivo in archivos]

# Mapear nombres actuales con los nombres correctos
mapa_nombres = {}
for correcto in nombres_correctos:
    for actual in nombres_actuales:
        # Si el nombre actual es parte del nombre correcto, lo mapeamos
        if actual.lower() in correcto.lower() or correcto.lower() in actual.lower():
            mapa_nombres[actual] = correcto

# Renombrar los archivos
for archivo in archivos:
    nombre_actual = archivo.replace(".jpg", "").replace("_", " ")
    
    if nombre_actual in mapa_nombres:
        nuevo_nombre = mapa_nombres[nombre_actual] + ".jpg"
        old_path = os.path.join(fotos_dir, archivo)
        new_path = os.path.join(fotos_dir, nuevo_nombre)
        
        os.rename(old_path, new_path)
        print(f"✅ {archivo} renombrado a {nuevo_nombre}")
    else:
        print(f"⚠ No se encontró coincidencia para: {archivo}")

print("✅ Renombrado completado.")
