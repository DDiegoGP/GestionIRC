#!/usr/bin/env python3
"""
Script de Diagnóstico - Detecta qué versiones están en uso
"""
import os
import sys
from pathlib import Path

def verificar_archivos():
    """Verifica que los archivos necesarios existen"""
    print("=" * 70)
    print("🔍 DIAGNÓSTICO DE SINCRONIZACIÓN")
    print("=" * 70)
    print()
    
    archivos_necesarios = {
        'src/utils/calculador_estados.py': 'Calculador centralizado',
        'src/gui/dashboard_sincronizado.py': 'Dashboard nuevo',
        'src/gui/sesiones_mejorado.py': 'Sesiones nuevo',
        'src/gui/solicitudes_real.py': 'Solicitudes actualizado'
    }
    
    print("📂 VERIFICANDO ARCHIVOS...")
    print()
    
    todos_existen = True
    for archivo, descripcion in archivos_necesarios.items():
        existe = os.path.exists(archivo)
        icono = "✅" if existe else "❌"
        print(f"   {icono} {archivo}")
        print(f"      {descripcion}")
        if not existe:
            todos_existen = False
    
    print()
    return todos_existen

def analizar_imports():
    """Analiza los imports en main_window.py"""
    print("🔍 ANALIZANDO IMPORTS EN main_window.py...")
    print()
    
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
        print("   ❌ No se encuentra main_window.py")
        print()
        return False
    
    print(f"   📄 Encontrado: {main_window_path}")
    print()
    
    # Leer archivo
    with open(main_window_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar imports
    problemas = []
    
    # 1. Dashboard
    print("   🔍 Verificando import de Dashboard...")
    if 'from src.gui.dashboard_sincronizado import' in contenido:
        print("      ✅ CORRECTO: Importa dashboard_sincronizado")
    elif 'from src.gui.dashboard import' in contenido:
        print("      ❌ INCORRECTO: Importa dashboard (versión antigua)")
        problemas.append({
            'tipo': 'dashboard',
            'actual': 'from src.gui.dashboard import',
            'correcto': 'from src.gui.dashboard_sincronizado import DashboardSincronizado as DashboardPanel'
        })
    else:
        print("      ⚠️  No se encuentra import de dashboard")
    
    print()
    
    # 2. Sesiones
    print("   🔍 Verificando import de Sesiones...")
    if 'from src.gui.sesiones_mejorado import' in contenido:
        print("      ✅ CORRECTO: Importa sesiones_mejorado")
    elif 'from src.gui.sesiones_nuevo import' in contenido:
        print("      ❌ INCORRECTO: Importa sesiones_nuevo (versión antigua)")
        problemas.append({
            'tipo': 'sesiones',
            'actual': 'from src.gui.sesiones_nuevo import',
            'correcto': 'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'
        })
    elif 'from src.gui.sesiones import' in contenido:
        print("      ❌ INCORRECTO: Importa sesiones (versión muy antigua)")
        problemas.append({
            'tipo': 'sesiones',
            'actual': 'from src.gui.sesiones import',
            'correcto': 'from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel'
        })
    else:
        print("      ⚠️  No se encuentra import de sesiones")
    
    print()
    
    # 3. Solicitudes
    print("   🔍 Verificando import de Solicitudes...")
    if 'from src.gui.solicitudes_real import' in contenido:
        print("      ✅ CORRECTO: Importa solicitudes_real")
        
        # Verificar que el archivo tiene el nuevo método
        if os.path.exists('src/gui/solicitudes_real.py'):
            with open('src/gui/solicitudes_real.py', 'r', encoding='utf-8') as f:
                sol_contenido = f.read()
            
            if 'def marcar_en_proceso' in sol_contenido:
                print("      ✅ Archivo actualizado (tiene método marcar_en_proceso)")
            else:
                print("      ⚠️  Archivo NO actualizado (falta método marcar_en_proceso)")
                problemas.append({
                    'tipo': 'solicitudes_archivo',
                    'actual': 'solicitudes_real.py antiguo',
                    'correcto': 'Reemplazar con la versión del ZIP'
                })
    else:
        print("      ⚠️  No se encuentra import de solicitudes")
    
    print()
    
    return problemas, main_window_path

def generar_solucion(problemas, main_window_path):
    """Genera instrucciones de solución"""
    if not problemas:
        print("✅ ¡TODO CORRECTO!")
        print()
        print("   Los imports están bien configurados.")
        print()
        return True
    
    print("=" * 70)
    print("⚠️  PROBLEMAS DETECTADOS")
    print("=" * 70)
    print()
    
    print(f"Se encontraron {len(problemas)} problema(s) de configuración.")
    print()
    
    # Soluciones
    print("🔧 SOLUCIÓN:")
    print()
    print(f"Abre el archivo: {main_window_path}")
    print()
    
    for i, problema in enumerate(problemas, 1):
        print(f"{i}. {problema['tipo'].upper()}:")
        print()
        print("   BUSCA esta línea:")
        print(f"   {problema['actual']}...")
        print()
        print("   CÁMBIALA por:")
        print(f"   {problema['correcto']}")
        print()
    
    # Generar archivo de parche
    print("💡 OPCIÓN RÁPIDA: Generando archivo de corrección...")
    print()
    
    try:
        with open('CORRECCION_IMPORTS.txt', 'w', encoding='utf-8') as f:
            f.write("# CORRECCIONES NECESARIAS EN main_window.py\n")
            f.write("#" * 70 + "\n\n")
            
            for problema in problemas:
                f.write(f"# {problema['tipo'].upper()}\n")
                f.write(f"# ANTES:\n")
                f.write(f"# {problema['actual']}...\n\n")
                f.write(f"# AHORA:\n")
                f.write(f"{problema['correcto']}\n")
                f.write("\n" + "-" * 70 + "\n\n")
        
        print("   ✅ Archivo creado: CORRECCION_IMPORTS.txt")
        print("      Contiene las líneas exactas que necesitas cambiar.")
        print()
    except Exception as e:
        print(f"   ⚠️  No se pudo crear archivo: {e}")
        print()
    
    return False

def verificar_google_sheets():
    """Verifica configuración de Google Sheets"""
    print("=" * 70)
    print("📊 VERIFICANDO GOOGLE SHEETS")
    print("=" * 70)
    print()
    
    try:
        from src.utils.sheets_manager import sheets_manager
        from src.constants_real import HEADERS_SOLICITUDES
        
        # Intentar leer datos
        print("   🔄 Conectando a Google Sheets...")
        data = sheets_manager.get_all_data('Solicitudes')
        
        if not data:
            print("   ❌ No se pudo leer la hoja 'Solicitudes'")
            return False
        
        print(f"   ✅ Conexión exitosa")
        print(f"   📊 {len(data) - 1} solicitudes encontradas")
        print()
        
        # Verificar columna Estado
        headers = data[0]
        if 'Estado' in headers:
            print("   ✅ Columna 'Estado' existe")
            
            # Contar estados
            estados = {}
            for row in data[1:]:
                if len(row) > 0:
                    idx_estado = headers.index('Estado')
                    estado = row[idx_estado] if len(row) > idx_estado and row[idx_estado] else 'Vacío'
                    estados[estado] = estados.get(estado, 0) + 1
            
            print()
            print("   📈 DISTRIBUCIÓN DE ESTADOS:")
            for estado, count in sorted(estados.items()):
                print(f"      • {estado}: {count}")
            print()
            
            # Verificar sesiones
            print("   🔍 Verificando sesiones...")
            data_sesiones = sheets_manager.get_all_data('Sesiones')
            print(f"   ✅ {len(data_sesiones) - 1} sesiones encontradas")
            print()
            
        else:
            print("   ❌ Columna 'Estado' NO existe")
            print()
            print("   📝 ACCIÓN: Añade la columna 'Estado' a Google Sheets")
            print("      Ejecuta: python verificar_columnas.py")
            print()
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print()
        return False

def main():
    """Función principal"""
    
    # 1. Verificar archivos
    if not verificar_archivos():
        print("⚠️  Faltan archivos necesarios.")
        print("   Copia los archivos del ZIP antes de continuar.")
        print()
        return 1
    
    # 2. Analizar imports
    problemas, main_window_path = analizar_imports()
    
    if not problemas:
        print("✅ Imports correctos")
        print()
    else:
        if not generar_solucion(problemas, main_window_path):
            print()
            print("=" * 70)
            print("📝 RESUMEN")
            print("=" * 70)
            print()
            print("1. Abre main_window.py")
            print("2. Cambia los imports según las instrucciones arriba")
            print("3. Guarda el archivo")
            print("4. Reinicia la aplicación")
            print()
            return 1
    
    # 3. Verificar Google Sheets
    verificar_google_sheets()
    
    # Resumen final
    print("=" * 70)
    print("✅ DIAGNÓSTICO COMPLETO")
    print("=" * 70)
    print()
    
    if problemas:
        print("⚠️  Hay cambios pendientes en main_window.py")
        print("   Sigue las instrucciones arriba.")
    else:
        print("✅ Todo configurado correctamente")
        print()
        print("   Si los números siguen sin coincidir:")
        print("   1. Cierra completamente la aplicación")
        print("   2. Reiníciala con: python main.py")
        print("   3. Click en 🔄 Actualizar en cada pestaña")
    
    print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
