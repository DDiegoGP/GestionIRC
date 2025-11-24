"""
Script de compilación para Gestión IRC
Genera el ejecutable de Windows con PyInstaller
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def limpiar_builds_anteriores():
    """Limpia builds anteriores"""
    print("🧹 Limpiando builds anteriores...")
    
    dirs_limpiar = ['build', 'dist']
    for dir_name in dirs_limpiar:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   ✓ Eliminado: {dir_name}/")
    
    print()

def verificar_archivos_necesarios():
    """Verifica que existen todos los archivos necesarios"""
    print("🔍 Verificando archivos necesarios...")
    
    archivos_requeridos = [
        'main.py',
        'config/service_account.json',
        'resources/irc_icon.ico',
        'formularios/anexo_III_2025_V8.pdf',
        'Gestion_IRC.spec'
    ]
    
    faltantes = []
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"   ✓ {archivo}")
        else:
            print(f"   ✗ {archivo} - FALTA")
            faltantes.append(archivo)
    
    # Verificar carpeta formularios
    if os.path.exists('formularios') and os.path.isdir('formularios'):
        print(f"   ✓ formularios/ (carpeta)")
    else:
        print(f"   ✗ formularios/ - FALTA")
        faltantes.append('formularios/')
    
    print()
    
    if faltantes:
        print("❌ Faltan archivos necesarios:")
        for f in faltantes:
            print(f"   - {f}")
        return False
    
    return True

def compilar():
    """Compila el ejecutable con PyInstaller"""
    print("🔨 Compilando con PyInstaller...")
    print("   (Esto puede tardar 2-5 minutos...)")
    print()
    
    try:
        # Ejecutar sin capturar salida para ver progreso en tiempo real
        resultado = subprocess.run(
            ['python', '-m', 'PyInstaller', 'Gestion_IRC.spec', '--clean'],
            check=True
        )
        
        if resultado.returncode == 0:
            print()
            print("✅ Compilación exitosa!")
            return True
        else:
            print()
            print("❌ Error en la compilación")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar PyInstaller: {e}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller no está instalado.")
        print("   Instálalo con: pip install pyinstaller")
        print("   O verifica tu instalación de Python")
        return False

def verificar_ejecutable():
    """Verifica que el ejecutable se creó correctamente"""
    print()
    print("🔍 Verificando ejecutable...")
    
    exe_path = Path('dist/GestionIRC.exe')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ Ejecutable creado: {exe_path}")
        print(f"   ✓ Tamaño: {size_mb:.2f} MB")
        return True
    else:
        print(f"   ✗ No se encontró el ejecutable en {exe_path}")
        return False

def crear_paquete_distribucion():
    """Crea el paquete de distribución completo"""
    print()
    print("📦 Creando paquete de distribución...")
    
    # Crear carpeta de distribución
    dist_folder = Path('dist/GestionIRC_v4.0')
    dist_folder.mkdir(exist_ok=True)
    
    # Copiar ejecutable
    shutil.copy('dist/GestionIRC.exe', dist_folder / 'GestionIRC.exe')
    print("   ✓ Ejecutable copiado")
    
    # Crear carpetas necesarias
    (dist_folder / 'data').mkdir(exist_ok=True)
    (dist_folder / 'logs').mkdir(exist_ok=True)
    (dist_folder / 'exports').mkdir(exist_ok=True)
    (dist_folder / 'backups').mkdir(exist_ok=True)
    print("   ✓ Carpetas de trabajo creadas")
    
    # Copiar carpeta config con service_account.json
    if os.path.exists('config/service_account.json'):
        (dist_folder / 'config').mkdir(exist_ok=True)
        shutil.copy('config/service_account.json', dist_folder / 'config' / 'service_account.json')
        print("   ✓ Credenciales de Google Sheets copiadas")
    else:
        print("   ⚠️  Advertencia: config/service_account.json no encontrado")
    
    # Copiar carpeta formularios con template PDF
    if os.path.exists('formularios'):
        shutil.copytree('formularios', dist_folder / 'formularios', dirs_exist_ok=True)
        print("   ✓ Templates PDF copiados")
    else:
        print("   ⚠️  Advertencia: carpeta formularios/ no encontrada")
    
    # Crear README
    readme_content = """# Gestión IRC - Universidad Complutense de Madrid

## Instalación

1. Extraer todos los archivos en una carpeta
2. Ejecutar GestionIRC.exe

## Primer Uso

Al abrir la aplicación por primera vez:

1. Se abrirá la ventana de configuración automáticamente
2. Introduce el ID del Google Sheets (proporcionado por el administrador)
3. Las credenciales de acceso ya están incluidas en config/service_account.json
4. Click en "Guardar" y la aplicación se conectará automáticamente

## Estructura de Carpetas

- `config/` - Credenciales de Google Sheets (NO modificar)
- `formularios/` - Templates de PDF para solicitudes
- `data/` - Datos de configuración de la aplicación
- `logs/` - Archivos de log del sistema
- `exports/` - PDFs y reportes exportados
- `backups/` - Copias de seguridad automáticas

## Requisitos

- Windows 10 o superior
- Conexión a Internet (para sincronización con Google Sheets)

## Notas Importantes

- NO elimines ni modifiques la carpeta config/
- NO compartas el archivo service_account.json fuera de tu organización
- Los datos se sincronizan automáticamente con Google Sheets

## Soporte

Para soporte técnico o problemas, contacta con el administrador del sistema.

---
Universidad Complutense de Madrid - Gestión IRC v4.0
Sistema de Gestión de Instalaciones Radiactivas
"""
    
    with open(dist_folder / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("   ✓ README creado")
    
    print()
    print(f"✅ Paquete de distribución creado en: {dist_folder}")
    print()
    print("📋 Contenido:")
    print("   - GestionIRC.exe")
    print("   - README.txt")
    print("   - config/service_account.json (credenciales Google Sheets)")
    print("   - formularios/ (templates PDF)")
    print("   - Carpetas: data/, logs/, exports/, backups/")

def main():
    """Función principal"""
    print("=" * 60)
    print("   COMPILACIÓN GESTIÓN IRC - UCM")
    print("=" * 60)
    print()
    
    # 1. Limpiar builds anteriores
    limpiar_builds_anteriores()
    
    # 2. Verificar archivos necesarios
    if not verificar_archivos_necesarios():
        print()
        print("❌ Compilación abortada: faltan archivos necesarios")
        sys.exit(1)
    
    # 3. Compilar
    if not compilar():
        print()
        print("❌ Compilación fallida")
        sys.exit(1)
    
    # 4. Verificar ejecutable
    if not verificar_ejecutable():
        print()
        print("❌ El ejecutable no se generó correctamente")
        sys.exit(1)
    
    # 5. Crear paquete de distribución
    crear_paquete_distribucion()
    
    print()
    print("=" * 60)
    print("   ✅ COMPILACIÓN COMPLETADA CON ÉXITO")
    print("=" * 60)
    print()
    print("📦 El ejecutable está listo para distribuir en:")
    print("   dist/GestionIRC_v4.0/")
    print()

if __name__ == "__main__":
    main()
