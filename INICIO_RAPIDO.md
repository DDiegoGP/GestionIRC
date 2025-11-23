# 🚀 GUÍA DE INICIO RÁPIDO - Sistema de Gestión IRC

## ✅ ¡Proyecto Completo Generado!

Has recibido el proyecto completo del Sistema de Gestión IRC v4.0 convertido a aplicación de escritorio Windows.

---

## 📦 ¿Qué Incluye?

```
GestionIRC/
│
├── 📄 main.py              - Archivo principal
├── 📄 config.py            - Configuración
├── 📄 requirements.txt     - Dependencias Python
├── 📄 build_exe.bat        - Script para generar ejecutable
├── 📄 README.md            - Documentación completa
│
├── 📁 src/                 - Código fuente
│   ├── gui/                - Interfaz gráfica
│   ├── models/             - Modelos de datos
│   ├── utils/              - Utilidades
│   └── constants.py        - Tarifas 2025
│
├── 📁 data/                - Datos locales
├── 📁 templates/           - Plantillas
├── 📁 exports/             - Exportaciones
├── 📁 logs/                - Registros
│
└── 📁 docs/                - Documentación detallada
    ├── CONFIGURACION_GOOGLE_SHEETS.md
    └── FAQ.md
```

---

## 🎯 SIGUIENTE PASO: Elegir tu Camino

### Opción 1: Generar Ejecutable (RECOMENDADO)

**Para**: Distribuir a usuarios que no tienen Python

1. **Instala Python 3.8+** (si no lo tienes):
   - Descarga de https://python.org
   - ✅ Marca "Add Python to PATH" durante instalación

