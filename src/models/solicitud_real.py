"""
Modelo de Solicitud de Servicio IRC - Adaptado a estructura real
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json
import uuid


@dataclass
class Solicitud:
    """Representa una solicitud de servicio IRC con estructura real del Google Sheets"""
    
    # === IDENTIFICACIÓN ===
    id_solicitud: str = field(default_factory=lambda: f"IRC-Sol-{uuid.uuid4().hex[:7]}")
    fecha_solicitud: datetime = field(default_factory=datetime.now)
    estado: str = "⏳ Pendiente"  # ⏳ Pendiente, 🕓 En progreso, ✅ Completado, ❌ Cancelado
    
    # === SERVICIO ===
    servicio_solicitado: str = ""
    coste_estimado_iva_0: float = 0.0
    detalles_servicio: Dict[str, Any] = field(default_factory=dict)  # JSON con detalles específicos
    
    # === DATOS DEL SOLICITANTE ===
    nombre_solicitante: str = ""
    email: str = ""
    telefono: str = ""
    organismo_centro_solicitante: str = ""
    departamento_solicitante: str = ""
    investigador_principal: str = ""
    tipo_usuario: str = "UCM"  # UCM o OPI
    
    # === DATOS DE FACTURACIÓN ===
    organismo_centro_facturacion: str = ""
    departamento_facturacion: str = ""
    cif: str = ""
    domicilio_fiscal: str = ""
    domicilio_postal: str = ""
    oficina_contable: str = ""
    organo_gestor: str = ""
    centro_gestor: str = ""  # Unidad Tramitadora
    proyecto: str = ""
    numero_contabilidad: str = ""
    
    # === OTROS ===
    observaciones: str = ""
    
    # === METADATOS (no en sheets) ===
    creado_por: str = ""
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def calcular_coste(self, tarifas: Dict[str, Any]) -> float:
        """
        Calcula el coste de la solicitud según las tarifas 2025.
        
        Args:
            tarifas: Diccionario con las tarifas de servicios
            
        Returns:
            float: Coste calculado
        """
        # Mapeo de nombres de servicio a claves de tarifa
        servicio_map = {
            "Irradiación a dosis menores de 10 Gy": "Irradiación < 10 Gy",
            "Irradiación a dosis mayores de 10 Gy": "Irradiación > 10 Gy",
            "Gestión dosimétrica": "Gestión dosimétrica",
            "Gestión/retirada de residuos radiactivos/fuentes huerfanas": "Gestión/retirada de residuos",
            "Contador Gamma < 1h": "Contador Gamma < 1h",
            "Contador Gamma > 1h": "Contador Gamma > 1h",
            "Contador microBeta < 1h": "Contador microBeta < 1h",
            "Contador microBeta > 1h": "Contador microBeta > 1h",
        }
        
        servicio_key = servicio_map.get(self.servicio_solicitado, self.servicio_solicitado)
        
        if servicio_key not in tarifas:
            return 0.0
        
        tarifa = tarifas[servicio_key].get(self.tipo_usuario, 0)
        
        # Tarifas simples (precio fijo)
        if isinstance(tarifa, (int, float)):
            # Para irradiación < 10 Gy, multiplicar por número de canisters
            if "< 10 Gy" in servicio_key:
                canisters = self.detalles_servicio.get('canisters', 1)
                self.coste_estimado_iva_0 = tarifa * canisters
            else:
                self.coste_estimado_iva_0 = tarifa
            return self.coste_estimado_iva_0
        
        # Tarifas complejas (con base + extra)
        if isinstance(tarifa, dict):
            coste = tarifa.get('base', 0)
            
            # Irradiación > 10 Gy
            if 'extra_por_gy' in tarifa:
                canisters = self.detalles_servicio.get('canisters', 1)
                dosis_por_canister = self.detalles_servicio.get('dosis_por_canister_Gy', 0)
                
                # Calcular irradiaciones (cada canister puede tener múltiples irradiaciones)
                irradiaciones = self.detalles_servicio.get('irradiaciones', 1)
                
                # Coste base por canister
                coste_base = coste * canisters * irradiaciones
                
                # Coste extra por dosis > 10 Gy
                if dosis_por_canister > 10:
                    extra_gy = dosis_por_canister - 10
                    coste_extra = extra_gy * tarifa['extra_por_gy'] * canisters * irradiaciones
                    coste = coste_base + coste_extra
                else:
                    coste = coste_base
            
            # Contadores > 1h
            elif 'extra_hora' in tarifa:
                horas = self.detalles_servicio.get('horas', 1)
                if horas > 1:
                    extra_horas = horas - 1
                    coste += extra_horas * tarifa['extra_hora']
            
            # Gestión dosimétrica
            elif servicio_key == "Gestión dosimétrica":
                dosimetros = self.detalles_servicio.get('dosimetros', 1)
                meses = self.detalles_servicio.get('meses', 1)
                coste = tarifa * dosimetros * meses
            
            self.coste_estimado_iva_0 = round(coste, 2)
            return self.coste_estimado_iva_0
        
        return 0.0
    
    def to_sheet_row(self) -> list:
        """Convierte la solicitud a fila de Google Sheets (24 columnas)"""
        return [
            self.id_solicitud,
            self.fecha_solicitud.strftime("%Y-%m-%d") if self.fecha_solicitud else "",
            self.estado,
            self.servicio_solicitado,
            str(self.coste_estimado_iva_0),
            json.dumps(self.detalles_servicio, ensure_ascii=False),  # JSON como string
            self.nombre_solicitante,
            self.email,
            self.telefono,
            self.organismo_centro_solicitante,
            self.departamento_solicitante,
            self.investigador_principal,
            self.tipo_usuario,
            self.organismo_centro_facturacion,
            self.departamento_facturacion,
            self.cif,
            self.domicilio_fiscal,
            self.domicilio_postal,
            self.oficina_contable,
            self.organo_gestor,
            self.centro_gestor,
            self.proyecto,
            self.numero_contabilidad,
            self.observaciones,
        ]
    
    @classmethod
    def from_sheet_row(cls, row: list) -> 'Solicitud':
        """Crea una solicitud desde una fila de Google Sheets"""
        def safe_get(index, default=""):
            return row[index] if len(row) > index and row[index] else default
        
        def safe_date(value):
            if not value:
                return None
            try:
                # Intentar varios formatos
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                    try:
                        return datetime.strptime(str(value).split()[0], fmt)
                    except:
                        continue
                return None
            except:
                return None
        
        def safe_float(value):
            try:
                return float(value) if value else 0.0
            except:
                return 0.0
        
        def safe_json(value):
            if not value:
                return {}
            try:
                if isinstance(value, dict):
                    return value
                return json.loads(value)
            except:
                return {}
        
        return cls(
            id_solicitud=safe_get(0),
            fecha_solicitud=safe_date(safe_get(1)) or datetime.now(),
            estado=safe_get(2, "⏳ Pendiente"),
            servicio_solicitado=safe_get(3),
            coste_estimado_iva_0=safe_float(safe_get(4)),
            detalles_servicio=safe_json(safe_get(5)),
            nombre_solicitante=safe_get(6),
            email=safe_get(7),
            telefono=safe_get(8),
            organismo_centro_solicitante=safe_get(9),
            departamento_solicitante=safe_get(10),
            investigador_principal=safe_get(11),
            tipo_usuario=safe_get(12, "UCM"),
            organismo_centro_facturacion=safe_get(13),
            departamento_facturacion=safe_get(14),
            cif=safe_get(15),
            domicilio_fiscal=safe_get(16),
            domicilio_postal=safe_get(17),
            oficina_contable=safe_get(18),
            organo_gestor=safe_get(19),
            centro_gestor=safe_get(20),
            proyecto=safe_get(21),
            numero_contabilidad=safe_get(22),
            observaciones=safe_get(23),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la solicitud a diccionario"""
        return {
            'id_solicitud': self.id_solicitud,
            'fecha_solicitud': self.fecha_solicitud.isoformat() if self.fecha_solicitud else None,
            'estado': self.estado,
            'servicio_solicitado': self.servicio_solicitado,
            'coste_estimado_iva_0': self.coste_estimado_iva_0,
            'detalles_servicio': self.detalles_servicio,
            'nombre_solicitante': self.nombre_solicitante,
            'email': self.email,
            'telefono': self.telefono,
            'organismo_centro_solicitante': self.organismo_centro_solicitante,
            'departamento_solicitante': self.departamento_solicitante,
            'investigador_principal': self.investigador_principal,
            'tipo_usuario': self.tipo_usuario,
            'organismo_centro_facturacion': self.organismo_centro_facturacion,
            'departamento_facturacion': self.departamento_facturacion,
            'cif': self.cif,
            'domicilio_fiscal': self.domicilio_fiscal,
            'domicilio_postal': self.domicilio_postal,
            'oficina_contable': self.oficina_contable,
            'organo_gestor': self.organo_gestor,
            'centro_gestor': self.centro_gestor,
            'proyecto': self.proyecto,
            'numero_contabilidad': self.numero_contabilidad,
            'observaciones': self.observaciones,
        }
    
    def validar(self) -> tuple[bool, str]:
        """
        Valida que la solicitud tenga los datos mínimos necesarios.
        
        Returns:
            tuple: (es_valida, mensaje_error)
        """
        if not self.nombre_solicitante:
            return False, "El nombre del solicitante es obligatorio"
        
        if not self.email:
            return False, "El email es obligatorio"
        
        if not self.servicio_solicitado:
            return False, "Debe seleccionar un tipo de servicio"
        
        if not self.tipo_usuario:
            return False, "El tipo de usuario es obligatorio"
        
        # Validaciones específicas por tipo de servicio
        if "mayor" in self.servicio_solicitado.lower() or "> 10" in self.servicio_solicitado:
            if not self.detalles_servicio.get('canisters'):
                return False, "Debe especificar el número de canisters"
            if not self.detalles_servicio.get('dosis_por_canister_Gy'):
                return False, "Debe especificar la dosis por canister"
        
        if "menor" in self.servicio_solicitado.lower() or "< 10" in self.servicio_solicitado:
            if not self.detalles_servicio.get('canisters'):
                return False, "Debe especificar el número de canisters"
        
        if "dosimétrica" in self.servicio_solicitado.lower():
            if not self.detalles_servicio.get('dosimetros'):
                return False, "Debe especificar el número de dosímetros"
            if not self.detalles_servicio.get('meses'):
                return False, "Debe especificar los meses"
        
        return True, ""
    
    def __str__(self) -> str:
        return f"{self.id_solicitud} - {self.nombre_solicitante} - {self.servicio_solicitado}"
