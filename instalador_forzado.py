#!/usr/bin/env python3
"""
INSTALADOR FORZADO - Copia archivos directamente
No depende de imports, reemplaza los archivos problemáticos
"""
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

def encontrar_proyecto():
    """Encuentra el proyecto GestionIRC"""
    print("🔍 Buscando proyecto GestionIRC...")
    print()
    
    # Directorio actual
    cwd = Path.cwd()
    
    # Verificar si estamos en el proyecto
    if (cwd / "src").exists() and (cwd / "main.py").exists():
        print(f"✅ Proyecto encontrado: {cwd}")
        return cwd
    
    # Buscar GestionIRC en el path actual
    if "GestionIRC" in str(cwd):
        # Subir hasta encontrar src/
        for parent in [cwd] + list(cwd.parents):
            if (parent / "src").exists() and (parent / "main.py").exists():
                print(f"✅ Proyecto encontrado: {parent}")
                return parent
    
    # Preguntar manualmente
    print("⚠️  No se encontró automáticamente")
    print()
    print("Introduce la ruta completa de la carpeta GestionIRC")
    print("(la que contiene 'src' y 'main.py')")
    print()
    
    ruta = input("Ruta: ").strip().strip('"').strip("'")
    ruta = Path(ruta)
    
    if ruta.exists() and (ruta / "src").exists():
        print(f"✅ Usando: {ruta}")
        return ruta
    
    print("❌ Ruta inválida")
    return None

def backup(filepath):
    """Hace backup de un archivo"""
    if not filepath.exists():
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"{filepath.name}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def copiar_archivo(origen, destino):
    """Copia un archivo haciendo backup del original"""
    print(f"   📄 {destino.name}")
    
    if destino.exists():
        backup_path = backup(destino)
        if backup_path:
            print(f"      💾 Backup: {backup_path.name}")
    
    # Crear directorio si no existe
    destino.parent.mkdir(parents=True, exist_ok=True)
    
    # Copiar
    shutil.copy2(origen, destino)
    print(f"      ✅ Copiado")

def instalar_archivos(proyecto_root):
    """Instala todos los archivos necesarios"""
    print("=" * 70)
    print("📦 INSTALANDO ARCHIVOS")
    print("=" * 70)
    print()
    
    # Directorio donde está este script (donde están los archivos del ZIP)
    script_dir = Path(__file__).parent
    gestion_dir = script_dir / "GestionIRC"
    
    if not gestion_dir.exists():
        print("❌ No se encuentra la carpeta 'GestionIRC' con los archivos")
        print(f"   Esperado en: {gestion_dir}")
        print()
        print("Asegúrate de que:")
        print("  1. Extrajiste el ZIP completo")
        print("  2. Estás ejecutando el script desde la carpeta extraída")
        return False
    
    # Archivos a copiar
    archivos = [
        ("GestionIRC/src/utils/calculador_estados.py", "src/utils/calculador_estados.py"),
        ("GestionIRC/src/gui/dashboard_sincronizado.py", "src/gui/dashboard_sincronizado.py"),
        ("GestionIRC/src/gui/sesiones_mejorado.py", "src/gui/sesiones_mejorado.py"),
        ("GestionIRC/src/gui/solicitudes_real.py", "src/gui/solicitudes_real.py"),
    ]
    
    print("Copiando archivos:")
    print()
    
    for origen_rel, destino_rel in archivos:
        origen = script_dir / origen_rel
        destino = proyecto_root / destino_rel
        
        if not origen.exists():
            print(f"   ❌ No se encuentra: {origen_rel}")
            continue
        
        try:
            copiar_archivo(origen, destino)
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    print()
    return True

