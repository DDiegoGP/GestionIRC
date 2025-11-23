"""
Gestor de Configuración Dinámica
Maneja configuraciones que pueden cambiar en tiempo de ejecución
"""
import json
from pathlib import Path
from typing import Optional, Any

from config import CONFIG_FILE, PDF_CONFIG, SHEETS_CONFIG


class ConfigManager:
    """Gestor de configuración dinámica"""
    
    def __init__(self):
        self.config = {}
        self.load()
    
    def load(self):
        """Carga la configuración desde el archivo"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error al cargar configuración: {e}")
                self.config = {}
        else:
            self.config = {}
        
        # Asegurar valores por defecto
        self._set_defaults()
    
    def _set_defaults(self):
        """Establece valores por defecto si no existen"""
        if 'spreadsheet_id' not in self.config:
            self.config['spreadsheet_id'] = SHEETS_CONFIG.get('SPREADSHEET_ID', '')
        
        if 'plantilla_pdf' not in self.config:
            self.config['plantilla_pdf'] = str(PDF_CONFIG['PLANTILLA_SOLICITUD'])
        
        if 'ultimo_spreadsheet_usado' not in self.config:
            self.config['ultimo_spreadsheet_usado'] = ''
    
    def save(self):
        """Guarda la configuración en el archivo"""
        try:
            CONFIG_FILE.parent.mkdir(exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Establece un valor de configuración"""
        self.config[key] = value
        self.save()
    
    # Métodos específicos
    
    def get_spreadsheet_id(self) -> str:
        """Obtiene el ID del spreadsheet actual"""
        return self.config.get('spreadsheet_id', '')
    
    def set_spreadsheet_id(self, spreadsheet_id: str):
        """Establece el ID del spreadsheet"""
        self.config['spreadsheet_id'] = spreadsheet_id
        self.config['ultimo_spreadsheet_usado'] = spreadsheet_id
        self.save()
    
    def get_plantilla_pdf(self) -> str:
        """Obtiene la ruta de la plantilla PDF"""
        return self.config.get('plantilla_pdf', str(PDF_CONFIG['PLANTILLA_SOLICITUD']))
    
    def set_plantilla_pdf(self, ruta: str):
        """Establece la ruta de la plantilla PDF"""
        self.config['plantilla_pdf'] = ruta
        self.save()
    
    def get_spreadsheets_recientes(self) -> list:
        """Obtiene la lista de spreadsheets usados recientemente"""
        return self.config.get('spreadsheets_recientes', [])
    
    def add_spreadsheet_reciente(self, spreadsheet_id: str, nombre: str = ""):
        """Añade un spreadsheet a los recientes"""
        recientes = self.get_spreadsheets_recientes()
        
        # Eliminar si ya existe
        recientes = [s for s in recientes if s.get('id') != spreadsheet_id]
        
        # Añadir al principio
        recientes.insert(0, {
            'id': spreadsheet_id,
            'nombre': nombre,
            'fecha': str(Path.ctime(CONFIG_FILE)) if CONFIG_FILE.exists() else ""
        })
        
        # Mantener solo los últimos 5
        recientes = recientes[:5]
        
        self.config['spreadsheets_recientes'] = recientes
        self.save()


# Instancia global
config_manager = ConfigManager()
