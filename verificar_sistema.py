"""
Script de Verificación Rápida
Verifica que los métodos de sheets_manager funcionen
"""
import sys
from pathlib import Path

# Añadir ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.sheets_manager import sheets_manager
from src.utils.config_manager import config_manager

print("=" * 60)
print("VERIFICACIÓN RÁPIDA DEL SISTEMA")
print("=" * 60)

# 1. Verificar configuración
print("\n1️⃣ CONFIGURACIÓN:")
print(f"   Spreadsheet ID: {config_manager.get_spreadsheet_id()}")
print(f"   Plantilla PDF: {config_manager.get_plantilla_pdf()}")

# 2. Verificar archivo de plantilla
print("\n2️⃣ PLANTILLA PDF:")
plantilla = Path(config_manager.get_plantilla_pdf())
if plantilla.exists():
    print(f"   ✅ Archivo encontrado: {plantilla}")
else:
    print(f"   ❌ Archivo NO encontrado: {plantilla}")
    print(f"   SOLUCIÓN: Abre la app y ve a ⚙️ Configuración")

# 3. Verificar conexión a Sheets
print("\n3️⃣ CONEXIÓN GOOGLE SHEETS:")
if sheets_manager.is_authenticated():
    print("   ✅ Autenticado correctamente")
    
    # Verificar métodos
    print("\n4️⃣ MÉTODOS DISPONIBLES:")
    metodos = ['append_row', 'update_row', 'delete_row', 'get_all_data']
    for metodo in metodos:
        if hasattr(sheets_manager, metodo):
            print(f"   ✅ {metodo}")
        else:
            print(f"   ❌ {metodo} - NO ENCONTRADO")
else:
    print("   ❌ No autenticado")
    print("   SOLUCIÓN: Configura credenciales en la app")

print("\n" + "=" * 60)
print("FIN DE VERIFICACIÓN")
print("=" * 60)
