"""
Panel de Sesiones - Con calendario visual y progreso
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


class SesionesPanel:
    """Panel de gestión de sesiones con calendario"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        
        self.sesiones = []
        self.solicitudes = []
        self.mes_actual = date.today().month
        self.anio_actual = date.today().year
        self.dia_seleccionado = None
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Construye la interfaz del panel"""
        # Frame principal
        main_frame = tk.Frame(self.parent, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_frame)
        
        # Contenedor principal con dos paneles
        content_frame = tk.Frame(main_frame, bg=self.theme.COLORS['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Panel izquierdo: Sesiones y Progreso
        left_panel = tk.Frame(content_frame, bg=self.theme.COLORS['bg_main'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.create_sesiones_section(left_panel)
        self.create_progreso_section(left_panel)
        
        # Panel derecho: Calendario
        right_panel = tk.Frame(content_frame, bg=self.theme.COLORS['bg_main'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.create_calendario_section(right_panel)
    
    def create_header(self, parent):
        """Crea el header del panel"""
        header_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = self.theme.create_header_label(header_frame, "🔬 Sesiones de Servicio")
        title.pack(side=tk.LEFT)
        
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
    
    def create_sesiones_section(self, parent):
        """Crea la sección de lista de sesiones"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Título
        title_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = self.theme.create_title_label(title_frame, "📋 Sesiones Registradas")
        title.pack(side=tk.LEFT)
        
        # Filtros
        filter_frame = tk.Frame(title_frame, bg=self.theme.COLORS['card_bg'])
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            filter_frame,
            text="Tipo:",
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small'])
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_tipo = ttk.Combobox(
            filter_frame,
            values=["Todas", "Realizadas", "Planificadas"],
            state='readonly',
            width=12
        )
        self.filter_tipo.set("Todas")
        self.filter_tipo.pack(side=tk.LEFT)
        self.filter_tipo.bind('<<ComboboxSelected>>', lambda e: self.update_sesiones_tree())
        
        # Tabla
        table_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        
        # Treeview
        columns = ('fecha', 'tipo', 'solicitud', 'servicio', 'detalles', 'operador')
        self.sesiones_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=8
        )
        
        # Configurar columnas
        self.sesiones_tree.heading('fecha', text='Fecha')
        self.sesiones_tree.heading('tipo', text='Tipo')
        self.sesiones_tree.heading('solicitud', text='Solicitud')
        self.sesiones_tree.heading('servicio', text='Servicio')
        self.sesiones_tree.heading('detalles', text='Detalles')
        self.sesiones_tree.heading('operador', text='Operador')
        
        self.sesiones_tree.column('fecha', width=100)
        self.sesiones_tree.column('tipo', width=90)
        self.sesiones_tree.column('solicitud', width=120)
        self.sesiones_tree.column('servicio', width=150)
        self.sesiones_tree.column('detalles', width=180)
        self.sesiones_tree.column('operador', width=100)
        
        vsb.config(command=self.sesiones_tree.yview)
        hsb.config(command=self.sesiones_tree.xview)
        
        # Pack
        self.sesiones_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind doble click
        self.sesiones_tree.bind('<Double-1>', lambda e: self.editar_sesion())
        
        # Botones de acción
        btn_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        btn_editar = self.theme.create_secondary_button(
            btn_frame,
            "✏️ Editar",
            self.editar_sesion
        )
        btn_editar.pack(side=tk.LEFT, padx=(0, 5))
        
        btn_eliminar = tk.Button(
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
        btn_eliminar.pack(side=tk.LEFT)
    
    def create_progreso_section(self, parent):
        """Crea la sección de progreso de solicitudes"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = self.theme.create_title_label(card, "📊 Progreso por Solicitud")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame scrollable
        canvas = tk.Canvas(card, bg=self.theme.COLORS['card_bg'], highlightthickness=0, height=250)
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
    
    def create_calendario_section(self, parent):
        """Crea la sección del calendario"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True)
        
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
            self.update_sesiones_tree()
            self.update_progreso()
            self.crear_calendario()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status(f"✅ {len(self.sesiones)} sesiones cargadas")
            
            logger.info(f"🔄 Datos actualizados: {len(self.sesiones)} sesiones, {len(self.solicitudes)} solicitudes")
            
        except Exception as e:
            logger.error(f"Error al cargar datos: {e}")
            self.sesiones = []
            self.solicitudes = []
            messagebox.showerror("Error", f"Error al cargar datos:\n{e}")
    
    def update_sesiones_tree(self):
        """Actualiza la tabla de sesiones"""
        # Limpiar
        for item in self.sesiones_tree.get_children():
            self.sesiones_tree.delete(item)
        
        # Filtrar
        filtro = self.filter_tipo.get()
        sesiones_filtradas = self.sesiones
        
        if filtro == "Realizadas":
            sesiones_filtradas = [s for s in self.sesiones if s.tipo_sesion == "Realizada"]
        elif filtro == "Planificadas":
            sesiones_filtradas = [s for s in self.sesiones if s.tipo_sesion == "Planificada"]
        
        # Ordenar por fecha (más reciente primero)
        sesiones_filtradas = sorted(sesiones_filtradas, key=lambda s: s.fecha_sesion, reverse=True)
        
        # Agregar a tabla
        for sesion in sesiones_filtradas:
            fecha_str = sesion.fecha_sesion.strftime("%d/%m/%Y")
            detalles = self.get_detalles_sesion(sesion)
            
            self.sesiones_tree.insert('', tk.END, values=(
                fecha_str,
                sesion.tipo_sesion,
                sesion.id_solicitud,
                sesion.servicio,
                detalles,
                sesion.operador
            ), tags=(sesion.id_sesion,))
    
    def get_detalles_sesion(self, sesion: Sesion) -> str:
        """Obtiene el texto de detalles de una sesión"""
        detalles = []
        
        if sesion.canisters_procesados > 0:
            detalles.append(f"{sesion.canisters_procesados} canisters")
        
        if sesion.dosis_aplicada_gy > 0:
            detalles.append(f"{sesion.dosis_aplicada_gy} Gy")
        
        if sesion.mes_gestion:
            detalles.append(f"Mes: {sesion.mes_gestion}")
        
        if sesion.dosimetros_gestionados > 0:
            detalles.append(f"{sesion.dosimetros_gestionados} dosímetros")
        
        if sesion.horas_contador > 0:
            detalles.append(f"{sesion.horas_contador} h")
        
        if sesion.descripcion_residuos:
            detalles.append(sesion.descripcion_residuos[:30])
        
        return " | ".join(detalles) if detalles else "Sin detalles"
    
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
                self.create_progreso_card(solicitud, sesiones_solicitud)
    
    def create_progreso_card(self, solicitud: Solicitud, sesiones: List[Sesion]):
        """Crea una card de progreso para una solicitud"""
        # Calcular progreso
        progreso_calc = SolicitudConProgreso(solicitud, sesiones)
        progreso = progreso_calc.calcular_progreso()
        
        # Card
        card = tk.Frame(
            self.progreso_frame,
            bg='white',
            relief='solid',
            borderwidth=1
        )
        card.pack(fill=tk.X, pady=5)
        
        content = tk.Frame(card, bg='white')
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Header
        header = tk.Frame(content, bg='white')
        header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            header,
            text=f"{solicitud.id_solicitud} - {solicitud.nombre_solicitante}",
            bg='white',
            fg='#333',
            font=(self.theme.FONTS['family'], 10, 'bold'),
            anchor='w'
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header,
            text=solicitud.servicio_solicitado,
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9),
            anchor='e'
        ).pack(side=tk.RIGHT)
        
        # Barra de progreso
        progress_frame = tk.Frame(content, bg='white')
        progress_frame.pack(fill=tk.X, pady=5)
        
        # Background
        progress_bg = tk.Frame(progress_frame, bg='#E0E0E0', height=20)
        progress_bg.pack(fill=tk.X)
        
        # Barra
        width_percent = progreso['porcentaje']
        if width_percent > 0:
            progress_bar = tk.Frame(progress_bg, bg='#4CAF50', height=20)
            progress_bar.place(relwidth=width_percent/100, relheight=1)
            
            # Texto en barra
            tk.Label(
                progress_bar,
                text=f"{width_percent:.0f}%",
                bg='#4CAF50',
                fg='white',
                font=(self.theme.FONTS['family'], 9, 'bold')
            ).pack(expand=True)
        
        # Detalles
        detalles_frame = tk.Frame(content, bg='white')
        detalles_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(
            detalles_frame,
            text=progreso['detalles'],
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9)
        ).pack(side=tk.LEFT)
        
        sesiones_realizadas = [s for s in sesiones if s.tipo_sesion == "Realizada"]
        sesiones_planificadas = [s for s in sesiones if s.tipo_sesion == "Planificada"]
        
        tk.Label(
            detalles_frame,
            text=f"✅ {len(sesiones_realizadas)} | 📅 {len(sesiones_planificadas)}",
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], 9)
        ).pack(side=tk.RIGHT)
    
    def nueva_sesion(self, fecha=None):
        """Crea una nueva sesión"""
        from src.gui.formulario_sesion_nuevo import FormularioSesion
        FormularioSesion(self.main_window, self, fecha_inicial=fecha)
    
    def planificar_sesion(self):
        """Planifica una sesión futura"""
        from src.gui.formulario_sesion_nuevo import FormularioSesion
        FormularioSesion(self.main_window, self, es_planificada=True)
    
    def editar_sesion(self):
        """Edita la sesión seleccionada"""
        selection = self.sesiones_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una sesión para editar")
            return
        
        # Obtener ID de sesión de los tags
        tags = self.sesiones_tree.item(selection[0])['tags']
        if not tags:
            return
        
        id_sesion = tags[0]
        sesion = next((s for s in self.sesiones if s.id_sesion == id_sesion), None)
        
        if sesion:
            from src.gui.formulario_sesion_nuevo import FormularioSesion
            FormularioSesion(self.main_window, self, sesion=sesion)
    
    def eliminar_sesion(self):
        """Elimina la sesión seleccionada"""
        selection = self.sesiones_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una sesión para eliminar")
            return
        
        if not messagebox.askyesno("Confirmar", "¿Estás seguro de eliminar esta sesión?"):
            return
        
        try:
            tags = self.sesiones_tree.item(selection[0])['tags']
            if not tags:
                return
            
            id_sesion = tags[0]
            
            # Buscar índice en Sheets
            data = sheets_manager.get_all_data('Sesiones')
            row_index = None
            
            for i, row in enumerate(data[1:], start=2):
                if len(row) > 0 and row[0] == id_sesion:
                    row_index = i
                    break
            
            if row_index:
                sheets_manager.delete_row('Sesiones', row_index)
                logger.info(f"✅ Sesión eliminada: {id_sesion}")
                
                # Recargar
                self.load_data()
                messagebox.showinfo("Éxito", "Sesión eliminada correctamente")
            else:
                messagebox.showerror("Error", "No se encontró la sesión en la base de datos")
            
        except Exception as e:
            logger.error(f"Error al eliminar sesión: {e}")
            messagebox.showerror("Error", f"Error al eliminar:\n{e}")
