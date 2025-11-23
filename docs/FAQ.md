# ❓ Preguntas Frecuentes (FAQ)

## General

### ¿Qué es esta aplicación?
Sistema de gestión para el Instituto de Radiaciones Corpusculares de la UCM que permite gestionar solicitudes, sesiones, calcular tarifas y generar informes.

### ¿Necesito internet?
Sí, para sincronizar con Google Sheets. La aplicación funciona localmente pero necesita conexión para guardar/cargar datos.

### ¿Cuántos usuarios pueden usarla simultáneamente?
Hasta 3 usuarios pueden trabajar al mismo tiempo compartiendo el mismo Google Sheets.

---

## Instalación

### ¿Necesito instalar Python?
NO, si usas el ejecutable `.exe`. Solo necesitas Python si vas a ejecutar desde código fuente.

### ¿Dónde pongo las credenciales?
En la misma carpeta donde está el archivo `GestionIRC.exe`.

### Windows Defender bloquea el ejecutable
Normal con aplicaciones nuevas. Click derecho > Más información > Ejecutar de todos modos.

---

## Google Sheets

### ¿Qué opción de credenciales elijo?
**Service Account** es más fácil y recomendado para múltiples usuarios.

### ¿Dónde encuentro el ID del Spreadsheet?
En la URL de tu Google Sheets, la parte entre `/d/` y `/edit`.

### No puedo compartir con el service account
Asegúrate de copiar EXACTAMENTE el email del `client_email` del archivo JSON.

### Los cambios no se guardan
Verifica que el service account tenga permisos de "Editor", no solo "Lector".

---

## Uso

### ¿Cómo calculo el coste de una solicitud?
Automático al guardar. Solo rellena el formulario con tipo de usuario y servicio.

### ¿Puedo editar una solicitud?
Sí, selecciónala en la tabla y click en "✏️ Editar".

### ¿Cómo exporto a Excel?
Ve a la pestaña "📊 Informes" y click en "📥 Exportar a Excel".

### ¿Los gráficos son interactivos?
Los del dashboard son estáticos pero se actualizan en tiempo real.

---

## Errores Comunes

### "Error de conexión con Google Sheets"
- Verifica tu internet
- Comprueba que el archivo de credenciales esté en la carpeta
- Revisa que la API esté habilitada

### "No se encontró el spreadsheet"
- Verifica el ID
- Comprueba que hayas compartido el Sheet con la service account
- Asegúrate de que existe

### "Campos obligatorios vacíos"
Rellena todos los campos marcados con asterisco (*).

### El ejecutable tarda en abrir
Normal la primera vez. Puede tardar 10-20 segundos.

---

## Rendimiento

### ¿Por qué tarda en cargar los datos?
Depende de:
- Cantidad de solicitudes
- Velocidad de internet
- Hay un caché para mejorar velocidad

### ¿Cómo hago que vaya más rápido?
Click en 🔄 solo cuando necesites datos frescos. El caché dura 5 minutos.

---

## Backups

### ¿Se hacen backups automáticos?
Sí, cada 24 horas en `data/backups/`.

### ¿Cómo restauro un backup?
Copia el contenido del backup al Google Sheets manualmente.

---

## Problemas Técnicos

### El programa se cierra solo
Revisa el archivo `logs/gestion_irc.log` para ver el error.

### No aparecen los datos
1. Verifica conexión
2. Click en 🔄 Actualizar
3. Revisa que las hojas se llamen exactamente "Solicitudes" y "Sesiones"

### Los gráficos no se muestran
Puede ser un problema con matplotlib. Reinicia la aplicación.

---

## Contacto

**¿No encuentras tu respuesta?**

- 📧 Email: [tu-email@ucm.es]
- 📞 Teléfono: [tu-teléfono]
- 📍 Ubicación: Instituto de Radiaciones Corpusculares - UCM
- 📝 Documentación: Ver carpeta `docs/`

---

Última actualización: Noviembre 2025
