"""
Calculador Centralizado de Estados y Progreso
Asegura que Dashboard y Sesiones usen la misma lógica
"""
from datetime import date, timedelta
from typing import List, Dict, Optional
from src.models.solicitud_real import Solicitud
from src.models.sesion import Sesion


class CalculadorEstados:
    """
    Calcula estados y progreso de forma centralizada.
    Todos los componentes (Dashboard, Sesiones) deben usar esta clase.
    """
    
    @staticmethod
    def calcular_estado_y_progreso(solicitud: Solicitud, sesiones: List[Sesion]) -> Dict:
        """
        Calcula el estado completo de una solicitud.
        
        Returns:
            {
                'estado': str,  # 'Pendiente' | 'En proceso' | 'Completado'
                'estado_original': str,  # Estado guardado en la solicitud
                'progreso_porcentaje': float,  # 0-100
                'progreso_actual': int/float,  # Valor actual (ej: 7 canisters)
                'progreso_total': int/float,  # Valor total (ej: 10 canisters)
                'progreso_texto': str,  # "7/10 canisters"
                'sesiones_realizadas': int,
                'sesiones_planificadas': int,
                'ultima_sesion': date | None,
                'proxima_sesion': date | None,
                'dias_sin_actividad': int,
                'esta_atrasado': bool,
                'necesita_atencion': bool
            }
        """
        # Filtrar sesiones
        sesiones_realizadas = [s for s in sesiones if s.tipo_sesion == "Realizada"]
        sesiones_planificadas = [s for s in sesiones if s.tipo_sesion == "Planificada"]
        
        # Fechas
        ultima_sesion = max((s.fecha_sesion for s in sesiones_realizadas), default=None)
        proxima_sesion = min((s.fecha_sesion for s in sesiones_planificadas), default=None)
        
        # Días sin actividad
        dias_sin_actividad = 0
        if ultima_sesion:
            dias_sin_actividad = (date.today() - ultima_sesion).days
        
        # Calcular progreso específico según tipo de servicio
        progreso = CalculadorEstados._calcular_progreso_especifico(solicitud, sesiones_realizadas)
        
        # Determinar estado real
        estado_calculado = CalculadorEstados._determinar_estado(
            solicitud,
            progreso['porcentaje'],
            len(sesiones_realizadas),
            len(sesiones_planificadas)
        )
        
        # Determinar si está atrasado o necesita atención
        esta_atrasado = False
        if progreso['porcentaje'] < 100 and dias_sin_actividad > 7:
            esta_atrasado = True
        
        necesita_atencion = (
            (solicitud.estado == "Pendiente" and dias_sin_actividad > 10) or
            esta_atrasado
        )
        
        return {
            'estado': estado_calculado,
            'estado_original': solicitud.estado,
            'progreso_porcentaje': progreso['porcentaje'],
            'progreso_actual': progreso['actual'],
            'progreso_total': progreso['total'],
            'progreso_texto': progreso['texto'],
            'sesiones_realizadas': len(sesiones_realizadas),
            'sesiones_planificadas': len(sesiones_planificadas),
            'ultima_sesion': ultima_sesion,
            'proxima_sesion': proxima_sesion,
            'dias_sin_actividad': dias_sin_actividad,
            'esta_atrasado': esta_atrasado,
            'necesita_atencion': necesita_atencion
        }
    
    @staticmethod
    def _calcular_progreso_especifico(solicitud: Solicitud, sesiones_realizadas: List[Sesion]) -> Dict:
        """Calcula el progreso según el tipo de servicio"""
        servicio = solicitud.servicio_solicitado.lower()
        detalles = solicitud.detalles_servicio
        
        if not isinstance(detalles, dict):
            return {
                'porcentaje': 0,
                'actual': 0,
                'total': 0,
                'texto': 'Sin detalles'
            }
        
        # IRRADIACIÓN
        if "irradiación" in servicio or "irradiador" in servicio:
            canisters_totales = detalles.get('canisters', 0)
            canisters_procesados = sum(s.canisters_procesados for s in sesiones_realizadas)
            
            porcentaje = (canisters_procesados / canisters_totales * 100) if canisters_totales > 0 else 0
            
            return {
                'porcentaje': min(porcentaje, 100),
                'actual': canisters_procesados,
                'total': canisters_totales,
                'texto': f"{canisters_procesados}/{canisters_totales} canisters"
            }
        
        # DOSIMETRÍA
        elif "dosimétrica" in servicio or "dosimetri" in servicio:
            meses_totales = detalles.get('meses', 0)
            dosimetros = detalles.get('dosimetros', 0)
            
            # Contar meses únicos gestionados
            meses_gestionados = set()
            for sesion in sesiones_realizadas:
                if sesion.mes_gestion:
                    meses_gestionados.add(sesion.mes_gestion)
            
            meses_completados = len(meses_gestionados)
            porcentaje = (meses_completados / meses_totales * 100) if meses_totales > 0 else 0
            
            return {
                'porcentaje': min(porcentaje, 100),
                'actual': meses_completados,
                'total': meses_totales,
                'texto': f"{meses_completados}/{meses_totales} meses ({dosimetros} dosímetros)"
            }
        
        # CONTADOR
        elif "contador" in servicio:
            horas_totales = detalles.get('horas', 0)
            horas_usadas = sum(s.horas_contador for s in sesiones_realizadas)
            
            porcentaje = (horas_usadas / horas_totales * 100) if horas_totales > 0 else 0
            
            return {
                'porcentaje': min(porcentaje, 100),
                'actual': horas_usadas,
                'total': horas_totales,
                'texto': f"{horas_usadas:.1f}/{horas_totales:.1f} horas"
            }
        
        # RESIDUOS
        elif "residuos" in servicio or "huérfanas" in servicio:
            # Para residuos, consideramos completado si hay al menos una sesión
            if sesiones_realizadas:
                return {
                    'porcentaje': 100,
                    'actual': 1,
                    'total': 1,
                    'texto': "Gestionado"
                }
            else:
                return {
                    'porcentaje': 0,
                    'actual': 0,
                    'total': 1,
                    'texto': "Pendiente"
                }
        
        # GENÉRICO
        else:
            # Si hay sesiones, consideramos que está en progreso
            if sesiones_realizadas:
                return {
                    'porcentaje': 50,  # Asumimos 50% si hay actividad
                    'actual': len(sesiones_realizadas),
                    'total': len(sesiones_realizadas) * 2,
                    'texto': f"{len(sesiones_realizadas)} sesión(es)"
                }
            else:
                return {
                    'porcentaje': 0,
                    'actual': 0,
                    'total': 1,
                    'texto': "Sin sesiones"
                }
    
    @staticmethod
    def _determinar_estado(solicitud: Solicitud, progreso: float, 
                      sesiones_realizadas: int, sesiones_planificadas: int) -> str:
        """
        Determina el estado de una solicitud.
    
        Lógica:
        1. Si progreso = 100% → Completado (automático)
        2. En otro caso → Usa el estado guardado en Google Sheets
    
        El cambio de Pendiente → En proceso se hace manualmente con botón "PDF Firmado"
        """
        # Si progreso = 100%, cambiar a completado automáticamente
        if progreso >= 100:
            return "Completado"
    
        # En cualquier otro caso, usar el estado guardado
        return solicitud.estado
    
    @staticmethod
    def calcular_resumen_general(solicitudes: List[Solicitud], todas_sesiones: List[Sesion]) -> Dict:
        """
        Calcula un resumen general para el dashboard.
        
        Returns:
            {
                'total_solicitudes': int,
                'pendientes': int,
                'en_proceso': int,
                'completados': int,
                'sesiones_hoy': int,
                'sesiones_semana': int,
                'atrasados': int,
                'necesitan_atencion': List[str]  # IDs de solicitudes
            }
        """
        # Agrupar sesiones por solicitud
        sesiones_por_solicitud = {}
        for sesion in todas_sesiones:
            if sesion.id_solicitud not in sesiones_por_solicitud:
                sesiones_por_solicitud[sesion.id_solicitud] = []
            sesiones_por_solicitud[sesion.id_solicitud].append(sesion)
        
        # Contadores
        total = len(solicitudes)
        pendientes = 0
        en_proceso = 0
        completados = 0
        atrasados = 0
        necesitan_atencion = []
        
        # Analizar cada solicitud
        for solicitud in solicitudes:
            sesiones = sesiones_por_solicitud.get(solicitud.id_solicitud, [])
            info = CalculadorEstados.calcular_estado_y_progreso(solicitud, sesiones)
            
            # Contar por estado
            if info['estado'] == 'Pendiente':
                pendientes += 1
            elif info['estado'] == 'En proceso':
                en_proceso += 1
            elif info['estado'] == 'Completado':
                completados += 1
            
            # Contar atrasados
            if info['esta_atrasado']:
                atrasados += 1
            
            # Necesitan atención
            if info['necesita_atencion']:
                necesitan_atencion.append(solicitud.id_solicitud)
        
        # Sesiones de hoy y esta semana
        hoy = date.today()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        
        sesiones_hoy = len([s for s in todas_sesiones if s.fecha_sesion == hoy])
        sesiones_semana = len([s for s in todas_sesiones 
                               if inicio_semana <= s.fecha_sesion <= fin_semana])
        
        return {
            'total_solicitudes': total,
            'pendientes': pendientes,
            'en_proceso': en_proceso,
            'completados': completados,
            'sesiones_hoy': sesiones_hoy,
            'sesiones_semana': sesiones_semana,
            'atrasados': atrasados,
            'necesitan_atencion': necesitan_atencion
        }
    
    @staticmethod
    def get_color_estado(estado: str) -> str:
        """Retorna el color hexadecimal para un estado"""
        colores = {
            'Pendiente': '#F44336',    # Rojo
            'En proceso': '#FF9800',   # Naranja
            'Completado': '#4CAF50'    # Verde
        }
        return colores.get(estado, '#9E9E9E')  # Gris por defecto
    
    @staticmethod
    def get_icono_estado(estado: str) -> str:
        """Retorna el emoji/icono para un estado"""
        iconos = {
            'Pendiente': '🔴',
            'En proceso': '🟡',
            'Completado': '🟢'
        }
        return iconos.get(estado, '⚪')
