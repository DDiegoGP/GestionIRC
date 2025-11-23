#!/usr/bin/env python3
"""
Script para Limpiar Estados en Google Sheets
Elimina emojis y normaliza los estados
"""
import sys
import re
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger

def limpiar_estado(estado: str) -> str:
    """
    Limpia un estado eliminando emojis y normalizando texto.
    
    Args:
        estado: Estado original (puede tener emojis)
    
    Returns:
        Estado limpio sin emojis
    """
    if not estado:
        return "Pendiente"
    
    # Eliminar emojis comunes
    estado_limpio = estado
    
    # Lista de emojis a eliminar
    emojis = ['⏳', '✅', '🔴', '🟡', '🟢', '📋', '⚠️', '🚀', '✨']
    for emoji in emojis:
        estado_limpio = estado_limpio.replace(emoji, '')
    
    # Eliminar espacios extra
    estado_limpio = estado_limpio.strip()
    
    # Normalizar variantes
    estado_lower = estado_limpio.lower()
    
    if 'complet' in estado_lower:
        return "Completado"
    elif 'proceso' in estado_lower:
        return "En proceso"
    elif 'pendiente' in estado_lower or estado_limpio == '':
        return "Pendiente"
    
    # Si no coincide con ninguno, devolver el limpio
    return estado_limpio if estado_limpio else "Pendiente"

def limpiar_estados_google_sheets():
    """Limpia todos los estados en Google Sheets"""
    
    print("=" * 70)
    print("🧹 LIMPIEZA DE ESTADOS EN GOOGLE SHEETS")
    print("=" * 70)
    print()
    
    try:
        # Leer datos
        print("📊 Leyendo datos de Google Sheets...")
        data = sheets_manager.get_all_data('Solicitudes')
        
        if not data or len(data) < 2:
            print("❌ No hay datos para limpiar")
            return False
        
        headers = data[0]
        
        # Encontrar columna Estado
        if 'Estado' not in headers:
            print("❌ No se encuentra la columna 'Estado'")
            print("   Añade primero la columna 'Estado' a Google Sheets")
            return False
        
        idx_estado = headers.index('Estado')
        print(f"✅ Columna 'Estado' encontrada en posición {idx_estado + 1}")
        print()
        
        # Analizar estados
        print("🔍 Analizando estados actuales...")
        print()
        
        estados_originales = {}
        for i, row in enumerate(data[1:], start=2):
            if len(row) > idx_estado:
                estado = row[idx_estado] if row[idx_estado] else ""
                if estado not in estados_originales:
                    estados_originales[estado] = []
                estados_originales[estado].append(i)
        
        # Mostrar estados encontrados
        print("📋 ESTADOS ACTUALES:")
        for estado, filas in sorted(estados_originales.items()):
            estado_limpio = limpiar_estado(estado)
            flecha = "→" if estado != estado_limpio else " "
            print(f"   '{estado}' ({len(filas)} solicitudes) {flecha} '{estado_limpio}'")
        
        print()
        
        # Contar cambios necesarios
        cambios_necesarios = sum(
            len(filas) for estado, filas in estados_originales.items()
            if limpiar_estado(estado) != estado
        )
        
        if cambios_necesarios == 0:
            print("✅ ¡Todos los estados ya están limpios!")
            print()
            return True
        
        print(f"⚠️  Se necesitan limpiar {cambios_necesarios} estado(s)")
        print()
        
        # Pedir confirmación
        print("Esta operación va a:")
        print("  1. Eliminar todos los emojis de los estados")
        print("  2. Normalizar los estados a:")
        print("     • Pendiente")
        print("     • En proceso")
        print("     • Completado")
        print("  3. Actualizar Google Sheets")
        print()
        
        respuesta = input("¿Continuar? (s/n): ").lower()
        
        if respuesta != 's':
            print("Operación cancelada.")
            return False
        
        print()
        print("🔄 Limpiando estados...")
        print()
        
        # Limpiar cada fila
        cambios_realizados = 0
        errores = 0
        
        for i, row in enumerate(data[1:], start=2):
            if len(row) > idx_estado:
                estado_original = row[idx_estado] if row[idx_estado] else ""
                estado_limpio = limpiar_estado(estado_original)
                
                if estado_original != estado_limpio:
                    try:
                        # Actualizar la fila completa con el estado corregido
                        row_actualizada = row.copy()
                        
                        # Extender la fila si es necesario
                        while len(row_actualizada) <= idx_estado:
                            row_actualizada.append('')
                        
                        # Actualizar solo el estado
                        row_actualizada[idx_estado] = estado_limpio
                        
                        # Actualizar en Google Sheets
                        resultado = sheets_manager.update_row(
                            'Solicitudes',
                            i,
                            row_actualizada
                        )
                        
                        if resultado:
                            print(f"   ✅ Fila {i}: '{estado_original}' → '{estado_limpio}'")
                            cambios_realizados += 1
                        else:
                            print(f"   ⚠️  Fila {i}: No se pudo actualizar")
                            errores += 1
                        
                    except Exception as e:
                        print(f"   ❌ Fila {i}: Error - {e}")
                        errores += 1
        
        print()
        print("=" * 70)
        print("✅ LIMPIEZA COMPLETADA")
        print("=" * 70)
        print()
        print(f"📊 Resultados:")
        print(f"   • Cambios realizados: {cambios_realizados}")
        print(f"   • Errores: {errores}")
        print()
        
        if errores > 0:
            print("⚠️  Algunos estados no se pudieron limpiar")
            print("   Revisa manualmente en Google Sheets")
            print()
        
        # Mostrar estados finales
        print("🔍 Verificando estados limpios...")
        data_nueva = sheets_manager.get_all_data('Solicitudes')
        
        estados_limpios = {}
        for row in data_nueva[1:]:
            if len(row) > idx_estado:
                estado = row[idx_estado] if row[idx_estado] else "Pendiente"
                estados_limpios[estado] = estados_limpios.get(estado, 0) + 1
        
        print()
        print("📈 ESTADOS FINALES:")
        for estado, count in sorted(estados_limpios.items()):
            print(f"   • {estado}: {count}")
        
        print()
        print("✅ Ahora reinicia la aplicación para ver los cambios:")
        print("   python main.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print()
        print("Detalles del error:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    resultado = limpiar_estados_google_sheets()
    
    if resultado:
        sys.exit(0)
    else:
        sys.exit(1)
