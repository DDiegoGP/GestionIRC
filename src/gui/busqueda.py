"""
Panel de Búsqueda Avanzada - Filtros múltiples estilo Microsoft 365
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List
import json

from src.models.solicitud_real import Solicitud
from src.constants_real import TIPOS_SERVICIOS, ESTADOS_SOLICITUD, TIPOS_USUARIO
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class BusquedaPanel:
    """Panel de búsqueda avanzada con filtros múltiples"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        self.todas_solicitudes: List[Solicitud] = []
        self.resultados: List[Solicitud] = []
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Construye la interfaz"""
        # Frame principal
        main_frame = tk.Frame(self.parent, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        header_frame = tk.Frame(main_frame, bg=self.theme.COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = self.theme.create_header_label(header_frame, "🔍 Búsqueda Avanzada")
        title.pack(side=tk.LEFT)
        
        # Botón actualizar
        btn_refresh = self.theme.create_secondary_button(
            header_frame,
            "🔄 Actualizar Datos",
            self.load_data
        )
        btn_refresh.pack(side=tk.RIGHT)
        
        # Panel de filtros
        self.create_filters_panel(main_frame)
        
        # Resultados
        self.create_results_panel(main_frame)
    
    def create_filters_panel(self, parent):
        """Crea el panel de filtros"""
        # Card contenedor
        filters_card = self.theme.create_card_frame(parent)
        filters_card.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title = self.theme.create_title_label(filters_card, "Filtros de Búsqueda")
        title.pack(anchor=tk.W, pady=(0, 15))
        
        # Filtro de texto general
        text_frame = tk.Frame(filters_card, bg=self.theme.COLORS['card_bg'])
        text_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            text_frame,
            text="🔎 Búsqueda por texto:",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.aplicar_filtros())
        
        search_entry = self.theme.create_entry(text_frame)
        search_entry.config(textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            text_frame,
            text="Busca por: ID, Nombre, Email, Organismo, etc.",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_tertiary']
        ).pack(anchor=tk.W)
        
        # Separador
        ttk.Separator(filters_card, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Grid de filtros específicos
        filters_grid = tk.Frame(filters_card, bg=self.theme.COLORS['card_bg'])
        filters_grid.pack(fill=tk.X)
        
        filters_grid.grid_columnconfigure(0, weight=1)
        filters_grid.grid_columnconfigure(1, weight=1)
        filters_grid.grid_columnconfigure(2, weight=1)
        
        # Filtro por Estado
        self.create_filter_combo(
            filters_grid,
            "📊 Estado:",
            "filtro_estado",
            ["Todos"] + ESTADOS_SOLICITUD,
            0, 0
        )
        
        # Filtro por Tipo de Usuario
        self.create_filter_combo(
            filters_grid,
            "👤 Tipo Usuario:",
            "filtro_tipo_usuario",
            ["Todos"] + TIPOS_USUARIO,
            0, 1
        )
        
        # Filtro por Servicio
        self.create_filter_combo(
            filters_grid,
            "🔬 Servicio:",
            "filtro_servicio",
            ["Todos"] + TIPOS_SERVICIOS,
            0, 2
        )
        
        # Separador
        ttk.Separator(filters_card, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Filtros de fecha
        fecha_frame = tk.Frame(filters_card, bg=self.theme.COLORS['card_bg'])
        fecha_frame.pack(fill=tk.X)
        
        tk.Label(
            fecha_frame,
            text="📅 Rango de Fechas:",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary']
        ).pack(anchor=tk.W, pady=(0, 10))
        
        fecha_inputs = tk.Frame(fecha_frame, bg=self.theme.COLORS['card_bg'])
        fecha_inputs.pack(fill=tk.X)
        
        # Fecha desde
        desde_frame = tk.Frame(fecha_inputs, bg=self.theme.COLORS['card_bg'])
        desde_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        tk.Label(
            desde_frame,
            text="Desde (DD/MM/YYYY):",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        ).pack(anchor=tk.W)
        
        self.fecha_desde = self.theme.create_entry(desde_frame)
        self.fecha_desde.pack(fill=tk.X, pady=(5, 0))
        self.fecha_desde.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
        
        # Fecha hasta
        hasta_frame = tk.Frame(fecha_inputs, bg=self.theme.COLORS['card_bg'])
        hasta_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))
        
        tk.Label(
            hasta_frame,
            text="Hasta (DD/MM/YYYY):",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        ).pack(anchor=tk.W)
        
        self.fecha_hasta = self.theme.create_entry(hasta_frame)
        self.fecha_hasta.pack(fill=tk.X, pady=(5, 0))
        self.fecha_hasta.bind('<KeyRelease>', lambda e: self.aplicar_filtros())
        
        # Botones de acción
        btn_frame = tk.Frame(filters_card, bg=self.theme.COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        btn_clear = self.theme.create_secondary_button(
            btn_frame,
            "🔄 Limpiar Filtros",
            self.limpiar_filtros
        )
        btn_clear.pack(side=tk.LEFT)
        
        # Label de resultados
        self.results_label = tk.Label(
            btn_frame,
            text="0 resultados",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['primary']
        )
        self.results_label.pack(side=tk.RIGHT)
    
    def create_filter_combo(self, parent, label, var_name, values, row, col):
        """Crea un combo de filtro"""
        frame = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        tk.Label(
            frame,
            text=label,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        combo = ttk.Combobox(frame, values=values, state='readonly')
        combo.set("Todos")
        combo.pack(fill=tk.X)
        combo.bind('<<ComboboxSelected>>', lambda e: self.aplicar_filtros())
        
        setattr(self, var_name, combo)
    
    def create_results_panel(self, parent):
        """Crea el panel de resultados"""
        # Card contenedor
        results_card = self.theme.create_card_frame(parent)
        results_card.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = self.theme.create_title_label(results_card, "Resultados")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Lista de resultados
        list_frame = tk.Frame(results_card, bg=self.theme.COLORS['card_bg'])
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("ID", "Fecha", "Solicitante", "Email", "Servicio", "Estado", "Tipo", "Coste")
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
        self.tree.column("ID", width=140, anchor=tk.W)
        self.tree.column("Fecha", width=90, anchor=tk.CENTER)
        self.tree.column("Solicitante", width=150, anchor=tk.W)
        self.tree.column("Email", width=180, anchor=tk.W)
        self.tree.column("Servicio", width=200, anchor=tk.W)
        self.tree.column("Estado", width=120, anchor=tk.CENTER)
        self.tree.column("Tipo", width=70, anchor=tk.CENTER)
        self.tree.column("Coste", width=90, anchor=tk.E)
        
        # Encabezados
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W if col in ["ID", "Solicitante", "Email", "Servicio"] else tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Eventos
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def load_data(self):
        """Carga todas las solicitudes"""
        try:
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("Cargando solicitudes...")
            
            data = sheets_manager.get_all_data('Solicitudes')
            
            if len(data) > 1:
                self.todas_solicitudes = [Solicitud.from_sheet_row(row) for row in data[1:]]
            else:
                self.todas_solicitudes = []
            
            self.aplicar_filtros()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status(f"✅ {len(self.todas_solicitudes)} solicitudes cargadas")
            
        except Exception as e:
            logger.error(f"Error al cargar solicitudes: {e}")
            self.todas_solicitudes = []
            self.aplicar_filtros()
    
    def aplicar_filtros(self):
        """Aplica todos los filtros y actualiza resultados"""
        resultados = self.todas_solicitudes.copy()
        
        # Filtro de texto
        texto_busqueda = self.search_var.get().lower().strip()
        if texto_busqueda:
            resultados = [
                s for s in resultados
                if (texto_busqueda in s.id_solicitud.lower() or
                    texto_busqueda in s.nombre_solicitante.lower() or
                    texto_busqueda in s.email.lower() or
                    texto_busqueda in s.organismo_centro_solicitante.lower() or
                    texto_busqueda in s.departamento_solicitante.lower())
            ]
        
        # Filtro por estado
        if hasattr(self, 'filtro_estado'):
            estado = self.filtro_estado.get()
            if estado != "Todos":
                resultados = [s for s in resultados if s.estado == estado]
        
        # Filtro por tipo usuario
        if hasattr(self, 'filtro_tipo_usuario'):
            tipo = self.filtro_tipo_usuario.get()
            if tipo != "Todos":
                resultados = [s for s in resultados if s.tipo_usuario == tipo]
        
        # Filtro por servicio
        if hasattr(self, 'filtro_servicio'):
            servicio = self.filtro_servicio.get()
            if servicio != "Todos":
                resultados = [s for s in resultados if s.servicio_solicitado == servicio]
        
        # Filtro por fecha desde
        fecha_desde_str = self.fecha_desde.get().strip()
        if fecha_desde_str:
            try:
                fecha_desde = datetime.strptime(fecha_desde_str, "%d/%m/%Y").date()
                resultados = [s for s in resultados if s.fecha_solicitud and s.fecha_solicitud.date() >= fecha_desde]
            except:
                pass  # Ignorar si fecha inválida
        
        # Filtro por fecha hasta
        fecha_hasta_str = self.fecha_hasta.get().strip()
        if fecha_hasta_str:
            try:
                fecha_hasta = datetime.strptime(fecha_hasta_str, "%d/%m/%Y").date()
                resultados = [s for s in resultados if s.fecha_solicitud and s.fecha_solicitud.date() <= fecha_hasta]
            except:
                pass  # Ignorar si fecha inválida
        
        self.resultados = resultados
        self.update_results()
    
    def update_results(self):
        """Actualiza la vista de resultados"""
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Actualizar label de resultados
        self.results_label.config(text=f"{len(self.resultados)} resultado{'s' if len(self.resultados) != 1 else ''}")
        
        # Agregar resultados
        for sol in self.resultados:
            fecha = sol.fecha_solicitud.strftime("%d/%m/%Y") if sol.fecha_solicitud else ""
            coste = f"{sol.coste_estimado_iva_0:.2f}€"
            
            self.tree.insert('', tk.END, values=(
                sol.id_solicitud,
                fecha,
                sol.nombre_solicitante,
                sol.email,
                sol.servicio_solicitado,
                sol.estado,
                sol.tipo_usuario,
                coste
            ))
    
    def limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.search_var.set("")
        if hasattr(self, 'filtro_estado'):
            self.filtro_estado.set("Todos")
        if hasattr(self, 'filtro_tipo_usuario'):
            self.filtro_tipo_usuario.set("Todos")
        if hasattr(self, 'filtro_servicio'):
            self.filtro_servicio.set("Todos")
        self.fecha_desde.delete(0, tk.END)
        self.fecha_hasta.delete(0, tk.END)
        
        self.aplicar_filtros()
    
    def on_double_click(self, event):
        """Maneja el doble click para ver detalles"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        id_solicitud = item['values'][0]
        
        # Buscar solicitud
        solicitud = next((s for s in self.resultados if s.id_solicitud == id_solicitud), None)
        
        if solicitud:
            self.mostrar_detalles(solicitud)
    
    def mostrar_detalles(self, solicitud: Solicitud):
        """Muestra los detalles de una solicitud en ventana modal"""
        # Crear ventana modal
        detalle_window = tk.Toplevel(self.main_window.root)
        detalle_window.title(f"Detalles - {solicitud.id_solicitud}")
        detalle_window.geometry("600x500")
        detalle_window.transient(self.main_window.root)
        
        # Centrar ventana
        detalle_window.update_idletasks()
        x = (detalle_window.winfo_screenwidth() // 2) - 300
        y = (detalle_window.winfo_screenheight() // 2) - 250
        detalle_window.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(detalle_window, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = self.theme.create_header_label(main_frame, f"📋 {solicitud.id_solicitud}")
        title.pack(anchor=tk.W, pady=(0, 15))
        
        # Texto con detalles
        text_frame = tk.Frame(main_frame, bg=self.theme.COLORS['bg_main'])
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(text_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = self.theme.create_text(text_frame, yscrollcommand=vsb.set, state='normal')
        text.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=text.yview)
        
        # Insertar detalles (mismo formato que solicitudes_real.py)
        text.insert(tk.END, f"📅 Fecha: {solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')}\n")
        text.insert(tk.END, f"📊 Estado: {solicitud.estado}\n\n")
        
        text.insert(tk.END, "👤 SOLICITANTE\n", 'header')
        text.insert(tk.END, f"Nombre: {solicitud.nombre_solicitante}\n")
        text.insert(tk.END, f"Email: {solicitud.email}\n")
        text.insert(tk.END, f"Teléfono: {solicitud.telefono}\n")
        text.insert(tk.END, f"Tipo: {solicitud.tipo_usuario}\n\n")
        
        text.insert(tk.END, "🔬 SERVICIO\n", 'header')
        text.insert(tk.END, f"Tipo: {solicitud.servicio_solicitado}\n")
        text.insert(tk.END, f"Detalles: {json.dumps(solicitud.detalles_servicio, indent=2, ensure_ascii=False)}\n")
        text.insert(tk.END, f"Coste: {solicitud.coste_estimado_iva_0:.2f}€\n\n")
        
        if solicitud.observaciones:
            text.insert(tk.END, "💬 OBSERVACIONES\n", 'header')
            text.insert(tk.END, f"{solicitud.observaciones}\n")
        
        text.tag_config('header', font=(self.theme.FONTS['family'], self.theme.FONTS['size_medium'], 'bold'),
                       foreground=self.theme.COLORS['primary'])
        
        text.config(state='disabled')
        
        # Botón cerrar
        btn_close = self.theme.create_primary_button(
            main_frame,
            "Cerrar",
            detalle_window.destroy
        )
        btn_close.pack(pady=(15, 0))
