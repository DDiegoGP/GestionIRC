"""
Modelo de Sesión - Vinculado a Solicitudes
Una solicitud puede tener múltiples sesiones
"""
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any
import json
import uuid


@dataclass
class Sesion:
    """Representa una sesión de servicio vinculada a una solicitud"""
    
    # === IDENTIFICACIÓN ===
    id_sesion: str = field(default_factory=lambda: f"IRC-Ses-{uuid.uuid4().hex[:7]}")
    id_solicitud: str = ""  # ID de la solicitud padre
    fecha_sesion: date = field(default_factory=date.today)
    tipo_sesion: str = "Realizada"  # Realizada, Planificada
    
    # === DATOS DE LA SESIÓN ===
    servicio: str = ""  # Copia del servicio de la solicitud
    solicitante: str = ""  # Copia del nombre para referencia rápida
    
    # === DETALLES ESPECÍFICOS POR TIPO DE SERVICIO ===
    # Para irradiación:
    canisters_procesados: int = 0  # Canisters irradiados en esta sesión
    dosis_aplicada_gy: float = 0.0  # Dosis en Gy (para servicios > 10 Gy)
    
    # Para dosimetría:
    mes_gestion: str = ""  # "2025-01" formato YYYY-MM
    dosimetros_gestionados: int = 0
    
    # Para otros servicios:
    horas_contador: float = 0.0  # Para servicios de contador
    descripcion_residuos: str = ""  # Para gestión de residuos
    
    # === OBSERVACIONES ===
    notas: str = ""
    operador: str = ""  # Quién realizó/planificó la sesión
    
    # === METADATOS ===
    creado_por: str = ""
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def to_sheet_row(self) -> list:
        """
        Convierte la sesión a una fila de Google Sheets
        
        Orden de columnas:
        1. ID Sesión
        2. ID Solicitud (vinculación)
        3. Fecha Sesión
        4. Tipo (Realizada/Planificada)
        5. Servicio
        6. Solicitante
        7. Canisters Procesados
        8. Dosis Aplicada (Gy)
        9. Mes Gestión
        10. Dosímetros Gestionados
        11. Horas Contador
        12. Descripción Residuos
        13. Notas
        14. Operador
        """
        fecha_str = self.fecha_sesion.strftime("%Y-%m-%d") if isinstance(self.fecha_sesion, date) else str(self.fecha_sesion)
        
        return [
            self.id_sesion,
            self.id_solicitud,
            fecha_str,
            self.tipo_sesion,
            self.servicio,
            self.solicitante,
            self.canisters_procesados,
            self.dosis_aplicada_gy,
            self.mes_gestion,
            self.dosimetros_gestionados,
            self.horas_contador,
            self.descripcion_residuos,
            self.notas,
            self.operador
        ]
    
    @staticmethod
    def from_sheet_row(row: list) -> 'Sesion':
        """Crea una Sesión desde una fila de Google Sheets"""
        sesion = Sesion()
        
        if len(row) > 0:
            sesion.id_sesion = str(row[0]) if row[0] else sesion.id_sesion
        if len(row) > 1:
            sesion.id_solicitud = str(row[1]) if row[1] else ""
        if len(row) > 2:
            try:
                sesion.fecha_sesion = datetime.strptime(str(row[2]), "%Y-%m-%d").date()
            except:
                sesion.fecha_sesion = date.today()
        if len(row) > 3:
            sesion.tipo_sesion = str(row[3]) if row[3] else "Realizada"
        if len(row) > 4:
            sesion.servicio = str(row[4]) if row[4] else ""
        if len(row) > 5:
            sesion.solicitante = str(row[5]) if row[5] else ""
        if len(row) > 6:
            try:
                sesion.canisters_procesados = int(row[6]) if row[6] else 0
            except:
                sesion.canisters_procesados = 0
        if len(row) > 7:
            try:
                sesion.dosis_aplicada_gy = float(row[7]) if row[7] else 0.0
            except:
                sesion.dosis_aplicada_gy = 0.0
        if len(row) > 8:
            sesion.mes_gestion = str(row[8]) if row[8] else ""
        if len(row) > 9:
            try:
                sesion.dosimetros_gestionados = int(row[9]) if row[9] else 0
            except:
                sesion.dosimetros_gestionados = 0
        if len(row) > 10:
            try:
                sesion.horas_contador = float(row[10]) if row[10] else 0.0
            except:
                sesion.horas_contador = 0.0
        if len(row) > 11:
            sesion.descripcion_residuos = str(row[11]) if row[11] else ""
        if len(row) > 12:
            sesion.notas = str(row[12]) if row[12] else ""
        if len(row) > 13:
            sesion.operador = str(row[13]) if row[13] else ""
        
        return sesion
    
    @staticmethod
    def get_sheet_headers() -> list:
        """Retorna los encabezados para la hoja de Sesiones"""
        return [
            "ID Sesión",
            "ID Solicitud",
            "Fecha Sesión",
            "Tipo",
            "Servicio",
            "Solicitante",
            "Canisters Procesados",
            "Dosis Aplicada (Gy)",
            "Mes Gestión",
            "Dosímetros Gestionados",
            "Horas Contador",
            "Descripción Residuos",
            "Notas",
            "Operador"
        ]


