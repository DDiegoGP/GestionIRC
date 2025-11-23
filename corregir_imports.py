#!/usr/bin/env python3
"""
Script de Corrección Automática de Imports
Corrige los imports en main_window.py automáticamente
"""
import os
import sys
import shutil
from datetime import datetime

def hacer_backup(filepath):
    """Crea una copia de seguridad del archivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def corregir_imports(filepath):
    """Corrige los imports en el archivo"""
    print("=" * 70)
    print("🔧 CORRECCIÓN AUTOMÁTICA DE IMPORTS")
    print("=" * 70)
    print()
    
    if not os.path.exists(filepath):
        print(f"❌ No se encuentra: {filepath}")
        return False
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios = []
    
    # 1. Corregir Dashboard
    if 'from src.gui.dashboard_sincronizado import' not in contenido:
        print("🔄 Corrigiendo import de Dashboard...")
        
        # Variantes posibles
        variantes = [
            'from src.gui.dashboard import Dashboard',
            'from src.gui.dashboard import DashboardPanel',
        ]
        
        for variante in variantes:
            if variante in contenido:
                contenido = contenido.replace(
                    variante,
                    'from src.gui.dashboard_sincronizado import DashboardSincronizado as DashboardPanel'
                )
                cambios.append(f"   ✅ Dashboard: {variante} → dashboard_sincronizado")
                break
    
    # 2. Corregir Sesiones
    if 'from src.gui.sesiones_mejorado import' not in contenido:
        print("🔄 Corrigiendo import de Sesiones...")
        
        variantes = [
            'from src.gui.sesiones_nuevo import SesionesPanel',
            'from src.gui.sesiones import SesionesPanel',
            'from src.gui.sesiones_con_calendario import SesionesPanel',
        ]
        
        for variante in variantes:
            if variante in contenido:
                contenido = contenido.replace(
                    variante,
                    'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'
                )
                cambios.append(f"   ✅ Sesiones: {variante} → sesiones_mejorado")
                break
    
    # 3. Verificar si hubo cambios
    if contenido == contenido_original:
        print()
        print("ℹ️  No se necesitan cambios, los imports ya están correctos.")
        print()
        return True
    
    # Hacer backup
    print()
    print("💾 Creando backup...")
    backup_path = hacer_backup(filepath)
    print(f"   ✅ Backup creado: {backup_path}")
    print()
    
    # Guardar cambios
    print("💾 Guardando cambios...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("   ✅ Archivo actualizado")
    print()
    
    # Mostrar cambios
    if cambios:
        print("📝 CAMBIOS REALIZADOS:")
        for cambio in cambios:
            print(cambio)
        print()
    
    print("✅ CORRECCIÓN COMPLETADA")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("   1. Cierra la aplicación si está abierta")
    print("   2. Ejecuta: python main.py")
    print("   3. Verifica que Dashboard y Sesiones muestren datos correctos")
    print()
    
    return True

def main():
    """Función principal"""
    
    # Buscar main_window.py
    posibles_rutas = [
        'src/gui/main_window.py',
        'main_window.py',
        'gui/main_window.py'
    ]
    
    main_window_path = None
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            main_window_path = ruta
            break
    
    if not main_window_path:
        print("❌ No se encuentra main_window.py")
        print()
        print("Busca el archivo manualmente y ejecútalo así:")
        print("python corregir_imports.py ruta/al/main_window.py")
        return 1
    
    print(f"📄 Archivo encontrado: {main_window_path}")
    print()
    
    # Pedir confirmación
    print("Este script va a:")
    print("  1. Crear un backup de main_window.py")
    print("  2. Cambiar los imports automáticamente")
    print("  3. Guardar los cambios")
    print()
    
    respuesta = input("¿Continuar? (s/n): ").lower()
    
    if respuesta != 's':
        print("Operación cancelada.")
        return 0
    
    print()
    
    # Corregir
    if corregir_imports(main_window_path):
        return 0
    else:
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Ruta proporcionada como argumento
        filepath = sys.argv[1]
        if corregir_imports(filepath):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(main())
