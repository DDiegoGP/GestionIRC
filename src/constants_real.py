"""
Constantes del Sistema - Tarifas 2025 y Servicios IRC (Adaptado a estructura real)
"""

# Tarifas de Servicios 2025 (según TARIFAS_2025.pdf del proyecto)
TARIFAS_SERVICIOS = {
    "Irradiación < 10 Gy": {"OPI": 26, "UCM": 20},
    "Irradiación > 10 Gy": {
        "OPI": {"base": 26, "extra_por_gy": 0.1}, 
        "UCM": {"base": 20, "extra_por_gy": 0.1}
    },
    "Contador Gamma < 1h": {"OPI": 22, "UCM": 17},
    "Contador Gamma > 1h": {
        "OPI": {"base": 20, "extra_hora": 10}, 
        "UCM": {"base": 15, "extra_hora": 10}
    },
    "Contador microBeta < 1h": {"OPI": 22, "UCM": 17},
    "Contador microBeta > 1h": {
        "OPI": {"base": 22, "extra_hora": 10}, 
        "UCM": {"base": 17, "extra_hora": 10}
    },
    "Gestión de fuentes no encapsuladas": {"OPI": 20, "UCM": 15},
    "Gestión/retirada de residuos": {"OPI": 10, "UCM": 7.5},
    "Trámites regulatorios": {"OPI": 900, "UCM": 700},
    "Gestión dosimétrica": {"OPI": 30, "UCM": 25},
}

# Mapeo de nombres del formulario web a nombres de tarifa
SERVICIO_MAPPING = {
    "Irradiación a dosis menores de 10 Gy": "Irradiación < 10 Gy",
    "Irradiación a dosis mayores de 10 Gy": "Irradiación > 10 Gy",
    "Gestión dosimétrica": "Gestión dosimétrica",
    "Gestión/retirada de residuos radiactivos/fuentes huerfanas": "Gestión/retirada de residuos",
    "Gestión/retirada de residuos": "Gestión/retirada de residuos",
    "Trámites regulatorios": "Trámites regulatorios",
}

# Tipos de servicios (nombres del formulario web)
TIPOS_SERVICIOS = [
    "Irradiación a dosis menores de 10 Gy",
    "Irradiación a dosis mayores de 10 Gy",
    "Contador Gamma < 1h",
    "Contador Gamma > 1h",
    "Contador microBeta < 1h",
    "Contador microBeta > 1h",
    "Gestión de fuentes no encapsuladas",
    "Gestión/retirada de residuos radiactivos/fuentes huerfanas",
    "Trámites regulatorios",
    "Gestión dosimétrica",
]

# Tipos de usuario
TIPOS_USUARIO = ["OPI", "UCM"]

# Estados de solicitud (con emojis como en el Excel original)
ESTADOS_SOLICITUD = [
    "⏳ Pendiente",
    "🕓 En progreso",
    "✅ Completado",
    "❌ Cancelado",
]

# Estados de sesión
ESTADOS_SESION = [
    "🕓 En progreso",
    "✅ Completado",
]

# Departamentos UCM (basados en los PDFs)
DEPARTAMENTOS_UCM = [
    "Inmunología, Oftalmología y ORL",
    "Bioquímica y Biología Molecular",
    "Física Aplicada",
    "Química Física",
    "Biología Celular",
    "Medicina",
    "Farmacia",
    "Veterinaria",
    "Química Inorgánica",
    "Química Orgánica",
    "Otro"
]

# Organismos/Centros comunes (basados en los PDFs)
ORGANISMOS_COMUNES = [
    "Facultad de Medicina",
    "Facultad de Ciencias Químicas",
    "Facultad de Ciencias Biológicas",
    "Facultad de Farmacia",
    "Facultad de Veterinaria",
    "Facultad de Ciencias Físicas",
    "FGUCM",
    "Otro"
]

