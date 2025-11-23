"""
Configuración del Sistema de Gestión IRC - UCM
"""
import os
import sys
from pathlib import Path

# Directorios del proyecto
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BACKUPS_DIR = DATA_DIR / "backups"
TEMPLATES_DIR = BASE_DIR / "templates"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
FORMULARIOS_DIR = BASE_DIR / "formularios"

# Crear directorios si no existen
for directory in [DATA_DIR, BACKUPS_DIR, TEMPLATES_DIR, EXPORTS_DIR, LOGS_DIR, FORMULARIOS_DIR]:
    directory.mkdir(exist_ok=True)

# Google Sheets Configuration
SHEETS_CONFIG = {
    'SPREADSHEET_ID': '',  # Se configura en primera ejecución
    'SHEET_SOLICITUDES': 'Solicitudes',
    'SHEET_SESIONES': 'Sesiones',
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets']
}

# Archivos de credenciales
if getattr(sys, 'frozen', False):
    # Si es ejecutable empaquetado
    CREDENTIALS_FILE = Path(sys.executable).parent / "config" / "credentials.json"
    TOKEN_FILE = Path(sys.executable).parent / "config" / "token.json"
    SERVICE_ACCOUNT_FILE = Path(sys.executable).parent / "config" / "service_account.json"
else:
    # Si es desarrollo
    CREDENTIALS_FILE = BASE_DIR / "config" / "credentials.json"
    TOKEN_FILE = BASE_DIR / "config" / "token.json"
    SERVICE_ACCOUNT_FILE = BASE_DIR / "config" / "service_account.json"

# Configuración de PDFs
PDF_CONFIG = {
    'PLANTILLA_SOLICITUD': FORMULARIOS_DIR / "anexo_III_2025_V8.pdf",
}

# Archivo de configuración dinámica
CONFIG_FILE = DATA_DIR / "app_config.json"

# Configuración de la aplicación
APP_CONFIG = {
    'NOMBRE': 'Gestión IRC - UCM',
    'VERSION': '4.0.0',
    'AUTOR': 'Universidad Complutense de Madrid',
    'BACKUP_AUTO': True,
    'BACKUP_INTERVAL_HOURS': 24,
    'CACHE_ENABLED': True,
    'CACHE_TTL_MINUTES': 5,
}

# Configuración de la interfaz
UI_CONFIG = {
    'WINDOW_WIDTH': 1400,
    'WINDOW_HEIGHT': 900,
    'FONT_FAMILY': 'Segoe UI',
    'FONT_SIZE_NORMAL': 10,
    'FONT_SIZE_TITLE': 14,
    'FONT_SIZE_HEADER': 12,
    'COLOR_PRIMARY': '#1976D2',
    'COLOR_SUCCESS': '#4CAF50',
    'COLOR_WARNING': '#FF9800',
    'COLOR_ERROR': '#F44336',
    'COLOR_BG': '#F5F5F5',
}

# Validaciones
VALIDACIONES = {
    'MIN_NOMBRE_LENGTH': 3,
    'MAX_NOMBRE_LENGTH': 100,
    'EMAIL_REGEX': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'TELEFONO_REGEX': r'^\+?[\d\s\-()]+$',
}

# Logs
LOG_CONFIG = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'FILE': LOGS_DIR / 'gestion_irc.log',
    'MAX_BYTES': 10 * 1024 * 1024,  # 10 MB
    'BACKUP_COUNT': 5,
}
