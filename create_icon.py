"""
Script para crear un icono .ico desde una imagen PNG o JPG
Ejecuta este script antes de compilar el .exe
"""

from PIL import Image
import os

def crear_icono():
    # Buscar si existe una imagen
    imagenes = []
    for archivo in os.listdir('.'):
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            imagenes.append(archivo)
    
    if not imagenes:
        print("No se encontraron imágenes PNG o JPG en la carpeta actual")
        print("Por favor, copia una imagen (PNG o JPG) a esta carpeta primero")
        return False
    
    if len(imagenes) == 1:
        imagen = imagenes[0]
    else:
        print("Se encontraron varias imágenes:")
        for i, img in enumerate(imagenes, 1):
            print(f"{i}. {img}")
        seleccion = input("¿Cuál deseas usar como icono? (número): ")
        try:
            imagen = imagenes[int(seleccion) - 1]
        except:
            print("Selección inválida")
            return False
    
    try:
        print(f"Procesando: {imagen}")
        img = Image.open(imagen)
        
        # Redimensionar a 256x256 (tamaño estándar para iconos)
        img = img.convert('RGBA')
        img = img.resize((256, 256), Image.Resampling.LANCZOS)
        
        # Guardar como .ico
        img.save('icon.ico')
        print("✅ ¡Icono creado exitosamente: icon.ico")
        return True
    except Exception as e:
        print(f"❌ Error al crear el icono: {e}")
        return False

if __name__ == "__main__":
    print("Generador de Iconos")
    print("-" * 40)
    crear_icono()
