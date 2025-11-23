
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
