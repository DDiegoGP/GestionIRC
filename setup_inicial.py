"""
Script de Configuración Inicial - Aplicación IRC
Ejecutar este script antes de compilar o distribuir la aplicación
"""

import os
import json
import sys

def create_directory_structure():
    """Crea la estructura de directorios necesaria"""
    directories = [
        'resources',
        'config',
        'templates',
        'pdf_generados'
    ]
    
    print("📁 Creando estructura de directorios...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}/")
    
    print()

def check_logo():
    """Verifica si existe el logo"""
    print("🖼️  Verificando logo...")
    
    logo_files = {
        'Logo PNG': 'resources/irc_logo.png',
        'Logo Header': 'resources/irc_logo_header.png',
        'Logo Splash': 'resources/irc_logo_splash.png',
        'Icono ICO': 'resources/irc_icon.ico'
    }
    
    missing = []
    for name, path in logo_files.items():
        if os.path.exists(path):
            print(f"   ✅ {name}: OK")
        else:
            print(f"   ❌ {name}: NO ENCONTRADO")
            missing.append(path)
    
    if missing:
        print()
        print("⚠️  Faltan archivos de logo. Para crearlos:")
        print("   1. Coloca tu logo (PNG) en la carpeta actual")
        print("   2. Ejecuta: python convert_logo.py tu_logo.png")
    
    print()

def check_credentials():
    """Verifica si existe el archivo de credenciales"""
    print("🔑 Verificando credenciales de Google...")
    
    creds_path = 'config/service_account.json'
    
    if os.path.exists(creds_path):
        print(f"   ✅ Credenciales encontradas")
        
        # Intentar leer y mostrar el email
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
                email = creds.get('client_email', 'No encontrado')
                print(f"   📧 Email de cuenta de servicio: {email}")
                print()
                print("   ⚠️  Recuerda compartir tu Google Sheet con este email!")
        except:
            print(f"   ⚠️  El archivo existe pero no se pudo leer")
    else:
        print(f"   ❌ NO ENCONTRADO: {creds_path}")
        print()
        print("   Para obtener las credenciales:")
        print("   1. Ve a https://console.cloud.google.com")
        print("   2. Crea un proyecto")
        print("   3. Habilita Google Sheets API y Google Drive API")
        print("   4. Crea una cuenta de servicio")
        print("   5. Descarga el archivo JSON")
        print("   6. Renómbralo a 'service_account.json'")
        print("   7. Colócalo en la carpeta 'config/'")
    
    print()

