"""
Gestor de Google Sheets usando Cuenta de Servicio
Para uso multi-usuario sin necesidad de login individual
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import sys
import json

class GoogleSheetsManager:
    """
    Gestor de conexión y operaciones con Google Sheets
    Usa una Cuenta de Servicio para acceso sin autenticación de usuario
    """
    
    def __init__(self, sheet_id=None):
        """
        Inicializa el gestor
        
        Args:
            sheet_id: ID de la Google Sheet (opcional, se puede configurar después)
        """
        self.client = None
        self.sheet = None
        self.sheet_id = sheet_id
        self.connected = False
        
    def get_credentials_path(self):
        """
        Obtiene la ruta al archivo de credenciales de la cuenta de servicio
        Funciona tanto en desarrollo como en ejecutable empaquetado
        """
        # Determinar directorio base
        if getattr(sys, 'frozen', False):
            # Si es ejecutable empaquetado (PyInstaller)
            if hasattr(sys, '_MEIPASS'):
                # Directorio temporal de PyInstaller
                base_path = sys._MEIPASS
            else:
                # Directorio del ejecutable
                base_path = os.path.dirname(sys.executable)
        else:
            # Modo desarrollo
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Buscar en config/
        creds_path = os.path.join(base_path, 'config', 'service_account.json')
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                f"⚠️ No se encontró el archivo de credenciales:\n{creds_path}\n\n"
                "Por favor, asegúrate de que el archivo 'service_account.json' "
                "esté en la carpeta 'config/'"
            )
        
        return creds_path
    
    def connect(self):
        """
        Establece conexión con Google Sheets usando la cuenta de servicio
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Definir alcance de permisos
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Cargar credenciales
            creds_path = self.get_credentials_path()
            
            print(f"📁 Cargando credenciales desde: {creds_path}")
            
            credentials = Credentials.from_service_account_file(
                creds_path,
                scopes=scopes
            )
            
            # Autorizar cliente
            self.client = gspread.authorize(credentials)
            
            self.connected = True
            print("✅ Conexión exitosa con Google Sheets")
            
            return True
            
        except FileNotFoundError as e:
            print(f"❌ Error: {e}")
            return False
            
        except json.JSONDecodeError:
            print("❌ Error: El archivo de credenciales no es un JSON válido")
            return False
            
        except Exception as e:
            print(f"❌ Error conectando con Google Sheets: {e}")
            return False
    
    def set_sheet_id(self, sheet_id):
        """Establece el ID de la Google Sheet a usar"""
        self.sheet_id = sheet_id
    
    def open_sheet(self, sheet_id=None):
        """
        Abre una hoja de cálculo por su ID
        
        Args:
            sheet_id: ID de la Google Sheet (opcional si ya se estableció)
            
        Returns:
            bool: True si se abrió correctamente
        """
        if not self.connected:
            print("⚠️ Primero debes conectar con connect()")
            return False
        
        if sheet_id:
            self.sheet_id = sheet_id
        
        if not self.sheet_id:
            print("⚠️ No se ha especificado un ID de Google Sheet")
            return False
        
        try:
            self.sheet = self.client.open_by_key(self.sheet_id)
            print(f"✅ Hoja '{self.sheet.title}' abierta correctamente")
            return True
            
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"❌ Error: No se encontró la hoja con ID: {self.sheet_id}")
            print("   Verifica que:")
            print("   1. El ID sea correcto")
            print("   2. La hoja esté compartida con la cuenta de servicio")
            return False
            
        except gspread.exceptions.APIError as e:
            print(f"❌ Error de API de Google: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Error abriendo la hoja: {e}")
            return False
    
    def get_worksheet(self, worksheet_name):
        """
        Obtiene una hoja de trabajo específica, creándola si no existe
        
        Args:
            worksheet_name: Nombre de la hoja de trabajo
            
        Returns:
            Worksheet object o None si hay error
        """
        if not self.sheet:
            print("⚠️ Primero debes abrir una hoja con open_sheet()")
            return None
        
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            return worksheet
            
        except gspread.exceptions.WorksheetNotFound:
            # Si no existe, crear la hoja
            print(f"📝 Creando hoja '{worksheet_name}'...")
            worksheet = self.sheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=20
            )
            return worksheet
            
        except Exception as e:
            print(f"❌ Error obteniendo hoja '{worksheet_name}': {e}")
            return None
    
    def initialize_sheets(self):
        """
        Inicializa las hojas necesarias con sus encabezados
        """
        # Hoja de Solicitudes
        solicitudes = self.get_worksheet('Solicitudes')
        if solicitudes and solicitudes.row_count == 0:
            headers = [
                'ID', 'Fecha', 'Solicitante', 'Email', 'Teléfono',
                'Servicio', 'Descripción', 'Muestras', 'Urgente',
                'Estado', 'Fecha Inicio', 'Fecha Fin', 'Coste Total',
                'Observaciones', 'Creado Por', 'Última Modificación'
            ]
            solicitudes.append_row(headers)
            print("✅ Hoja 'Solicitudes' inicializada")
        
        # Hoja de Sesiones
        sesiones = self.get_worksheet('Sesiones')
        if sesiones and sesiones.row_count == 0:
            headers = [
                'ID Sesión', 'ID Solicitud', 'Fecha Programada',
                'Fecha Realizada', 'Tipo Servicio', 'Canister/Unidad',
                'Estado', 'Técnico', 'Observaciones', 'Creado'
            ]
            sesiones.append_row(headers)
            print("✅ Hoja 'Sesiones' inicializada")
        
        # Hoja de Configuración
        config = self.get_worksheet('Configuracion')
        if config and config.row_count == 0:
            headers = ['Parámetro', 'Valor', 'Descripción']
            config.append_row(headers)
            
            # Valores por defecto
            default_config = [
                ['app_version', '1.0.0', 'Versión de la aplicación'],
                ['ultima_actualizacion', datetime.now().strftime('%Y-%m-%d %H:%M'), 'Última actualización de datos'],
                ['auto_update_dosimetric', 'true', 'Actualización automática de servicios dosimétricos'],
            ]
            
            for row in default_config:
                config.append_row(row)
            
            print("✅ Hoja 'Configuracion' inicializada")
    
    # =============== OPERACIONES CON SOLICITUDES ===============
    
    def read_all_requests(self):
        """
        Lee todas las solicitudes
        
        Returns:
            list: Lista de diccionarios con las solicitudes
        """
        worksheet = self.get_worksheet('Solicitudes')
        if not worksheet:
            return []
        
        try:
            records = worksheet.get_all_records()
            return records
        except Exception as e:
            print(f"❌ Error leyendo solicitudes: {e}")
            return []
    
    def add_request(self, request_data):
        """
        Agrega una nueva solicitud
        
        Args:
            request_data: Diccionario con los datos de la solicitud
            
        Returns:
            bool: True si se agregó correctamente
        """
        worksheet = self.get_worksheet('Solicitudes')
        if not worksheet:
            return False
        
        try:
            # Preparar fila con los datos en el orden correcto
            row = [
                request_data.get('id', ''),
                request_data.get('fecha', datetime.now().strftime('%Y-%m-%d')),
                request_data.get('solicitante', ''),
                request_data.get('email', ''),
                request_data.get('telefono', ''),
                request_data.get('servicio', ''),
                request_data.get('descripcion', ''),
                request_data.get('muestras', ''),
                request_data.get('urgente', 'No'),
                request_data.get('estado', 'Pendiente'),
                request_data.get('fecha_inicio', ''),
                request_data.get('fecha_fin', ''),
                request_data.get('coste_total', ''),
                request_data.get('observaciones', ''),
                request_data.get('creado_por', 'Sistema'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            worksheet.append_row(row)
            print(f"✅ Solicitud {request_data.get('id')} agregada")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando solicitud: {e}")
            return False
    
    def update_request(self, request_id, updated_data):
        """
        Actualiza una solicitud existente
        
        Args:
            request_id: ID de la solicitud a actualizar
            updated_data: Diccionario con los campos a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        worksheet = self.get_worksheet('Solicitudes')
        if not worksheet:
            return False
        
        try:
            # Buscar la fila por ID
            cell = worksheet.find(str(request_id))
            
            if not cell:
                print(f"⚠️ No se encontró la solicitud con ID: {request_id}")
                return False
            
            row_num = cell.row
            
            # Obtener encabezados para mapear columnas
            headers = worksheet.row_values(1)
            
            # Actualizar cada campo
            for key, value in updated_data.items():
                if key in headers:
                    col_num = headers.index(key) + 1
                    worksheet.update_cell(row_num, col_num, value)
            
            # Actualizar timestamp de modificación
            if 'Última Modificación' in headers:
                col_num = headers.index('Última Modificación') + 1
                worksheet.update_cell(
                    row_num, 
                    col_num, 
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
            
            print(f"✅ Solicitud {request_id} actualizada")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando solicitud: {e}")
            return False
    
    def delete_request(self, request_id):
        """
        Elimina una solicitud
        
        Args:
            request_id: ID de la solicitud a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        worksheet = self.get_worksheet('Solicitudes')
        if not worksheet:
            return False
        
        try:
            cell = worksheet.find(str(request_id))
            
            if not cell:
                print(f"⚠️ No se encontró la solicitud con ID: {request_id}")
                return False
            
            worksheet.delete_rows(cell.row)
            print(f"✅ Solicitud {request_id} eliminada")
            return True
            
        except Exception as e:
            print(f"❌ Error eliminando solicitud: {e}")
            return False
    
    # =============== OPERACIONES CON SESIONES ===============
    
    def add_session(self, session_data):
        """
        Agrega una nueva sesión
        
        Args:
            session_data: Diccionario con los datos de la sesión
            
        Returns:
            bool: True si se agregó correctamente
        """
        worksheet = self.get_worksheet('Sesiones')
        if not worksheet:
            return False
        
        try:
            row = [
                session_data.get('id_sesion', ''),
                session_data.get('id_solicitud', ''),
                session_data.get('fecha_programada', ''),
                session_data.get('fecha_realizada', ''),
                session_data.get('tipo_servicio', ''),
                session_data.get('canister_unidad', ''),
                session_data.get('estado', 'Programada'),
                session_data.get('tecnico', ''),
                session_data.get('observaciones', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            worksheet.append_row(row)
            print(f"✅ Sesión agregada para solicitud {session_data.get('id_solicitud')}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando sesión: {e}")
            return False
    
    def get_sessions_for_request(self, request_id):
        """
        Obtiene todas las sesiones de una solicitud específica
        
        Args:
            request_id: ID de la solicitud
            
        Returns:
            list: Lista de diccionarios con las sesiones
        """
        worksheet = self.get_worksheet('Sesiones')
        if not worksheet:
            return []
        
        try:
            all_sessions = worksheet.get_all_records()
            request_sessions = [
                s for s in all_sessions 
                if str(s.get('ID Solicitud')) == str(request_id)
            ]
            return request_sessions
            
        except Exception as e:
            print(f"❌ Error obteniendo sesiones: {e}")
            return []
    
    # =============== UTILIDADES ===============
    
    def get_service_account_email(self):
        """
        Obtiene el email de la cuenta de servicio para facilitar el compartir
        
        Returns:
            str: Email de la cuenta de servicio
        """
        try:
            creds_path = self.get_credentials_path()
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            return creds_data.get('client_email', 'No encontrado')
        except Exception as e:
            return f"Error: {e}"
    
    def test_connection(self):
        """
        Prueba la conexión completa
        
        Returns:
            dict: Resultado de las pruebas
        """
        results = {
            'credentials': False,
            'connection': False,
            'sheet_access': False,
            'email': None
        }
        
        # Test 1: Verificar credenciales
        try:
            self.get_credentials_path()
            results['credentials'] = True
            results['email'] = self.get_service_account_email()
        except:
            return results
        
        # Test 2: Conectar
        if self.connect():
            results['connection'] = True
        else:
            return results
        
        # Test 3: Acceder a la hoja
        if self.sheet_id and self.open_sheet():
            results['sheet_access'] = True
        
        return results


# =============== EJEMPLO DE USO ===============

if __name__ == "__main__":
    print("=" * 60)
    print("  PRUEBA DE CONEXIÓN - Google Sheets Manager")
    print("=" * 60)
    print()
    
    # Crear instancia
    manager = GoogleSheetsManager()
    
    # Obtener email de la cuenta de servicio
    email = manager.get_service_account_email()
    print(f"📧 Email de la Cuenta de Servicio:")
    print(f"   {email}")
    print()
    print("⚠️  Asegúrate de compartir tu Google Sheet con este email")
    print()
    
    # Probar conexión
    print("🔄 Probando conexión...")
    results = manager.test_connection()
    
    print()
    print("Resultados:")
    print(f"  ✅ Credenciales encontradas: {results['credentials']}")
    print(f"  ✅ Conexión establecida: {results['connection']}")
    
    if results['connection']:
        # Pedir ID de la hoja para probar acceso
        print()
        sheet_id = input("Ingresa el ID de tu Google Sheet (o Enter para omitir): ").strip()
        
        if sheet_id:
            manager.set_sheet_id(sheet_id)
            if manager.open_sheet():
                print("  ✅ Acceso a la hoja: OK")
                
                # Inicializar hojas
                print()
                print("🔄 Inicializando estructura de hojas...")
                manager.initialize_sheets()
                
                print()
                print("✅ ¡Todo configurado correctamente!")
            else:
                print("  ❌ No se pudo acceder a la hoja")
                print()
                print("Verifica que la hoja esté compartida con:")
                print(f"  {email}")
    
    print()
    print("=" * 60)
