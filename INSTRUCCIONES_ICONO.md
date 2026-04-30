# 📁 Instrucciones para Agregar Icono al .exe

## Paso 1: Preparar la imagen del icono

1. Coloca una imagen PNG o JPG en esta carpeta (ej: `mi_icono.png`)
   - Recomendado: tamaño 256x256 o mayor
   - Fondo transparente opcional

## Paso 2: Convertir imagen a .ico

Opción A - Automática (Recomendado):
```
python create_icon.py
```
Selecciona la imagen y se creará automáticamente `icon.ico`

Opción B - Manual:
```
pip install Pillow
python -c "from PIL import Image; img = Image.open('tu_imagen.png').resize((256, 256)); img.save('icon.ico')"
```

## Paso 3: Compilar el .exe con icono

### Opción A - Automática (Recomendado):
```
build.bat
```

### Opción B - Manual:
```
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name="File Organizer" main.py
```

## Resultado

El ejecutable estará en: `dist/File Organizer.exe`

## Archivos necesarios:
- ✅ `main.py` - Código de la aplicación
- ✅ `icon.ico` - Icono del ejecutable (se crea con los scripts)
- ✅ `build.bat` - Script para compilar
- ✅ `create_icon.py` - Script para generar icono

## Notas:
- El main.py ya está configurado para usar el icono en la ventana
- Si no encuentras `icon.ico`, la app funcionará normal sin icono
- Para cambiar el nombre del .exe, edita `build.bat` o usa el comando manual

¡Listo! 🎉