def create_config_file():
    """Crea el archivo de configuración si no existe"""
    print("⚙️  Verificando configuración...")
    
    config_path = 'config/app_config.json'
    
    if os.path.exists(config_path):
        print(f"   ✅ Archivo de configuración existe")
    else:
        print(f"   📝 Creando archivo de configuración...")
        
        config = {
            "app_name": "Gestión IRC",
            "app_version": "1.0.0",
            "google_sheet_id": "",
            "worksheets": {
                "requests": "Solicitudes",
                "sessions": "Sesiones",
                "config": "Configuracion"
            },
            "pdf_settings": {
                "template_path": "",
                "output_folder": "pdf_generados",
                "auto_open": True
            },
            "ui_settings": {
                "theme": "default",
                "window_size": "1200x800",
                "show_splash": True
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Creado: {config_path}")
        print(f"   ⚠️  Recuerda actualizar el 'google_sheet_id' en el archivo")
    
    print()

def check_dependencies():
    """Verifica las dependencias de Python"""
    print("📦 Verificando dependencias de Python...")
    
    required_packages = [
        'tkinter',
        'gspread',
        'google-auth',
        'google-auth-oauthlib',
        'Pillow',
        'reportlab',
        'PyPDF2',
        'pyinstaller'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'gspread':
                import gspread
            elif package == 'google-auth':
                import google.auth
            elif package == 'google-auth-oauthlib':
                import google_auth_oauthlib
            elif package == 'Pillow':
                import PIL
            elif package == 'reportlab':
                import reportlab
            elif package == 'PyPDF2':
                import PyPDF2
            elif package == 'pyinstaller':
                import PyInstaller
            
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NO INSTALADO")
            missing.append(package)
    
    if missing:
        print()
        print("⚠️  Instalar paquetes faltantes con:")
        print(f"   pip install {' '.join(missing)}")
    
    print()

def create_readme():
    """Crea un archivo README con instrucciones"""
    print("📄 Creando archivo README...")
    
    readme_content = """
═══════════════════════════════════════════════════════════
  GESTIÓN DE SOLICITUDES IRC v1.0
═══════════════════════════════════════════════════════════

📋 ARCHIVOS IMPORTANTES:

1. config/service_account.json
   - Credenciales de Google Cloud
   - NO compartir públicamente
   - Necesario para acceder a Google Sheets

2. config/app_config.json
   - Configuración de la aplicación
   - Actualizar 'google_sheet_id' con tu hoja

3. resources/
   - irc_icon.ico: Icono de la aplicación
   - irc_logo.png: Logo original
   - irc_logo_header.png: Logo para interfaz
   - irc_logo_splash.png: Logo para splash screen

4. main.py
   - Archivo principal de la aplicación

═══════════════════════════════════════════════════════════

🚀 PASOS PARA DISTRIBUIR:

1. ANTES DE COMPILAR:
   ✅ Verificar que todos los archivos necesarios estén presentes
   ✅ Actualizar google_sheet_id en config/app_config.json
   ✅ Compartir Google Sheet con el email de la cuenta de servicio
   ✅ Probar la aplicación en modo desarrollo: python main.py

2. COMPILAR:
   pyinstaller irc_app.spec

3. PROBAR EL EJECUTABLE:
   - El ejecutable estará en: dist/Gestion_IRC.exe
   - Probarlo en tu máquina
   - Probarlo en otra máquina limpia

4. PREPARAR PARA DISTRIBUCIÓN:
   - Copiar dist/Gestion_IRC.exe
   - Copiar carpeta config/ con service_account.json
   - Copiar carpeta resources/ (si no están empaquetadas)
   - Incluir instrucciones de instalación

5. DISTRIBUIR:
   - Comprimir todo en un ZIP
   - Compartir con los usuarios
   - Proporcionar instrucciones claras

═══════════════════════════════════════════════════════════

⚠️  SEGURIDAD:

- NUNCA compartir service_account.json públicamente
- NO incluir credenciales en repositorios Git públicos
- Usar archivo .gitignore para excluir archivos sensibles

═══════════════════════════════════════════════════════════

📞 SOPORTE:

Para problemas o dudas, contactar a:
[TU_EMAIL_AQUI]

═══════════════════════════════════════════════════════════
"""
    
    with open('README_DISTRIBUCION.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("   ✅ README_DISTRIBUCION.txt creado")
    print()

def create_gitignore():
    """Crea un .gitignore para proteger archivos sensibles"""
    print("🔒 Creando .gitignore...")
    
    gitignore_content = """# Archivos sensibles - NO compartir
config/service_account.json
config/*.json

# Credenciales
*.json

# Archivos de compilación
build/
dist/
*.spec

# Archivos temporales
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/

# PDFs generados
pdf_generados/

# Entornos virtuales
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Sistema operativo
.DS_Store
Thumbs.db
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("   ✅ .gitignore creado")
    print()

def main():
    """Ejecuta todas las verificaciones y setup"""
    print()
    print("=" * 60)
    print("  CONFIGURACIÓN INICIAL - APLICACIÓN IRC")
    print("=" * 60)
    print()
    
    # 1. Crear estructura de directorios
    create_directory_structure()
    
    # 2. Verificar logo
    check_logo()
    
    # 3. Verificar credenciales
    check_credentials()
    
    # 4. Crear archivo de configuración
    create_config_file()
    
    # 5. Verificar dependencias
    check_dependencies()
    
    # 6. Crear README
    create_readme()
    
    # 7. Crear .gitignore
    create_gitignore()
    
    # Resumen final
    print("=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print()
    print("✅ Setup completado")
    print()
    print("Próximos pasos:")
    print("1. Coloca tu logo en la carpeta actual")
    print("2. Ejecuta: python convert_logo.py tu_logo.png")
    print("3. Coloca service_account.json en config/")
    print("4. Actualiza google_sheet_id en config/app_config.json")
    print("5. Comparte tu Google Sheet con la cuenta de servicio")
    print("6. Prueba la aplicación: python main.py")
    print("7. Compila: pyinstaller irc_app.spec")
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()
