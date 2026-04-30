# 📁 File Organizer

Una aplicación moderna para organizar archivos automáticamente por tipo.

## ✨ Características

- 🎯 Interfaz gráfica intuitiva
- 📂 Organiza archivos automáticamente por extensión
- 🔄 Prevención de conflictos (renombra automáticamente si existen duplicados)
- 🎨 Tema oscuro moderno con colores personalizados
- ⚡ Operación en segundo plano (sin congelar la UI)
- 📦 Empaquetado como un único ejecutable

## 🚀 Descarga Rápida

### Opción 1: Descargar Ejecutable (Recomendado)
[Descargar File Organizer.exe v1.0.0](https://github.com/JSTranquility/FilesOrganizer/releases/tag/v1.0.0)

### Opción 2: Ejecutar desde Código Fuente

**Requisitos:**
- Python 3.6+
- pip

**Instalación:**
```bash
git clone https://github.com/JSTranquility/FilesOrganizer.git
cd FilesOrganizer
pip install -r requirements.txt
python main.py
```

## 📖 Cómo Usar

1. **Ejecuta la aplicación** - `File Organizer.exe` o `python main.py`
2. **Selecciona una carpeta** - Click en "📁 Seleccionar Carpeta"
3. **Organiza los archivos** - Click en "✨ Organizar Archivos"
4. **¡Listo!** - Los archivos se organizarán automáticamente

## 📋 Extensiones Soportadas

| Tipo | Extensiones |
|------|-------------|
| Imágenes | PNG, JPG, JPEG |
| Documentos | TXT, PDF, DOCX, XLSX |
| Ejecutables | EXE |
| Multimedia | MP3, MP4 |
| Otros | Todos los demás archivos |

## 🛠️ Compilación desde Código Fuente

Si deseas compilar tu propio `.exe` con icono personalizado:

```bash
# Instalar dependencias
pip install pyinstaller pillow customtkinter

# Convertir imagen a icono (opcional)
python create_icon.py

# Compilar
python compilar.py
```

El ejecutable estará en la carpeta `dist/`

## 📦 Requisitos

- **Python 3.6+** (solo si ejecutas desde código fuente)
- **customtkinter** - Interfaz gráfica moderna
- **pyinstaller** - Para compilar el ejecutable

## 📄 Archivos Incluidos

- `main.py` - Código principal de la aplicación
- `compilar.py` - Script para compilar a .exe
- `create_icon.py` - Script para convertir imágenes a icono
- `build.bat` - Script de compilación para Windows
- `icon.ico` - Icono de la aplicación
- `INSTRUCCIONES_ICONO.md` - Guía detallada para cambiar el icono

## 🐛 Troubleshooting

### "La carpeta está vacía"
Asegúrate de que selecciones una carpeta que contenga archivos.

### El ejecutable se ve como archivo desconocido
Esto es normal en la primera ejecución. Windows verifica el archivo automáticamente.

### Antivirus reporta falso positivo
El archivo `.exe` es seguro. Si lo deseas, puedes compilarlo tú mismo desde el código fuente.

## 📝 Licencia

MIT - Ver `LICENSE` para más detalles

## 👨‍💻 Contribuciones

¡Las contribuciones son bienvenidas! Para cambios mayores, abre un issue primero para discutir qué cambios te gustaría hacer.

## 📧 Contacto

Para reportar bugs o sugerencias, abre un [issue](https://github.com/JSTranquility/FilesOrganizer/issues)

---

**Versión:** 1.0.0  
**Última actualización:** 2026-04-30
