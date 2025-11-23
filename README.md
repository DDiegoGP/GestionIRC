# 🧪 Sistema de Gestión IRC - UCM

## Versión 4.0 - Aplicación de Escritorio

Sistema completo de gestión de servicios del Instituto de Radiaciones Corpusculares de la Universidad Complutense de Madrid.

---

## 📋 Descripción

Aplicación de escritorio profesional para Windows que permite gestionar:

- ✅ Solicitudes de servicios IRC
- 📅 Sesiones de trabajo
- 💰 Cálculo automático de tarifas
- 📊 Dashboard con métricas en tiempo real
- 📈 Generación de informes
- 🔍 Búsqueda avanzada
- 📥 Exportación a Excel
- ☁️ Sincronización con Google Sheets

---

## 🎯 Características Principales

### ✨ Interfaz Moderna
- Diseño limpio e intuitivo
- Navegación por pestañas
- Sin necesidad de conocimientos técnicos

### 💾 Base de Datos
- Integración con Google Sheets
- Multi-usuario (hasta 3 usuarios simultáneos)
- Backups automáticos
- Sincronización en tiempo real

### 📊 Dashboard Inteligente
- Métricas en tiempo real
- Gráficos interactivos
- Sistema de alertas
- Calendario de sesiones

### 💰 Gestión de Tarifas 2025
- Cálculo automático según tipo de usuario (OPI/UCM)
- Tarifas diferenciadas por servicio
- Cálculo de costes complejos (dosis, horas)
- Control de facturación

### 📝 Gestión de Solicitudes
- Formulario intuitivo
- Carga desde PDF
- Validación automática de datos
- Seguimiento de estados

---

## 🚀 Instalación Rápida

### Opción 1: Usar el Ejecutable (RECOMENDADO)

1. **Descargar** la carpeta `GestionIRC_Portable`
2. **Copiar** tu archivo de credenciales (ver sección Configuración)
3. **Ejecutar** `GestionIRC.exe`
4. **¡Listo!** 🎉

### Opción 2: Desde Código Fuente

```bash
# 1. Clonar/Descargar el proyecto
git clone <tu-repo> GestionIRC
cd GestionIRC

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python main.py
```

---

## ⚙️ Configuración

### 🔑 Credenciales de Google Sheets

Tienes 2 opciones:

#### Opción A: Service Account (Recomendado - Más Fácil)

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto
3. Habilita la API de Google Sheets
4. Crea una Service Account
5. Descarga el JSON de credenciales
6. Renómbralo a `service_account.json`
7. Cópialo en la carpeta de la aplicación
8. Comparte tu Google Sheets con el email del service account

**📹 Tutorial detallado:** Ver `docs/CONFIGURACION_GOOGLE_SHEETS.md`

#### Opción B: OAuth 2.0 (Login de Usuario)

1. Crea credenciales OAuth 2.0 en Google Cloud
2. Descarga el archivo `credentials.json`
3. Cópialo en la carpeta de la aplicación
4. Al ejecutar, se abrirá el navegador para autorizar

### 📄 Configurar el Google Sheets

1. Crea un Google Sheets con estas hojas:
   - `Solicitudes`
   - `Sesiones`
   
2. Copia el ID del Sheets (la parte entre `/d/` y `/edit` en la URL)

3. Pégalo en la aplicación cuando lo solicite

---

## 📚 Estructura del Proyecto

```
GestionIRC/
│
├── main.py                    # Punto de entrada
├── config.py                  # Configuración general
├── requirements.txt           # Dependencias
├── build_exe.bat             # Script para generar .exe
│
├── src/
│   ├── gui/                  # Interfaz gráfica
│   │   ├── main_window.py    # Ventana principal
│   │   ├── dashboard.py      # Dashboard
│   │   ├── solicitudes.py    # Gestión de solicitudes
│   │   ├── sesiones.py       # Gestión de sesiones
│   │   ├── busqueda.py       # Búsqueda avanzada
│   │   └── informes.py       # Informes
│   │
│   ├── models/               # Modelos de datos
│   │   ├── solicitud.py      # Modelo Solicitud
│   │   └── sesion.py         # Modelo Sesión
│   │
│   ├── utils/                # Utilidades
│   │   ├── sheets_manager.py # Gestión Google Sheets
│   │   ├── logger.py         # Sistema de logs
│   │   └── pdf_processor.py  # Procesamiento PDFs
│   │
│   └── constants.py          # Constantes y tarifas
│
├── data/                     # Datos locales
│   ├── backups/              # Copias de seguridad
│   └── gestion_irc.db        # Base de datos local (caché)
│
├── templates/                # Plantillas PDF
├── exports/                  # Archivos exportados
├── logs/                     # Archivos de log
│
└── docs/                     # Documentación
    ├── INSTALACION.md
    ├── CONFIGURACION_GOOGLE_SHEETS.md
    ├── GUIA_USUARIO.md
    └── FAQ.md
```

