# 🔧 Configuración de Google Sheets - Guía Completa

## Índice
1. [Opción A: Service Account (Recomendada)](#opción-a-service-account)
2. [Opción B: OAuth 2.0](#opción-b-oauth-20)
3. [Configurar el Spreadsheet](#configurar-el-spreadsheet)
4. [Solución de Problemas](#solución-de-problemas)

---

## Opción A: Service Account (RECOMENDADA)

### ✅ Ventajas
- No requiere login de usuario
- Funcionamiento automático
- Ideal para compartir entre varios usuarios
- Más seguro para entornos corporativos

### 📋 Pasos Detallados

#### 1. Crear Proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Click en el menú desplegable de proyectos (arriba a la izquierda)
3. Click en **"NUEVO PROYECTO"**
   - Nombre: `Gestion-IRC-UCM`
   - Click en **"CREAR"**
4. Espera a que se cree (unos segundos)
5. Selecciona el proyecto recién creado

#### 2. Habilitar la API de Google Sheets

1. En el menú lateral, ve a **"APIs y servicios" > "Biblioteca"**
2. En el buscador, escribe: `Google Sheets API`
3. Click en **"Google Sheets API"**
4. Click en **"HABILITAR"**
5. Espera a que se active (unos segundos)

#### 3. Crear una Service Account

1. En el menú lateral, ve a **"APIs y servicios" > "Credenciales"**
2. Click en **"+ CREAR CREDENCIALES"** (arriba)
3. Selecciona **"Cuenta de servicio"**
4. Rellena el formulario:
   - Nombre: `gestion-irc-service`
   - ID: (se rellena automáticamente)
   - Descripción: `Cuenta de servicio para Gestión IRC`
5. Click en **"CREAR Y CONTINUAR"**
6. En "Otorgar acceso", puedes saltarlo → Click en **"CONTINUAR"**
7. En "Otorgar acceso a usuarios", también saltar → Click en **"LISTO"**

#### 4. Descargar las Credenciales JSON

1. En la lista de Service Accounts, verás `gestion-irc-service@...`
2. Click en el **email** de la service account
3. Ve a la pestaña **"CLAVES"**
4. Click en **"AGREGAR CLAVE" > "Crear clave nueva"**
5. Selecciona **"JSON"**
6. Click en **"CREAR"**
7. Se descargará automáticamente un archivo JSON
8. **IMPORTANTE**: Renombra este archivo a `service_account.json`

#### 5. Colocar las Credenciales

1. Copia el archivo `service_account.json` en la carpeta de la aplicación:
   ```
   GestionIRC/
   └── service_account.json  ← AQUÍ
   ```

#### 6. Compartir el Google Sheets

1. Abre el archivo `service_account.json` con un editor de texto
2. Busca la línea que dice `"client_email":`
3. Copia el email (será algo como `gestion-irc-service@proyecto.iam.gserviceaccount.com`)
4. Abre tu Google Sheets
5. Click en **"Compartir"** (botón verde arriba a la derecha)
6. Pega el email copiado
7. Asegúrate de darle permisos de **"Editor"**
8. **Desactiva** "Notificar personas"
9. Click en **"Compartir"**

### ✅ ¡Listo! Ya está configurado

---

## Opción B: OAuth 2.0

### ℹ️ Cuándo Usar Esta Opción
- Si prefieres que cada usuario haga login
- Si quieres más control sobre los accesos
- Si no quieres compartir credenciales

### 📋 Pasos

#### 1-2. Igual que Service Account
Sigue los pasos 1 y 2 de la Opción A

#### 3. Configurar OAuth Consent Screen

1. Ve a **"APIs y servicios" > "Pantalla de consentimiento de OAuth"**
2. Selecciona **"Interno"** (o "Externo" si no eres de UCM)
3. Click en **"CREAR"**
4. Rellena el formulario:
   - Nombre de la aplicación: `Gestión IRC UCM`
   - Email de asistencia: tu email
   - Dominio: (dejar vacío)
   - Email de contacto: tu email
5. Click en **"GUARDAR Y CONTINUAR"**
6. En "Permisos", no añadas nada → **"GUARDAR Y CONTINUAR"**
7. En "Usuarios de prueba", añade los emails de los usuarios
8. Click en **"GUARDAR Y CONTINUAR"**
9. Resumen → Click en **"VOLVER AL PANEL"**

#### 4. Crear Credenciales OAuth

1. Ve a **"APIs y servicios" > "Credenciales"**
2. Click en **"+ CREAR CREDENCIALES"**
3. Selecciona **"ID de cliente de OAuth"**
4. Tipo: **"Aplicación de escritorio"**
5. Nombre: `Gestión IRC - Desktop`
6. Click en **"CREAR"**
7. Se mostrará un diálogo con el ID y secreto
8. Click en **"DESCARGAR JSON"**
9. Renombra el archivo a `credentials.json`

#### 5. Colocar las Credenciales

1. Copia `credentials.json` en la carpeta de la aplicación
2. La primera vez que ejecutes, se abrirá el navegador
3. Inicia sesión con tu cuenta de Google
4. Autoriza la aplicación
5. ¡Listo!

---

## Configurar el Spreadsheet

### Estructura Requerida

Tu Google Sheets debe tener estas hojas con estos nombres EXACTOS:

#### Hoja 1: "Solicitudes"

Encabezados (primera fila):

```
ID | Número Solicitud | Nombre | Apellidos | Email | Teléfono | Departamento | 
Tipo Usuario | Tipo Servicio | Descripción | Observaciones | Dosis (Gy) | 
Horas Uso | Fecha Solicitud | Fecha Inicio | Fecha Fin | Estado | 
Prioridad | Coste Calculado | Coste Final | Facturada | Fecha Facturación
```

#### Hoja 2: "Sesiones"

Encabezados (primera fila):

```
ID | Solicitud ID | Número Sesión | Fecha Sesión | Hora Inicio | Hora Fin | 
Duración (h) | Tipo Servicio | Descripción | Dosis Aplicada | Equipos | 
Observaciones Técnicas | Responsable | Técnicos | Resultados | Incidencias | 
Archivos | Estado | Completada
```

### Plantilla Lista para Usar

[DESCARGA: Plantilla Google Sheets](https://docs.google.com/spreadsheets/d/...)

O crea una nueva y copia los encabezados de arriba.

### Obtener el ID del Spreadsheet

1. Abre tu Google Sheets
2. Mira la URL, será algo como:
   ```
   https://docs.google.com/spreadsheets/d/1ABC123xyz456/edit
   ```
3. Copia la parte entre `/d/` y `/edit`:
   ```
   1ABC123xyz456  ← Este es tu ID
   ```
4. Cuando ejecutes la aplicación por primera vez, pégalo cuando lo solicite

---

## Solución de Problemas

### ❌ "Error de autenticación"

**Causa**: El archivo de credenciales no está o está mal nombrado

**Solución**:
1. Verifica que el archivo se llame EXACTAMENTE:
   - `service_account.json` o
   - `credentials.json`
2. Verifica que esté en la carpeta raíz de la aplicación
3. Abre el JSON y verifica que sea válido (debe empezar con `{`)

### ❌ "No se puede acceder al spreadsheet"

**Causa**: No has compartido el Sheet con la service account

**Solución**:
1. Abre tu Google Sheets
2. Click en "Compartir"
3. Añade el email de la service account
4. Dale permisos de "Editor"

### ❌ "API not enabled"

**Causa**: No has habilitado la API de Google Sheets

**Solución**:
1. Ve a Google Cloud Console
2. APIs y servicios > Biblioteca
3. Busca "Google Sheets API"
4. Click en "HABILITAR"

### ❌ "403: Access Denied"

**Causa**: El proyecto no tiene los permisos necesarios

**Solución**:
1. Verifica que la API esté habilitada
2. Verifica que hayas compartido el Sheet
3. Verifica que los permisos sean de "Editor"

### ❌ "Token expired"

**Causa**: (Solo OAuth) El token ha caducado

**Solución**:
1. Elimina el archivo `data/token.json`
2. Ejecuta de nuevo
3. Vuelve a autorizar en el navegador

---

## 🔒 Seguridad

### ⚠️ IMPORTANTE

- **NUNCA** compartas tu archivo `service_account.json` públicamente
- **NUNCA** lo subas a GitHub o repositorios públicos
- Guárdalo en un lugar seguro
- Si se compromete, elimina la service account y crea una nueva

### Permisos Recomendados

- Service Account: Solo acceso al Spreadsheet específico
- Usuarios OAuth: Solo usuarios de confianza de tu organización

---

## 📞 ¿Necesitas Ayuda?

Si sigues teniendo problemas:

1. Revisa el archivo de log: `logs/gestion_irc.log`
2. Busca en la sección FAQ: `docs/FAQ.md`
3. Contacta con soporte técnico

---

## ✅ Checklist Final

Antes de usar la aplicación, verifica:

- [ ] Proyecto creado en Google Cloud Console
- [ ] API de Google Sheets habilitada
- [ ] Service Account o OAuth configurado
- [ ] Archivo de credenciales en la carpeta correcta
- [ ] Google Sheets creado con la estructura correcta
- [ ] Sheet compartido con la service account (si aplica)
- [ ] ID del Spreadsheet anotado

Si todo está ✅ → ¡La aplicación debería funcionar perfectamente!

---

**Última actualización**: Noviembre 2025
**Versión**: 4.0
