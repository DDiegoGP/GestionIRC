"""
Modelo de Solicitud de Servicio IRC
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class Solicitud:
    """Representa una solicitud de servicio IRC"""
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    numero_solicitud: Optional[str] = None
    
    # Datos del solicitante
    nombre: str = ""
    apellidos: str = ""
    email: str = ""
    telefono: str = ""
    departamento: str = ""
    
    # Tipo de usuario y servicio
    tipo_usuario: str = "UCM"  # UCM o OPI
    tipo_servicio: str = ""
    
    # Detalles del servicio
    descripcion: str = ""
    observaciones: str = ""
    
    # Parámetros específicos
    dosis_gy: Optional[float] = None  # Para irradiación > 10 Gy
    horas_uso: Optional[float] = None  # Para contadores > 1h
    
    # Fechas
    fecha_solicitud: datetime = field(default_factory=datetime.now)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    
    # Estado y seguimiento
    estado: str = "Pendiente"
    prioridad: str = "Normal"  # Baja, Normal, Alta, Urgente
    
    # Facturación
    coste_calculado: float = 0.0
    coste_final: Optional[float] = None
    facturada: bool = False
    fecha_facturacion: Optional[datetime] = None
    
    # Metadatos
    creado_por: str = ""
    modificado_por: str = ""
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_modificacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones y generaciones automáticas"""
        if not self.numero_solicitud:
            self.numero_solicitud = self._generar_numero_solicitud()
    
    def _generar_numero_solicitud(self) -> str:
        """Genera un número de solicitud único"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"IRC-{timestamp}-{self.id}"
    
    def calcular_coste(self, tarifas: Dict[str, Any]) -> float:
        """
        Calcula el coste de la solicitud según las tarifas.
        
        Args:
            tarifas: Diccionario con las tarifas de servicios
            
        Returns:
            float: Coste calculado
        """
        if self.tipo_servicio not in tarifas:
            return 0.0
        
        tarifa = tarifas[self.tipo_servicio][self.tipo_usuario]
        
        # Tarifas simples (precio fijo)
        if isinstance(tarifa, (int, float)):
            self.coste_calculado = tarifa
            return self.coste_calculado
        
        # Tarifas complejas (con base + extra)
        if isinstance(tarifa, dict):
            coste = tarifa.get('base', 0)
            
            # Irradiación > 10 Gy
            if 'extra_por_gy' in tarifa and self.dosis_gy:
                if self.dosis_gy > 10:
                    extra_gy = self.dosis_gy - 10
                    coste += extra_gy * tarifa['extra_por_gy']
            
            # Contadores > 1h
            if 'extra_hora' in tarifa and self.horas_uso:
                if self.horas_uso > 1:
                    extra_horas = self.horas_uso - 1
                    coste += extra_horas * tarifa['extra_hora']
            
            self.coste_calculado = round(coste, 2)
            return self.coste_calculado
        
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la solicitud a diccionario"""
        return {
            'id': self.id,
            'numero_solicitud': self.numero_solicitud,
            'nombre': self.nombre,
            'apellidos': self.apellidos,
            'email': self.email,
            'telefono': self.telefono,
            'departamento': self.departamento,
            'tipo_usuario': self.tipo_usuario,
            'tipo_servicio': self.tipo_servicio,
            'descripcion': self.descripcion,
            'observaciones': self.observaciones,
            'dosis_gy': self.dosis_gy,
            'horas_uso': self.horas_uso,
            'fecha_solicitud': self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'estado': self.estado,
            'prioridad': self.prioridad,
            'coste_calculado': self.coste_calculado,
            'coste_final': self.coste_final,
            'facturada': self.facturada,
            'fecha_facturacion': self.fecha_facturacion.isoformat() if self.fecha_facturacion else None,
            'creado_por': self.creado_por,
            'modificado_por': self.modificado_por,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
        }
    
    def to_sheet_row(self) -> list:
        """Convierte la solicitud a fila de Google Sheets"""
        return [
            self.id,
            self.numero_solicitud,
            self.nombre,
            self.apellidos,
            self.email,
            self.telefono,
            self.departamento,
            self.tipo_usuario,
            self.tipo_servicio,
            self.descripcion,
            self.observaciones,
            str(self.dosis_gy) if self.dosis_gy else "",
            str(self.horas_uso) if self.horas_uso else "",
            self.fecha_solicitud.strftime("%d/%m/%Y %H:%M") if self.fecha_solicitud else "",
            self.fecha_inicio.strftime("%d/%m/%Y") if self.fecha_inicio else "",
            self.fecha_fin.strftime("%d/%m/%Y") if self.fecha_fin else "",
            self.estado,
            self.prioridad,
            str(self.coste_calculado),
            str(self.coste_final) if self.coste_final else "",
            "Sí" if self.facturada else "No",
            self.fecha_facturacion.strftime("%d/%m/%Y") if self.fecha_facturacion else "",
        ]
    
    @classmethod
    def from_sheet_row(cls, row: list) -> 'Solicitud':
        """Crea una solicitud desde una fila de Google Sheets"""
        def safe_get(index, default=""):
            return row[index] if len(row) > index else default
        
        def safe_float(value):
            try:
                return float(value) if value else None
            except:
                return None
        
        def safe_date(value):
            try:
                return datetime.strptime(value, "%d/%m/%Y %H:%M") if value else None
            except:
                try:
                    return datetime.strptime(value, "%d/%m/%Y") if value else None
                except:
                    return None
        
        return cls(
            id=safe_get(0),
            numero_solicitud=safe_get(1),
            nombre=safe_get(2),
            apellidos=safe_get(3),
            email=safe_get(4),
            telefono=safe_get(5),
            departamento=safe_get(6),
            tipo_usuario=safe_get(7, "UCM"),
            tipo_servicio=safe_get(8),
            descripcion=safe_get(9),
            observaciones=safe_get(10),
            dosis_gy=safe_float(safe_get(11)),
            horas_uso=safe_float(safe_get(12)),
            fecha_solicitud=safe_date(safe_get(13)),
            fecha_inicio=safe_date(safe_get(14)),
            fecha_fin=safe_date(safe_get(15)),
            estado=safe_get(16, "Pendiente"),
            prioridad=safe_get(17, "Normal"),
            coste_calculado=safe_float(safe_get(18)) or 0.0,
            coste_final=safe_float(safe_get(19)),
            facturada=safe_get(20, "No").lower() in ["sí", "si", "yes", "true"],
            fecha_facturacion=safe_date(safe_get(21)),
        )
    
    def validar(self) -> tuple[bool, str]:
        """
        Valida que la solicitud tenga los datos mínimos necesarios.
        
        Returns:
            tuple: (es_valida, mensaje_error)
        """
        if not self.nombre or not self.apellidos:
            return False, "El nombre y apellidos son obligatorios"
        
        if not self.email:
            return False, "El email es obligatorio"
        
        if not self.tipo_servicio:
            return False, "Debe seleccionar un tipo de servicio"
        
        if not self.departamento:
            return False, "El departamento es obligatorio"
        
        # Validaciones específicas por tipo de servicio
        if "Irradiación > 10 Gy" in self.tipo_servicio and not self.dosis_gy:
            return False, "Debe especificar la dosis en Gy"
        
        if "> 1h" in self.tipo_servicio and not self.horas_uso:
            return False, "Debe especificar las horas de uso"
        
        return True, ""
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo"""
        return f"{self.nombre} {self.apellidos}".strip()
    
    @property
    def dias_desde_solicitud(self) -> int:
        """Calcula los días transcurridos desde la solicitud"""
        if not self.fecha_solicitud:
            return 0
        delta = datetime.now() - self.fecha_solicitud
        return delta.days
    
    def __str__(self) -> str:
        return f"{self.numero_solicitud} - {self.nombre_completo} - {self.tipo_servicio}"
