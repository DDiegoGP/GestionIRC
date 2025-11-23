# Guía Rápida: Configurar Google Sheets para la Aplicación

## 📋 Resumen
Esta guía te muestra cómo configurar Google Sheets para que la aplicación IRC pueda acceder a los datos sin que cada usuario necesite iniciar sesión.

---

## Paso 1: Crear Cuenta de Servicio en Google Cloud

### 1.1 Acceder a Google Cloud Console
```
URL: https://console.cloud.google.com
```

### 1.2 Crear Proyecto
```
1. Click en el selector de proyectos (arriba a la izquierda)
2. Click en "NUEVO PROYECTO"
3. Nombre del proyecto: "IRC-App" (o el que prefieras)
4. Click en "CREAR"
5. Esperar unos segundos y seleccionar el nuevo proyecto
```

### 1.3 Habilitar APIs
```
1. Ir a: Menú ☰ → APIs y Servicios → Biblioteca
2. Buscar "Google Sheets API"
3. Click en el resultado
4. Click en "HABILITAR"
5. Repetir para "Google Drive API"
```

### 1.4 Crear Cuenta de Servicio
```
1. Ir a: Menú ☰ → APIs y Servicios → Credenciales
2. Click en "+ CREAR CREDENCIALES" (arriba)
3. Seleccionar "Cuenta de servicio"
4. Configurar:
   - Nombre: irc-app-service
   - ID: irc-app-service (se genera automático)
   - Descripción: Cuenta para aplicación de gestión IRC
5. Click en "CREAR Y CONTINUAR"
6. Función: Editor (o dejarlo vacío)
7. Click en "CONTINUAR"
8. Click en "LISTO"
```

### 1.5 Descargar Credenciales
```
1. En la lista de cuentas de servicio, click en la que acabas de crear
2. Ir a la pestaña "CLAVES"
3. Click en "AGREGAR CLAVE" → "Crear clave nueva"
4. Tipo: JSON
5. Click en "CREAR"
6. Se descargará un archivo (nombre largo tipo: irc-app-123456-abcdef.json)

⚠️  IMPORTANTE: 
   - Renombrar el archivo a: service_account.json
   - Guardar en la carpeta: config/service_account.json
   - NO compartir este archivo públicamente
```

### 1.6 Copiar Email de la Cuenta de Servicio
```
El archivo JSON contiene un campo "client_email" que se ve así:
irc-app-service@irc-app-123456.iam.gserviceaccount.com

Copia este email completo. Lo necesitarás en el siguiente paso.
```

---

## Paso 2: Crear y Configurar Google Sheet

### 2.1 Crear Nueva Google Sheet
```
1. Ir a: https://sheets.google.com
2. Click en "+ Nuevo" o "Hoja de cálculo en blanco"
3. Nombrar la hoja: "IRC - Gestión de Solicitudes"
4. La hoja se crea automáticamente
```

### 2.2 Obtener el ID de la Google Sheet
```
Mira la URL de tu hoja, se verá así:
https://docs.google.com/spreadsheets/d/ESTE_ES_EL_ID_QUE_NECESITAS/edit

Ejemplo real:
https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
                                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      Este es el ID que necesitas

Copia este ID completo.
```

### 2.3 Compartir con la Cuenta de Servicio
```
1. Click en el botón "Compartir" (arriba a la derecha)
2. En el campo "Agregar personas y grupos", pega el email de la cuenta de servicio
   (el que copiaste en el Paso 1.6)
3. Permisos: Seleccionar "Editor"
4. ⚠️  IMPORTANTE: Desmarcar "Notificar a las personas"
5. Click en "Compartir"

✅ Listo! La cuenta de servicio ahora tiene acceso a tu hoja
```

---

## Paso 3: Configurar la Aplicación

### 3.1 Actualizar Configuración
```
Editar el archivo: config/app_config.json

Buscar la línea:
"google_sheet_id": "",

Cambiar por (usando tu ID copiado en Paso 2.2):
"google_sheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",

Guardar el archivo.
```