2. **Instala dependencias**:
   ```bash
   cd GestionIRC
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Genera el ejecutable**:
   ```bash
   build_exe.bat
   ```
   
4. **Resultado**: `dist/GestionIRC_Portable/GestionIRC.exe`

5. **Distribuir**: 
   - Copia toda la carpeta `GestionIRC_Portable`
   - Incluye el archivo de credenciales
   - ¡Ya está listo para usar!

### Opción 2: Ejecutar desde Python

**Para**: Desarrollo o pruebas

1. **Instala Python 3.8+** (si no lo tienes)

2. **Crea entorno virtual**:
   ```bash
   cd GestionIRC
   python -m venv venv
   ```

3. **Activa el entorno**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Instala dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecuta**:
   ```bash
   python main.py
   ```

---

## 🔑 CONFIGURACIÓN DE GOOGLE SHEETS

### Paso Crítico: Obtener Credenciales

**👉 Lee PRIMERO**: `docs/CONFIGURACION_GOOGLE_SHEETS.md`

#### Resumen Rápido:

**Opción A - Service Account (MÁS FÁCIL):**

1. Google Cloud Console → Nuevo Proyecto
2. Habilitar "Google Sheets API"
3. Crear Service Account
4. Descargar JSON → Renombrar a `service_account.json`
5. Copiar a carpeta de la app
6. Compartir tu Google Sheets con el email del service account

**Opción B - OAuth 2.0:**

1. Igual que opción A (pasos 1-2)
2. Configurar pantalla de consentimiento
3. Crear credenciales OAuth
4. Descargar JSON → Renombrar a `credentials.json`
5. Primera ejecución: Autorizar en navegador

### Preparar el Google Sheets

1. **Crear nuevo Google Sheets**
2. **Crear dos hojas**:
   - `Solicitudes`
   - `Sesiones`
3. **Copiar encabezados** (ver README.md)
4. **Obtener el ID** (de la URL)
5. **Compartir** con service account (si aplica)

---

## 📚 DOCUMENTACIÓN COMPLETA

- **README.md** → Documentación general completa
- **docs/CONFIGURACION_GOOGLE_SHEETS.md** → Guía paso a paso con capturas
- **docs/FAQ.md** → Preguntas frecuentes y soluciones

---

## ✨ CARACTERÍSTICAS PRINCIPALES

### Lo que YA está implementado:

✅ **Interfaz Gráfica Completa**
- Ventana principal con pestañas
- Dashboard con métricas en tiempo real
- Gráficos de análisis
- Sistema de alertas

✅ **Gestión de Solicitudes**
- Crear, editar, eliminar
- Formulario completo con validación
- Carga desde PDF
- Cálculo automático de costes

✅ **Gestión de Sesiones**
- Registro de sesiones
- Vinculación con solicitudes
- Seguimiento temporal

✅ **Búsqueda Avanzada**
- Filtros múltiples
- Búsqueda en tiempo real

✅ **Informes y Exportación**
- Varios tipos de informes
- Exportación a Excel
- Vista previa en pantalla

✅ **Sincronización Google Sheets**
- Lectura/escritura
- Caché inteligente
- Multi-usuario

✅ **Sistema Robusto**
- Logs detallados
- Manejo de errores
- Validaciones

### Mejoras respecto al Notebook:

🎯 **Interfaz**: De Colab a aplicación profesional
🚀 **Velocidad**: Caché local, operaciones rápidas
👥 **Multi-usuario**: Hasta 3 usuarios simultáneos
💾 **Offline**: Caché permite ver datos sin conexión
🔒 **Seguridad**: Logs, validaciones, backups
📊 **Visualización**: Gráficos mejorados con matplotlib
🎨 **UX**: Interfaz intuitiva, sin código visible

---

## 🔧 PERSONALIZACIÓN

### Cambiar Tarifas

Edita: `src/constants.py` → `TARIFAS_SERVICIOS`

### Cambiar Colores/Fuentes

Edita: `config.py` → `UI_CONFIG`

### Añadir Servicios

Edita: `src/constants.py` → `TIPOS_SERVICIOS`

### Añadir Departamentos

Edita: `src/constants.py` → `DEPARTAMENTOS_UCM`

---

## ⚠️ CONSIDERACIONES IMPORTANTES

### Antes de Distribuir:

1. **Prueba exhaustivamente** con datos reales
2. **Verifica** que todos los usuarios puedan acceder al Google Sheets
3. **Prepara** una copia del README para usuarios
4. **Incluye** el archivo de credenciales (¡pero cuidado con la seguridad!)
5. **Crea backups** del Google Sheets original

### Seguridad:

- ❌ NO subas `service_account.json` a repositorios públicos
- ❌ NO compartas las credenciales fuera de tu organización
- ✅ Usa permisos mínimos necesarios
- ✅ Revisa los logs periódicamente

### Rendimiento:

- Primera ejecución puede tardar 10-20 segundos
- El caché mejora la velocidad después
- Con muchos datos (>1000 solicitudes) puede ir más lento

---

## 🐛 SI ALGO NO FUNCIONA

### 1. Revisa los Logs

```
logs/gestion_irc.log
```

### 2. Verifica lo Básico

- [ ] Python instalado (si ejecutas desde código)
- [ ] Dependencias instaladas
- [ ] Archivo de credenciales en lugar correcto
- [ ] Google Sheets con estructura correcta
- [ ] Internet funcionando

### 3. Consulta la FAQ

```
docs/FAQ.md
```

### 4. Busca el Error Específico

Los logs son muy descriptivos y te dirán exactamente qué falló.

---

## 📞 SOPORTE

Si necesitas ayuda adicional:

1. **Lee la documentación completa** (README.md)
2. **Revisa la FAQ** (docs/FAQ.md)
3. **Consulta los logs** (logs/gestion_irc.log)
4. **Contacta** con el desarrollador

---

## 🎉 ¡LISTO PARA EMPEZAR!

### Lista de Verificación Final:

- [ ] Leí el README.md
- [ ] Configuré las credenciales de Google Sheets
- [ ] Preparé el Google Sheets con las hojas correctas
- [ ] Instalé las dependencias (si ejecuto desde Python)
- [ ] Probé la aplicación
- [ ] Todo funciona correctamente

### Si todo está ✅ → **¡A trabajar!** 🚀

---

**Versión**: 4.0.0  
**Fecha**: Noviembre 2025  
**Desarrollado para**: IRC - Universidad Complutense de Madrid

¡Éxito con tu nueva aplicación! 🧪✨
