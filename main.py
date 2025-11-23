"""
Sistema de Gestión IRC - Universidad Complutense de Madrid
Versión 4.0 - Ejecutable Windows

Punto de entrada principal de la aplicación
"""
import sys
import os
from pathlib import Path

# Configurar el path para importaciones
if getattr(sys, 'frozen', False):
    # Si está ejecutándose como ejecutable
    application_path = Path(sys.executable).parent
else:
    # Si está ejecutándose como script
    application_path = Path(__file__).parent

os.chdir(application_path)
sys.path.insert(0, str(application_path))

# Importar la ventana principal
from src.gui.main_window import MainWindow
from src.utils.logger import logger
from config import APP_CONFIG

def main():
    """Función principal"""
    try:
        logger.info("="*60)
        logger.info(f"Iniciando {APP_CONFIG['NOMBRE']} v{APP_CONFIG['VERSION']}")
        logger.info("="*60)
        
        # Crear y ejecutar la aplicación
        app = MainWindow()
        app.run()
        
        logger.info("Aplicación cerrada correctamente")
        
    except Exception as e:
        logger.critical(f"Error fatal en la aplicación: {e}", exc_info=True)
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error Fatal",
            f"Error al iniciar la aplicación:\n\n{str(e)}\n\n"
            "Consulta el archivo de log para más detalles."
        )
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
