"""
Generador de PDFs de Solicitud
Rellena automáticamente el formulario Anexo III con los datos de la solicitud
"""
import os
from typing import Optional
from datetime import datetime
from pypdf import PdfReader, PdfWriter

from src.models.solicitud_real import Solicitud

# Logger opcional
try:
    from src.utils.logger import logger
except:
    import logging
    logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generador de PDFs de solicitud"""
    
    @staticmethod
    def get_template_path() -> str:
        """Obtiene la ruta de la plantilla PDF desde la configuración"""
        try:
            from src.utils.config_manager import config_manager
            return config_manager.get_plantilla_pdf()
        except:
            # Fallback al path por defecto
            return "formularios/anexo_III_2025_V8.pdf"
    
    @staticmethod
    def generar_pdf_solicitud(solicitud: Solicitud, output_path: str, template_path: str = None) -> bool:
        """
        Genera un PDF rellenado con los datos de la solicitud
        
        Args:
            solicitud: Objeto Solicitud con los datos
            output_path: Ruta donde guardar el PDF generado
            template_path: Ruta al template PDF (opcional, usa configuración si no se especifica)
            
        Returns:
            True si se generó correctamente, False en caso de error
        """
        try:
            # Obtener ruta del template
            if template_path is None:
                template_path = PDFGenerator.get_template_path()
            
            # Verificar que existe el template
            if not os.path.exists(template_path):
                logger.error(f"No se encuentra el template PDF en: {template_path}")
                return False
            
            # Leer el template
            reader = PdfReader(template_path)
            writer = PdfWriter()
            
            # Clonar el documento completo incluyendo el formulario
            writer.clone_document_from_reader(reader)
            
            # Preparar datos para rellenar
            field_data = PDFGenerator._preparar_datos_formulario(solicitud)
            
            # Rellenar campos
            writer.update_page_form_field_values(
                writer.pages[0],
                field_data,
                auto_regenerate=False
            )
            
            # Guardar PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            logger.info(f"✅ PDF generado: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error al generar PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def _preparar_datos_formulario(solicitud: Solicitud) -> dict:
        """
        Prepara un diccionario con los datos para rellenar el formulario
        
        Args:
            solicitud: Objeto Solicitud
            
        Returns:
            Diccionario con nombres de campos y valores
        """
        # Mapeo de campos del formulario PDF
        datos = {}
        
        # --- DATOS DEL SOLICITANTE ---
        datos["SOLICITUD DE SERVICIO Nº"] = solicitud.id_solicitud
        datos["NOMBRE Y APELLIDOS"] = solicitud.nombre_solicitante
        datos["ORGANISMO / CENTRO"] = solicitud.organismo_centro_solicitante
        datos["DEPARTAMENTO"] = solicitud.departamento_solicitante
        datos["TELÉFONO"] = solicitud.telefono
        datos["E-MAIL*"] = solicitud.email
        
        # --- DATOS DE FACTURACIÓN ---
        datos["INVESTIGADOR PRINCIPAL"] = solicitud.investigador_principal or solicitud.nombre_solicitante
        datos["ORGANISMO / CENTRO_1"] = solicitud.organismo_centro_facturacion or solicitud.organismo_centro_solicitante
        datos["DEPARTAMENTO_1"] = solicitud.departamento_facturacion or solicitud.departamento_solicitante
        datos["PROYECTO"] = solicitud.proyecto
        datos["CENTRO GESTOR"] = solicitud.centro_gestor
        datos["OFICINA CONTABLE"] = solicitud.oficina_contable
        datos["Nº CONTABILIDAD"] = solicitud.numero_contabilidad
        # UNIDAD CONTABLE no existe en el modelo, usar organo_gestor
        datos["UNIDAD CONTABLE"] = solicitud.organo_gestor
        datos["DOMICILIO FISCAL"] = solicitud.domicilio_fiscal
        datos["DOMICILIO POSTAL"] = solicitud.domicilio_postal
        datos["CIF"] = solicitud.cif
        
        # --- TIPO DE USUARIO ---
        # Los radio buttons en PDF se manejan diferente
        # El campo "USUARIO" puede tener valores específicos según el botón seleccionado
        if solicitud.tipo_usuario == "UCM":
            datos["USUARIO"] = "UCM"  # Valor para el botón UCM
        elif solicitud.tipo_usuario == "OPI":
            datos["USUARIO"] = "OPI"  # Valor para el botón OPI
        else:
            datos["USUARIO"] = "EMPRESA"  # Valor para el botón EMPRESA
        
        # --- SERVICIO SOLICITADO ---
        datos["SERVICIO"] = solicitud.servicio_solicitado
        
        # --- EQUIPO ---
        # Determinar qué equipo según el servicio
        if "Irradiación" in solicitud.servicio_solicitado:
            datos["EQUIPO"] = "IRRADIADOR"
        elif "contador gamma" in solicitud.servicio_solicitado.lower():
            datos["EQUIPO"] = "CONTADOR GAMMA"
        elif "contador beta" in solicitud.servicio_solicitado.lower():
            datos["EQUIPO"] = "CONTADOR BETA"
        
        # --- DETALLES DEL SERVICIO ---
        detalles = solicitud.detalles_servicio
        
        # Tipo de muestra
        if "tipo_muestra" in detalles:
            datos["TIPO DE MUESTRA"] = detalles["tipo_muestra"]
        
        # Número de muestras
        if "numero_muestras" in detalles:
            datos["Nº DE MUESTRAS"] = str(detalles["numero_muestras"])
        
        # Devolución de muestra
        if "devolucion_muestra" in detalles:
            datos["DEVOLUCION"] = "SI" if detalles["devolucion_muestra"] else "NO"
        else:
            datos["DEVOLUCION"] = "NO"
        
        # Dosis suministrada
        if "dosis_total_gy" in detalles:
            datos["DOSIS PORIRRADIACIÓN"] = str(detalles.get("dosis_por_irradiacion", detalles["dosis_total_gy"]))
            datos["NÚMERO DE IRRADIACIONES"] = str(detalles.get("numero_irradiaciones", 1))
        
        # Observaciones
        if solicitud.observaciones:
            datos["OBSERVACIONES"] = solicitud.observaciones
        
        # --- COSTE ---
        # Primera línea de coste
        datos["PRECIO UNITARIO"] = f"{solicitud.coste_estimado_iva_0:.2f}"
        datos["UNIDAD/TIEMPO"] = "servicio"
        datos["COSTE TOTAL"] = f"{solicitud.coste_estimado_iva_0:.2f}€"
        
        # Total
        datos["TOTAL"] = f"{solicitud.coste_estimado_iva_0:.2f}€"
        
        # --- FECHA ---
        if solicitud.fecha_solicitud:
            fecha_str = solicitud.fecha_solicitud.strftime("%d-%m-%Y")
            datos["Fecha1_af_date"] = fecha_str
            datos["Fecha3_af_date"] = fecha_str  # Fecha de hoy para el formulario
        
        return datos
    
    @staticmethod
    def generar_nombre_archivo(solicitud: Solicitud) -> str:
        """
        Genera un nombre de archivo estándar para el PDF
        
        Args:
            solicitud: Objeto Solicitud
            
        Returns:
            Nombre de archivo (ej: "IRC-Sol-1131722.pdf")
        """
        return f"{solicitud.id_solicitud}.pdf"
    
    @staticmethod
    def generar_pdf_en_carpeta(solicitud: Solicitud, carpeta_salida: str) -> Optional[str]:
        """
        Genera el PDF en una carpeta específica con nombre automático
        
        Args:
            solicitud: Objeto Solicitud
            carpeta_salida: Carpeta donde guardar el PDF
            
        Returns:
            Ruta completa del PDF generado, o None si hubo error
        """
        try:
            # Crear carpeta si no existe
            os.makedirs(carpeta_salida, exist_ok=True)
            
            # Generar nombre de archivo
            nombre_archivo = PDFGenerator.generar_nombre_archivo(solicitud)
            ruta_completa = os.path.join(carpeta_salida, nombre_archivo)
            
            # Generar PDF
            if PDFGenerator.generar_pdf_solicitud(solicitud, ruta_completa):
                return ruta_completa
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error al generar PDF en carpeta: {e}")
            return None


# Función de conveniencia
def generar_pdf_solicitud(solicitud: Solicitud, output_path: str) -> bool:
    """
    Función de conveniencia para generar un PDF de solicitud
    
    Args:
        solicitud: Objeto Solicitud con los datos
        output_path: Ruta donde guardar el PDF
        
    Returns:
        True si se generó correctamente, False en caso de error
    """
    return PDFGenerator.generar_pdf_solicitud(solicitud, output_path)
