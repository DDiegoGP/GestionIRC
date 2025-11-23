"""
Formulario de Sesión - Adaptable según tipo de servicio (VERSIÓN CORREGIDA)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from typing import Optional
import json

from src.models.sesion import Sesion
from src.models.solicitud_real import Solicitud
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class FormularioSesion:
    """Formulario para crear/editar sesiones"""
    
    def __init__(self, main_window, sesiones_panel, sesion: Optional[Sesion] = None, 
                 fecha_inicial: Optional[date] = None, es_planificada: bool = False):
        self.main_window = main_window
        self.sesiones_panel = sesiones_panel
        self.theme = main_window.theme
        self.sesion = sesion
        self.es_edicion = sesion is not None
        self.fecha_inicial = fecha_inicial or date.today()
        self.es_planificada = es_planificada
        
        # Cargar solicitudes disponibles
        self.solicitudes = []
        self.load_solicitudes()
        
        # Variables de formulario
        self.vars = {}
        
        # Crear ventana
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Editar Sesión" if self.es_edicion else "Nueva Sesión")
        self.window.geometry("700x750")
        self.window.transient(main_window.root)
        self.window.grab_set()
        
        # Centrar ventana
        self.center_window()
        
        # Construir interfaz
        self.build_ui()
        
        # Cargar datos si es edición
        if self.es_edicion:
            self.cargar_datos()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 700
        height = 750
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def load_solicitudes(self):
        """Carga las solicitudes disponibles"""
        try:
            logger.info("Cargando solicitudes para formulario...")
            data = sheets_manager.get_all_data('Solicitudes')
            
            if len(data) > 1:
                self.solicitudes = [Solicitud.from_sheet_row(row) for row in data[1:]]
                # Filtrar solo solicitudes activas o en progreso
                self.solicitudes = [s for s in self.solicitudes if s.estado == "En proceso"]
                logger.info(f"✅ {len(self.solicitudes)} solicitudes cargadas")
            else:
                self.solicitudes = []
                logger.warning("⚠️ No hay solicitudes disponibles")
                
        except Exception as e:
            logger.error(f"❌ Error al cargar solicitudes: {e}")
            self.solicitudes = []
            messagebox.showerror(
                "Error", 
                f"No se pudieron cargar las solicitudes:\n{e}\n\n"
                "Verifica la conexión con Google Sheets."
            )
    
    def build_ui(self):
        """Construye la interfaz"""
        # Frame principal con scroll
        container = tk.Frame(self.window, bg=self.theme.COLORS['bg_main'])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        canvas = tk.Canvas(container, bg=self.theme.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.theme.COLORS['bg_main'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Padding interno
        main_frame = tk.Frame(scrollable_frame, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Título
        title_text = "✏️ Editar Sesión" if self.es_edicion else ("📅 Planificar Sesión" if self.es_planificada else "➕ Nueva Sesión")
        title = self.theme.create_header_label(main_frame, title_text)
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Verificar si hay solicitudes
        if not self.solicitudes:
            self.create_no_solicitudes_message(main_frame)
            return
        
        # Campos básicos
        self.create_basic_fields(main_frame)
        
        # Campos específicos (se mostrarán según el servicio seleccionado)
        self.campos_especificos_frame = tk.Frame(main_frame, bg=self.theme.COLORS['bg_main'])
        self.campos_especificos_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Notas
        self.create_notes_field(main_frame)
        
        # Botones
        self.create_buttons(main_frame)
    
    def create_no_solicitudes_message(self, parent):
        """Muestra mensaje cuando no hay solicitudes"""
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        msg = tk.Label(
            card,
            text="⚠️ No hay solicitudes disponibles\n\n"
                 "Necesitas crear al menos una solicitud activa\n"
                 "antes de poder registrar sesiones.\n\n"
                 "Ve a la pestaña 📋 Solicitudes y crea una.",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal']),
            justify=tk.CENTER,
            pady=40
        )
        msg.pack(fill=tk.BOTH, expand=True)
        
        # Botón cerrar
        btn_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        btn_close = self.theme.create_secondary_button(
            btn_frame,
            "Cerrar",
            self.window.destroy
        )
        btn_close.pack()
    
    def create_basic_fields(self, parent):
        """Crea los campos básicos"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Grid para campos
        fields_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        fields_frame.pack(fill=tk.X, padx=15, pady=15)
        
        row = 0
        
        # Solicitud
        tk.Label(
            fields_frame,
            text="Solicitud:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        # Dropdown de solicitudes
        solicitudes_opciones = [f"{s.id_solicitud} - {s.nombre_solicitante} - {s.servicio_solicitado}" 
                               for s in self.solicitudes]
        
        self.vars['solicitud'] = tk.StringVar()
        self.solicitud_combo = ttk.Combobox(
            fields_frame,
            textvariable=self.vars['solicitud'],
            values=solicitudes_opciones,
            state='readonly',
            width=60
        )
        self.solicitud_combo.grid(row=row, column=1, sticky='ew', pady=5)
        self.solicitud_combo.bind('<<ComboboxSelected>>', self.on_solicitud_change)
        
        if solicitudes_opciones:
            self.solicitud_combo.current(0)
            # Llamar después de que la ventana esté completamente construida
            self.window.after(100, lambda: self.on_solicitud_change(None))
        
        row += 1
        
        # Fecha
        tk.Label(
            fields_frame,
            text="Fecha:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        fecha_frame = tk.Frame(fields_frame, bg=self.theme.COLORS['card_bg'])
        fecha_frame.grid(row=row, column=1, sticky='w', pady=5)
        
        self.vars['fecha_dia'] = tk.StringVar(value=str(self.fecha_inicial.day).zfill(2))
        self.vars['fecha_mes'] = tk.StringVar(value=str(self.fecha_inicial.month).zfill(2))
        self.vars['fecha_anio'] = tk.StringVar(value=str(self.fecha_inicial.year))
        
        tk.Entry(fecha_frame, textvariable=self.vars['fecha_dia'], width=3).pack(side=tk.LEFT, padx=2)
        tk.Label(fecha_frame, text="/", bg=self.theme.COLORS['card_bg']).pack(side=tk.LEFT)
        tk.Entry(fecha_frame, textvariable=self.vars['fecha_mes'], width=3).pack(side=tk.LEFT, padx=2)
        tk.Label(fecha_frame, text="/", bg=self.theme.COLORS['card_bg']).pack(side=tk.LEFT)
        tk.Entry(fecha_frame, textvariable=self.vars['fecha_anio'], width=5).pack(side=tk.LEFT, padx=2)
        
        row += 1
        
        # Tipo
        tk.Label(
            fields_frame,
            text="Tipo:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.vars['tipo'] = tk.StringVar(value="Planificada" if self.es_planificada else "Realizada")
        tipo_frame = tk.Frame(fields_frame, bg=self.theme.COLORS['card_bg'])
        tipo_frame.grid(row=row, column=1, sticky='w', pady=5)
        
        tk.Radiobutton(
            tipo_frame,
            text="Realizada",
            variable=self.vars['tipo'],
            value="Realizada",
            bg=self.theme.COLORS['card_bg']
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Radiobutton(
            tipo_frame,
            text="Planificada",
            variable=self.vars['tipo'],
            value="Planificada",
            bg=self.theme.COLORS['card_bg']
        ).pack(side=tk.LEFT)
        
        row += 1
        
        # Operador
        tk.Label(
            fields_frame,
            text="Operador:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=row, column=0, sticky='w', pady=5)
        
        self.vars['operador'] = tk.StringVar()
        tk.Entry(
            fields_frame,
            textvariable=self.vars['operador'],
            width=40
        ).grid(row=row, column=1, sticky='w', pady=5)
        
        # Configurar grid
        fields_frame.columnconfigure(1, weight=1)
    
    def on_solicitud_change(self, event):
        """Actualiza los campos específicos según la solicitud seleccionada"""
        try:
            # Obtener solicitud seleccionada
            solicitud_str = self.vars['solicitud'].get()
            logger.info(f"📝 Solicitud seleccionada: {solicitud_str}")
            
            if not solicitud_str:
                logger.warning("⚠️ No hay solicitud seleccionada")
                return
            
            # Extraer ID
            id_solicitud = solicitud_str.split(" - ")[0]
            solicitud = next((s for s in self.solicitudes if s.id_solicitud == id_solicitud), None)
            
            if not solicitud:
                logger.error(f"❌ No se encontró la solicitud: {id_solicitud}")
                return
            
            logger.info(f"✅ Solicitud encontrada: {solicitud.servicio_solicitado}")
            
            # Limpiar campos específicos
            for widget in self.campos_especificos_frame.winfo_children():
                widget.destroy()
            
            # Crear campos según el tipo de servicio
            servicio = solicitud.servicio_solicitado.lower()
            logger.info(f"🔍 Tipo de servicio: {servicio}")
            
            if "irradiación" in servicio or "irradiador" in servicio:
                logger.info("📦 Creando campos de irradiación")
                self.create_irradiacion_fields(solicitud)
            elif "dosimétrica" in servicio or "dosimetri" in servicio:
                logger.info("📊 Creando campos de dosimetría")
                self.create_dosimetria_fields(solicitud)
            elif "contador" in servicio:
                logger.info("⏱️ Creando campos de contador")
                self.create_contador_fields(solicitud)
            elif "residuos" in servicio or "huérfanas" in servicio:
                logger.info("♻️ Creando campos de residuos")
                self.create_residuos_fields(solicitud)
            else:
                logger.info("📄 Creando campos genéricos")
                self.create_generic_fields(solicitud)
            
            logger.info("✅ Campos específicos creados")
            
        except Exception as e:
            logger.error(f"❌ Error en on_solicitud_change: {e}")
            import traceback
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error al cargar campos del servicio:\n{e}")
    
    def create_irradiacion_fields(self, solicitud: Solicitud):
        """Crea campos para servicios de irradiación"""
        # Card
        card = self.theme.create_card_frame(self.campos_especificos_frame)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = self.theme.create_title_label(card, "📦 Detalles de Irradiación")
        title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Info de la solicitud
        detalles = solicitud.detalles_servicio
        canisters_totales = detalles.get('canisters', 0) if isinstance(detalles, dict) else 0
        
        info = tk.Label(
            card,
            text=f"Total solicitado: {canisters_totales} canisters",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        )
        info.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Fields
        fields_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        fields_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Canisters procesados
        tk.Label(
            fields_frame,
            text="Canisters procesados en esta sesión:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.vars['canisters'] = tk.StringVar(value="0")
        tk.Entry(
            fields_frame,
            textvariable=self.vars['canisters'],
            width=10
        ).grid(row=0, column=1, sticky='w', pady=5, padx=5)
        
        # Dosis (solo para > 10 Gy)
        if "> 10 gy" in solicitud.servicio_solicitado.lower():
            tk.Label(
                fields_frame,
                text="Dosis aplicada (Gy):",
                bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'],
                font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
            ).grid(row=1, column=0, sticky='w', pady=5)
            
            self.vars['dosis'] = tk.StringVar(value="0")
            tk.Entry(
                fields_frame,
                textvariable=self.vars['dosis'],
                width=10
            ).grid(row=1, column=1, sticky='w', pady=5, padx=5)
    
    def create_dosimetria_fields(self, solicitud: Solicitud):
        """Crea campos para gestión dosimétrica"""
        # Card
        card = self.theme.create_card_frame(self.campos_especificos_frame)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = self.theme.create_title_label(card, "📊 Gestión Dosimétrica")
        title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Info de la solicitud
        detalles = solicitud.detalles_servicio
        dosimetros = detalles.get('dosimetros', 0) if isinstance(detalles, dict) else 0
        meses = detalles.get('meses', 0) if isinstance(detalles, dict) else 0
        
        info = tk.Label(
            card,
            text=f"Total: {dosimetros} dosímetros durante {meses} meses",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        )
        info.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Fields
        fields_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        fields_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Mes de gestión
        tk.Label(
            fields_frame,
            text="Mes de gestión (YYYY-MM):",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        mes_actual = date.today().strftime("%Y-%m")
        self.vars['mes_gestion'] = tk.StringVar(value=mes_actual)
        tk.Entry(
            fields_frame,
            textvariable=self.vars['mes_gestion'],
            width=10
        ).grid(row=0, column=1, sticky='w', pady=5, padx=5)
        
        # Dosímetros gestionados
        tk.Label(
            fields_frame,
            text="Dosímetros gestionados:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.vars['dosimetros'] = tk.StringVar(value=str(dosimetros))
        tk.Entry(
            fields_frame,
            textvariable=self.vars['dosimetros'],
            width=10
        ).grid(row=1, column=1, sticky='w', pady=5, padx=5)
    
    def create_contador_fields(self, solicitud: Solicitud):
        """Crea campos para contadores"""
        # Card
        card = self.theme.create_card_frame(self.campos_especificos_frame)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = self.theme.create_title_label(card, "⏱️ Uso de Contador")
        title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Info de la solicitud
        detalles = solicitud.detalles_servicio
        horas_totales = detalles.get('horas', 0) if isinstance(detalles, dict) else 0
        
        info = tk.Label(
            card,
            text=f"Total contratado: {horas_totales} horas",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        )
        info.pack(anchor=tk.W, padx=15, pady=(0, 10))
        
        # Fields
        fields_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        fields_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Horas utilizadas
        tk.Label(
            fields_frame,
            text="Horas utilizadas en esta sesión:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.vars['horas'] = tk.StringVar(value="0")
        tk.Entry(
            fields_frame,
            textvariable=self.vars['horas'],
            width=10
        ).grid(row=0, column=1, sticky='w', pady=5, padx=5)
    
    def create_residuos_fields(self, solicitud: Solicitud):
        """Crea campos para gestión de residuos"""
        # Card
        card = self.theme.create_card_frame(self.campos_especificos_frame)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = self.theme.create_title_label(card, "♻️ Gestión de Residuos")
        title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Fields
        fields_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        fields_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # Descripción
        tk.Label(
            fields_frame,
            text="Descripción de los residuos gestionados:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.vars['descripcion_residuos'] = tk.StringVar()
        tk.Entry(
            fields_frame,
            textvariable=self.vars['descripcion_residuos'],
            width=50
        ).grid(row=0, column=1, sticky='ew', pady=5, padx=5)
        
        fields_frame.columnconfigure(1, weight=1)
    
    def create_generic_fields(self, solicitud: Solicitud):
        """Crea campos genéricos para otros servicios"""
        # Card
        card = self.theme.create_card_frame(self.campos_especificos_frame)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Info
        info = tk.Label(
            card,
            text=f"📄 Servicio: {solicitud.servicio_solicitado}\n\n"
                 "Este tipo de servicio no requiere campos específicos adicionales.",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            justify=tk.CENTER
        )
        info.pack(anchor=tk.CENTER, padx=15, pady=20)
    
    def create_notes_field(self, parent):
        """Crea el campo de notas"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(20, 10))
        
        # Título
        title = self.theme.create_title_label(card, "📝 Notas y Observaciones")
        title.pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Text area
        self.notas_text = tk.Text(
            card,
            height=5,
            wrap=tk.WORD,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'])
        )
        self.notas_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
    
    def create_buttons(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón guardar
        btn_save = self.theme.create_primary_button(
            btn_frame,
            "💾 Guardar",
            self.guardar
        )
        btn_save.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón cancelar
        btn_cancel = self.theme.create_secondary_button(
            btn_frame,
            "✖ Cancelar",
            self.window.destroy
        )
        btn_cancel.pack(side=tk.LEFT)
    
    def cargar_datos(self):
        """Carga los datos de la sesión en el formulario"""
        if not self.sesion:
            return
        
        try:
            # Buscar y seleccionar solicitud
            solicitudes_opciones = self.solicitud_combo['values']
            for i, opt in enumerate(solicitudes_opciones):
                if self.sesion.id_solicitud in opt:
                    self.solicitud_combo.current(i)
                    self.on_solicitud_change(None)
                    break
            
            # Fecha
            self.vars['fecha_dia'].set(str(self.sesion.fecha_sesion.day).zfill(2))
            self.vars['fecha_mes'].set(str(self.sesion.fecha_sesion.month).zfill(2))
            self.vars['fecha_anio'].set(str(self.sesion.fecha_sesion.year))
            
            # Tipo
            self.vars['tipo'].set(self.sesion.tipo_sesion)
            
            # Operador
            self.vars['operador'].set(self.sesion.operador)
            
            # Campos específicos
            if 'canisters' in self.vars:
                self.vars['canisters'].set(str(self.sesion.canisters_procesados))
            if 'dosis' in self.vars:
                self.vars['dosis'].set(str(self.sesion.dosis_aplicada_gy))
            if 'mes_gestion' in self.vars:
                self.vars['mes_gestion'].set(self.sesion.mes_gestion)
            if 'dosimetros' in self.vars:
                self.vars['dosimetros'].set(str(self.sesion.dosimetros_gestionados))
            if 'horas' in self.vars:
                self.vars['horas'].set(str(self.sesion.horas_contador))
            if 'descripcion_residuos' in self.vars:
                self.vars['descripcion_residuos'].set(self.sesion.descripcion_residuos)
            
            # Notas
            self.notas_text.insert('1.0', self.sesion.notas)
            
        except Exception as e:
            logger.error(f"Error al cargar datos de sesión: {e}")
            messagebox.showerror("Error", f"Error al cargar datos:\n{e}")
    
    def guardar(self):
        """Guarda la sesión"""
        try:
            # Validar campos
            solicitud_str = self.vars['solicitud'].get()
            if not solicitud_str:
                messagebox.showerror("Error", "Selecciona una solicitud")
                return
            
            # Extraer datos de solicitud
            id_solicitud = solicitud_str.split(" - ")[0]
            solicitud = next((s for s in self.solicitudes if s.id_solicitud == id_solicitud), None)
            
            if not solicitud:
                messagebox.showerror("Error", "Solicitud no encontrada")
                return
            
            # Crear o actualizar sesión
            if self.es_edicion:
                sesion = self.sesion
            else:
                sesion = Sesion()
            
            # Datos básicos
            sesion.id_solicitud = id_solicitud
            sesion.servicio = solicitud.servicio_solicitado
            sesion.solicitante = solicitud.nombre_solicitante
            
            # Fecha
            try:
                dia = int(self.vars['fecha_dia'].get())
                mes = int(self.vars['fecha_mes'].get())
                anio = int(self.vars['fecha_anio'].get())
                sesion.fecha_sesion = date(anio, mes, dia)
            except:
                messagebox.showerror("Error", "Fecha inválida")
                return
            
            # Tipo
            sesion.tipo_sesion = self.vars['tipo'].get()
            
            # Operador
            sesion.operador = self.vars['operador'].get()
            
            # Campos específicos
            if 'canisters' in self.vars:
                try:
                    sesion.canisters_procesados = int(self.vars['canisters'].get())
                except:
                    sesion.canisters_procesados = 0
            
            if 'dosis' in self.vars:
                try:
                    sesion.dosis_aplicada_gy = float(self.vars['dosis'].get())
                except:
                    sesion.dosis_aplicada_gy = 0.0
            
            if 'mes_gestion' in self.vars:
                sesion.mes_gestion = self.vars['mes_gestion'].get()
            
            if 'dosimetros' in self.vars:
                try:
                    sesion.dosimetros_gestionados = int(self.vars['dosimetros'].get())
                except:
                    sesion.dosimetros_gestionados = 0
            
            if 'horas' in self.vars:
                try:
                    sesion.horas_contador = float(self.vars['horas'].get())
                except:
                    sesion.horas_contador = 0.0
            
            if 'descripcion_residuos' in self.vars:
                sesion.descripcion_residuos = self.vars['descripcion_residuos'].get()
            
            # Notas
            sesion.notas = self.notas_text.get('1.0', tk.END).strip()
            
            # Guardar en Google Sheets
            try:
                if self.es_edicion:
                    # Actualizar fila existente
                    logger.info(f"📝 Actualizando sesión: {sesion.id_sesion}")
                    row = sesion.to_sheet_row()
                    
                    # Buscar índice
                    data = sheets_manager.get_all_data('Sesiones')
                    row_index = None
                    
                    for i, data_row in enumerate(data[1:], start=2):
                        if len(data_row) > 0 and data_row[0] == sesion.id_sesion:
                            row_index = i
                            break
                    
                    if row_index:
                        resultado = sheets_manager.update_row('Sesiones', row_index, row)
                        if resultado:
                            logger.info(f"✅ Sesión actualizada correctamente")
                        else:
                            raise Exception("No se pudo actualizar en Google Sheets")
                    else:
                        # Si no se encuentra, añadir como nueva
                        resultado = sheets_manager.append_row('Sesiones', row)
                        if not resultado:
                            raise Exception("No se pudo añadir en Google Sheets")
                else:
                    # Añadir nueva fila
                    logger.info(f"➕ Añadiendo nueva sesión: {sesion.id_sesion}")
                    row = sesion.to_sheet_row()
                    
                    resultado = sheets_manager.append_row('Sesiones', row)
                    if resultado:
                        logger.info(f"✅ Nueva sesión añadida correctamente")
                    else:
                        raise Exception("No se pudo añadir en Google Sheets")
                
                # Actualizar panel
                self.sesiones_panel.load_data()
                
                messagebox.showinfo("Éxito", "Sesión guardada correctamente")
                self.window.destroy()
                
            except Exception as e_sheets:
                logger.error(f"❌ Error al guardar en Sheets: {e_sheets}")
                messagebox.showerror(
                    "Error al Guardar",
                    f"No se pudo guardar en Google Sheets:\n\n{e_sheets}\n\n"
                    "Verifica la conexión y permisos."
                )
                return
            
        except Exception as e:
            logger.error(f"Error al guardar sesión: {e}")
            import traceback
            logger.error(traceback.format_exc())
            messagebox.showerror("Error", f"Error al guardar:\n{e}")
