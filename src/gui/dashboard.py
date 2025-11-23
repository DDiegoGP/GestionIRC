"""
Dashboard Ejecutivo - Estilo Microsoft 365
Panel principal con KPIs, gráficos y alertas
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import List
import json

from src.models.solicitud_real import Solicitud
from src.models.sesion_real import Sesion
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class DashboardPanel:
    """Dashboard ejecutivo con métricas principales"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        self.solicitudes: List[Solicitud] = []
        self.sesiones: List[Sesion] = []
        
        self.build_ui()
        self.load_data()
    
    def build_ui(self):
        """Construye la interfaz del dashboard"""
        # Frame principal con scroll
        main_frame = tk.Frame(self.parent, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame, bg=self.theme.COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        
        # Frame scrolleable
        scrollable_frame = tk.Frame(canvas, bg=self.theme.COLORS['bg_main'])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Título
        header_frame = tk.Frame(scrollable_frame, bg=self.theme.COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = self.theme.create_header_label(header_frame, "📊 Dashboard Ejecutivo")
        title.pack(side=tk.LEFT)
        
        # Botón actualizar
        btn_refresh = self.theme.create_secondary_button(
            header_frame,
            "🔄 Actualizar",
            self.load_data
        )
        btn_refresh.pack(side=tk.RIGHT)
        
        # KPIs principales
        self.create_kpi_section(scrollable_frame)
        
        # Alertas
        self.create_alerts_section(scrollable_frame)
        
        # Gráficos
        self.create_charts_section(scrollable_frame)
        
        # Actividad reciente
        self.create_activity_section(scrollable_frame)
        
        # Bind scroll
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def create_kpi_section(self, parent):
        """Crea la sección de KPIs principales"""
        # Frame contenedor
        kpi_container = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        kpi_container.pack(fill=tk.X, pady=(0, 20))
        
        # Grid de 3x2 para 6 KPIs
        for i in range(2):  # 2 filas
            kpi_container.grid_rowconfigure(i, weight=1)
        for i in range(3):  # 3 columnas
            kpi_container.grid_columnconfigure(i, weight=1, uniform="kpi")
        
        # KPI 1: Total Solicitudes
        self.kpi_total = self.create_kpi_card(
            kpi_container, 
            "📋", 
            "Total Solicitudes", 
            "0",
            "Registradas en sistema",
            self.theme.COLORS['primary']
        )
        self.kpi_total.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # KPI 2: Pendientes
        self.kpi_pendientes = self.create_kpi_card(
            kpi_container,
            "⏳",
            "Pendientes",
            "0",
            "Requieren atención",
            "#FFB900"
        )
        self.kpi_pendientes.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # KPI 3: En Progreso
        self.kpi_progreso = self.create_kpi_card(
            kpi_container,
            "🕓",
            "En Progreso",
            "0",
            "Servicios activos",
            "#00B7C3"
        )
        self.kpi_progreso.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        # KPI 4: Completados
        self.kpi_completados = self.create_kpi_card(
            kpi_container,
            "✅",
            "Completados",
            "0",
            "Servicios finalizados",
            "#107C10"
        )
        self.kpi_completados.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # KPI 5: Alertas
        self.kpi_alertas = self.create_kpi_card(
            kpi_container,
            "⚠️",
            "Alertas",
            "0",
            "Pendientes > 7 días",
            "#D13438"
        )
        self.kpi_alertas.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # KPI 6: Facturación Mes
        self.kpi_facturacion = self.create_kpi_card(
            kpi_container,
            "💰",
            "Mes Actual",
            "0€",
            datetime.now().strftime("%B %Y"),
            "#8764B8"
        )
        self.kpi_facturacion.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
    
    def create_kpi_card(self, parent, icon, title, value, subtitle, color):
        """Crea una card de KPI"""
        # Card frame
        card = tk.Frame(parent, bg='white', relief='flat', bd=1, highlightthickness=1,
                       highlightbackground=self.theme.COLORS['border'])
        
        # Frame interior con padding
        inner = tk.Frame(card, bg='white')
        inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icono y título
        header = tk.Frame(inner, bg='white')
        header.pack(fill=tk.X, pady=(0, 10))
        
        icon_label = tk.Label(
            header,
            text=icon,
            font=(self.theme.FONTS['family'], 24),
            bg='white',
            fg=color
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(
            header,
            text=title,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg='white',
            fg=self.theme.COLORS['text_secondary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Valor principal
        value_label = tk.Label(
            inner,
            text=value,
            font=(self.theme.FONTS['family'], 36, 'bold'),
            bg='white',
            fg=color
        )
        value_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            inner,
            text=subtitle,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg='white',
            fg=self.theme.COLORS['text_tertiary']
        )
        subtitle_label.pack(anchor=tk.W)
        
        # Guardar referencia al label del valor
        card.value_label = value_label
        
        return card
    
    def create_alerts_section(self, parent):
        """Crea la sección de alertas"""
        # Card contenedor
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title = self.theme.create_title_label(card, "⚠️ Centro de Alertas")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Separador
        sep = ttk.Separator(card, orient='horizontal')
        sep.pack(fill=tk.X, pady=(0, 10))
        
        # Frame para alertas
        self.alerts_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        self.alerts_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensaje inicial
        no_alerts = tk.Label(
            self.alerts_frame,
            text="✅ No hay alertas en este momento",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        )
        no_alerts.pack(pady=20)
    
    def create_charts_section(self, parent):
        """Crea la sección de gráficos"""
        # Container de 2 columnas
        charts_container = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        charts_container.pack(fill=tk.X, pady=(0, 20))
        
        charts_container.grid_columnconfigure(0, weight=1, uniform="chart")
        charts_container.grid_columnconfigure(1, weight=1, uniform="chart")
        
        # Card 1: Distribución por Servicio
        card1 = self.theme.create_card_frame(charts_container)
        card1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        title1 = self.theme.create_title_label(card1, "📊 Por Tipo de Servicio")
        title1.pack(anchor=tk.W, pady=(0, 10))
        
        sep1 = ttk.Separator(card1, orient='horizontal')
        sep1.pack(fill=tk.X, pady=(0, 10))
        
        self.servicios_frame = tk.Frame(card1, bg=self.theme.COLORS['card_bg'])
        self.servicios_frame.pack(fill=tk.BOTH, expand=True)
        
        # Card 2: Distribución por Estado
        card2 = self.theme.create_card_frame(charts_container)
        card2.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        title2 = self.theme.create_title_label(card2, "📈 Por Estado")
        title2.pack(anchor=tk.W, pady=(0, 10))
        
        sep2 = ttk.Separator(card2, orient='horizontal')
        sep2.pack(fill=tk.X, pady=(0, 10))
        
        self.estados_frame = tk.Frame(card2, bg=self.theme.COLORS['card_bg'])
        self.estados_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_activity_section(self, parent):
        """Crea la sección de actividad reciente"""
        # Card contenedor
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title = self.theme.create_title_label(card, "📅 Actividad Reciente")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Separador
        sep = ttk.Separator(card, orient='horizontal')
        sep.pack(fill=tk.X, pady=(0, 10))
        
        # Lista de actividades
        self.activity_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        self.activity_frame.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Carga los datos desde Google Sheets"""
        try:
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("Cargando dashboard...")
            
            # Leer solicitudes
            data_sol = sheets_manager.get_all_data('Solicitudes')
            if len(data_sol) > 1:
                self.solicitudes = [Solicitud.from_sheet_row(row) for row in data_sol[1:]]
            else:
                self.solicitudes = []
            
            # Leer sesiones
            data_ses = sheets_manager.get_all_data('Sesiones')
            if len(data_ses) > 1:
                self.sesiones = [Sesion.from_sheet_row(row) for row in data_ses[1:]]
            else:
                self.sesiones = []
            
            # Actualizar métricas
            self.update_kpis()
            self.update_alerts()
            self.update_charts()
            self.update_activity()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("✅ Dashboard actualizado")
            
        except Exception as e:
            logger.error(f"Error al cargar datos del dashboard: {e}")
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("❌ Error al cargar dashboard")
    
    def update_kpis(self):
        """Actualiza los KPIs principales"""
        if not self.solicitudes:
            return
        
        # Total
        total = len(self.solicitudes)
        self.kpi_total.value_label.config(text=str(total))
        
        # Por estado
        pendientes = len([s for s in self.solicitudes if "Pendiente" in s.estado])
        en_progreso = len([s for s in self.solicitudes if "progreso" in s.estado])
        completados = len([s for s in self.solicitudes if "Completado" in s.estado])
        
        self.kpi_pendientes.value_label.config(text=str(pendientes))
        self.kpi_progreso.value_label.config(text=str(en_progreso))
        self.kpi_completados.value_label.config(text=str(completados))
        
        # Alertas (pendientes > 7 días)
        alertas = 0
        hoy = datetime.now().date()
        for sol in self.solicitudes:
            if "Pendiente" in sol.estado and sol.fecha_solicitud:
                dias = (hoy - sol.fecha_solicitud.date()).days
                if dias > 7:
                    alertas += 1
        
        self.kpi_alertas.value_label.config(text=str(alertas))
        
        # Facturación del mes
        mes_actual = datetime.now().month
        facturacion = 0
        
        for sesion in self.sesiones:
            if sesion.fecha_sesion and sesion.fecha_sesion.month == mes_actual:
                facturacion += sesion.coste_sesion
        
        self.kpi_facturacion.value_label.config(text=f"{facturacion:,.0f}€")
    
    def update_alerts(self):
        """Actualiza las alertas"""
        # Limpiar
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
        
        # Encontrar solicitudes con alertas
        alertas = []
        hoy = datetime.now().date()
        
        for sol in self.solicitudes:
            if "Pendiente" in sol.estado and sol.fecha_solicitud:
                dias = (hoy - sol.fecha_solicitud.date()).days
                if dias > 7:
                    alertas.append((sol, dias))
        
        if not alertas:
            # Sin alertas
            no_alerts = tk.Label(
                self.alerts_frame,
                text="✅ No hay alertas en este momento",
                font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal']),
                bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_secondary']
            )
            no_alerts.pack(pady=20)
        else:
            # Mostrar alertas
            for sol, dias in alertas[:5]:  # Máximo 5
                alert_frame = tk.Frame(
                    self.alerts_frame,
                    bg='#FFF4E5',
                    relief='flat',
                    bd=1,
                    highlightthickness=1,
                    highlightbackground='#FFB900'
                )
                alert_frame.pack(fill=tk.X, pady=5)
                
                inner = tk.Frame(alert_frame, bg='#FFF4E5')
                inner.pack(fill=tk.X, padx=15, pady=10)
                
                # Icono
                icon = tk.Label(
                    inner,
                    text="🚨",
                    font=(self.theme.FONTS['family'], 16),
                    bg='#FFF4E5'
                )
                icon.pack(side=tk.LEFT, padx=(0, 10))
                
                # Texto
                text_frame = tk.Frame(inner, bg='#FFF4E5')
                text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                title_text = tk.Label(
                    text_frame,
                    text=f"{sol.id_solicitud} - {sol.nombre_solicitante}",
                    font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
                    bg='#FFF4E5',
                    fg='#323130',
                    anchor=tk.W
                )
                title_text.pack(fill=tk.X)
                
                subtitle_text = tk.Label(
                    text_frame,
                    text=f"Pendiente desde hace {dias} días - {sol.servicio_solicitado}",
                    font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
                    bg='#FFF4E5',
                    fg='#605E5C',
                    anchor=tk.W
                )
                subtitle_text.pack(fill=tk.X)
            
            if len(alertas) > 5:
                more_label = tk.Label(
                    self.alerts_frame,
                    text=f"... y {len(alertas)-5} alertas más",
                    font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
                    bg=self.theme.COLORS['card_bg'],
                    fg=self.theme.COLORS['text_secondary']
                )
                more_label.pack(pady=10)
    
    def update_charts(self):
        """Actualiza los gráficos con barras simples"""
        # Limpiar
        for widget in self.servicios_frame.winfo_children():
            widget.destroy()
        for widget in self.estados_frame.winfo_children():
            widget.destroy()
        
        if not self.solicitudes:
            return
        
        # Distribución por servicio
        servicios_count = {}
        for sol in self.solicitudes:
            servicio = sol.servicio_solicitado
            servicios_count[servicio] = servicios_count.get(servicio, 0) + 1
        
        # Ordenar por cantidad
        servicios_sorted = sorted(servicios_count.items(), key=lambda x: x[1], reverse=True)
        
        # Mostrar top 5
        max_val = max([v for _, v in servicios_sorted]) if servicios_sorted else 1
        
        for servicio, count in servicios_sorted[:5]:
            self.create_bar_item(self.servicios_frame, servicio, count, max_val, self.theme.COLORS['primary'])
        
        # Distribución por estado
        estados_count = {}
        for sol in self.solicitudes:
            estado = sol.estado
            estados_count[estado] = estados_count.get(estado, 0) + 1
        
        # Colores por estado
        estado_colors = {
            "⏳ Pendiente": "#FFB900",
            "🕓 En progreso": "#00B7C3",
            "✅ Completado": "#107C10",
            "❌ Cancelado": "#D13438"
        }
        
        max_val_estado = max(estados_count.values()) if estados_count else 1
        
        for estado, count in estados_count.items():
            color = estado_colors.get(estado, self.theme.COLORS['primary'])
            self.create_bar_item(self.estados_frame, estado, count, max_val_estado, color)
    
    def create_bar_item(self, parent, label, value, max_value, color):
        """Crea un item de barra horizontal"""
        item_frame = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        item_frame.pack(fill=tk.X, pady=5)
        
        # Label
        label_text = tk.Label(
            item_frame,
            text=label,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            anchor=tk.W,
            width=25
        )
        label_text.pack(side=tk.LEFT)
        
        # Barra
        bar_container = tk.Frame(item_frame, bg=self.theme.COLORS['bg_secondary'], height=24)
        bar_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        percentage = (value / max_value) * 100 if max_value > 0 else 0
        
        bar = tk.Frame(bar_container, bg=color, height=24)
        bar.place(relwidth=percentage/100, relheight=1)
        
        # Valor
        value_label = tk.Label(
            item_frame,
            text=str(value),
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg=self.theme.COLORS['card_bg'],
            fg=color,
            width=4,
            anchor=tk.E
        )
        value_label.pack(side=tk.LEFT)
    
    def update_activity(self):
        """Actualiza la actividad reciente"""
        # Limpiar
        for widget in self.activity_frame.winfo_children():
            widget.destroy()
        
        if not self.solicitudes:
            return
        
        # Ordenar por fecha (más recientes primero)
        solicitudes_sorted = sorted(
            self.solicitudes,
            key=lambda x: x.fecha_solicitud if x.fecha_solicitud else datetime.min,
            reverse=True
        )
        
        # Mostrar últimas 5
        for sol in solicitudes_sorted[:5]:
            self.create_activity_item(sol)
    
    def create_activity_item(self, solicitud: Solicitud):
        """Crea un item de actividad"""
        item_frame = tk.Frame(
            self.activity_frame,
            bg='white',
            relief='flat',
            bd=1,
            highlightthickness=1,
            highlightbackground=self.theme.COLORS['border']
        )
        item_frame.pack(fill=tk.X, pady=5)
        
        inner = tk.Frame(item_frame, bg='white')
        inner.pack(fill=tk.X, padx=15, pady=10)
        
        # Fecha
        fecha_text = solicitud.fecha_solicitud.strftime("%d/%m/%Y %H:%M") if solicitud.fecha_solicitud else ""
        fecha_label = tk.Label(
            inner,
            text=fecha_text,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg='white',
            fg=self.theme.COLORS['text_tertiary'],
            width=15,
            anchor=tk.W
        )
        fecha_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Estado
        estado_label = tk.Label(
            inner,
            text=solicitud.estado,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg='white',
            fg=self.theme.COLORS['text_primary'],
            width=15,
            anchor=tk.W
        )
        estado_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Detalles
        text_frame = tk.Frame(inner, bg='white')
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_text = tk.Label(
            text_frame,
            text=f"{solicitud.id_solicitud} - {solicitud.nombre_solicitante}",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg='white',
            fg=self.theme.COLORS['text_primary'],
            anchor=tk.W
        )
        title_text.pack(fill=tk.X)
        
        subtitle_text = tk.Label(
            text_frame,
            text=solicitud.servicio_solicitado,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg='white',
            fg=self.theme.COLORS['text_secondary'],
            anchor=tk.W
        )
        subtitle_text.pack(fill=tk.X)
        
        # Coste
        coste_label = tk.Label(
            inner,
            text=f"{solicitud.coste_estimado_iva_0:.2f}€",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg='white',
            fg=self.theme.COLORS['primary'],
            width=10,
            anchor=tk.E
        )
        coste_label.pack(side=tk.LEFT)
