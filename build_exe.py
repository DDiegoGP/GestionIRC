"""
Script para generar el ejecutable de GestionIRC
Incluye el logo del IRC como icono
"""
import os
import sys
from pathlib import Path

def verificar_dependencias():
    """Verifica que estén instaladas las dependencias necesarias"""
    try:
        import PyInstaller
        print("✅ PyInstaller instalado")
    except ImportError:
        print("❌ PyInstaller no instalado")
        print("   Instálalo con: pip install pyinstaller")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow instalado")
    except ImportError:
        print("❌ Pillow no instalado")
        print("   Instálalo con: pip install pillow")
        return False
    
    return True

def convertir_logo_a_ico():
    """Convierte el logo PNG a ICO para Windows"""
    print("\n📝 Convirtiendo logo PNG a ICO...")
    
    try:
        from PIL import Image
        
        # Rutas
        png_path = Path("assets/logo-irc.png")
        ico_path = Path("assets/logo-irc.ico")
        
        if not png_path.exists():
            print(f"❌ No se encuentra {png_path}")
            return False
        
        # Abrir imagen
        img = Image.open(png_path)
        
        # Convertir a RGBA si no lo está
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Crear ICO con múltiples tamaños
        # Windows usa diferentes tamaños según el contexto
        img.save(
            ico_path,
            format='ICO',
            sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        )
        
        print(f"✅ Logo convertido a {ico_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir logo: {e}")
        return False

def build_ejecutable():
    """Genera el ejecutable con PyInstaller"""
    print("\n🔨 Generando ejecutable...")
    
    # Comando de PyInstaller
    comando = [
        'main.py',
        '--name=GestionIRC',
        '--icon=assets/logo-irc.ico',
        '--onefile',              # Un solo archivo .exe
        '--windowed',             # Sin consola
        '--add-data=assets;assets',  # Incluir carpeta assets
        '--hidden-import=PIL',
        '--hidden-import=PIL._imagingtk',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=matplotlib',
        '--hidden-import=matplotlib.backends.backend_tkagg',
        '--hidden-import=gspread',
        '--hidden-import=google.auth',
        '--hidden-import=google.oauth2',
        '--hidden-import=pdfplumber',
        '--collect-all=matplotlib',
        '--collect-all=PIL',
        '--noupx',  # No usar UPX (a veces da problemas)
        '--clean',  # Limpiar caché antes de build
    ]
    
    # Ejecutar PyInstaller
    import PyInstaller.__main__
    
    try:
        PyInstaller.__main__.run(comando)
        print("\n✅ Ejecutable generado exitosamente!")
        print("\n📂 El ejecutable está en: dist/GestionIRC.exe")
        print("\n📝 Próximos pasos:")
        print("   1. Prueba el ejecutable en dist/GestionIRC.exe")
        print("   2. Para distribuir, copia:")
        print("      - dist/GestionIRC.exe")
        print("      - credentials/ (credenciales de Google)")
        print("      - README_USUARIO.txt (instrucciones)")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al generar ejecutable: {e}")
        return False

