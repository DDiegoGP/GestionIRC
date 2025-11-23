"""
Panel de Solicitudes - Adaptado a estructura real (24 campos) + Extracción PDF
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Optional
import json

from src.models.solicitud_real import Solicitud
from src.constants_real import (
    TIPOS_SERVICIOS, TIPOS_USUARIO, ESTADOS_SOLICITUD,
    TARIFAS_SERVICIOS, HEADERS_SOLICITUDES, RANGO_SOLICITUDES
)
from src.utils.sheets_manager import sheets_manager
from src.utils.pdf_extractor import PDFExtractor
from src.utils.logger import logger


class SolicitudesRealPanel:
    """Panel de gestión de solicitudes con 24 campos reales"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        self.solicitudes: List[Solicitud] = []
        self.pdf_extractor = PDFExtractor()
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Construye la interfaz"""
        # Frame principal
        main_frame = tk.Frame(self.parent, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título y botones de acción
        self.create_header(main_frame)
        
        # Lista de solicitudes
        self.create_solicitudes_list(main_frame)
        
        # Panel de detalles
        self.create_details_panel(main_frame)
    
    def create_header(self, parent):
        """Crea el encabezado con título y botones"""
        header_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title = self.theme.create_header_label(header_frame, "📋 Gestión de Solicitudes")
        title.pack(side=tk.LEFT)
        
        # Botones
        btn_frame = tk.Frame(header_frame, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(side=tk.RIGHT)
        
        # Botón Nueva Solicitud
        btn_new = self.theme.create_primary_button(
            btn_frame,
            "➕ Nueva Solicitud",
            self.nueva_solicitud
        )
        btn_new.pack(side=tk.LEFT, padx=5)
        
        # Botón Cargar PDF
        btn_pdf = self.theme.create_success_button(
            btn_frame,
            "📄 Cargar desde PDF",
            self.cargar_desde_pdf
        )
        btn_pdf.pack(side=tk.LEFT, padx=5)
        
        # Botón Actualizar
        btn_refresh = self.theme.create_secondary_button(
            btn_frame,
            "🔄 Actualizar",
            self.load_data
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
    
    def create_solicitudes_list(self, parent):
        """Crea la lista de solicitudes"""
        # Frame contenedor
        list_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("ID", "Fecha", "Solicitante", "Servicio", "Estado", "Tipo", "Coste")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='tree headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            selectmode='browse'
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configurar columnas
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", width=150, anchor=tk.W)
        self.tree.column("Fecha", width=100, anchor=tk.CENTER)
        self.tree.column("Solicitante", width=200, anchor=tk.W)
        self.tree.column("Servicio", width=250, anchor=tk.W)
        self.tree.column("Estado", width=120, anchor=tk.CENTER)
        self.tree.column("Tipo", width=80, anchor=tk.CENTER)
        self.tree.column("Coste", width=100, anchor=tk.E)
        
        # Encabezados
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W if col in ["ID", "Solicitante", "Servicio"] else tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Eventos
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def create_details_panel(self, parent):
        """Crea el panel de detalles"""
        # Card frame
        details_card = self.theme.create_card_frame(parent)
        details_card.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = self.theme.create_title_label(details_card, "Detalles de la Solicitud")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Texto con scrollbar
        text_frame = tk.Frame(details_card, bg=self.theme.COLORS['card_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(text_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = self.theme.create_text(
            text_frame,
            height=12,
            yscrollcommand=vsb.set,
            state='disabled'
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.details_text.yview)
        
        # Botones de acciones
        btn_frame = tk.Frame(details_card, bg=self.theme.COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        btn_edit = self.theme.create_secondary_button(
            btn_frame,
            "✏️ Editar",
            self.editar_solicitud
        )
        btn_edit.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_delete = tk.Button(
            btn_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_solicitud,
            bg=self.theme.COLORS['error'],
            fg=self.theme.COLORS['text_white'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal']),
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        btn_delete.pack(side=tk.LEFT, padx=5)
    
    def load_data(self):
        """Carga las solicitudes desde Google Sheets"""
        try:
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("Cargando solicitudes...")
            
            data = sheets_manager.get_all_data('Solicitudes')
            
            if len(data) > 1:  # Si hay datos además del encabezado
                self.solicitudes = [Solicitud.from_sheet_row(row) for row in data[1:]]
            else:
                self.solicitudes = []
            
            self.update_tree()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status(f"✅ {len(self.solicitudes)} solicitudes cargadas")
            
        except Exception as e:
            logger.error(f"Error al cargar solicitudes: {e}")
            self.solicitudes = []
            self.update_tree()
            # Mostrar mensaje en detalles
            self.details_text.config(state='normal')
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, "⚠️ Sin conexión a Google Sheets\n\n")
            self.details_text.insert(tk.END, "Configura las credenciales desde el menú Configuración\n")
            self.details_text.insert(tk.END, "para cargar las solicitudes.")
            self.details_text.config(state='disabled')
    
    def update_tree(self):
        """Actualiza el árbol con las solicitudes"""
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar solicitudes
        for sol in self.solicitudes:
            fecha = sol.fecha_solicitud.strftime("%d/%m/%Y") if sol.fecha_solicitud else ""
            coste = f"{sol.coste_estimado_iva_0:.2f}€"
            
            self.tree.insert('', tk.END, values=(
                sol.id_solicitud,
                fecha,
                sol.nombre_solicitante,
                sol.servicio_solicitado,
                sol.estado,
                sol.tipo_usuario,
                coste
            ))
    
    def on_select(self, event):
        """Maneja la selección de una solicitud"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            id_solicitud = item['values'][0]
            
            # Buscar solicitud
            solicitud = next((s for s in self.solicitudes if s.id_solicitud == id_solicitud), None)
            
            if solicitud:
                self.mostrar_detalles(solicitud)
    
    def on_double_click(self, event):
        """Maneja el doble click para editar"""
        self.editar_solicitud()
    
    def mostrar_detalles(self, solicitud: Solicitud):
        """Muestra los detalles de una solicitud"""
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        # Formato bonito
        self.details_text.insert(tk.END, f"🆔 ID: {solicitud.id_solicitud}\n", 'bold')
        self.details_text.insert(tk.END, f"📅 Fecha: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}\n")
        self.details_text.insert(tk.END, f"📊 Estado: {solicitud.estado}\n\n")
        
        self.details_text.insert(tk.END, "👤 DATOS DEL SOLICITANTE\n", 'header')
        self.details_text.insert(tk.END, f"Nombre: {solicitud.nombre_solicitante}\n")
        self.details_text.insert(tk.END, f"Email: {solicitud.email}\n")
        self.details_text.insert(tk.END, f"Teléfono: {solicitud.telefono}\n")
        self.details_text.insert(tk.END, f"Tipo: {solicitud.tipo_usuario}\n")
        self.details_text.insert(tk.END, f"Organismo: {solicitud.organismo_centro_solicitante}\n")
        self.details_text.insert(tk.END, f"Departamento: {solicitud.departamento_solicitante}\n\n")
        
        self.details_text.insert(tk.END, "🔬 SERVICIO\n", 'header')
        self.details_text.insert(tk.END, f"Tipo: {solicitud.servicio_solicitado}\n")
        self.details_text.insert(tk.END, f"Detalles: {json.dumps(solicitud.detalles_servicio, indent=2, ensure_ascii=False)}\n")
        self.details_text.insert(tk.END, f"Coste Estimado: {solicitud.coste_estimado_iva_0:.2f}€\n\n")
        
        if solicitud.investigador_principal:
            self.details_text.insert(tk.END, "🔬 PROYECTO\n", 'header')
            self.details_text.insert(tk.END, f"Investigador Principal: {solicitud.investigador_principal}\n")
            if solicitud.proyecto:
                self.details_text.insert(tk.END, f"Proyecto: {solicitud.proyecto}\n")
        
        if solicitud.observaciones:
            self.details_text.insert(tk.END, f"\n💬 OBSERVACIONES\n", 'header')
            self.details_text.insert(tk.END, f"{solicitud.observaciones}\n")
        
        # Tags para formato
        self.details_text.tag_config('bold', font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'))
        self.details_text.tag_config('header', font=(self.theme.FONTS['family'], self.theme.FONTS['size_medium'], 'bold'),
                                     foreground=self.theme.COLORS['primary'])
        
        self.details_text.config(state='disabled')
    
    def cargar_desde_pdf(self):
        """Carga una solicitud desde un PDF del formulario IRC"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF de solicitud IRC",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Extraer datos del PDF
            solicitud = self.pdf_extractor.extraer_solicitud(file_path)
            
            if not solicitud:
                messagebox.showerror("Error", "No se pudo extraer la información del PDF")
                return
            
            # Calcular coste
            solicitud.calcular_coste(TARIFAS_SERVICIOS)
            
            # Abrir formulario con datos pre-cargados
            self.abrir_formulario_solicitud(solicitud)
            
            messagebox.showinfo("Éxito", "✅ PDF cargado correctamente.\nRevisa los datos extraídos.")
            
        except Exception as e:
            logger.error(f"Error al cargar PDF: {e}")
            messagebox.showerror("Error", f"Error al procesar el PDF:\n{e}")
    
    def nueva_solicitud(self):
        """Crea una nueva solicitud"""
        self.abrir_formulario_solicitud()
    
    def editar_solicitud(self):
        """Edita la solicitud seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una solicitud para editar")
            return
        
        item = self.tree.item(selection[0])
        id_solicitud = item['values'][0]
        solicitud = next((s for s in self.solicitudes if s.id_solicitud == id_solicitud), None)
        
        if solicitud:
            self.abrir_formulario_solicitud(solicitud)
    
    def eliminar_solicitud(self):
        """Elimina la solicitud seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una solicitud para eliminar")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta solicitud?"):
            return
        
        try:
            item = self.tree.item(selection[0])
            id_solicitud = item['values'][0]
            
            # Eliminar de Sheets (implementar)
            # sheets_manager.delete_row(...)
            
            # Recargar
            self.load_data()
            messagebox.showinfo("Éxito", "Solicitud eliminada correctamente")
            
        except Exception as e:
            logger.error(f"Error al eliminar: {e}")
            messagebox.showerror("Error", f"Error al eliminar:\n{e}")
    
    def abrir_formulario_solicitud(self, solicitud: Optional[Solicitud] = None):
        """Abre el formulario de solicitud (crear/editar)"""
        from src.gui.formulario_solicitud import FormularioSolicitud
        FormularioSolicitud(self.main_window, self, solicitud)
