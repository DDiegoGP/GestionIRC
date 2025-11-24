"""
Extractor de PDFs del Formulario IRC - VERSIÓN MEJORADA
Extrae datos de solicitudes desde los PDFs generados por el formulario web
"""
import pdfplumber
import re
from datetime import datetime
from typing import Dict, Any, Optional
import json

from src.models.solicitud_real import Solicitud
from src.utils.logger import logger


class PDFExtractor:
    """Extrae datos de PDFs de solicitudes IRC"""
    
    # Patrones de regex mejorados para extraer información
    PATTERNS = {
        # Identificación
        'codigo': r'C[oó]digo:\s*(IRC-Sol-\d+)',
        'hora_registro': r'Hora registro:\s*(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2})',
        
        # Datos del solicitante - MEJORADOS para manejar falta de espacios
        'nombre': r'Nombre:\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s\.]+?)(?=Apellidos:)',
        'apellidos': r'Apellidos:\s*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]+?)(?=Correo electrónico:)',
        'email': r'Correo electrónico:\s*(\S+@\S+)',
        'telefono': r'TELÉFONO:\s*(\d+)',
        'tipo_usuario': r'TIPO DE USUARIO:\s*(UCM|OPI)',
        
        # Organismo/Centro Solicitante - MEJORADO
        'organismo_solicitante': r'(?:DATOS DEL SOLICITANTE.*?)?ORGANISMO/CENTRO:\s*([^D]+?)(?=DEPARTAMENTO:)',
        'departamento_solicitante': r'(?:SOLICITANTE.*?)?DEPARTAMENTO:\s*([^T]+?)(?=TELÉFONO:)',
        
        # Datos de facturación - MEJORADOS
        'organismo_facturacion': r'DATOS DE FACTURACIÓN[^O]*ORGANISMO/CENTRO:\s*([^D]+?)(?=DEPARTAMENTO:)',
        'departamento_facturacion': r'(?:FACTURACIÓN.*?)?DEPARTAMENTO:\s*([^D]+?)(?=DIRECCIÓN:)',
        'direccion': r'DIRECCIÓN:\s*([^C]+?)(?=C\.P\.:)',
        'cp': r'C\.P\.:\s*(\d+)',
        'cif': r'CIF:\s*([A-Z0-9]+)',
        
        # Datos contables (UCM) - MEJORADOS
        'oficina_contable': r'OFICINA CONTABLE:\s*([A-Z0-9]+)',
        'organo_gestor': r'ÓRGANO GESTOR:\s*([A-Z0-9]+)',
        'unidad_tramitadora': r'UNIDAD TRAMITADORA:\s*([A-Z0-9]+)',
        
        # Proyecto - MEJORADOS
        'cargo_proyecto': r'CARGO A PROYECTO DE INVESTIGACIÓN:\s*(SI|NO)',
        'investigador_principal': r'INVESTIGADOR PRINCIPAL:\s*([^P\n]+?)(?=(?:PROYECTO|Nº CONTABILIDAD|SERVICIO SOLICITADO))',
        'proyecto': r'PROYECTO/PEP:\s*([^N\n]+?)(?=(?:Nº CONTABILIDAD|SERVICIO))',
        'numero_contabilidad': r'Nº CONTABILIDAD:\s*([^\n]+?)(?=(?:SERVICIO|$))',
        
        # Servicio
        'servicio': r'Servicio que solicita:\s*([^\n]+)',
        'observaciones': r'OBSERVACIONES:\s*([^M]+?)(?=Madrid)',
        
        # Campos específicos de servicios
        'canister_menor_10': r'Número de canister \(< 10 Gy\):\s*(\d+)',
        'canister_mayor_10': r'Número de canister \(> 10 Gy\):\s*(\d+)',
        'dosis_canister': r'Dosis por canister \(> 10 Gy\):\s*(\d+)',
        'dosimetros': r'Número de dosímetros:\s*(\d+)',
        'tiempo_meses': r'Tiempo de uso \(meses\):\s*(\d+)',
        'tiempo_horas': r'Tiempo de uso \(h\):\s*(\d+)',
    }
    
    def __init__(self):
        pass
    
    def extraer_solicitud(self, pdf_path: str) -> Optional[Solicitud]:
        """
        Extrae una solicitud completa desde un PDF del formulario IRC.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Solicitud: Objeto Solicitud con todos los datos extraídos
        """
        try:
            logger.info(f"📄 Extrayendo datos del PDF: {pdf_path}")
            
            with pdfplumber.open(pdf_path) as pdf:
                # Extraer texto de la primera página
                page = pdf.pages[0]
                text = page.extract_text()
                
                if not text:
                    raise ValueError("No se pudo extraer texto del PDF")
                
                logger.debug("✅ Texto extraído del PDF correctamente")
                
                # Extraer todos los campos
                datos = self._extraer_campos(text)
                
                # Crear objeto Solicitud
                solicitud = self._crear_solicitud(datos)
                
                logger.info(f"✅ Solicitud extraída: {solicitud.id_solicitud}")
                return solicitud
                
        except Exception as e:
            logger.error(f"❌ Error al extraer PDF: {e}", exc_info=True)
            return None
    
    def _extraer_campos(self, text: str) -> Dict[str, Any]:
        """Extrae todos los campos del texto del PDF"""
        datos = {}
        
        # Extraer cada campo usando los patrones
        for key, pattern in self.PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                valor = match.group(1).strip()
                datos[key] = valor
                logger.debug(f"✓ {key}: '{valor}'")
            else:
                logger.debug(f"✗ {key}: No encontrado")
        
        return datos
    
    def _crear_solicitud(self, datos: Dict[str, Any]) -> Solicitud:
        """Crea un objeto Solicitud desde los datos extraídos"""
        
        # Crear solicitud base
        solicitud = Solicitud()
        
        # === IDENTIFICACIÓN ===
        if 'codigo' in datos:
            solicitud.id_solicitud = datos['codigo']
            logger.info(f"ID extraído: {solicitud.id_solicitud}")
        
        # FECHA - Intentar múltiples formatos
        if 'hora_registro' in datos:
            fecha_str = datos['hora_registro']
            formatos = [
                "%d-%m-%Y %H:%M",
                "%d/%m/%Y %H:%M",
                "%Y-%m-%d %H:%M",
                "%d-%m-%Y",
                "%d/%m/%Y"
            ]
            
            fecha_parseada = False
            for formato in formatos:
                try:
                    solicitud.fecha_solicitud = datetime.strptime(fecha_str, formato)
                    fecha_parseada = True
                    logger.info(f"✅ Fecha parseada: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}")
                    break
                except:
                    continue
            
            if not fecha_parseada:
                logger.warning(f"⚠️ No se pudo parsear la fecha '{fecha_str}', usando fecha actual")
                solicitud.fecha_solicitud = datetime.now()
        else:
            logger.warning("⚠️ No se encontró fecha en el PDF, usando fecha actual")
            solicitud.fecha_solicitud = datetime.now()
        
        # === DATOS DEL SOLICITANTE ===
        nombre = datos.get('nombre', '').strip()
        apellidos = datos.get('apellidos', '').strip()
        
        if nombre and apellidos:
            solicitud.nombre_solicitante = f"{nombre} {apellidos}"
        elif nombre:
            solicitud.nombre_solicitante = nombre
        else:
            solicitud.nombre_solicitante = ""
            logger.warning("⚠️ No se pudo extraer el nombre del solicitante")
        
        solicitud.email = datos.get('email', '').strip()
        solicitud.telefono = datos.get('telefono', '').strip()
        solicitud.tipo_usuario = datos.get('tipo_usuario', 'UCM').strip()
        
        # Organismo/Centro y Departamento Solicitante
        solicitud.organismo_centro_solicitante = datos.get('organismo_solicitante', '').strip()
        solicitud.departamento_solicitante = datos.get('departamento_solicitante', '').strip()
        
        # === DATOS DE FACTURACIÓN ===
        solicitud.organismo_centro_facturacion = datos.get('organismo_facturacion', 
                                                           solicitud.organismo_centro_solicitante).strip()
        solicitud.departamento_facturacion = datos.get('departamento_facturacion',
                                                       solicitud.departamento_solicitante).strip()
        
        # Dirección fiscal
        if 'direccion' in datos:
            solicitud.domicilio_fiscal = datos['direccion'].strip()
        if 'cp' in datos:
            solicitud.domicilio_postal = datos['cp'].strip()
        
        solicitud.cif = datos.get('cif', '').strip()
        
        # Datos contables (UCM)
        solicitud.oficina_contable = datos.get('oficina_contable', '').strip()
        solicitud.organo_gestor = datos.get('organo_gestor', '').strip()
        solicitud.centro_gestor = datos.get('unidad_tramitadora', '').strip()
        
        # Proyecto
        solicitud.investigador_principal = datos.get('investigador_principal', '').strip()
        solicitud.proyecto = datos.get('proyecto', '').strip()
        solicitud.numero_contabilidad = datos.get('numero_contabilidad', '').strip()
        
        # === SERVICIO ===
        servicio = datos.get('servicio', '').strip()
        solicitud.servicio_solicitado = servicio
        
        # Extraer detalles específicos del servicio
        solicitud.detalles_servicio = self._extraer_detalles_servicio(servicio, datos)
        
        # Observaciones
        solicitud.observaciones = datos.get('observaciones', '').strip()
        
        # Estado inicial
        solicitud.estado = "Pendiente"
        
        logger.info(f"📋 Solicitud creada: {solicitud.nombre_solicitante} - {solicitud.servicio_solicitado}")
        
        return solicitud
    
    def _extraer_detalles_servicio(self, servicio: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae los detalles específicos del servicio y los convierte en diccionario JSON.
        
        Args:
            servicio: Tipo de servicio solicitado
            datos: Diccionario con todos los datos extraídos
            
        Returns:
            Dict con los detalles específicos del servicio
        """
        detalles = {}
        
        # Irradiación < 10 Gy
        if "menores de 10 Gy" in servicio or "< 10 Gy" in servicio:
            if 'canister_menor_10' in datos:
                detalles['canisters'] = int(datos['canister_menor_10'])
                detalles['irradiaciones'] = 1  # Por defecto
                logger.debug(f"Canisters < 10 Gy: {detalles['canisters']}")
        
        # Irradiación > 10 Gy
        elif "mayores de 10 Gy" in servicio or "> 10 Gy" in servicio:
            if 'canister_mayor_10' in datos:
                detalles['canisters'] = int(datos['canister_mayor_10'])
                logger.debug(f"Canisters > 10 Gy: {detalles['canisters']}")
            if 'dosis_canister' in datos:
                detalles['dosis_por_canister_Gy'] = float(datos['dosis_canister'])
                logger.debug(f"Dosis por canister: {detalles['dosis_por_canister_Gy']} Gy")
            detalles['irradiaciones'] = 1  # Por defecto
        
        # Gestión dosimétrica
        elif "dosimétrica" in servicio.lower():
            if 'dosimetros' in datos:
                detalles['dosimetros'] = int(datos['dosimetros'])
                logger.debug(f"Dosímetros: {detalles['dosimetros']}")
            if 'tiempo_meses' in datos:
                detalles['meses'] = int(datos['tiempo_meses'])
                logger.debug(f"Meses: {detalles['meses']}")
        
        # Contador (Gamma o microBeta)
        elif "Contador" in servicio:
            if 'tiempo_horas' in datos:
                detalles['horas'] = float(datos['tiempo_horas'])
                logger.debug(f"Horas: {detalles['horas']}")
        
        return detalles
    
    def extraer_y_mostrar(self, pdf_path: str) -> None:
        """Extrae y muestra los datos de un PDF (para debugging)"""
        logger.info(f"\n{'='*80}")
        logger.info(f"Extrayendo PDF: {pdf_path}")
        logger.info(f"{'='*80}\n")
        
        solicitud = self.extraer_solicitud(pdf_path)
        
        if solicitud:
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ Solicitud extraída correctamente")
            logger.info(f"{'='*80}")
            logger.info(f"ID: {solicitud.id_solicitud}")
            logger.info(f"Fecha: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}")
            logger.info(f"Solicitante: {solicitud.nombre_solicitante}")
            logger.info(f"Email: {solicitud.email}")
            logger.info(f"Teléfono: {solicitud.telefono}")
            logger.info(f"Tipo Usuario: {solicitud.tipo_usuario}")
            logger.info(f"Organismo: {solicitud.organismo_centro_solicitante}")
            logger.info(f"Departamento: {solicitud.departamento_solicitante}")
            logger.info(f"Servicio: {solicitud.servicio_solicitado}")
            logger.info(f"Detalles Servicio: {json.dumps(solicitud.detalles_servicio, indent=2, ensure_ascii=False)}")
            logger.info(f"Investigador: {solicitud.investigador_principal}")
            logger.info(f"Proyecto: {solicitud.proyecto}")
            if solicitud.observaciones:
                logger.info(f"Observaciones: {solicitud.observaciones}")
            logger.info(f"{'='*80}\n")
        else:
            logger.error("❌ No se pudo extraer la solicitud")


# Función auxiliar para uso directo
def extraer_pdf(pdf_path: str) -> Optional[Solicitud]:
    """
    Función auxiliar para extraer una solicitud desde un PDF.
    
    Args:
        pdf_path: Ruta al archivo PDF
        
    Returns:
        Solicitud o None si hay error
    """
    extractor = PDFExtractor()
    return extractor.extraer_solicitud(pdf_path)


# Para testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = PDFExtractor()
        extractor.extraer_y_mostrar(pdf_path)
    else:
        print("Uso: python pdf_extractor.py <ruta_al_pdf>")
