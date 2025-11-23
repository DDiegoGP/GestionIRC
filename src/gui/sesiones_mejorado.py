"""
Panel de Sesiones MEJORADO - Con cards visuales y progreso avanzado
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
from typing import Optional, List
import calendar

from src.models.sesion import Sesion, SolicitudConProgreso
from src.models.solicitud_real import Solicitud
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class SesionesPanelMejorado:
    """Panel de gestión de sesiones con diseño mejorado"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        
        self.sesiones = []
        self.solicitudes = []
        self.mes_actual = date.today().month
        self.anio_actual = date.today().year
        self.dia_seleccionado = None
        
        # Filtros
        self.filtro_tipo = "Todas"
        self.filtro_busqueda = ""
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Construye la interfaz del panel"""
        # Frame principal
        main_frame = tk.Frame(self.parent, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header con resumen ejecutivo
        self.create_header_with_summary(main_frame)
        
        # Contenedor principal con dos paneles
        content_frame = tk.Frame(main_frame, bg=self.theme.COLORS['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Panel izquierdo: Sesiones (cards)
        left_panel = tk.Frame(content_frame, bg=self.theme.COLORS['bg_main'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_sesiones_cards_section(left_panel)
        
        # Panel derecho: Calendario y Progreso
        right_panel = tk.Frame(content_frame, bg=self.theme.COLORS['bg_main'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_calendario_section(right_panel)
        self.create_progreso_mejorado_section(right_panel)
    
    def create_header_with_summary(self, parent):
        """Crea el header con resumen ejecutivo"""
        header_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título y resumen
        title_summary_frame = tk.Frame(header_frame, bg=self.theme.COLORS['bg_main'])
        title_summary_frame.pack(side=tk.LEFT)
        
        title = self.theme.create_header_label(title_summary_frame, "🔬 Sesiones de Servicio")
        title.pack(side=tk.LEFT)
        
        # Resumen ejecutivo (se actualizará dinámicamente)
        self.summary_label = tk.Label(
            title_summary_frame,
            text="",
            bg=self.theme.COLORS['bg_main'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        )
        self.summary_label.pack(side=tk.LEFT, padx=(15, 0))
        
        # Botones
        btn_frame = tk.Frame(header_frame, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(side=tk.RIGHT)
        
        btn_nueva = self.theme.create_primary_button(
            btn_frame,
            "➕ Nueva Sesión",
            self.nueva_sesion
        )
        btn_nueva.pack(side=tk.LEFT, padx=5)
        
        btn_planificar = self.theme.create_secondary_button(
            btn_frame,
            "📅 Planificar",
            self.planificar_sesion
        )
        btn_planificar.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = self.theme.create_secondary_button(
            btn_frame,
            "🔄 Actualizar",
            self.load_data
        )
        btn_refresh.pack(side=tk.LEFT)
    
    def update_summary(self):
        """Actualiza el resumen ejecutivo"""
        # Contar solicitudes activas
        solicitudes_con_sesiones = {}
        for sesion in self.sesiones:
            if sesion.id_solicitud not in solicitudes_con_sesiones:
                solicitudes_con_sesiones[sesion.id_solicitud] = []
            solicitudes_con_sesiones[sesion.id_solicitud].append(sesion)
        
        activas = len(solicitudes_con_sesiones)
        
        # Contar atrasadas (sin sesiones en últimos 7 días y con progreso < 100%)
        atrasadas = 0
        hace_7_dias = date.today() - timedelta(days=7)
        
        for solicitud in self.solicitudes:
            if solicitud.id_solicitud in solicitudes_con_sesiones:
                sesiones_sol = solicitudes_con_sesiones[solicitud.id_solicitud]
                sesiones_realizadas = [s for s in sesiones_sol if s.tipo_sesion == "Realizada"]
                
                if sesiones_realizadas:
                    ultima_fecha = max(s.fecha_sesion for s in sesiones_realizadas)
                    
                    # Calcular progreso
                    progreso_calc = SolicitudConProgreso(solicitud, sesiones_sol)
                    progreso = progreso_calc.calcular_progreso()
                    
                    # Si progreso < 100% y sin sesiones en 7 días
                    if progreso['porcentaje'] < 100 and ultima_fecha < hace_7_dias:
                        atrasadas += 1
        
        # Construir texto
        texto_parts = []
        
        if activas > 0:
            texto_parts.append(f"📊 {activas} activa{'s' if activas != 1 else ''}")
        
        if atrasadas > 0:
            texto_parts.append(f"⚠️ {atrasadas} atrasada{'s' if atrasadas != 1 else ''}")
        
        if not texto_parts:
            texto_parts.append("Sin servicios activos")
        
        self.summary_label.config(text=" • ".join(texto_parts))
    
    def create_sesiones_cards_section(self, parent):
        """Crea la sección de sesiones como cards"""
        # Card contenedor
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Título y filtros
        title_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = self.theme.create_title_label(title_frame, "📋 Sesiones Registradas")
        title.pack(side=tk.LEFT)
        
        # Filtros como chips
        filter_frame = tk.Frame(title_frame, bg=self.theme.COLORS['card_bg'])
        filter_frame.pack(side=tk.RIGHT)
        
        # Búsqueda
        search_frame = tk.Frame(filter_frame, bg=self.theme.COLORS['card_bg'])
        search_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            search_frame,
            text="🔍",
            bg=self.theme.COLORS['card_bg'],
            font=(self.theme.FONTS['family'], 12)
        ).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.update_sesiones_cards())
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=15,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Chips de filtro
        chips_frame = tk.Frame(filter_frame, bg=self.theme.COLORS['card_bg'])
        chips_frame.pack(side=tk.LEFT)
        
        for tipo in ["Todas", "Realizadas", "Planificadas"]:
            self.create_filter_chip(chips_frame, tipo)
        
        # Scroll container para cards
        scroll_container = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        scroll_container.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_container, bg=self.theme.COLORS['card_bg'], highlightthickness=0, height=400)
        scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        
        self.sesiones_cards_frame = tk.Frame(canvas, bg=self.theme.COLORS['card_bg'])
        
        self.sesiones_cards_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.sesiones_cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_filter_chip(self, parent, tipo):
        """Crea un chip de filtro"""
        def select_filter():
            self.filtro_tipo = tipo
            self.update_sesiones_cards()
        
        # Color según si está seleccionado
        is_selected = self.filtro_tipo == tipo
        bg_color = self.theme.COLORS['primary'] if is_selected else '#E0E0E0'
        fg_color = 'white' if is_selected else self.theme.COLORS['text_primary']
        
        chip = tk.Button(
            parent,
            text=tipo,
            command=select_filter,
            bg=bg_color,
            fg=fg_color,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            relief='flat',
            bd=0,
            padx=12,
            pady=4,
            cursor='hand2'
        )
        chip.pack(side=tk.LEFT, padx=2)
        
        # Guardar referencia para actualizar después
        if not hasattr(self, 'filter_chips'):
            self.filter_chips = {}
        self.filter_chips[tipo] = chip
    
    def update_filter_chips(self):
        """Actualiza el aspecto de los chips de filtro"""
        for tipo, chip in self.filter_chips.items():
            is_selected = self.filtro_tipo == tipo
            bg_color = self.theme.COLORS['primary'] if is_selected else '#E0E0E0'
            fg_color = 'white' if is_selected else self.theme.COLORS['text_primary']
            chip.config(bg=bg_color, fg=fg_color)
    
    def update_sesiones_cards(self):
        """Actualiza las cards de sesiones"""
        # Limpiar
        for widget in self.sesiones_cards_frame.winfo_children():
            widget.destroy()
        
        # Filtrar sesiones
        sesiones_filtradas = self.sesiones
        
        # Por tipo
        if self.filtro_tipo == "Realizadas":
            sesiones_filtradas = [s for s in sesiones_filtradas if s.tipo_sesion == "Realizada"]
        elif self.filtro_tipo == "Planificadas":
            sesiones_filtradas = [s for s in sesiones_filtradas if s.tipo_sesion == "Planificada"]
        
        # Por búsqueda
        busqueda = self.search_var.get().lower()
        if busqueda:
            sesiones_filtradas = [s for s in sesiones_filtradas 
                                 if busqueda in s.solicitante.lower() 
                                 or busqueda in s.id_solicitud.lower()
                                 or busqueda in s.servicio.lower()]
        
        # Ordenar por fecha (más reciente primero)
        sesiones_filtradas = sorted(sesiones_filtradas, key=lambda s: s.fecha_sesion, reverse=True)
        
        # Crear cards
        if not sesiones_filtradas:
            self.create_empty_state()
        else:
            for sesion in sesiones_filtradas:
                self.create_sesion_card(sesion)
        
        # Actualizar chips
        self.update_filter_chips()
    
    def create_empty_state(self):
        """Crea estado vacío"""
        empty_frame = tk.Frame(
            self.sesiones_cards_frame,
            bg=self.theme.COLORS['card_bg']
        )
        empty_frame.pack(fill=tk.BOTH, expand=True, pady=40)
        
        tk.Label(
            empty_frame,
            text="📭",
            bg=self.theme.COLORS['card_bg'],
            font=(self.theme.FONTS['family'], 48)
        ).pack()
        
        tk.Label(
            empty_frame,
            text="No hay sesiones que coincidan con los filtros",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'])
        ).pack(pady=(10, 0))
    
    def create_sesion_card(self, sesion: Sesion):
        """Crea una card para una sesión"""
        # Color según tipo
        if sesion.tipo_sesion == "Realizada":
            border_color = '#4CAF50'  # Verde
            tipo_bg = '#4CAF50'
            tipo_icon = "✅"
        else:
            border_color = '#2196F3'  # Azul
            tipo_bg = '#2196F3'
            tipo_icon = "📅"
        
        # Card principal
        card = tk.Frame(
            self.sesiones_cards_frame,
            bg='white',
            relief='solid',
            borderwidth=0,
            highlightbackground=border_color,
            highlightthickness=2
        )
        card.pack(fill=tk.X, pady=5, padx=5)
        
        # Contenido
        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.X, padx=12, pady=10)
        
        # Header: Fecha y Tipo
        header = tk.Frame(content, bg='white')
        header.pack(fill=tk.X, pady=(0, 5))
        
        # Fecha
        fecha_str = sesion.fecha_sesion.strftime("%d/%m/%Y")
        tk.Label(
            header,
            text=f"📅 {fecha_str}",
            bg='white',
            fg='#333',
            font=(self.theme.FONTS['family'], 11, 'bold')
        ).pack(side=tk.LEFT)
        
        # Tipo (chip)
        tipo_chip = tk.Label(
            header,
            text=f"{tipo_icon} {sesion.tipo_sesion.upper()}",
            bg=tipo_bg,
            fg='white',
            font=(self.theme.FONTS['family'], 9, 'bold'),
            padx=8,
            pady=2
        )
        tipo_chip.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botones de acción
        btn_frame = tk.Frame(header, bg='white')
        btn_frame.pack(side=tk.RIGHT)
        
        btn_edit = tk.Button(
            btn_frame,
            text="✏️",
            command=lambda s=sesion: self.editar_sesion_directa(s),
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 12),
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=5
        )
        btn_edit.pack(side=tk.LEFT)
        
        btn_delete = tk.Button(
            btn_frame,
            text="🗑️",
            command=lambda s=sesion: self.eliminar_sesion_directa(s),
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 12),
            relief='flat',
            bd=0,
            cursor='hand2',
            padx=5
        )
        btn_delete.pack(side=tk.LEFT)
        
        # Info principal
        info_frame = tk.Frame(content, bg='white')
        info_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Solicitud y solicitante
        tk.Label(
            info_frame,
            text=f"{sesion.id_solicitud} • {sesion.solicitante}",
            bg='white',
            fg='#333',
            font=(self.theme.FONTS['family'], 10, 'bold'),
            anchor='w'
        ).pack(fill=tk.X)
        
        # Servicio
        tk.Label(
            info_frame,
            text=sesion.servicio,
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9),
            anchor='w'
        ).pack(fill=tk.X)
        
        # Detalles específicos
        detalles = self.get_detalles_sesion(sesion)
        if detalles:
            detalles_frame = tk.Frame(content, bg='white')
            detalles_frame.pack(fill=tk.X, pady=(5, 0))
            
            tk.Label(
                detalles_frame,
                text=detalles,
                bg='white',
                fg='#2196F3',
                font=(self.theme.FONTS['family'], 9, 'bold'),
                anchor='w'
            ).pack(side=tk.LEFT)
            
            # Operador
            if sesion.operador:
                tk.Label(
                    detalles_frame,
                    text=f"• Operador: {sesion.operador}",
                    bg='white',
                    fg='#999',
                    font=(self.theme.FONTS['family'], 9),
                    anchor='w'
                ).pack(side=tk.LEFT, padx=(10, 0))
    
    def get_detalles_sesion(self, sesion: Sesion) -> str:
        """Obtiene el texto de detalles de una sesión"""
        detalles = []
        
        if sesion.canisters_procesados > 0:
            detalles.append(f"📦 {sesion.canisters_procesados} canisters")
        
        if sesion.dosis_aplicada_gy > 0:
            detalles.append(f"⚡ {sesion.dosis_aplicada_gy} Gy")
        
        if sesion.mes_gestion:
            detalles.append(f"📊 Mes {sesion.mes_gestion}")
        
        if sesion.dosimetros_gestionados > 0:
            detalles.append(f"🔬 {sesion.dosimetros_gestionados} dosímetros")
        
        if sesion.horas_contador > 0:
            detalles.append(f"⏱️ {sesion.horas_contador}h")
        
        if sesion.descripcion_residuos:
            detalles.append(f"♻️ {sesion.descripcion_residuos[:30]}")
        
        return " • ".join(detalles)
    
    def create_calendario_section(self, parent):
        """Crea la sección del calendario"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, pady=(0, 10))
        
        # Header del calendario
        header_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Botón anterior
        btn_prev = tk.Button(
            header_frame,
            text="◀",
            command=self.mes_anterior,
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['primary'],
            font=(self.theme.FONTS['family'], 14, 'bold'),
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        btn_prev.pack(side=tk.LEFT, padx=10)
        
        # Título mes/año
        self.calendario_titulo = tk.Label(
            header_frame,
            text="",
            font=(self.theme.FONTS['family'], 14, 'bold'),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary']
        )
        self.calendario_titulo.pack(side=tk.LEFT, expand=True)
        
        # Botón siguiente
        btn_next = tk.Button(
            header_frame,
            text="▶",
            command=self.mes_siguiente,
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['primary'],
            font=(self.theme.FONTS['family'], 14, 'bold'),
            relief='flat',
            bd=0,
            cursor='hand2'
        )
        btn_next.pack(side=tk.RIGHT, padx=10)
        
        # Botón hoy
        btn_today = self.theme.create_secondary_button(
            header_frame,
            "📅 Hoy",
            self.ir_a_hoy
        )
        btn_today.pack(side=tk.RIGHT, padx=5)
        
        # Frame del calendario
        self.calendario_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        self.calendario_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear calendario
        self.crear_calendario()
        
        # Leyenda
        leyenda_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        leyenda_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.create_leyenda(leyenda_frame)
    
    def create_leyenda(self, parent):
        """Crea la leyenda del calendario"""
        # Realizada
        frame1 = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        frame1.pack(side=tk.LEFT, padx=10)
        
        color_box1 = tk.Frame(frame1, bg='#4CAF50', width=20, height=20)
        color_box1.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            frame1,
            text="Realizada",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        ).pack(side=tk.LEFT)
        
        # Planificada
        frame2 = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        frame2.pack(side=tk.LEFT, padx=10)
        
        color_box2 = tk.Frame(frame2, bg='#2196F3', width=20, height=20)
        color_box2.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            frame2,
            text="Planificada",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        ).pack(side=tk.LEFT)
        
        # Hoy
        frame3 = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        frame3.pack(side=tk.LEFT, padx=10)
        
        color_box3 = tk.Frame(frame3, bg='#FF9800', width=20, height=20)
        color_box3.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(
            frame3,
            text="Hoy",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        ).pack(side=tk.LEFT)
    
    def crear_calendario(self):
        """Crea el calendario visual"""
        # Limpiar frame
        for widget in self.calendario_frame.winfo_children():
            widget.destroy()
        
        # Actualizar título
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        self.calendario_titulo.config(text=f"{meses[self.mes_actual - 1]} {self.anio_actual}")
        
        # Días de la semana
        dias_semana = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
        for i, dia in enumerate(dias_semana):
            label = tk.Label(
                self.calendario_frame,
                text=dia,
                font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'], 'bold'),
                bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_secondary']
            )
            label.grid(row=0, column=i, padx=2, pady=5, sticky='ew')
        
        # Obtener calendario del mes
        cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        
        # Crear botones para cada día
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Día vacío
                    label = tk.Label(
                        self.calendario_frame,
                        text="",
                        bg=self.theme.COLORS['card_bg']
                    )
                    label.grid(row=week_num, column=day_num, padx=2, pady=2, sticky='nsew')
                else:
                    # Día válido
                    fecha = date(self.anio_actual, self.mes_actual, day)
                    self.crear_boton_dia(fecha, week_num, day_num)
        
        # Configurar grid
        for i in range(7):
            self.calendario_frame.columnconfigure(i, weight=1)
    
    def crear_boton_dia(self, fecha, row, col):
        """Crea un botón para un día del calendario"""
        # Verificar si tiene sesiones
        sesiones_dia = [s for s in self.sesiones if s.fecha_sesion == fecha]
        tiene_realizadas = any(s.tipo_sesion == "Realizada" for s in sesiones_dia)
        tiene_planificadas = any(s.tipo_sesion == "Planificada" for s in sesiones_dia)
        
        # Determinar color
        hoy = date.today()
        if fecha == hoy:
            bg_color = '#FF9800'  # Naranja para hoy
            fg_color = 'white'
        elif tiene_realizadas:
            bg_color = '#4CAF50'  # Verde para realizadas
            fg_color = 'white'
        elif tiene_planificadas:
            bg_color = '#2196F3'  # Azul para planificadas
            fg_color = 'white'
        else:
            bg_color = self.theme.COLORS['card_bg']
            fg_color = self.theme.COLORS['text_primary']
        
        # Crear botón
        btn = tk.Button(
            self.calendario_frame,
            text=str(fecha.day),
            bg=bg_color,
            fg=fg_color,
            font=(self.theme.FONTS['family'], 10),
            relief='flat',
            bd=0,
            width=4,
            height=2,
            cursor='hand2',
            command=lambda f=fecha: self.click_dia(f)
        )
        btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        
        # Tooltip si tiene sesiones
        if sesiones_dia:
            self.create_tooltip(btn, f"{len(sesiones_dia)} sesión(es)")
    
    def create_tooltip(self, widget, text):
        """Crea un tooltip para un widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                bg='#333333',
                fg='white',
                relief='solid',
                borderwidth=1,
                font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
            )
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def mes_anterior(self):
        """Va al mes anterior"""
        if self.mes_actual == 1:
            self.mes_actual = 12
            self.anio_actual -= 1
        else:
            self.mes_actual -= 1
        self.crear_calendario()
    
    def mes_siguiente(self):
        """Va al mes siguiente"""
        if self.mes_actual == 12:
            self.mes_actual = 1
            self.anio_actual += 1
        else:
            self.mes_actual += 1
        self.crear_calendario()
    
    def ir_a_hoy(self):
        """Va al mes actual"""
        hoy = date.today()
        self.mes_actual = hoy.month
        self.anio_actual = hoy.year
        self.crear_calendario()
    
    def click_dia(self, fecha):
        """Maneja el click en un día del calendario"""
        self.dia_seleccionado = fecha
        
        # Buscar sesiones de ese día
        sesiones_dia = [s for s in self.sesiones if s.fecha_sesion == fecha]
        
        if sesiones_dia:
            # Mostrar diálogo con sesiones del día
            self.mostrar_sesiones_dia(fecha, sesiones_dia)
        else:
            # Preguntar si crear nueva
            if messagebox.askyesno(
                "Crear Sesión",
                f"No hay sesiones para {fecha.strftime('%d/%m/%Y')}.\n\n"
                "¿Deseas crear una nueva sesión para esta fecha?"
            ):
                self.nueva_sesion(fecha=fecha)
    
    def mostrar_sesiones_dia(self, fecha, sesiones):
        """Muestra un diálogo con las sesiones de un día"""
        dialog = tk.Toplevel(self.main_window.root)
        dialog.title(f"Sesiones - {fecha.strftime('%d/%m/%Y')}")
        dialog.geometry("600x400")
        dialog.transient(self.main_window.root)
        dialog.grab_set()
        
        # Centrar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300)
        y = (dialog.winfo_screenheight() // 2) - (200)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = tk.Frame(dialog, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = self.theme.create_title_label(
            main_frame,
            f"📋 Sesiones del {fecha.strftime('%d/%m/%Y')}"
        )
        title.pack(pady=(0, 15))
        
        # Lista
        for sesion in sesiones:
            self.create_sesion_card_mini(main_frame, sesion)
        
        # Botón cerrar
        btn_close = self.theme.create_secondary_button(
            main_frame,
            "Cerrar",
            dialog.destroy
        )
        btn_close.pack(pady=(15, 0))
    
    def create_sesion_card_mini(self, parent, sesion):
        """Crea una card mini para una sesión"""
        card = tk.Frame(
            parent,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        card.pack(fill=tk.X, pady=5)
        
        # Contenido
        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Tipo
        tipo_color = '#4CAF50' if sesion.tipo_sesion == "Realizada" else '#2196F3'
        tipo_label = tk.Label(
            content,
            text=sesion.tipo_sesion,
            bg=tipo_color,
            fg='white',
            font=(self.theme.FONTS['family'], 9, 'bold'),
            padx=8,
            pady=2
        )
        tipo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Info
        info_frame = tk.Frame(content, bg='white')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            info_frame,
            text=f"{sesion.servicio} - {sesion.solicitante}",
            bg='white',
            fg='#333',
            font=(self.theme.FONTS['family'], 10, 'bold'),
            anchor='w'
        ).pack(fill=tk.X)
        
        detalles = self.get_detalles_sesion(sesion)
        tk.Label(
            info_frame,
            text=detalles,
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9),
            anchor='w'
        ).pack(fill=tk.X)
    
    def create_progreso_mejorado_section(self, parent):
        """Crea la sección de progreso mejorado"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Título
        title = self.theme.create_title_label(card, "📊 Progreso por Solicitud")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame scrollable
        canvas = tk.Canvas(card, bg=self.theme.COLORS['card_bg'], highlightthickness=0, height=300)
        scrollbar = ttk.Scrollbar(card, orient="vertical", command=canvas.yview)
        
        self.progreso_frame = tk.Frame(canvas, bg=self.theme.COLORS['card_bg'])
        
        self.progreso_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.progreso_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_progreso(self):
        """Actualiza la sección de progreso"""
        # Limpiar
        for widget in self.progreso_frame.winfo_children():
            widget.destroy()
        
        # Agrupar sesiones por solicitud
        solicitudes_con_sesiones = {}
        for sesion in self.sesiones:
            if sesion.id_solicitud not in solicitudes_con_sesiones:
                solicitudes_con_sesiones[sesion.id_solicitud] = []
            solicitudes_con_sesiones[sesion.id_solicitud].append(sesion)
        
        # Mostrar progreso para cada solicitud
        for solicitud in self.solicitudes:
            if solicitud.id_solicitud in solicitudes_con_sesiones:
                sesiones_solicitud = solicitudes_con_sesiones[solicitud.id_solicitud]
                self.create_progreso_card_mejorada(solicitud, sesiones_solicitud)
    
    def create_progreso_card_mejorada(self, solicitud: Solicitud, sesiones: List[Sesion]):
        """Crea una card de progreso mejorada"""
        # Calcular progreso
        progreso_calc = SolicitudConProgreso(solicitud, sesiones)
        progreso = progreso_calc.calcular_progreso()
        
        sesiones_realizadas = [s for s in sesiones if s.tipo_sesion == "Realizada"]
        sesiones_planificadas = [s for s in sesiones if s.tipo_sesion == "Planificada"]
        
        # Determinar estado
        porcentaje = progreso['porcentaje']
        if porcentaje >= 100:
            estado = "🟢 Completado"
            estado_color = '#4CAF50'
        elif porcentaje >= 50:
            estado = "🟡 En progreso"
            estado_color = '#FF9800'
        else:
            estado = "🔴 Pendiente"
            estado_color = '#F44336'
        
        # Verificar si está atrasado (sin sesiones en 7 días)
        atrasado = False
        if sesiones_realizadas and porcentaje < 100:
            ultima_fecha = max(s.fecha_sesion for s in sesiones_realizadas)
            dias_sin_sesion = (date.today() - ultima_fecha).days
            if dias_sin_sesion > 7:
                atrasado = True
        
        # Card
        card = tk.Frame(
            self.progreso_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        card.pack(fill=tk.X, pady=5)
        
        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.X, padx=15, pady=12)
        
        # Header
        header = tk.Frame(content, bg='white')
        header.pack(fill=tk.X, pady=(0, 8))
        
        # ID y nombre
        tk.Label(
            header,
            text=f"{solicitud.id_solicitud} - {solicitud.nombre_solicitante}",
            bg='white',
            fg='#333',
            font=(self.theme.FONTS['family'], 10, 'bold'),
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # Estado
        estado_label = tk.Label(
            header,
            text=estado,
            bg=estado_color,
            fg='white',
            font=(self.theme.FONTS['family'], 9, 'bold'),
            padx=8,
            pady=2
        )
        estado_label.pack(side=tk.RIGHT)
        
        # Servicio
        tk.Label(
            content,
            text=solicitud.servicio_solicitado,
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9),
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 8))
        
        # Barra de progreso
        progress_frame = tk.Frame(content, bg='white')
        progress_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Background
        progress_bg = tk.Frame(progress_frame, bg='#E0E0E0', height=24)
        progress_bg.pack(fill=tk.X)
        
        # Barra
        width_percent = progreso['porcentaje']
        if width_percent > 0:
            bar_color = '#4CAF50' if width_percent >= 100 else '#2196F3'
            progress_bar = tk.Frame(progress_bg, bg=bar_color, height=24)
            progress_bar.place(relwidth=width_percent/100, relheight=1)
            
            # Texto en barra
            tk.Label(
                progress_bar,
                text=f"{width_percent:.0f}%",
                bg=bar_color,
                fg='white',
                font=(self.theme.FONTS['family'], 10, 'bold')
            ).pack(expand=True)
        
        # Detalles
        tk.Label(
            content,
            text=progreso['detalles'],
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9)
        ).pack(fill=tk.X, pady=(0, 8))
        
        # Info de sesiones
        info_frame = tk.Frame(content, bg='white')
        info_frame.pack(fill=tk.X)
        
        # Última y próxima
        info_text = []
        
        if sesiones_realizadas:
            ultima_fecha = max(s.fecha_sesion for s in sesiones_realizadas)
            info_text.append(f"✅ {len(sesiones_realizadas)} realizada{'s' if len(sesiones_realizadas) != 1 else ''} (última: {ultima_fecha.strftime('%d/%m/%Y')})")
        else:
            info_text.append(f"✅ 0 realizadas")
        
        if sesiones_planificadas:
            proxima_fecha = min(s.fecha_sesion for s in sesiones_planificadas)
            info_text.append(f"📅 {len(sesiones_planificadas)} planificada{'s' if len(sesiones_planificadas) != 1 else ''} (próxima: {proxima_fecha.strftime('%d/%m/%Y')})")
        
        # Alerta si está atrasado
        if atrasado:
            info_text.append(f"⚠️ Sin sesiones desde hace {dias_sin_sesion} días")
        
        for texto in info_text:
            tk.Label(
                info_frame,
                text=texto,
                bg='white',
                fg='#666',
                font=(self.theme.FONTS['family'], 8),
                anchor='w'
            ).pack(fill=tk.X)
    
    def load_data(self):
        """Carga sesiones y solicitudes desde Google Sheets"""
        try:
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("Cargando sesiones...")
            
            # Limpiar caché
            sheets_manager.clear_cache()
            
            # Cargar sesiones
            data_sesiones = sheets_manager.get_all_data('Sesiones')
            if len(data_sesiones) > 1:
                self.sesiones = [Sesion.from_sheet_row(row) for row in data_sesiones[1:]]
            else:
                self.sesiones = []
            
            # Cargar solicitudes
            data_solicitudes = sheets_manager.get_all_data('Solicitudes')
            if len(data_solicitudes) > 1:
                self.solicitudes = [Solicitud.from_sheet_row(row) for row in data_solicitudes[1:]]
            else:
                self.solicitudes = []
            
            # Actualizar UI
            self.update_sesiones_cards()
            self.update_progreso()
            self.update_summary()
            self.crear_calendario()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status(f"✅ {len(self.sesiones)} sesiones cargadas")
            
            logger.info(f"🔄 Datos actualizados: {len(self.sesiones)} sesiones, {len(self.solicitudes)} solicitudes")
            
        except Exception as e:
            logger.error(f"Error al cargar datos: {e}")
            self.sesiones = []
            self.solicitudes = []
            messagebox.showerror("Error", f"Error al cargar datos:\n{e}")
    
    def nueva_sesion(self, fecha=None):
        """Crea una nueva sesión"""
        from src.gui.formulario_sesion_nuevo import FormularioSesion
        FormularioSesion(self.main_window, self, fecha_inicial=fecha)
    
    def planificar_sesion(self):
        """Planifica una sesión futura"""
        from src.gui.formulario_sesion_nuevo import FormularioSesion
        FormularioSesion(self.main_window, self, es_planificada=True)
    
    def editar_sesion_directa(self, sesion: Sesion):
        """Edita una sesión directamente desde la card"""
        from src.gui.formulario_sesion_nuevo import FormularioSesion
        FormularioSesion(self.main_window, self, sesion=sesion)
    
    def eliminar_sesion_directa(self, sesion: Sesion):
        """Elimina una sesión directamente desde la card"""
        if not messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta sesión?"):
            return
        
        try:
            # Buscar índice en Sheets
            data = sheets_manager.get_all_data('Sesiones')
            row_index = None
            
            for i, row in enumerate(data[1:], start=2):
                if len(row) > 0 and row[0] == sesion.id_sesion:
                    row_index = i
                    break
            
            if row_index:
                sheets_manager.delete_row('Sesiones', row_index)
                logger.info(f"✅ Sesión eliminada: {sesion.id_sesion}")
                
                # Recargar
                self.load_data()
                messagebox.showinfo("Éxito", "Sesión eliminada correctamente")
            else:
                messagebox.showerror("Error", "No se encontró la sesión en la base de datos")
            
        except Exception as e:
            logger.error(f"Error al eliminar sesión: {e}")
            messagebox.showerror("Error", f"Error al eliminar:\n{e}")
