"""
Extractor de PDFs del Formulario IRC
Extrae datos de solicitudes desde los PDFs generados por el formulario web
"""
import pdfplumber
import re
from datetime import datetime
from typing import Dict, Any, Optional
import json

from src.models.solicitud_real import Solicitud


class PDFExtractor:
    """Extrae datos de PDFs de solicitudes IRC"""
    
    # Patrones de regex para extraer información
    PATTERNS = {
        # Identificación
        'codigo': r'C[oó]digo:\s*(IRC-Sol-\d+)',
        'hora_registro': r'Hora registro:\s*(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2})',
        
        # Datos del solicitante
        'nombre': r'Nombre:\s*([^\s]+(?:\s+[^\s]+)?)',
        'apellidos': r'Apellidos:\s*(.+?)(?=\s+Correo electrónico:)',
        'email': r'Correo electrónico:\s*(\S+@\S+)',
        'telefono': r'TELÉFONO:\s*(\d+)',
        'tipo_usuario': r'TIPO DE USUARIO:\s*(\w+)',
        
        # Organismo/Centro Solicitante
        'organismo_solicitante': r'ORGANISMO/CENTRO:\s*(.+?)(?=\s+DEPARTAMENTO:)',
        'departamento_solicitante': r'DEPARTAMENTO:\s*(.+?)(?=\s+(?:TELÉFONO|DIRECCIÓN|Para))',
        
        # Datos de facturación
        'organismo_facturacion': r'DATOS DE FACTURACIÓN[^O]*ORGANISMO/CENTRO:\s*(.+?)(?=\s+(?:DEPARTAMENTO|DIRECCIÓN))',
        'departamento_facturacion': r'FACTURACIÓN[^D]*DEPARTAMENTO:\s*(.+?)(?=\s+(?:DIRECCIÓN|CIF|Para))',
        'direccion': r'DIRECCIÓN:\s*(.+?)(?=\s+C\.P\.:)',
        'cp': r'C\.P\.:\s*(\d+)',
        'cif': r'CIF:\s*(\S+)',
        
        # Datos contables (UCM)
        'oficina_contable': r'OFICINA CONTABLE:\s*(\S+)',
        'organo_gestor': r'ÓRGANO GESTOR:\s*(\S+)',
        'unidad_tramitadora': r'UNIDAD TRAMITADORA:\s*(\S+)',
        
        # Proyecto
        'cargo_proyecto': r'CARGO A PROYECTO DE INVESTIGACIÓN:\s*(\w+)',
        'investigador_principal': r'INVESTIGADOR PRINCIPAL:\s*(.+?)(?=\s+(?:PROYECTO|Nº|SERVICIO|$))',
        'proyecto': r'PROYECTO/PEP:\s*(.+?)(?=\s+(?:Nº|SERVICIO|$))',
        'numero_contabilidad': r'Nº CONTABILIDAD:\s*(.+?)(?=\s+(?:SERVICIO|$))',
        
        # Servicio
        'servicio': r'Servicio que solicita:\s*(.+?)(?=\n)',
        'observaciones': r'OBSERVACIONES:\s*(.+?)(?=\n(?:Madrid|$))',
        
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
            with pdfplumber.open(pdf_path) as pdf:
                # Extraer texto de la primera página
                page = pdf.pages[0]
                text = page.extract_text()
                
                if not text:
                    raise ValueError("No se pudo extraer texto del PDF")
                
                # Extraer todos los campos
                datos = self._extraer_campos(text)
                
                # Crear objeto Solicitud
                solicitud = self._crear_solicitud(datos)
                
                return solicitud
                
        except Exception as e:
            print(f"❌ Error al extraer PDF: {e}")
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
        
        return datos
    
    def _crear_solicitud(self, datos: Dict[str, Any]) -> Solicitud:
        """Crea un objeto Solicitud desde los datos extraídos"""
        
        # Crear solicitud base
        solicitud = Solicitud()
        
        # === IDENTIFICACIÓN ===
        if 'codigo' in datos:
            solicitud.id_solicitud = datos['codigo']
        
        if 'hora_registro' in datos:
            try:
                solicitud.fecha_solicitud = datetime.strptime(
                    datos['hora_registro'], 
                    "%d-%m-%Y %H:%M"
                )
            except:
                solicitud.fecha_solicitud = datetime.now()
        
        # === DATOS DEL SOLICITANTE ===
        if 'nombre' in datos and 'apellidos' in datos:
            solicitud.nombre_solicitante = f"{datos['nombre']} {datos['apellidos']}"
        elif 'nombre' in datos:
            solicitud.nombre_solicitante = datos['nombre']
        
        solicitud.email = datos.get('email', '')
        solicitud.telefono = datos.get('telefono', '')
        solicitud.tipo_usuario = datos.get('tipo_usuario', 'UCM')
        
        # Organismo/Centro y Departamento Solicitante
        solicitud.organismo_centro_solicitante = datos.get('organismo_solicitante', '')
        solicitud.departamento_solicitante = datos.get('departamento_solicitante', '')
        
        # === DATOS DE FACTURACIÓN ===
        solicitud.organismo_centro_facturacion = datos.get('organismo_facturacion', 
                                                           datos.get('organismo_solicitante', ''))
        solicitud.departamento_facturacion = datos.get('departamento_facturacion',
                                                       datos.get('departamento_solicitante', ''))
        
        # Dirección fiscal
        if 'direccion' in datos and 'cp' in datos:
            solicitud.domicilio_fiscal = f"{datos['direccion']}"
            solicitud.domicilio_postal = datos['cp']
        
        solicitud.cif = datos.get('cif', '')
        
        # Datos contables (UCM)
        solicitud.oficina_contable = datos.get('oficina_contable', '')
        solicitud.organo_gestor = datos.get('organo_gestor', '')
        solicitud.centro_gestor = datos.get('unidad_tramitadora', '')
        
        # Proyecto
        solicitud.investigador_principal = datos.get('investigador_principal', '')
        solicitud.proyecto = datos.get('proyecto', '')
        solicitud.numero_contabilidad = datos.get('numero_contabilidad', '')
        
        # === SERVICIO ===
        servicio = datos.get('servicio', '')
        solicitud.servicio_solicitado = servicio
        
        # Extraer detalles específicos del servicio
        solicitud.detalles_servicio = self._extraer_detalles_servicio(servicio, datos)
        
        # Observaciones
        solicitud.observaciones = datos.get('observaciones', '')
        
        # Estado inicial
        solicitud.estado = "Pendiente"
        
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
        
        # Irradiación > 10 Gy
        elif "mayores de 10 Gy" in servicio or "> 10 Gy" in servicio:
            if 'canister_mayor_10' in datos:
                detalles['canisters'] = int(datos['canister_mayor_10'])
            if 'dosis_canister' in datos:
                detalles['dosis_por_canister_Gy'] = float(datos['dosis_canister'])
            detalles['irradiaciones'] = 1  # Por defecto
        
        # Gestión dosimétrica
        elif "dosimétrica" in servicio.lower():
            if 'dosimetros' in datos:
                detalles['dosimetros'] = int(datos['dosimetros'])
            if 'tiempo_meses' in datos:
                detalles['meses'] = int(datos['tiempo_meses'])
        
        # Contador (Gamma o microBeta)
        elif "Contador" in servicio:
            if 'tiempo_horas' in datos:
                detalles['horas'] = float(datos['tiempo_horas'])
        
        return detalles
    
    def extraer_y_mostrar(self, pdf_path: str) -> None:
        """Extrae y muestra los datos de un PDF (para debugging)"""
        solicitud = self.extraer_solicitud(pdf_path)
        
        if solicitud:
            print(f"\n{'='*60}")
            print(f"✅ Solicitud extraída correctamente")
            print(f"{'='*60}")
            print(f"ID: {solicitud.id_solicitud}")
            print(f"Fecha: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}")
            print(f"Solicitante: {solicitud.nombre_solicitante}")
            print(f"Email: {solicitud.email}")
            print(f"Tipo Usuario: {solicitud.tipo_usuario}")
            print(f"Servicio: {solicitud.servicio_solicitado}")
            print(f"Detalles Servicio: {json.dumps(solicitud.detalles_servicio, indent=2, ensure_ascii=False)}")
            print(f"Investigador: {solicitud.investigador_principal}")
            print(f"Proyecto: {solicitud.proyecto}")
            print(f"{'='*60}\n")
        else:
            print("❌ No se pudo extraer la solicitud")


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
