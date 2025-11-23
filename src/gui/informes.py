"""
Panel de Informes y Exportación
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd

from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger
from config import EXPORTS_DIR


class InformesPanel:
    """Panel de generación de informes"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz"""
        frame = ttk.Frame(self.parent, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="📊 Generación de Informes", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        # Tipos de informes
        informes_frame = ttk.LabelFrame(frame, text="Tipo de Informe", padding=15)
        informes_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(informes_frame, text="📊 Resumen General",
                  command=lambda: self.generar_informe('general')).pack(fill=tk.X, pady=5)
        
        ttk.Button(informes_frame, text="💰 Informe de Facturación",
                  command=lambda: self.generar_informe('facturacion')).pack(fill=tk.X, pady=5)
        
        ttk.Button(informes_frame, text="📈 Análisis por Servicio",
                  command=lambda: self.generar_informe('servicios')).pack(fill=tk.X, pady=5)
        
        ttk.Button(informes_frame, text="📅 Informe Mensual",
                  command=lambda: self.generar_informe('mensual')).pack(fill=tk.X, pady=5)
        
        # Exportación
        export_frame = ttk.LabelFrame(frame, text="Exportación", padding=15)
        export_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(export_frame, text="📥 Exportar a Excel",
                  command=self.exportar_excel).pack(fill=tk.X, pady=5)
        
        ttk.Button(export_frame, text="📄 Exportar a PDF",
                  command=self.exportar_pdf).pack(fill=tk.X, pady=5)
        
        # Vista previa
        preview_frame = ttk.LabelFrame(frame, text="Vista Previa", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD)
        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical",
                                      command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def generar_informe(self, tipo):
        """Genera un informe según el tipo"""
        self.preview_text.delete(1.0, tk.END)
        
        try:
            if tipo == 'general':
                self.informe_general()
            elif tipo == 'facturacion':
                self.informe_facturacion()
            elif tipo == 'servicios':
                self.informe_servicios()
            elif tipo == 'mensual':
                self.informe_mensual()
        except Exception as e:
            logger.error(f"Error al generar informe: {e}")
            messagebox.showerror("Error", f"Error al generar informe: {e}")
    
    def informe_general(self):
        """Genera informe general"""
        data = sheets_manager.get_all_data('Solicitudes')
        
        total = len(data) - 1
        
        self.preview_text.insert(tk.END, f"""
╔══════════════════════════════════════════════════════════╗
║              INFORME GENERAL - IRC UCM                    ║
║══════════════════════════════════════════════════════════║
║  Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}                           ║
╚══════════════════════════════════════════════════════════╝

RESUMEN GENERAL:
─────────────────────────────────────────────────────────

📊 Total de Solicitudes: {total}

🔄 Estados:
   • Pendientes: {self._contar_por_estado(data, 'Pendiente')}
   • En Proceso: {self._contar_por_estado(data, 'En Proceso')}
   • Completadas: {self._contar_por_estado(data, 'Completada')}

💰 Facturación:
   • Total Calculado: {self._calcular_total_facturacion(data):.2f} €
   • Pendiente de Facturar: {self._calcular_pendiente(data):.2f} €

        """)
    
    def informe_facturacion(self):
        """Genera informe de facturación"""
        self.preview_text.insert(tk.END, "Generando informe de facturación...\n")
    
    def informe_servicios(self):
        """Genera informe por servicios"""
        self.preview_text.insert(tk.END, "Generando análisis por servicio...\n")
    
    def informe_mensual(self):
        """Genera informe mensual"""
        self.preview_text.insert(tk.END, "Generando informe mensual...\n")
    
    def _contar_por_estado(self, data, estado):
        """Cuenta solicitudes por estado"""
        count = 0
        for row in data[1:]:
            if len(row) > 16 and row[16] == estado:
                count += 1
        return count
    
    def _calcular_total_facturacion(self, data):
        """Calcula la facturación total"""
        total = 0
        for row in data[1:]:
            if len(row) > 18:
                try:
                    total += float(row[18]) if row[18] else 0
                except:
                    pass
        return total
    
    def _calcular_pendiente(self, data):
        """Calcula la facturación pendiente"""
        pendiente = 0
        for row in data[1:]:
            if len(row) > 20:
                facturada = row[20].lower() if row[20] else ""
                if facturada not in ["sí", "si", "yes"]:
                    try:
                        pendiente += float(row[18]) if len(row) > 18 and row[18] else 0
                    except:
                        pass
        return pendiente
    
    def exportar_excel(self):
        """Exporta los datos a Excel"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialdir=EXPORTS_DIR
        )
        
        if filename:
            try:
                # Leer datos
                solicitudes = sheets_manager.get_all_data('Solicitudes')
                sesiones = sheets_manager.get_all_data('Sesiones')
                
                # Crear Excel con múltiples hojas
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    if solicitudes:
                        df_sol = pd.DataFrame(solicitudes[1:], columns=solicitudes[0])
                        df_sol.to_excel(writer, sheet_name='Solicitudes', index=False)
                    
                    if sesiones:
                        df_ses = pd.DataFrame(sesiones[1:], columns=sesiones[0])
                        df_ses.to_excel(writer, sheet_name='Sesiones', index=False)
                
                messagebox.showinfo("Éxito", f"Exportado a:\n{filename}")
            except Exception as e:
                logger.error(f"Error al exportar: {e}")
                messagebox.showerror("Error", f"Error al exportar: {e}")
    
    def exportar_pdf(self):
        """Exporta el informe actual a PDF"""
        messagebox.showinfo("Info", "Exportación a PDF en desarrollo")
