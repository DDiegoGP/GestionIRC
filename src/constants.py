"""
Constantes del Sistema - Tarifas 2025 y Servicios IRC
"""

# Tarifas de Servicios 2025
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

# Tipos de servicios
TIPOS_SERVICIOS = [
    "Irradiación < 10 Gy",
    "Irradiación > 10 Gy",
    "Contador Gamma < 1h",
    "Contador Gamma > 1h",
    "Contador microBeta < 1h",
    "Contador microBeta > 1h",
    "Gestión de fuentes no encapsuladas",
    "Gestión/retirada de residuos",
    "Trámites regulatorios",
    "Gestión dosimétrica",
]

# Tipos de usuario
TIPOS_USUARIO = ["OPI", "UCM"]

# Estados de solicitud
ESTADOS_SOLICITUD = [
    "Pendiente",
    "En Proceso",
    "Completada",
    "Cancelada",
    "En Espera"
]

# Departamentos UCM
DEPARTAMENTOS_UCM = [
    "Física Aplicada",
    "Química Física",
    "Biología Celular",
    "Medicina",
    "Farmacia",
    "Veterinaria",
    "Química Inorgánica",
    "Química Orgánica",
    "Bioquímica y Biología Molecular",
    "Otro"
]

# Campos del formulario de solicitud PDF
CAMPOS_PDF_SOLICITUD = {
    'nombre': 'Nombre',
    'apellidos': 'Apellidos',
    'email': 'Email',
    'telefono': 'Telefono',
    'departamento': 'Departamento',
    'tipo_usuario': 'TipoUsuario',
    'tipo_servicio': 'TipoServicio',
    'fecha_solicitud': 'FechaSolicitud',
    'descripcion': 'Descripcion',
    'observaciones': 'Observaciones',
}

# Meses en español
MESES_ESP = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Colores para gráficos
COLORES_GRAFICOS = {
    'primary': '#1976D2',
    'secondary': '#424242',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#F44336',
    'info': '#2196F3',
    'paleta': ['#1976D2', '#4CAF50', '#FF9800', '#F44336', '#9C27B0', '#00BCD4']
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
}

# Tooltips de ayuda
TOOLTIPS = {
    'tipo_usuario': 'OPI: Otros organismos públicos\nUCM: Universidad Complutense de Madrid',
    'tipo_servicio': 'Selecciona el tipo de servicio a solicitar',
    'estado': 'Estado actual de la solicitud',
    'backup': 'Crea una copia de seguridad de todos los datos',
    'exportar': 'Exporta los datos a un archivo Excel',
}
