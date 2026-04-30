"""
Script para compilar main.py a .exe con PyInstaller
"""

import subprocess
import sys
import os

def compile_exe():
    print("=" * 60)
    print("🔨 Compilador de File Organizer")
    print("=" * 60)
    
    # Verificar que main.py existe
    if not os.path.exists('main.py'):
        print("❌ Error: main.py no encontrado")
        return False
    
    # Opciones de compilación
    icon_option = ""
    if os.path.exists('icon.ico'):
        icon_option = f'--icon=icon.ico'
        print("✅ Se encontró icon.ico - Se usará como icono del ejecutable")
    else:
        print("⚠️  No se encontró icon.ico - Se compilará sin icono personalizado")
    
    # Comando de PyInstaller
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--onefile",              # Un solo archivo .exe
        "--windowed",             # Sin consola
        "--name=File Organizer",  # Nombre del ejecutable
        "--specpath=build",       # Carpeta para archivos de construcción
        "--distpath=dist",        # Carpeta para salida
        "--buildpath=build",
    ]
    
    if icon_option:
        cmd.append(icon_option)
    
    cmd.append("main.py")
    
    print("\n📦 Compilando...")
    print(f"Comando: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ ¡Compilación exitosa!")
        print("=" * 60)
        print("📁 El ejecutable está en: dist/File Organizer.exe")
        print("\n¡Listo para usar! 🎉")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ Error durante la compilación: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    compile_exe()