### 3.2 Verificar Estructura de Archivos
```
Tu carpeta debe verse así:

IRC_App/
│
├── main.py
├── google_sheets_manager.py
├── resource_manager.py
│
├── config/
│   ├── service_account.json          ⬅️ Credenciales de Google
│   └── app_config.json                ⬅️ ID de la hoja aquí
│
└── resources/
    ├── irc_icon.ico
    └── irc_logo.png
```

---

## Paso 4: Probar la Conexión

### 4.1 Ejecutar Script de Prueba
```bash
python google_sheets_manager.py
```

### 4.2 Resultados Esperados
```
✅ Credenciales encontradas: True
✅ Conexión establecida: True
✅ Acceso a la hoja: OK
✅ Hoja 'Solicitudes' inicializada
✅ Hoja 'Sesiones' inicializada
✅ Hoja 'Configuracion' inicializada
```

### 4.3 Si Hay Errores

**Error: "Archivo de credenciales no encontrado"**
```
Solución:
- Verifica que service_account.json esté en config/
- Verifica que el nombre del archivo sea exacto (con extensión .json)
```

**Error: "SpreadsheetNotFound"**
```
Solución:
- Verifica que el ID en app_config.json sea correcto
- Asegúrate de haber compartido la hoja con la cuenta de servicio
- Verifica que el email de la cuenta de servicio sea correcto
```

**Error: "API Error 403"**
```
Solución:
- Verifica que las APIs estén habilitadas en Google Cloud Console
- Espera unos minutos, las APIs pueden tardar en activarse
```

---

## 📝 Checklist Final

Antes de distribuir la aplicación, verifica:

- [ ] Cuenta de servicio creada en Google Cloud Console
- [ ] Google Sheets API y Google Drive API habilitadas
- [ ] Archivo service_account.json descargado y renombrado
- [ ] service_account.json colocado en config/
- [ ] Google Sheet creada
- [ ] ID de la Google Sheet copiado
- [ ] Google Sheet compartida con el email de la cuenta de servicio
- [ ] ID actualizado en config/app_config.json
- [ ] Script de prueba ejecutado exitosamente
- [ ] Hojas 'Solicitudes', 'Sesiones' y 'Configuracion' creadas automáticamente

---

## 🔄 Actualizar a una Nueva Hoja

Si necesitas cambiar a otra Google Sheet:

```
1. Crear nueva Google Sheet
2. Copiar su ID de la URL
3. Compartir con la misma cuenta de servicio (usar el mismo email)
4. Actualizar el ID en config/app_config.json
5. Reiniciar la aplicación
```

No necesitas crear una nueva cuenta de servicio, puedes usar la misma para múltiples hojas.

---

## 🚨 Problemas Comunes

### La aplicación no se conecta
```
1. Verificar que el archivo service_account.json exista
2. Verificar que el JSON sea válido (abrirlo con un editor de texto)
3. Verificar que las APIs estén habilitadas
4. Verificar conexión a Internet
```

### Los datos no se actualizan
```
1. Verificar que la hoja esté compartida con "Editor" (no solo "Lector")
2. Verificar que el ID de la hoja sea correcto
3. Cerrar y reabrir la aplicación
```

### Error de permisos
```
1. Re-compartir la hoja con la cuenta de servicio
2. Verificar que el email de la cuenta de servicio sea correcto
3. Esperar unos minutos, los permisos pueden tardar en propagarse
```

---

## 💡 Consejos

1. **Backup de credenciales**: Guarda una copia de service_account.json en un lugar seguro
2. **Múltiples hojas**: Una cuenta de servicio puede acceder a múltiples hojas
3. **Seguridad**: Nunca compartas service_account.json en repositorios públicos
4. **Testing**: Prueba siempre en una hoja de prueba antes de usar datos reales

---

## 📞 Soporte

Si sigues teniendo problemas:

1. Ejecuta el script de diagnóstico:
   ```bash
   python google_sheets_manager.py
   ```

2. Revisa los mensajes de error en la consola

3. Verifica cada paso de esta guía cuidadosamente

4. Contacta al administrador del sistema
