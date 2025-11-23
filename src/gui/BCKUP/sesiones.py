"""
Panel de Sesiones - Adaptado a estructura real (10 campos) + Estilo Microsoft 365
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List, Optional
import json

from src.models.sesion_real import Sesion
from src.models.solicitud_real import Solicitud
from src.constants_real import (
    TIPOS_SERVICIOS, ESTADOS_SESION, HEADERS_SESIONES, RANGO_SESIONES
)
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class SesionesPanel:
    """Panel de gestión de sesiones con 10 campos reales"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        self.sesiones: List[Sesion] = []
        self.solicitudes: List[Solicitud] = []
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Construye la interfaz"""
        # Frame principal
        main_frame = tk.Frame(self.parent, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título y botones de acción
        self.create_header(main_frame)
        
        # Lista de sesiones
        self.create_sesiones_list(main_frame)
        
        # Panel de detalles
        self.create_details_panel(main_frame)
    
    def create_header(self, parent):
        """Crea el encabezado con título y botones"""
        header_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title = self.theme.create_header_label(header_frame, "🔬 Gestión de Sesiones")
        title.pack(side=tk.LEFT)
        
        # Botones
        btn_frame = tk.Frame(header_frame, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(side=tk.RIGHT)
        
        # Botón Nueva Sesión
        btn_new = self.theme.create_primary_button(
            btn_frame,
            "➕ Nueva Sesión",
            self.nueva_sesion
        )
        btn_new.pack(side=tk.LEFT, padx=5)
        
        # Botón Actualizar
        btn_refresh = self.theme.create_secondary_button(
            btn_frame,
            "🔄 Actualizar",
            self.load_data
        )
        btn_refresh.pack(side=tk.LEFT, padx=5)
    
    def create_sesiones_list(self, parent):
        """Crea la lista de sesiones"""
        # Frame contenedor
        list_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("ID Solicitud", "Fecha", "Servicio", "Estado", "Coste", 
                  "Irradiaciones", "Dosis (Gy)", "Tiempo (h)", "Meses")
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
        self.tree.column("ID Solicitud", width=150, anchor=tk.W)
        self.tree.column("Fecha", width=100, anchor=tk.CENTER)
        self.tree.column("Servicio", width=200, anchor=tk.W)
        self.tree.column("Estado", width=120, anchor=tk.CENTER)
        self.tree.column("Coste", width=80, anchor=tk.E)
        self.tree.column("Irradiaciones", width=100, anchor=tk.CENTER)
        self.tree.column("Dosis (Gy)", width=80, anchor=tk.CENTER)
        self.tree.column("Tiempo (h)", width=80, anchor=tk.CENTER)
        self.tree.column("Meses", width=60, anchor=tk.CENTER)
        
        # Encabezados
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W if col in ["ID Solicitud", "Servicio"] else tk.CENTER)
        
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
        title = self.theme.create_title_label(details_card, "Detalles de la Sesión")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Texto con scrollbar
        text_frame = tk.Frame(details_card, bg=self.theme.COLORS['card_bg'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(text_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.details_text = self.theme.create_text(
            text_frame,
            height=8,
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
            self.editar_sesion
        )
        btn_edit.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_delete = tk.Button(
            btn_frame,
            text="🗑️ Eliminar",
            command=self.eliminar_sesion,
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
        """Carga las sesiones y solicitudes desde Google Sheets"""
        try:
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("Cargando sesiones...")
            
            # Cargar sesiones
            data_ses = sheets_manager.get_all_data('Sesiones')
            if len(data_ses) > 1:
                self.sesiones = [Sesion.from_sheet_row(row) for row in data_ses[1:]]
            else:
                self.sesiones = []
            
            # Cargar solicitudes (para vincular)
            data_sol = sheets_manager.get_all_data('Solicitudes')
            if len(data_sol) > 1:
                self.solicitudes = [Solicitud.from_sheet_row(row) for row in data_sol[1:]]
            else:
                self.solicitudes = []
            
            self.update_tree()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status(f"✅ {len(self.sesiones)} sesiones cargadas")
            
        except Exception as e:
            logger.error(f"Error al cargar sesiones: {e}")
            self.sesiones = []
            self.update_tree()
    
    def update_tree(self):
        """Actualiza el árbol con las sesiones"""
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar sesiones
        for sesion in self.sesiones:
            fecha = sesion.fecha_sesion.strftime("%d/%m/%Y") if sesion.fecha_sesion else ""
            coste = f"{sesion.coste_sesion:.2f}€"
            
            self.tree.insert('', tk.END, values=(
                sesion.id_solicitud,
                fecha,
                sesion.servicio_sesion,
                sesion.estado_servicio,
                coste,
                f"{sesion.irradiaciones_realizadas:.0f}" if sesion.irradiaciones_realizadas > 0 else "-",
                f"{sesion.dosis_suministrada:.1f}" if sesion.dosis_suministrada > 0 else "-",
                f"{sesion.tiempo_usado_h:.1f}" if sesion.tiempo_usado_h > 0 else "-",
                f"{sesion.tiempo_dosimetria_meses:.0f}" if sesion.tiempo_dosimetria_meses > 0 else "-"
            ))
    
    def on_select(self, event):
        """Maneja la selección de una sesión"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            id_solicitud = item['values'][0]
            fecha_str = item['values'][1]
            
            # Buscar sesión (por ID solicitud y fecha, ya que no tiene ID único)
            for sesion in self.sesiones:
                fecha_ses = sesion.fecha_sesion.strftime("%d/%m/%Y") if sesion.fecha_sesion else ""
                if sesion.id_solicitud == id_solicitud and fecha_ses == fecha_str:
                    self.mostrar_detalles(sesion)
                    break
    
    def on_double_click(self, event):
        """Maneja el doble click para editar"""
        self.editar_sesion()
    
    def mostrar_detalles(self, sesion: Sesion):
        """Muestra los detalles de una sesión"""
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)
        
        # Buscar solicitud vinculada
        solicitud = next((s for s in self.solicitudes if s.id_solicitud == sesion.id_solicitud), None)
        
        # Formato bonito
        self.details_text.insert(tk.END, f"🔗 ID Solicitud: {sesion.id_solicitud}\n", 'bold')
        if solicitud:
            self.details_text.insert(tk.END, f"👤 Solicitante: {solicitud.nombre_solicitante}\n")
        
        self.details_text.insert(tk.END, f"📅 Fecha Sesión: {sesion.fecha_sesion.strftime('%d/%m/%Y')}\n")
        self.details_text.insert(tk.END, f"📊 Estado: {sesion.estado_servicio}\n\n")
        
        self.details_text.insert(tk.END, "🔬 SERVICIO\n", 'header')
        self.details_text.insert(tk.END, f"Tipo: {sesion.servicio_sesion}\n")
        self.details_text.insert(tk.END, f"Coste: {sesion.coste_sesion:.2f}€\n\n")
        
        self.details_text.insert(tk.END, "📊 MÉTRICAS\n", 'header')
        if sesion.irradiaciones_realizadas > 0:
            self.details_text.insert(tk.END, f"Irradiaciones: {sesion.irradiaciones_realizadas:.0f}\n")
        if sesion.dosis_suministrada > 0:
            self.details_text.insert(tk.END, f"Dosis Suministrada: {sesion.dosis_suministrada:.1f} Gy\n")
        if sesion.tiempo_usado_h > 0:
            self.details_text.insert(tk.END, f"Tiempo Usado: {sesion.tiempo_usado_h:.1f} h\n")
        if sesion.tiempo_dosimetria_meses > 0:
            self.details_text.insert(tk.END, f"Tiempo Dosimetría: {sesion.tiempo_dosimetria_meses:.0f} meses\n")
        
        if sesion.observaciones_sesion:
            self.details_text.insert(tk.END, f"\n💬 OBSERVACIONES\n", 'header')
            self.details_text.insert(tk.END, f"{sesion.observaciones_sesion}\n")
        
        # Tags para formato
        self.details_text.tag_config('bold', font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'))
        self.details_text.tag_config('header', font=(self.theme.FONTS['family'], self.theme.FONTS['size_medium'], 'bold'),
                                     foreground=self.theme.COLORS['primary'])
        
        self.details_text.config(state='disabled')
    
    def nueva_sesion(self):
        """Crea una nueva sesión"""
        from src.gui.formulario_sesion import FormularioSesion
        FormularioSesion(self.main_window, self)
    
    def editar_sesion(self):
        """Edita la sesión seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una sesión para editar")
            return
        
        item = self.tree.item(selection[0])
        id_solicitud = item['values'][0]
        fecha_str = item['values'][1]
        
        # Buscar sesión
        sesion = None
        for ses in self.sesiones:
            fecha_ses = ses.fecha_sesion.strftime("%d/%m/%Y") if ses.fecha_sesion else ""
            if ses.id_solicitud == id_solicitud and fecha_ses == fecha_str:
                sesion = ses
                break
        
        if sesion:
            from src.gui.formulario_sesion import FormularioSesion
            FormularioSesion(self.main_window, self, sesion)
    
    def eliminar_sesion(self):
        """Elimina la sesión seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una sesión para eliminar")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta sesión?"):
            return
        
        try:
            # Eliminar de Sheets (implementar)
            messagebox.showinfo("Info", "Función de eliminación pendiente de implementar")
            
        except Exception as e:
            logger.error(f"Error al eliminar: {e}")
            messagebox.showerror("Error", f"Error al eliminar:\n{e}")