# Meses en español
MESES_ESP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Colores para gráficos (tema Microsoft 365)
COLORES_GRAFICOS = {
    'primary': '#0078D4',  # Azul Microsoft
    'secondary': '#50E6FF',  # Azul claro
    'success': '#107C10',  # Verde
    'warning': '#FFB900',  # Amarillo/Naranja
    'error': '#E81123',  # Rojo
    'info': '#00B7C3',  # Cian
    'paleta': ['#0078D4', '#107C10', '#FFB900', '#E81123', '#8764B8', '#00B7C3']
}

# Colores tema Microsoft 365 (para UI)
THEME_COLORS = {
    'primary': '#0078D4',
    'primary_dark': '#005A9E',
    'primary_light': '#50E6FF',
    'background': '#FFFFFF',
    'background_alt': '#F3F2F1',
    'text': '#323130',
    'text_secondary': '#605E5C',
    'border': '#EDEBE9',
    'hover': '#F3F2F1',
    'selected': '#DEECF9',
}

# Configuración de exportación
EXPORT_CONFIG = {
    'excel': {
        'engine': 'openpyxl',
        'date_format': 'DD/MM/YYYY',
        'datetime_format': 'DD/MM/YYYY HH:MM',
    },
    'pdf': {
        'page_size': 'A4',
        'orientation': 'portrait',
        'margin': 20,
    }
}

# Mensajes del sistema
MENSAJES = {
    'error_conexion': '❌ Error de conexión con Google Sheets. Revisa tu conexión a internet.',
    'error_credenciales': '❌ Error con las credenciales. Revisa la configuración.',
    'exito_guardado': '✅ Datos guardados correctamente.',
    'exito_actualizado': '✅ Datos actualizados correctamente.',
    'exito_eliminado': '✅ Datos eliminados correctamente.',
    'confirmacion_eliminar': '⚠️ ¿Estás seguro de que deseas eliminar este registro?',
    'campos_vacios': '⚠️ Por favor, completa todos los campos obligatorios.',
    'datos_invalidos': '⚠️ Los datos introducidos no son válidos.',
    'pdf_cargado': '✅ PDF cargado correctamente. Revisa los datos extraídos.',
    'pdf_error': '❌ Error al cargar el PDF. Verifica el formato.',
}

# Tooltips de ayuda
TOOLTIPS = {
    'tipo_usuario': 'OPI: Otros organismos públicos de investigación\nUCM: Universidad Complutense de Madrid',
    'tipo_servicio': 'Selecciona el tipo de servicio a solicitar',
    'estado': 'Estado actual de la solicitud',
    'backup': 'Crea una copia de seguridad de todos los datos',
    'exportar': 'Exporta los datos a un archivo Excel',
    'pdf': 'Carga una solicitud desde el PDF del formulario web IRC',
    'detalles_servicio': 'Detalles específicos según el tipo de servicio (se guarda como JSON)',
}

# Encabezados de Google Sheets (para validación)
HEADERS_SOLICITUDES = [
    "ID de Solicitud",
    "Fecha de Solicitud",
    "Estado",
    "Servicio Solicitado",
    "Coste_Estimado_IVA_0",
    "Detalles_Servicio",
    "Nombre del Solicitante",
    "Email",
    "Telefono",
    "Organismo/Centro Solicitante",
    "Departamento Solicitante",
    "Investigador Principal",
    "Tipo de Usuario",
    "Organismo/Centro Facturacion",
    "Departamento Facturacion",
    "CIF",
    "Domicilio Fiscal",
    "Domicilio Postal",
    "Oficina Contable",
    "Organo Gestor",
    "Centro Gestor",
    "Proyecto",
    "Numero de Contabilidad",
    "Observaciones",
]

HEADERS_SESIONES = [
    "ID de Solicitud",
    "Fecha de Sesion",
    "Servicio de la Sesion",
    "Observaciones de la Sesion",
    "Coste de la Sesion",
    "Irradiaciones realizadas",
    "Dosis suministrada",
    "Tiempo dosimetría (meses)",
    "Tiempo Usado (h)",
    "Estado del Servicio",
]

# Rangos de Google Sheets
RANGO_SOLICITUDES = "Solicitudes!A:X"  # 24 columnas
RANGO_SESIONES = "Sesiones!A:J"  # 10 columnas