class SolicitudConProgreso:
    """
    Clase auxiliar para calcular el progreso de una solicitud
    basándose en sus sesiones
    """
    
    def __init__(self, solicitud, sesiones: list):
        self.solicitud = solicitud
        self.sesiones = sesiones
        self.sesiones_realizadas = [s for s in sesiones if s.tipo_sesion == "Realizada"]
        self.sesiones_planificadas = [s for s in sesiones if s.tipo_sesion == "Planificada"]
    
    def calcular_progreso(self) -> Dict[str, Any]:
        """
        Calcula el progreso según el tipo de servicio
        
        Returns:
            Dict con:
            - total_esperado: int
            - completado: int
            - pendiente: int
            - porcentaje: float
            - detalles: str
        """
        servicio = self.solicitud.servicio_solicitado.lower()
        detalles = self.solicitud.detalles_servicio
        
        # IRRADIACIÓN
        if "irradiación" in servicio or "irradiador" in servicio:
            return self._progreso_irradiacion(detalles)
        
        # DOSIMETRÍA
        elif "dosimétrica" in servicio or "dosimetri" in servicio:
            return self._progreso_dosimetria(detalles)
        
        # CONTADOR
        elif "contador" in servicio:
            return self._progreso_contador(detalles)
        
        # RESIDUOS
        elif "residuos" in servicio or "huérfanas" in servicio:
            return self._progreso_residuos()
        
        # POR DEFECTO
        else:
            return {
                'total_esperado': 1,
                'completado': len(self.sesiones_realizadas),
                'pendiente': max(0, 1 - len(self.sesiones_realizadas)),
                'porcentaje': 100.0 if self.sesiones_realizadas else 0.0,
                'detalles': f"{len(self.sesiones_realizadas)} sesión(es) realizada(s)"
            }
    
    def _progreso_irradiacion(self, detalles: dict) -> dict:
        """Progreso para irradiación - basado en canisters"""
        canisters_totales = detalles.get('canisters', 0)
        
        # Contar canisters procesados
        canisters_procesados = sum(s.canisters_procesados for s in self.sesiones_realizadas)
        canisters_pendientes = max(0, canisters_totales - canisters_procesados)
        
        porcentaje = (canisters_procesados / canisters_totales * 100) if canisters_totales > 0 else 0
        
        return {
            'total_esperado': canisters_totales,
            'completado': canisters_procesados,
            'pendiente': canisters_pendientes,
            'porcentaje': porcentaje,
            'detalles': f"{canisters_procesados}/{canisters_totales} canisters irradiados",
            'tipo': 'canisters'
        }
    
    def _progreso_dosimetria(self, detalles: dict) -> dict:
        """Progreso para dosimetría - basado en meses"""
        dosimetros = detalles.get('dosimetros', 0)
        meses_totales = detalles.get('meses', 0)
        
        # Contar meses únicos gestionados
        meses_gestionados = len(set(s.mes_gestion for s in self.sesiones_realizadas if s.mes_gestion))
        meses_pendientes = max(0, meses_totales - meses_gestionados)
        
        porcentaje = (meses_gestionados / meses_totales * 100) if meses_totales > 0 else 0
        
        return {
            'total_esperado': meses_totales,
            'completado': meses_gestionados,
            'pendiente': meses_pendientes,
            'porcentaje': porcentaje,
            'detalles': f"{meses_gestionados}/{meses_totales} meses gestionados ({dosimetros} dosímetros)",
            'tipo': 'meses'
        }
    
    def _progreso_contador(self, detalles: dict) -> dict:
        """Progreso para contadores - basado en horas"""
        horas_totales = detalles.get('horas', 0)
        
        # Sumar horas usadas
        horas_usadas = sum(s.horas_contador for s in self.sesiones_realizadas)
        horas_pendientes = max(0, horas_totales - horas_usadas)
        
        porcentaje = (horas_usadas / horas_totales * 100) if horas_totales > 0 else 0
        
        return {
            'total_esperado': horas_totales,
            'completado': horas_usadas,
            'pendiente': horas_pendientes,
            'porcentaje': porcentaje,
            'detalles': f"{horas_usadas:.1f}/{horas_totales:.1f} horas utilizadas",
            'tipo': 'horas'
        }
    
    def _progreso_residuos(self) -> dict:
        """Progreso para gestión de residuos - simple realizado/no"""
        realizado = len(self.sesiones_realizadas) > 0
        
        return {
            'total_esperado': 1,
            'completado': 1 if realizado else 0,
            'pendiente': 0 if realizado else 1,
            'porcentaje': 100.0 if realizado else 0.0,
            'detalles': "Gestión realizada" if realizado else "Pendiente",
            'tipo': 'servicio_unico'
        }