def corregir_main_window(proyecto_root):
    """Corrige main_window.py"""
    print("=" * 70)
    print("🔧 CORRIGIENDO main_window.py")
    print("=" * 70)
    print()
    
    main_window = proyecto_root / "src" / "gui" / "main_window.py"
    
    if not main_window.exists():
        print(f"❌ No se encuentra: {main_window}")
        return False
    
    print(f"📄 Archivo: {main_window}")
    print()
    
    # Leer
    with open(main_window, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    original = contenido
    cambios = []
    
    # 1. Dashboard
    if 'dashboard_sincronizado' not in contenido:
        # Buscar import de dashboard
        import_patterns = [
            'from src.gui.dashboard import Dashboard',
            'from src.gui.dashboard import DashboardPanel',
            'from .dashboard import Dashboard',
            'from .dashboard import DashboardPanel',
        ]
        
        for pattern in import_patterns:
            if pattern in contenido:
                contenido = contenido.replace(
                    pattern,
                    'from src.gui.dashboard_sincronizado import DashboardSincronizado as Dashboard'
                )
                cambios.append(f"✅ Dashboard import actualizado")
                break
        
        # Buscar instanciación de Dashboard
        if 'Dashboard(' in contenido and 'DashboardSincronizado' not in contenido:
            # Buscar la línea específica
            lines = contenido.split('\n')
            for i, line in enumerate(lines):
                if 'Dashboard(' in line and '#' not in line:
                    # Comentar la línea vieja
                    lines[i] = f"# {line}  # Comentado por instalador"
                    # Añadir la nueva
                    indent = len(line) - len(line.lstrip())
                    lines.insert(i+1, ' ' * indent + 'DashboardSincronizado(dashboard_frame, self)')
                    cambios.append(f"✅ Dashboard instanciación actualizada")
                    break
            contenido = '\n'.join(lines)
    
    # 2. Sesiones
    if 'sesiones_mejorado' not in contenido:
        import_patterns = [
            'from src.gui.sesiones_nuevo import SesionesPanel',
            'from src.gui.sesiones import SesionesPanel',
            'from src.gui.sesiones_con_calendario import SesionesPanel',
            'from .sesiones_nuevo import SesionesPanel',
            'from .sesiones import SesionesPanel',
        ]
        
        for pattern in import_patterns:
            if pattern in contenido:
                contenido = contenido.replace(
                    pattern,
                    'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'
                )
                cambios.append(f"✅ Sesiones import actualizado")
                break
    
    if contenido == original:
        print("ℹ️  No hay cambios necesarios (ya está actualizado)")
        print()
        return True
    
    # Backup
    backup_path = backup(main_window)
    if backup_path:
        print(f"💾 Backup creado: {backup_path.name}")
        print()
    
    # Guardar
    with open(main_window, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Cambios aplicados:")
    for cambio in cambios:
        print(f"   {cambio}")
    print()
    
    return True

def corregir_pdf_extractor(proyecto_root):
    """Corrige PDF extractor"""
    print("=" * 70)
    print("🔧 CORRIGIENDO pdf_extractor.py")
    print("=" * 70)
    print()
    
    pdf_extractor = proyecto_root / "src" / "utils" / "pdf_extractor.py"
    
    if not pdf_extractor.exists():
        print("ℹ️  No se encuentra pdf_extractor.py")
        print()
        return True
    
    print(f"📄 Archivo: {pdf_extractor}")
    print()
    
    # Leer
    with open(pdf_extractor, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    original = contenido
    
    # Quitar emojis de estados
    cambios = []
    
    if '⏳ Pendiente' in contenido:
        contenido = contenido.replace('"⏳ Pendiente"', '"Pendiente"')
        cambios.append('✅ Quitado emoji ⏳')
    
    if '✅ Completado' in contenido:
        contenido = contenido.replace('"✅ Completado"', '"Completado"')
        cambios.append('✅ Quitado emoji ✅')
    
    if '🟡 En proceso' in contenido:
        contenido = contenido.replace('"🟡 En proceso"', '"En proceso"')
        cambios.append('✅ Quitado emoji 🟡')
    
    if contenido == original:
        print("ℹ️  No hay emojis para quitar")
        print()
        return True
    
    # Backup
    backup_path = backup(pdf_extractor)
    if backup_path:
        print(f"💾 Backup creado: {backup_path.name}")
        print()
    
    # Guardar
    with open(pdf_extractor, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("✅ Cambios aplicados:")
    for cambio in cambios:
        print(f"   {cambio}")
    print()
    
    return True

def verificar_instalacion(proyecto_root):
    """Verifica que todo esté instalado correctamente"""
    print("=" * 70)
    print("✅ VERIFICACIÓN")
    print("=" * 70)
    print()
    
    errores = []
    
    # 1. Archivos
    print("📂 Archivos necesarios:")
    archivos = [
        "src/utils/calculador_estados.py",
        "src/gui/dashboard_sincronizado.py",
        "src/gui/sesiones_mejorado.py",
        "src/gui/solicitudes_real.py",
    ]
    
    for archivo in archivos:
        path = proyecto_root / archivo
        if path.exists():
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTA")
            errores.append(f"Falta {archivo}")
    
    print()
    
    # 2. Imports en main_window
    print("📝 Imports en main_window.py:")
    main_window = proyecto_root / "src" / "gui" / "main_window.py"
    
    if main_window.exists():
        with open(main_window, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'dashboard_sincronizado' in contenido:
            print("   ✅ Dashboard import correcto")
        else:
            print("   ❌ Dashboard import incorrecto")
            errores.append("Dashboard import incorrecto")
        
        if 'sesiones_mejorado' in contenido:
            print("   ✅ Sesiones import correcto")
        else:
            print("   ❌ Sesiones import incorrecto")
            errores.append("Sesiones import incorrecto")
    else:
        print("   ❌ main_window.py no encontrado")
        errores.append("main_window.py no encontrado")
    
    print()
    
    # 3. PDF Extractor
    print("📄 PDF Extractor:")
    pdf_extractor = proyecto_root / "src" / "utils" / "pdf_extractor.py"
    
    if pdf_extractor.exists():
        with open(pdf_extractor, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if '⏳' in contenido or '✅' in contenido:
            print("   ⚠️  Aún tiene emojis")
            errores.append("PDF Extractor con emojis")
        else:
            print("   ✅ Sin emojis")
    else:
        print("   ℹ️  No se encuentra (opcional)")
    
    print()
    
    return len(errores) == 0, errores

def main():
    """Función principal"""
    print()
    print("=" * 70)
    print("🚀 INSTALADOR FORZADO - GestionIRC")
    print("=" * 70)
    print()
    print("Este instalador va a:")
    print("  1. Buscar tu proyecto GestionIRC")
    print("  2. REEMPLAZAR archivos directamente")
    print("  3. Corregir main_window.py")
    print("  4. Corregir pdf_extractor.py")
    print("  5. Verificar instalación")
    print()
    print("Se harán backups de todos los archivos modificados.")
    print()
    
    respuesta = input("¿Continuar? (s/n): ").lower()
    
    if respuesta != 's':
        print("Cancelado.")
        return 0
    
    print()
    
    # Encontrar proyecto
    proyecto = encontrar_proyecto()
    if not proyecto:
        print("❌ No se pudo encontrar el proyecto")
        return 1
    
    print()
    
    # Instalar archivos
    if not instalar_archivos(proyecto):
        print("❌ Error al instalar archivos")
        return 1
    
    # Corregir main_window
    if not corregir_main_window(proyecto):
        print("❌ Error al corregir main_window.py")
        return 1
    
    # Corregir PDF extractor
    corregir_pdf_extractor(proyecto)
    
    # Verificar
    todo_ok, errores = verificar_instalacion(proyecto)
    
    # Resumen
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print()
    
    if todo_ok:
        print("✅ ¡INSTALACIÓN COMPLETA!")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("   1. Cierra la aplicación si está abierta")
        print("   2. Ejecuta: python main.py")
        print("   3. Verifica que:")
        print("      • Dashboard tiene 6 KPIs grandes")
        print("      • Números coinciden en todas las pestañas")
        print("      • Sesiones muestra solo servicios 'En proceso'")
        print()
        return 0
    else:
        print("⚠️  PROBLEMAS DETECTADOS:")
        for error in errores:
            print(f"   • {error}")
        print()
        print("Revisa los errores y vuelve a ejecutar.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
