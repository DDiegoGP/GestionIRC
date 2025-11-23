"""
Script para convertir el logo de IRC de PNG a formato ICO
Uso: python convert_logo.py irc_logo.png
"""

from PIL import Image
import sys
import os

def convert_png_to_ico(png_path, output_dir='resources'):
    """
    Convierte una imagen PNG a formato ICO para usar en Windows
    
    Args:
        png_path: Ruta al archivo PNG original
        output_dir: Directorio donde guardar el archivo ICO
    """
    
    if not os.path.exists(png_path):
        print(f"❌ Error: No se encontró el archivo {png_path}")
        return False
    
    try:
        # Crear directorio de salida si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Abrir imagen original
        img = Image.open(png_path)
        print(f"✅ Imagen cargada: {img.size[0]}x{img.size[1]} píxeles")
        
        # Crear icono con múltiples tamaños
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Ruta de salida
        ico_path = os.path.join(output_dir, 'irc_icon.ico')
        
        # Guardar como ICO
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        print(f"✅ Icono creado exitosamente: {ico_path}")
        print(f"   Tamaños incluidos: {', '.join([f'{s[0]}x{s[1]}' for s in icon_sizes])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir la imagen: {e}")
        return False

def resize_logo_for_ui(png_path, output_dir='resources'):
    """
    Crea versiones redimensionadas del logo para la interfaz
    """
    
    try:
        img = Image.open(png_path)
        
        # Logo para header (200x80)
        logo_header = img.copy()
        logo_header.thumbnail((200, 80), Image.Resampling.LANCZOS)
        header_path = os.path.join(output_dir, 'irc_logo_header.png')
        logo_header.save(header_path, 'PNG')
        print(f"✅ Logo para header creado: {header_path}")
        
        # Logo para splash screen (400x200)
        logo_splash = img.copy()
        logo_splash.thumbnail((400, 200), Image.Resampling.LANCZOS)
        splash_path = os.path.join(output_dir, 'irc_logo_splash.png')
        logo_splash.save(splash_path, 'PNG')
        print(f"✅ Logo para splash creado: {splash_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al redimensionar logos: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Conversor de Logo IRC - PNG a ICO")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Uso: python convert_logo.py ruta_al_logo.png")
        print()
        print("Ejemplo: python convert_logo.py irc_logo.png")
        sys.exit(1)
    
    png_file = sys.argv[1]
    
    # Convertir a ICO
    print("Convirtiendo a formato ICO...")
    success_ico = convert_png_to_ico(png_file)
    
    print()
    
    # Crear versiones redimensionadas
    print("Creando versiones para interfaz...")
    success_resize = resize_logo_for_ui(png_file)
    
    print()
    print("=" * 60)
    
    if success_ico and success_resize:
        print("✅ ¡Proceso completado exitosamente!")
        print()
        print("Archivos creados en la carpeta 'resources/':")
        print("  - irc_icon.ico (icono de aplicación)")
        print("  - irc_logo_header.png (logo para interfaz)")
        print("  - irc_logo_splash.png (logo para splash screen)")
    else:
        print("❌ Hubo errores en el proceso")
    
    print("=" * 60)
