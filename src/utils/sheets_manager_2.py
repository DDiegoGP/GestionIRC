"""
Gestor de Google Sheets - Múltiples métodos de autenticación
Soporta: OAuth2, Service Account, y credenciales directas
"""
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    SHEETS_CONFIG, 
    CREDENTIALS_FILE, 
    TOKEN_FILE, 
    SERVICE_ACCOUNT_FILE,
    DATA_DIR
)

logger = logging.getLogger(__name__)


class SheetsManager:
    """Gestor de conexión y operaciones con Google Sheets"""
    
    def __init__(self):
        self.service = None
        self.spreadsheet_id = None
        self.cache = {}
        self.cache_timestamp = {}
        self.cache_ttl = timedelta(minutes=5)
        self._load_config()
        
        # Intentar autenticar automáticamente
        try:
            self.authenticate('auto')
        except Exception as e:
            logger.debug(f"No se pudo autenticar automáticamente: {e}")
        
    def _load_config(self):
        """Carga la configuración guardada"""
        config_file = DATA_DIR / "sheets_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.spreadsheet_id = config.get('spreadsheet_id')
    
    def is_authenticated(self) -> bool:
        """
        Verifica si hay una sesión autenticada activa.
        
        Returns:
            bool: True si está autenticado
        """
        return self.service is not None
                
    def _save_config(self):
        """Guarda la configuración"""
        config_file = DATA_DIR / "sheets_config.json"
        with open(config_file, 'w') as f:
            json.dump({'spreadsheet_id': self.spreadsheet_id}, f)
    
    def authenticate(self, method='auto') -> bool:
        """
        Autentica con Google Sheets usando el método especificado.
        
        Args:
            method: 'auto', 'service_account', 'oauth', 'token'
            
        Returns:
            bool: True si autenticación exitosa
        """
        try:
            if method == 'auto':
                # Intentar en orden: service_account -> token -> oauth
                if self._try_service_account():
                    logger.info("✅ Autenticado con Service Account")
                    return True
                elif self._try_token():
                    logger.info("✅ Autenticado con Token guardado")
                    return True
                elif self._try_oauth():
                    logger.info("✅ Autenticado con OAuth2")
                    return True
                else:
                    logger.error("❌ No se pudo autenticar con ningún método")
                    return False
                    
            elif method == 'service_account':
                return self._try_service_account()
                
            elif method == 'oauth':
                return self._try_oauth()
                
            elif method == 'token':
                return self._try_token()
                
            return False
            
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            return False
    
    def _try_service_account(self) -> bool:
        """Intenta autenticar con Service Account"""
        try:
            if not SERVICE_ACCOUNT_FILE.exists():
                return False
                
            creds = service_account.Credentials.from_service_account_file(
                str(SERVICE_ACCOUNT_FILE),
                scopes=SHEETS_CONFIG['SCOPES']
            )
            
            self.service = build('sheets', 'v4', credentials=creds)
            return True
            
        except Exception as e:
            logger.debug(f"Service Account no disponible: {e}")
            return False
    
    def _try_token(self) -> bool:
        """Intenta autenticar con token guardado"""
        try:
            if not TOKEN_FILE.exists():
                return False
                
            creds = Credentials.from_authorized_user_file(
                str(TOKEN_FILE),
                SHEETS_CONFIG['SCOPES']
            )
            
            # Renovar si es necesario
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Guardar token renovado
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            
            if creds and creds.valid:
                self.service = build('sheets', 'v4', credentials=creds)
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Token no válido: {e}")
            return False
    
    def _try_oauth(self) -> bool:
        """Intenta autenticar con OAuth2 (abre navegador)"""
        try:
            if not CREDENTIALS_FILE.exists():
                logger.error(f"No se encontró {CREDENTIALS_FILE}")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE),
                SHEETS_CONFIG['SCOPES']
            )
            
            creds = flow.run_local_server(port=0)
            
            # Guardar token para próximas ejecuciones
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
            
            self.service = build('sheets', 'v4', credentials=creds)
            return True
            
        except Exception as e:
            logger.error(f"Error en OAuth2: {e}")
            return False
    
    def set_spreadsheet_id(self, spreadsheet_id: str):
        """Establece el ID del spreadsheet"""
        self.spreadsheet_id = spreadsheet_id
        self._save_config()
    
    def test_connection(self) -> bool:
        """Prueba la conexión con el spreadsheet"""
        try:
            if not self.service or not self.spreadsheet_id:
                return False
                
            self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            return True
            
        except HttpError as e:
            logger.error(f"Error al probar conexión: {e}")
            return False
    
    def read_range(self, sheet_name: str, range_name: str) -> List[List[Any]]:
        """
        Lee un rango de celdas del sheet.
        
        Args:
            sheet_name: Nombre de la hoja
            range_name: Rango en formato A1 (ej: 'A1:Z100')
            
        Returns:
            Lista de listas con los valores
        """
        try:
            cache_key = f"{sheet_name}!{range_name}"
            
            # Verificar caché
            if cache_key in self.cache:
                if datetime.now() - self.cache_timestamp[cache_key] < self.cache_ttl:
                    logger.debug(f"Cache hit para {cache_key}")
                    return self.cache[cache_key]
            
            # Leer del sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}"
            ).execute()
            
            values = result.get('values', [])
            
            # Actualizar caché
            self.cache[cache_key] = values
            self.cache_timestamp[cache_key] = datetime.now()
            
            return values
            
        except HttpError as e:
            logger.error(f"Error al leer rango {sheet_name}!{range_name}: {e}")
            return []
    
    def write_range(self, sheet_name: str, range_name: str, values: List[List[Any]]) -> bool:
        """
        Escribe valores en un rango de celdas.
        
        Args:
            sheet_name: Nombre de la hoja
            range_name: Rango en formato A1
            values: Lista de listas con los valores a escribir
            
        Returns:
            bool: True si escritura exitosa
        """
        try:
            body = {'values': values}
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!{range_name}",
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            # Invalidar caché
            cache_key = f"{sheet_name}!{range_name}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            logger.info(f"✅ Escritura exitosa: {result.get('updatedCells', 0)} celdas")
            return True
            
        except HttpError as e:
            logger.error(f"Error al escribir en {sheet_name}!{range_name}: {e}")
            return False
    
    def append_rows(self, sheet_name: str, values: List[List[Any]]) -> bool:
        """
        Añade filas al final de la hoja.
        
        Args:
            sheet_name: Nombre de la hoja
            values: Lista de listas con los valores a añadir
            
        Returns:
            bool: True si append exitoso
        """
        try:
            body = {'values': values}
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1",
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            logger.info(f"✅ Añadidas {len(values)} filas a {sheet_name}")
            return True
            
        except HttpError as e:
            logger.error(f"Error al añadir filas en {sheet_name}: {e}")
            return False
    
    def clear_cache(self):
        """Limpia la caché"""
        self.cache = {}
        self.cache_timestamp = {}
        logger.info("🧹 Caché limpiada")
    
    def get_all_data(self, sheet_name: str) -> List[List[Any]]:
        """Obtiene todos los datos de una hoja"""
        return self.read_range(sheet_name, "A1:Z10000")
    
    def search_by_column(self, sheet_name: str, column_index: int, search_value: str) -> List[List[Any]]:
        """
        Busca filas donde una columna específica contenga un valor.
        
        Args:
            sheet_name: Nombre de la hoja
            column_index: Índice de la columna (0-based)
            search_value: Valor a buscar
            
        Returns:
            Lista de filas que coinciden
        """
        all_data = self.get_all_data(sheet_name)
        results = []
        
        for row in all_data:
            if len(row) > column_index:
                if search_value.lower() in str(row[column_index]).lower():
                    results.append(row)
        
        return results
    
    def set_credentials(self, credentials_path: str) -> bool:
        """
        Configura las credenciales desde un archivo.
        
        Args:
            credentials_path: Ruta al archivo de credenciales (service account JSON)
            
        Returns:
            bool: True si se configuró correctamente
        """
        try:
            # Copiar el archivo a la ubicación esperada
            import shutil
            shutil.copy(credentials_path, SERVICE_ACCOUNT_FILE)
            
            # Intentar autenticar
            success = self.authenticate('service_account')
            
            if success:
                logger.info("✅ Credenciales configuradas correctamente")
            else:
                logger.error("❌ Error al autenticar con las credenciales proporcionadas")
            
            return success
            
        except Exception as e:
            logger.error(f"Error al configurar credenciales: {e}")
            return False
    
    def set_spreadsheet_id(self, spreadsheet_id: str):
        """
        Configura el ID del spreadsheet a usar.
        
        Args:
            spreadsheet_id: ID del Google Spreadsheet
        """
        self.spreadsheet_id = spreadsheet_id
        self._save_config()
        logger.info(f"✅ Spreadsheet ID configurado: {spreadsheet_id}")


# Instancia global del gestor
sheets_manager = SheetsManager()
