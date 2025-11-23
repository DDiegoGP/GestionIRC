#!/usr/bin/env python3
"""
MEGA-PARCHE - Arregla TODOS los problemas de una vez
1. Corrige PDF Extractor (quita emojis)
2. Corrige imports en main_window.py
3. Limpia estados en Google Sheets
4. Verifica todo
"""
import os
import sys
import shutil
from datetime import datetime

def hacer_backup(filepath):
    """Crea backup de un archivo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"   💾 Backup: {backup_path}")
    return backup_path

def corregir_pdf_extractor():
    """Corrige el PDF extractor para NO usar emojis"""
    print("=" * 70)
    print("🔧 PASO 1: Corrigiendo PDF Extractor")
    print("=" * 70)
    print()
    
    filepath = 'src/utils/pdf_extractor.py'
    
    if not os.path.exists(filepath):
        print(f"⚠️  No se encuentra: {filepath}")
        print("   Esto es opcional, continuando...")
        return True
    
    # Leer archivo
    with open(filepath, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar líneas problemáticas
    cambios = []
    
    # 1. Estado con emoji en línea 179
    if 'solicitud.estado = "⏳ Pendiente"' in contenido:
        hacer_backup(filepath)
        contenido = contenido.replace(
            'solicitud.estado = "⏳ Pendiente"',
            'solicitud.estado = "Pendiente"'
        )
        cambios.append("   ✅ Quitado emoji ⏳ de estado inicial")
    
    # 2. Cualquier otro emoji en estados
    if '✅' in contenido and 'solicitud.estado' in contenido:
        contenido = contenido.replace('"✅ Completado"', '"Completado"')
        cambios.append("   ✅ Quitado emoji ✅ de estado completado")
    
    if cambios:
        # Guardar
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("📝 Cambios realizados:")
        for cambio in cambios:
            print(cambio)
        print()
        return True
    else:
        print("✅ PDF Extractor ya está correcto")
        print()
        return True

def corregir_main_window():
    """Corrige los imports en main_window.py"""
    print("=" * 70)
    print("🔧 PASO 2: Corrigiendo Imports en main_window.py")
    print("=" * 70)
    print()
    
    # Buscar archivo
    posibles = [
        'src/gui/main_window.py',
        'main_window.py',
        'gui/main_window.py'
    ]
    
    filepath = None
    for ruta in posibles:
        if os.path.exists(ruta):
            filepath = ruta
            break
    
    if not filepath:
        print("❌ No se encuentra main_window.py")
        return False
    
    print(f"📄 Archivo: {filepath}")
    print()
    
    # Leer
    with open(filepath, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_original = contenido
    cambios = []
    
    # 1. Dashboard
    if 'from src.gui.dashboard_sincronizado import' not in contenido:
        # Buscar y reemplazar
        variantes_dashboard = [
            ('from src.gui.dashboard import Dashboard', 
             'from src.gui.dashboard_sincronizado import DashboardSincronizado as Dashboard'),
            ('from src.gui.dashboard import DashboardPanel',
             'from src.gui.dashboard_sincronizado import DashboardSincronizado as DashboardPanel'),
        ]
        
        for antes, despues in variantes_dashboard:
            if antes in contenido:
                contenido = contenido.replace(antes, despues)
                cambios.append(f"   ✅ Dashboard: {antes} → dashboard_sincronizado")
                break
    
    # 2. Sesiones
    if 'from src.gui.sesiones_mejorado import' not in contenido:
        variantes_sesiones = [
            ('from src.gui.sesiones_nuevo import SesionesPanel',
             'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'),
            ('from src.gui.sesiones import SesionesPanel',
             'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'),
            ('from src.gui.sesiones_con_calendario import SesionesPanel',
             'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'),
        ]
        
        for antes, despues in variantes_sesiones:
            if antes in contenido:
                contenido = contenido.replace(antes, despues)
                cambios.append(f"   ✅ Sesiones: {antes.split()[1]} → sesiones_mejorado")
                break
    
    if contenido == contenido_original:
        print("✅ Imports ya están correctos")
        print()
        return True
    
    # Hacer backup
    hacer_backup(filepath)
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print("📝 Cambios realizados:")
    for cambio in cambios:
        print(cambio)
    print()
    
    return True

def limpiar_google_sheets():
    """Limpia estados con emojis en Google Sheets"""
    print("=" * 70)
    print("🔧 PASO 3: Limpiando Estados en Google Sheets")
    print("=" * 70)
    print()
    
    try:
        from src.utils.sheets_manager import sheets_manager
        
        # Leer datos
        print("📊 Leyendo Google Sheets...")
        data = sheets_manager.get_all_data('Solicitudes')
        
        if not data or len(data) < 2:
            print("⚠️  No hay datos para limpiar")
            return True
        
        headers = data[0]
        
        if 'Estado' not in headers:
            print("⚠️  No hay columna 'Estado'")
            return True
        
        idx_estado = headers.index('Estado')
        
        # Limpiar estados
        cambios = 0
        for i, row in enumerate(data[1:], start=2):
            if len(row) > idx_estado:
                estado = row[idx_estado] if row[idx_estado] else ""
                
                # Limpiar emojis
                estado_limpio = estado
                for emoji in ['⏳', '✅', '🔴', '🟡', '🟢']:
                    estado_limpio = estado_limpio.replace(emoji, '')
                estado_limpio = estado_limpio.strip()
                
                # Normalizar
                if 'complet' in estado_limpio.lower():
                    estado_limpio = "Completado"
                elif 'proceso' in estado_limpio.lower():
                    estado_limpio = "En proceso"
                elif estado_limpio.lower() == '' or 'pendiente' in estado_limpio.lower():
                    estado_limpio = "Pendiente"
                
                if estado != estado_limpio:
                    # Actualizar
                    row_actualizada = row.copy()
                    while len(row_actualizada) <= idx_estado:
                        row_actualizada.append('')
                    row_actualizada[idx_estado] = estado_limpio
                    
                    sheets_manager.update_row('Solicitudes', i, row_actualizada)
                    print(f"   ✅ Fila {i}: '{estado}' → '{estado_limpio}'")
                    cambios += 1
        
        if cambios > 0:
            print()
            print(f"✅ {cambios} estado(s) limpiados")
        else:
            print("✅ Estados ya están limpios")
        
        print()
        return True
        
    except Exception as e:
        print(f"⚠️  Error al limpiar Google Sheets: {e}")
        print("   Puedes ejecutar: python limpiar_estados.py")
        print()
        return True  # No es crítico

def verificar_todo():
    """Verifica que todo esté correcto"""
    print("=" * 70)
    print("✅ PASO 4: Verificación Final")
    print("=" * 70)
    print()
    
    errores = []
    
    # 1. Archivos necesarios
    archivos = {
        'src/utils/calculador_estados.py': 'Calculador centralizado',
        'src/gui/dashboard_sincronizado.py': 'Dashboard nuevo',
        'src/gui/sesiones_mejorado.py': 'Sesiones nuevo',
        'src/gui/solicitudes_real.py': 'Solicitudes actualizado'
    }
    
    print("📂 Verificando archivos...")
    for archivo, desc in archivos.items():
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTA")
            errores.append(f"Falta archivo: {archivo}")
    
    print()
    
    # 2. Imports
    print("📝 Verificando imports...")
    posibles = ['src/gui/main_window.py', 'main_window.py', 'gui/main_window.py']
    main_path = None
    for p in posibles:
        if os.path.exists(p):
            main_path = p
            break
    
    if main_path:
        with open(main_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if 'dashboard_sincronizado' in contenido:
            print("   ✅ Import de Dashboard correcto")
        else:
            print("   ❌ Import de Dashboard incorrecto")
            errores.append("Import de Dashboard incorrecto")
        
        if 'sesiones_mejorado' in contenido:
            print("   ✅ Import de Sesiones correcto")
        else:
            print("   ❌ Import de Sesiones incorrecto")
            errores.append("Import de Sesiones incorrecto")
    else:
        print("   ⚠️  No se encuentra main_window.py")
        errores.append("No se encuentra main_window.py")
    
    print()
    
    # 3. PDF Extractor
    print("📄 Verificando PDF Extractor...")
    if os.path.exists('src/utils/pdf_extractor.py'):
        with open('src/utils/pdf_extractor.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if '⏳ Pendiente' in contenido or '✅ Completado' in contenido:
            print("   ⚠️  PDF Extractor aún tiene emojis")
            errores.append("PDF Extractor con emojis")
        else:
            print("   ✅ PDF Extractor sin emojis")
    
    print()
    
    return len(errores) == 0, errores

def main():
    """Función principal"""
    print()
    print("=" * 70)
    print("🚀 MEGA-PARCHE - Arreglo Total de Sincronización")
    print("=" * 70)
    print()
    print("Este script va a:")
    print("  1. Corregir PDF Extractor (quitar emojis)")
    print("  2. Corregir imports en main_window.py")
    print("  3. Limpiar estados en Google Sheets")
    print("  4. Verificar que todo esté correcto")
    print()
    
    respuesta = input("¿Continuar? (s/n): ").lower()
    
    if respuesta != 's':
        print("Operación cancelada.")
        return 0
    
    print()
    
    # Ejecutar pasos
    exito = True
    
    # Paso 1
    if not corregir_pdf_extractor():
        exito = False
    
    # Paso 2
    if not corregir_main_window():
        exito = False
    
    # Paso 3
    if not limpiar_google_sheets():
        exito = False
    
    # Paso 4
    todo_ok, errores = verificar_todo()
    
    # Resumen
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print()
    
    if todo_ok and exito:
        print("✅ ¡TODO CORREGIDO!")
        print()
        print("📋 PRÓXIMOS PASOS:")
        print("   1. Cierra la aplicación si está abierta")
        print("   2. Ejecuta: python main.py")
        print("   3. Verifica que:")
        print("      • Dashboard tiene 6 KPIs grandes")
        print("      • Números coinciden: Total=11, Pendientes=7, Completados=3")
        print("      • Sesiones muestra iconos con colores")
        print()
        return 0
    else:
        print("⚠️  HAY PROBLEMAS PENDIENTES:")
        print()
        for error in errores:
            print(f"   • {error}")
        print()
        print("Revisa los errores arriba y vuelve a ejecutar el script.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
