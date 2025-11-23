# Guía de Distribución - Aplicación IRC

## 📋 Índice
1. [Integración del Logo](#1-integración-del-logo)
2. [Configuración Google Sheets Multi-Usuario](#2-configuración-google-sheets-multi-usuario)
3. [Empaquetado como Ejecutable](#3-empaquetado-como-ejecutable)
4. [Instalación en Equipos de Usuarios](#4-instalación-en-equipos-de-usuarios)

---

## 1. Integración del Logo

### 1.1 Preparar el Logo
- Formato recomendado: **PNG** con fondo transparente
- Tamaños necesarios:
  - **Icono de aplicación**: 256x256px (se convertirá a .ico)
  - **Logo en ventana**: 200x80px aprox.
  - **Logo splash screen**: 400x200px

### 1.2 Código para Integrar el Logo

```python
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

class IRCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Solicitudes IRC")
        
        # CARGAR Y ESTABLECER ICONO DE LA VENTANA
        self.setup_app_icon()
        
        # CARGAR LOGO PARA MOSTRAR EN LA INTERFAZ
        self.load_logo()
        
        # Crear interfaz
        self.create_ui()
    
    def setup_app_icon(self):
        """Establece el icono de la aplicación en la barra de título"""
        icon_path = self.get_resource_path('resources/irc_icon.ico')
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                print("No se pudo cargar el icono .ico")
    
    def load_logo(self):
        """Carga el logo para mostrar en la interfaz"""
        logo_path = self.get_resource_path('resources/irc_logo.png')
        
        if os.path.exists(logo_path):
            try:
                # Cargar imagen
                img = Image.open(logo_path)
                # Redimensionar si es necesario
                img = img.resize((200, 80), Image.Resampling.LANCZOS)
                # Convertir para tkinter
                self.logo_image = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error cargando logo: {e}")
                self.logo_image = None
        else:
            self.logo_image = None
    
    def get_resource_path(self, relative_path):
        """
        Obtiene la ruta correcta tanto en desarrollo como en ejecutable
        """
        try:
            # PyInstaller crea una carpeta temporal _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            # En desarrollo, usa la carpeta actual
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def create_ui(self):
        """Crea la interfaz con el logo"""
        # FRAME SUPERIOR CON LOGO
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        if self.logo_image:
            logo_label = ttk.Label(header_frame, image=self.logo_image)
            logo_label.pack(side='left', padx=10)
        
        # Título al lado del logo
        title_label = ttk.Label(
            header_frame,
            text="Gestión de Solicitudes\nInstalación Radiactiva de Categoría",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(side='left', padx=20)
        
        # ... resto de la interfaz ...
```

### 1.3 Convertir Logo a Icono (.ico)

```python
# Script para convertir PNG a ICO
from PIL import Image

def convert_png_to_ico(png_path, ico_path):
    """Convierte una imagen PNG a formato ICO para Windows"""
    img = Image.open(png_path)
    
    # Crear múltiples tamaños para el icono
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    print(f"Icono creado: {ico_path}")

# Uso
convert_png_to_ico('irc_logo.png', 'resources/irc_icon.ico')
```

---

## 2. Configuración Google Sheets Multi-Usuario

### 🎯 OPCIÓN RECOMENDADA: Cuenta de Servicio (Service Account)

**Ventajas:**
- ✅ Un solo punto de acceso para todos los usuarios
- ✅ No requiere que cada usuario tenga credenciales de Google
- ✅ Más seguro y fácil de mantener
- ✅ Perfecto para aplicaciones empresariales internas

### 2.1 Crear Cuenta de Servicio en Google Cloud

**Paso 1: Acceder a Google Cloud Console**
1. Ve a https://console.cloud.google.com
2. Crea un nuevo proyecto o selecciona uno existente
3. Nombre del proyecto: "IRC-App" (o el que prefieras)

**Paso 2: Activar APIs necesarias**
```
1. Ve a "APIs y Servicios" → "Biblioteca"
2. Busca y habilita:
   - Google Sheets API
   - Google Drive API
```

**Paso 3: Crear Cuenta de Servicio**
```
1. Ve a "APIs y Servicios" → "Credenciales"
2. Clic en "Crear credenciales" → "Cuenta de servicio"
3. Nombre: "irc-app-service"
4. Descripción: "Cuenta de servicio para app IRC"
5. Clic en "Crear y continuar"
6. Rol: "Editor" (o puedes dejarlo sin rol)
7. Clic en "Listo"
```

**Paso 4: Descargar Credenciales JSON**
```
1. En la lista de cuentas de servicio, clic en la que acabas de crear
2. Ve a la pestaña "Claves"
3. Clic en "Agregar clave" → "Crear clave nueva"
4. Tipo: JSON
5. Descargar el archivo (se llamará algo como: irc-app-xxxx.json)
6. ⚠️ GUARDAR ESTE ARCHIVO DE FORMA SEGURA
```

**Paso 5: Compartir Google Sheet con la Cuenta de Servicio**
```
1. Abre el archivo JSON descargado
2. Copia el valor de "client_email" (algo como: irc-app-service@proyecto.iam.gserviceaccount.com)
3. Ve a tu Google Sheet nueva
4. Clic en "Compartir"
5. Pega el email de la cuenta de servicio
6. Permisos: "Editor"
7. Desmarcar "Notificar a las personas"
8. Clic en "Compartir"
```

### 2.2 Código para Usar Cuenta de Servicio

```python
import gspread
from google.oauth2.service_account import Credentials
import os
import sys

class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self.sheet = None
        self.connect()
    
    def get_credentials_path(self):
        """Obtiene la ruta al archivo de credenciales"""
        # Buscar en la carpeta de la aplicación
        if getattr(sys, 'frozen', False):
            # Si es ejecutable empaquetado
            app_path = os.path.dirname(sys.executable)
        else:
            # Si está en desarrollo
            app_path = os.path.dirname(os.path.abspath(__file__))
        
        creds_path = os.path.join(app_path, 'config', 'service_account.json')
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                f"No se encontró el archivo de credenciales en: {creds_path}\n"
                "Por favor, coloca el archivo service_account.json en la carpeta 'config'"
            )
        
        return creds_path
    
    def connect(self):
        """Conecta con Google Sheets usando cuenta de servicio"""
        try:
            # Definir el alcance
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Cargar credenciales
            creds_path = self.get_credentials_path()
            credentials = Credentials.from_service_account_file(
                creds_path,
                scopes=scopes
            )
            
            # Autorizar cliente
            self.client = gspread.authorize(credentials)
            
            print("✅ Conexión exitosa con Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Error conectando con Google Sheets: {e}")
            return False
    
    def open_sheet(self, sheet_key):
        """Abre una hoja de cálculo por su clave/ID"""
        try:
            self.sheet = self.client.open_by_key(sheet_key)
            print(f"✅ Hoja '{self.sheet.title}' abierta correctamente")
            return True
        except Exception as e:
            print(f"❌ Error abriendo la hoja: {e}")
            return False
    
    def get_worksheet(self, worksheet_name):
        """Obtiene una hoja de trabajo específica"""
        if not self.sheet:
            raise ValueError("Primero debes abrir una hoja con open_sheet()")
        
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            return worksheet
        except:
            # Si no existe, crear la hoja
            worksheet = self.sheet.add_worksheet(
                title=worksheet_name,
                rows=1000,
                cols=20
            )
            return worksheet
    
    def read_all_requests(self):
        """Lee todas las solicitudes"""
        worksheet = self.get_worksheet('Solicitudes')
        return worksheet.get_all_records()
    
    def add_request(self, request_data):
        """Agrega una nueva solicitud"""
        worksheet = self.get_worksheet('Solicitudes')
        
        # Convertir diccionario a lista en el orden correcto
        row = [
            request_data.get('id', ''),
            request_data.get('fecha', ''),
            request_data.get('solicitante', ''),
            request_data.get('servicio', ''),
            request_data.get('estado', 'Pendiente'),
            # ... más campos ...
        ]
        
        worksheet.append_row(row)
        return True
    
    def update_request(self, request_id, updated_data):
        """Actualiza una solicitud existente"""
        worksheet = self.get_worksheet('Solicitudes')
        
        # Buscar la fila por ID
        cell = worksheet.find(request_id)
        
        if cell:
            row_num = cell.row
            
            # Actualizar los campos que han cambiado
            # ... código para actualizar ...
            
            return True
        
        return False
```

### 2.3 Configuración en la Aplicación

```python
# config/app_config.py

CONFIG = {
    # ID de la Google Sheet (se obtiene de la URL)
    # https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
    'GOOGLE_SHEET_ID': 'TU_ID_DE_GOOGLE_SHEET_AQUI',
    
    # Nombre de las hojas de trabajo
    'WORKSHEETS': {
        'requests': 'Solicitudes',
        'sessions': 'Sesiones',
        'config': 'Configuracion'
    },
    
    # Configuración de la aplicación
    'APP_NAME': 'Gestión IRC',
    'APP_VERSION': '1.0.0',
}
```

---

## 3. Empaquetado como Ejecutable

### 3.1 Instalar PyInstaller

```bash
pip install pyinstaller
```

### 3.2 Crear Archivo de Configuración (spec file)

```python
# irc_app.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],  # Tu archivo principal
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),  # Incluir carpeta de recursos (logos, iconos)
        ('config/service_account.json', 'config'),  # Incluir credenciales
    ],
    hiddenimports=[
        'gspread',
        'google.auth',
        'google.oauth2',
        'PIL',
        'reportlab',
        'PyPDF2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Gestion_IRC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/irc_icon.ico'  # Icono de la aplicación
)
```

### 3.3 Compilar la Aplicación

```bash
# Usando el archivo .spec
pyinstaller irc_app.spec

# O comando directo (más simple)
pyinstaller --onefile --windowed --icon=resources/irc_icon.ico --name="Gestion_IRC" --add-data "resources;resources" --add-data "config;config" main.py
```

**Resultado:**
- Se creará la carpeta `dist/`
- Dentro estará el ejecutable: `Gestion_IRC.exe`

### 3.4 Estructura de Carpetas para Distribución

```
IRC_App_v1.0/
│
├── Gestion_IRC.exe          # Ejecutable principal
│
├── config/
│   ├── service_account.json # Credenciales de Google (⚠️ IMPORTANTE)
│   └── app_config.json      # Configuración de la app
│
├── resources/               # (Opcional si no están empaquetadas)
│   ├── irc_logo.png
│   └── irc_icon.ico
│
├── LEEME.txt               # Instrucciones de instalación
└── templates/              # Plantillas PDF si las hay
    └── plantilla_solicitud.pdf
```

---

## 4. Instalación en Equipos de Usuarios

### 4.1 Crear Archivo LEEME.txt

```text
═══════════════════════════════════════════════════════════
  INSTALACIÓN - GESTIÓN DE SOLICITUDES IRC v1.0
═══════════════════════════════════════════════════════════

📋 REQUISITOS:
- Windows 10 o superior
- Conexión a Internet (para acceder a Google Sheets)

🚀 INSTALACIÓN:

1. Copiar toda la carpeta "IRC_App_v1.0" a:
   C:\Program Files\IRC_App\
   
   O cualquier otra ubicación que prefieras.

2. Crear acceso directo:
   - Click derecho en "Gestion_IRC.exe"
   - "Enviar a" → "Escritorio (crear acceso directo)"

3. Primera ejecución:
   - Doble click en el ejecutable
   - La aplicación se conectará automáticamente a la base de datos

⚠️ IMPORTANTE:
- NO mover ni eliminar la carpeta "config"
- NO compartir el archivo "service_account.json" con terceros

📞 SOPORTE:
- Contacto: [tu_email@irc.com]
- Teléfono: [teléfono]

═══════════════════════════════════════════════════════════
```

### 4.2 Distribución a Usuarios

**Opción 1: Carpeta Compartida (Red Local)**
```
1. Copiar IRC_App_v1.0 a una carpeta compartida
2. Los usuarios copian la carpeta a su equipo
3. Ejecutan desde su máquina local
```

**Opción 2: Servidor de Archivos/SharePoint**
```
1. Subir ZIP con la aplicación
2. Usuarios descargan e instalan
```

**Opción 3: Instalador MSI (Más profesional)**
```
Usar herramientas como:
- Inno Setup (gratuito)
- NSIS
- Advanced Installer
```

### 4.3 Actualizaciones

**Sistema de versionado simple:**

```python
# En el código, verificar versión al inicio
APP_VERSION = "1.0.0"
REMOTE_VERSION_URL = "https://tu-servidor.com/version.txt"

def check_for_updates():
    try:
        response = requests.get(REMOTE_VERSION_URL)
        remote_version = response.text.strip()
        
        if remote_version > APP_VERSION:
            messagebox.showinfo(
                "Actualización disponible",
                f"Hay una nueva versión disponible: {remote_version}\n"
                f"Versión actual: {APP_VERSION}\n\n"
                "Por favor, contacta con el administrador para actualizar."
            )
    except:
        pass  # No hay conexión o el servidor no responde
```

---

## 5. Seguridad y Mejores Prácticas

### ⚠️ IMPORTANTE: Protección de Credenciales

**Nunca compartir públicamente:**
- ❌ service_account.json
- ❌ API keys
- ❌ Contraseñas

**Alternativa más segura (Opcional):**
- Cifrar el archivo service_account.json
- Descifrarlo en memoria al ejecutarse

```python
from cryptography.fernet import Fernet

def encrypt_credentials(json_file, key):
    """Cifra el archivo de credenciales"""
    f = Fernet(key)
    
    with open(json_file, 'rb') as file:
        file_data = file.read()
    
    encrypted_data = f.encrypt(file_data)
    
    with open(json_file + '.encrypted', 'wb') as file:
        file.write(encrypted_data)

def decrypt_credentials(encrypted_file, key):
    """Descifra y devuelve las credenciales en memoria"""
    f = Fernet(key)
    
    with open(encrypted_file, 'rb') as file:
        encrypted_data = file.read()
    
    decrypted_data = f.decrypt(encrypted_data)
    return json.loads(decrypted_data)
```

---

## 📝 Checklist Final Antes de Distribuir

- [ ] Logo integrado correctamente
- [ ] Icono de aplicación funcionando
- [ ] Cuenta de servicio creada y configurada
- [ ] Google Sheet compartida con la cuenta de servicio
- [ ] ID de Google Sheet configurado en la app
- [ ] Aplicación probada en modo desarrollo
- [ ] Ejecutable compilado con PyInstaller
- [ ] Carpeta config/ incluida con service_account.json
- [ ] Archivo LEEME.txt creado
- [ ] Probada la aplicación en otro equipo Windows
- [ ] Accesos directos funcionando
- [ ] Documentación entregada a usuarios

---

## 🎯 Resumen Rápido

1. **Logo**: Agregar en carpeta `resources/` y usar código proporcionado
2. **Google Sheets**: Usar Cuenta de Servicio (más simple y seguro)
3. **Compilar**: `pyinstaller irc_app.spec`
4. **Distribuir**: Copiar carpeta completa con config/
5. **Instalar**: Usuarios copian a su equipo y ejecutan

---

¿Necesitas que te ayude con alguna parte específica?
