"""
Modelo de Sesión de Servicio IRC - Adaptado a estructura real
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Sesion:
    """Representa una sesión de servicio IRC con estructura real del Google Sheets"""
    
    # === IDENTIFICACIÓN ===
    id_solicitud: str = ""  # FK a Solicitud
    fecha_sesion: datetime = field(default_factory=datetime.now)
    
    # === SERVICIO ===
    servicio_sesion: str = ""
    observaciones_sesion: str = ""
    coste_sesion: float = 0.0
    
    # === MÉTRICAS ESPECÍFICAS ===
    irradiaciones_realizadas: float = 0.0
    dosis_suministrada: float = 0.0  # en Gy
    tiempo_dosimetria_meses: float = 0.0
    tiempo_usado_h: float = 0.0
    
    # === ESTADO ===
    estado_servicio: str = "🕓 En progreso"  # 🕓 En progreso, ✅ Completado
    
    # === METADATOS (no en sheets) ===
    creado_por: str = ""
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def to_sheet_row(self) -> list:
        """Convierte la sesión a fila de Google Sheets (10 columnas)"""
        return [
            self.id_solicitud,
            self.fecha_sesion.strftime("%Y-%m-%d") if self.fecha_sesion else "",
            self.servicio_sesion,
            self.observaciones_sesion,
            str(self.coste_sesion),
            str(self.irradiaciones_realizadas),
            str(self.dosis_suministrada),
            str(self.tiempo_dosimetria_meses),
            str(self.tiempo_usado_h),
            self.estado_servicio,
        ]
    
    @classmethod
    def from_sheet_row(cls, row: list) -> 'Sesion':
        """Crea una sesión desde una fila de Google Sheets"""
        def safe_get(index, default=""):
            return row[index] if len(row) > index and row[index] else default
        
        def safe_date(value):
            if not value:
                return datetime.now()
            try:
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        return datetime.strptime(str(value).split()[0], fmt)
                    except:
                        continue
                return datetime.now()
            except:
                return datetime.now()
        
        def safe_float(value):
            try:
                return float(value) if value else 0.0
            except:
                return 0.0
        
        return cls(
            id_solicitud=safe_get(0),
            fecha_sesion=safe_date(safe_get(1)),
            servicio_sesion=safe_get(2),
            observaciones_sesion=safe_get(3),
            coste_sesion=safe_float(safe_get(4)),
            irradiaciones_realizadas=safe_float(safe_get(5)),
            dosis_suministrada=safe_float(safe_get(6)),
            tiempo_dosimetria_meses=safe_float(safe_get(7)),
            tiempo_usado_h=safe_float(safe_get(8)),
            estado_servicio=safe_get(9, "🕓 En progreso"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la sesión a diccionario"""
        return {
            'id_solicitud': self.id_solicitud,
            'fecha_sesion': self.fecha_sesion.isoformat() if self.fecha_sesion else None,
            'servicio_sesion': self.servicio_sesion,
            'observaciones_sesion': self.observaciones_sesion,
            'coste_sesion': self.coste_sesion,
            'irradiaciones_realizadas': self.irradiaciones_realizadas,
            'dosis_suministrada': self.dosis_suministrada,
            'tiempo_dosimetria_meses': self.tiempo_dosimetria_meses,
            'tiempo_usado_h': self.tiempo_usado_h,
            'estado_servicio': self.estado_servicio,
        }
    
    def validar(self) -> tuple[bool, str]:
        """
        Valida que la sesión tenga los datos mínimos necesarios.
        
        Returns:
            tuple: (es_valida, mensaje_error)
        """
        if not self.id_solicitud:
            return False, "Debe estar asociada a una solicitud"
        
        if not self.fecha_sesion:
            return False, "La fecha de sesión es obligatoria"
        
        if not self.servicio_sesion:
            return False, "Debe especificar el tipo de servicio"
        
        if self.coste_sesion < 0:
            return False, "El coste no puede ser negativo"
        
        return True, ""
    
    def __str__(self) -> str:
        return f"{self.id_solicitud} - {self.servicio_sesion} - {self.fecha_sesion.strftime('%d/%m/%Y')}"
