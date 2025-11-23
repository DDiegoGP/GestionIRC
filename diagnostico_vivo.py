#!/usr/bin/env python3
"""
DIAGNÓSTICO EN VIVO - Muestra qué archivos se están usando AHORA
"""
import sys
from pathlib import Path

def diagnosticar():
    """Diagnostica qué está pasando AHORA"""
    print()
    print("=" * 70)
    print("🔍 DIAGNÓSTICO EN VIVO")
    print("=" * 70)
    print()
    
    try:
        # Importar el sistema
        print("📦 Importando sistema...")
        
        # Dashboard
        print()
        print("1️⃣  DASHBOARD")
        print("-" * 70)
        try:
            from src.gui import dashboard
            from src.gui import dashboard_sincronizado
            
            dashboard_file = Path(dashboard.__file__)
            dashboard_sync_file = Path(dashboard_sincronizado.__file__)
            
            print(f"   📄 dashboard.py: {dashboard_file}")
            print(f"   📄 dashboard_sincronizado.py: {dashboard_sync_file}")
            print()
            
            # Ver cuál se está usando
            from src.gui.main_window import MainWindow
            import inspect
            
            source = inspect.getsource(MainWindow.__init__)
            
            if 'dashboard_sincronizado' in source or 'DashboardSincronizado' in source:
                print("   ✅ main_window.py IMPORTA dashboard_sincronizado")
            elif 'from src.gui.dashboard import' in source or 'from .dashboard import' in source:
                print("   ❌ main_window.py IMPORTA dashboard (ANTIGUO)")
            else:
                print("   ⚠️  No se detecta import de dashboard")
            
        except ImportError as e:
            print(f"   ❌ Error al importar: {e}")
        
        # Sesiones
        print()
        print("2️⃣  SESIONES")
        print("-" * 70)
        try:
            from src.gui import sesiones_mejorado
            
            sesiones_file = Path(sesiones_mejorado.__file__)
            print(f"   📄 sesiones_mejorado.py: {sesiones_file}")
            print()
            
            # Ver cuál se está usando
            source = inspect.getsource(MainWindow.__init__)
            
            if 'sesiones_mejorado' in source or 'SesionesPanelMejorado' in source:
                print("   ✅ main_window.py IMPORTA sesiones_mejorado")
            elif 'sesiones_nuevo' in source:
                print("   ❌ main_window.py IMPORTA sesiones_nuevo (ANTIGUO)")
            elif 'from src.gui.sesiones import' in source:
                print("   ❌ main_window.py IMPORTA sesiones (MUY ANTIGUO)")
            else:
                print("   ⚠️  No se detecta import de sesiones")
            
        except ImportError as e:
            print(f"   ❌ Error al importar: {e}")
        
        # Calculador
        print()
        print("3️⃣  CALCULADOR DE ESTADOS")
        print("-" * 70)
        try:
            from src.utils import calculador_estados
            
            calc_file = Path(calculador_estados.__file__)
            print(f"   📄 calculador_estados.py: {calc_file}")
            print()
            
            # Ver si tiene las funciones correctas
            if hasattr(calculador_estados, 'CalculadorEstados'):
                print("   ✅ Tiene clase CalculadorEstados")
                
                if hasattr(calculador_estados.CalculadorEstados, 'calcular_resumen_general'):
                    print("   ✅ Tiene método calcular_resumen_general")
                else:
                    print("   ❌ NO tiene método calcular_resumen_general")
            else:
                print("   ❌ NO tiene clase CalculadorEstados")
            
        except ImportError as e:
            print(f"   ❌ No existe calculador_estados: {e}")
        
        # Google Sheets
        print()
        print("4️⃣  DATOS EN GOOGLE SHEETS")
        print("-" * 70)
        try:
            from src.utils.sheets_manager import sheets_manager
            
            data = sheets_manager.get_all_data('Solicitudes')
            
            if not data or len(data) < 2:
                print("   ⚠️  No hay datos")
            else:
                headers = data[0]
                
                if 'Estado' not in headers:
                    print("   ❌ NO hay columna 'Estado'")
                else:
                    idx = headers.index('Estado')
                    print(f"   ✅ Columna 'Estado' en posición {idx + 1}")
                    print()
                    
                    # Contar estados
                    estados = {}
                    for row in data[1:]:
                        if len(row) > idx:
                            estado = row[idx] if row[idx] else "Vacío"
                            estados[estado] = estados.get(estado, 0) + 1
                    
                    print("   📊 ESTADOS ACTUALES:")
                    for estado, count in sorted(estados.items()):
                        emoji_warning = " ⚠️ (CON EMOJI)" if any(e in estado for e in ['⏳', '✅', '🟢', '🟡', '🔴']) else ""
                        print(f"      • {estado}: {count}{emoji_warning}")
        
        except Exception as e:
            print(f"   ❌ Error al leer Google Sheets: {e}")
        
        # Resumen
        print()
        print("=" * 70)
        print("📊 RESUMEN DEL PROBLEMA")
        print("=" * 70)
        print()
        
        print("Si ves:")
        print("   ❌ 'main_window.py IMPORTA dashboard (ANTIGUO)'")
        print("   → El dashboard NO se actualizó")
        print()
        print("   ❌ 'main_window.py IMPORTA sesiones_nuevo (ANTIGUO)'")
        print("   → Las sesiones NO se actualizaron")
        print()
        print("   ⚠️ Estados CON EMOJI en Google Sheets")
        print("   → Necesitas limpiar Google Sheets")
        print()
        print("SOLUCIÓN:")
        print("   python instalador_forzado.py")
        print()
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar()