def crear_readme_distribucion():
    """Crea el README para usuarios finales"""
    print("\n📝 Creando README para distribución...")
    
    readme = """
# GestionIRC - Instalación

## 📥 Archivos Necesarios

Para ejecutar GestionIRC necesitas:

```
GestionIRC/
├── GestionIRC.exe              ← Ejecutable principal
├── credentials/
│   └── service_account.json    ← Credenciales de Google
└── README_USUARIO.txt          ← Este archivo
```

## 🚀 Instalación

### Primera Vez:

1. **Copia la carpeta completa** a tu computadora
   Ejemplo: `C:\\Usuarios\\TuNombre\\GestionIRC\\`

2. **Verifica las credenciales**:
   - Abre la carpeta `credentials/`
   - Asegúrate de que existe `service_account.json`
   - Si no lo tienes, solicítalo al administrador

3. **Primera ejecución**:
   - Doble click en `GestionIRC.exe`
   - Se abrirá un asistente de configuración
   - Introduce el ID de tu Google Sheet
   - El programa guardará tu configuración

### Ejecuciones Posteriores:

- Simplemente doble click en `GestionIRC.exe`
- La configuración se carga automáticamente

## 🔧 Configuración Inicial

En la primera ejecución, necesitarás:

### 1. ID de Google Sheet

Es un texto largo como:
```
1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

**¿Dónde lo encuentro?**
- Abre tu Google Sheet en el navegador
- Mira la URL:
  `https://docs.google.com/spreadsheets/d/[AQUÍ_ESTÁ_EL_ID]/edit`
- Copia solo la parte del ID

### 2. Archivo de Credenciales

El archivo `service_account.json` debe estar en:
```
credentials/service_account.json
```

**Si no lo tienes**:
1. Habla con el administrador del sistema
2. Pídele que te proporcione el archivo
3. Guárdalo en la carpeta `credentials/`

## 📊 Uso del Programa

### Pestañas Principales:

1. **📋 Solicitudes**
   - Ver y crear solicitudes de servicio
   - Descargar PDFs
   - Cambiar estados

2. **🔬 Sesiones**
   - Registrar sesiones de trabajo
   - Ver calendario de actividades
   - Seguir el progreso de cada servicio

3. **📊 Dashboard**
   - Vista general del estado
   - Estadísticas y gráficos
   - Alertas de servicios atrasados

4. **⚙️ Configuración**
   - Cambiar Google Sheet
   - Actualizar credenciales
   - Ver información del sistema

### Flujo de Trabajo Típico:

**1. Crear Solicitud**:
   - Pestaña 📋 Solicitudes
   - Click en "➕ Nueva Solicitud"
   - Rellenar formulario
   - Guardar

**2. Descargar PDF**:
   - En la tabla, selecciona la solicitud
   - Click en "📄 Descargar PDF"
   - Imprime y entrégala al cliente para firmar

**3. Procesar PDF Firmado**:
   - Cuando te devuelvan el PDF firmado
   - Click en "📄" junto a la solicitud
   - Click en "✅ Marcar como En Proceso"

**4. Registrar Sesión**:
   - Pestaña 🔬 Sesiones
   - Click en "➕ Nueva Sesión"
   - Selecciona la solicitud
   - Rellena los datos de la sesión
   - Guardar

**5. Ver Progreso**:
   - En 🔬 Sesiones, ve el panel "📊 Progreso"
   - Verás el % completado de cada servicio
   - Alertas si algo está atrasado

## 🆘 Solución de Problemas

### No se conecta a Google Sheets

**Problema**: Sale error "No se pudo conectar"

**Soluciones**:
1. Verifica tu conexión a Internet
2. Comprueba que `service_account.json` existe
3. Asegúrate de que el ID de Sheet es correcto
4. Habla con el administrador

### El programa se cierra al abrirse

**Problema**: Se abre y se cierra inmediatamente

**Soluciones**:
1. Abre una terminal (cmd)
2. Navega a la carpeta: `cd C:\\ruta\\a\\GestionIRC`
3. Ejecuta: `GestionIRC.exe`
4. Lee el error que aparece
5. Comunícaselo al administrador

### Faltan datos en las tablas

**Problema**: No veo todas las solicitudes/sesiones

**Soluciones**:
1. Click en "🔄 Actualizar"
2. Cierra y abre el programa
3. Verifica que estás conectado a Internet
4. Pregunta al administrador si cambió la Sheet

### No puedo crear nuevas solicitudes

**Problema**: Sale error al guardar

**Soluciones**:
1. Verifica todos los campos requeridos
2. Asegúrate de tener permisos en la Sheet
3. Prueba con "🔄 Actualizar" primero
4. Contacta al administrador

## 📞 Soporte

### Para Problemas Técnicos:

Contacta al administrador del sistema con:
1. Descripción del problema
2. Captura de pantalla del error
3. Qué estabas haciendo cuando ocurrió

### Para Dudas de Uso:

Consulta este manual o pregunta a tus compañeros.

## 🔄 Actualizaciones

Cuando haya una nueva versión:

1. Descarga el nuevo `GestionIRC.exe`
2. Cierra el programa actual
3. Reemplaza el archivo .exe antiguo
4. **NO borres** la carpeta `credentials/`
5. Abre el nuevo ejecutable

Tu configuración se mantendrá.

## ✅ Checklist de Instalación

- [ ] Tengo la carpeta GestionIRC completa
- [ ] Existe credentials/service_account.json
- [ ] Sé el ID de mi Google Sheet
- [ ] Puedo ejecutar GestionIRC.exe
- [ ] Completé la configuración inicial
- [ ] Puedo ver las pestañas principales
- [ ] Puedo crear una solicitud de prueba

Si todos los checks están ✅, ¡estás listo! 🚀

---

**GestionIRC v1.0**
Instituto de Radiaciones Corpusculares - UCM
"""
    
    try:
        with open("dist/README_USUARIO.txt", "w", encoding='utf-8') as f:
            f.write(readme)
        print("✅ README creado en dist/README_USUARIO.txt")
        return True
    except Exception as e:
        print(f"❌ Error al crear README: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 BUILD DE EJECUTABLE - GestionIRC")
    print("=" * 60)
    
    # Verificar dependencias
    if not verificar_dependencias():
        print("\n❌ Faltan dependencias. Instálalas y vuelve a ejecutar.")
        return 1
    
    # Convertir logo
    if not convertir_logo_a_ico():
        print("\n⚠️  Advertencia: No se pudo convertir el logo")
        print("   El ejecutable se creará sin icono personalizado")
        respuesta = input("\n¿Continuar de todos modos? (s/n): ")
        if respuesta.lower() != 's':
            return 1
    
    # Generar ejecutable
    if not build_ejecutable():
        return 1
    
    # Crear README
    crear_readme_distribucion()
    
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    print("\n📦 Archivos generados:")
    print("   - dist/GestionIRC.exe")
    print("   - dist/README_USUARIO.txt")
    print("\n📝 Para distribuir:")
    print("   1. Copia todo el contenido de dist/")
    print("   2. Añade la carpeta credentials/")
    print("   3. Entrega a los usuarios")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