---

## 🎓 Guía de Uso Rápido

### 1️⃣ Primera Ejecución

1. Ejecuta `GestionIRC.exe`
2. Si es la primera vez, aparecerá el diálogo de configuración
3. Introduce el ID o URL de tu Google Sheets
4. Si usa OAuth, autoriza en el navegador
5. ¡Ya está configurado!

### 2️⃣ Crear una Solicitud

1. Ve a la pestaña **"📝 Solicitudes"**
2. Click en **"➕ Nueva Solicitud"**
3. Rellena el formulario
4. Click en **"💾 Guardar"**
5. El coste se calcula automáticamente

### 3️⃣ Cargar desde PDF

1. En **"📝 Solicitudes"**, click en **"📄 Desde PDF"**
2. Selecciona el PDF de la solicitud
3. Los datos se extraen automáticamente
4. Revisa y guarda

### 4️⃣ Ver Dashboard

1. Ve a la pestaña **"📊 Dashboard"**
2. Visualiza las métricas en tiempo real
3. Revisa las alertas
4. Analiza los gráficos

### 5️⃣ Generar Informes

1. Ve a **"📊 Informes"**
2. Selecciona el tipo de informe
3. Vista previa en pantalla
4. Exporta a Excel o PDF

---

## 💡 Consejos y Buenas Prácticas

### ✅ Recomendaciones

- **Actualiza regularmente**: Click en 🔄 para sincronizar datos
- **Backups automáticos**: Se crean cada 24 horas
- **Revisa alertas**: Verifica el dashboard diariamente
- **Valida datos**: Antes de guardar, revisa que todo sea correcto

### ⚠️ Problemas Comunes

**"No se puede conectar con Google Sheets"**
- Verifica tu conexión a internet
- Comprueba que el archivo de credenciales esté en la carpeta
- Revisa que hayas compartido el Sheet con el service account

**"El ejecutable no inicia"**
- Ejecuta como Administrador
- Verifica que Windows Defender no lo bloquee
- Revisa el archivo de log en `logs/gestion_irc.log`

**"Los datos no se guardan"**
- Verifica permisos de escritura en Google Sheets
- Comprueba que todos los campos obligatorios estén completos
- Revisa las alertas en la barra de estado

---

## 🔧 Generación del Ejecutable

### Desde el proyecto

```batch
# En Windows
build_exe.bat
```

El ejecutable se generará en `dist/GestionIRC_Portable/`

### Requisitos para generar el .exe

- Python 3.8 o superior
- PyInstaller
- Todas las dependencias instaladas

---

## 📊 Tarifas 2025

### Servicios Disponibles

| Servicio | OPI | UCM |
|----------|-----|-----|
| Irradiación < 10 Gy | 26€ | 20€ |
| Irradiación > 10 Gy | 26€ + 0.1€/Gy | 20€ + 0.1€/Gy |
| Contador Gamma < 1h | 22€ | 17€ |
| Contador Gamma > 1h | 20€ + 10€/h | 15€ + 10€/h |
| Contador microBeta < 1h | 22€ | 17€ |
| Contador microBeta > 1h | 22€ + 10€/h | 17€ + 10€/h |
| Gestión fuentes no encapsuladas | 20€ | 15€ |
| Gestión/retirada residuos | 10€ | 7.5€ |
| Trámites regulatorios | 900€ | 700€ |
| Gestión dosimétrica | 30€ | 25€ |

---

## 🤝 Soporte

### Documentación

- **Instalación**: `docs/INSTALACION.md`
- **Configuración**: `docs/CONFIGURACION_GOOGLE_SHEETS.md`
- **Guía de Usuario**: `docs/GUIA_USUARIO.md`
- **FAQ**: `docs/FAQ.md`

### Contacto

- **Email**: [tu-email@ucm.es]
- **Teléfono**: [tu-teléfono]
- **Ubicación**: Instituto de Radiaciones Corpusculares - UCM

---

## 📝 Changelog

### v4.0.0 (2025-11-12)
- 🎉 Primera versión ejecutable
- ✨ Interfaz gráfica completa con tkinter
- 📊 Dashboard con métricas y gráficos
- 💾 Integración con Google Sheets
- 📝 Gestión completa de solicitudes
- 📅 Gestión de sesiones
- 🔍 Búsqueda avanzada
- 📊 Generación de informes
- 📥 Exportación a Excel
- 🔒 Sistema de logs
- 💰 Tarifas 2025 actualizadas

### v3.0 (Notebook)
- Versión anterior en Google Colab

---

## 📄 Licencia

Copyright © 2025 Universidad Complutense de Madrid

Uso interno exclusivo del IRC-UCM

---

## 🙏 Agradecimientos

Desarrollado para el Instituto de Radiaciones Corpusculares de la Universidad Complutense de Madrid.

**¡Gracias por usar el Sistema de Gestión IRC!** 🧪✨
