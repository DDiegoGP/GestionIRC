"""
Dashboard Ejecutivo ACTUALIZADO - Con sincronización de estados
Usa el calculador centralizado para mostrar información consistente
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, date
from typing import List
import json

from src.models.solicitud_real import Solicitud
from src.models.sesion import Sesion
from src.utils.calculador_estados import CalculadorEstados
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class DashboardSincronizado:
    """Dashboard con estados sincronizados usando calculador centralizado"""
    
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
        
        # Fila 1
        # KPI 1: Total Solicitudes
        self.kpi_total = self.create_kpi_card(
            kpi_container, 
            "📊", 
            "Total Solicitudes", 
            "0",
            "#2196F3",
            0, 0
        )
        
        # KPI 2: Pendientes
        self.kpi_pendientes = self.create_kpi_card(
            kpi_container,
            "🔴",
            "Pendientes",
            "0",
            "#F44336",
            0, 1
        )
        
        # KPI 3: En Proceso
        self.kpi_proceso = self.create_kpi_card(
            kpi_container,
            "🟡",
            "En Proceso",
            "0",
            "#FF9800",
            0, 2
        )
        
        # Fila 2
        # KPI 4: Completados
        self.kpi_completados = self.create_kpi_card(
            kpi_container,
            "🟢",
            "Completados",
            "0",
            "#4CAF50",
            1, 0
        )
        
        # KPI 5: Sesiones Hoy
        self.kpi_sesiones_hoy = self.create_kpi_card(
            kpi_container,
            "📅",
            "Sesiones Hoy",
            "0",
            "#9C27B0",
            1, 1
        )
        
        # KPI 6: Atrasados
        self.kpi_atrasados = self.create_kpi_card(
            kpi_container,
            "⚠️",
            "Atrasados",
            "0",
            "#FF5722",
            1, 2
        )
    
    def create_kpi_card(self, parent, icono, titulo, valor, color, row, col):
        """Crea una tarjeta KPI"""
        # Card
        card = tk.Frame(
            parent,
            bg='white',
            relief='solid',
            borderwidth=1,
            highlightbackground='#E0E0E0',
            highlightthickness=1
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        
        # Contenido
        content = tk.Frame(card, bg='white')
        content.pack(expand=True, padx=20, pady=15)
        
        # Icono
        tk.Label(
            content,
            text=icono,
            bg='white',
            font=(self.theme.FONTS['family'], 32)
        ).pack()
        
        # Valor
        valor_label = tk.Label(
            content,
            text=valor,
            bg='white',
            fg=color,
            font=(self.theme.FONTS['family'], 32, 'bold')
        )
        valor_label.pack()
        
        # Título
        tk.Label(
            content,
            text=titulo,
            bg='white',
            fg='#666',
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'])
        ).pack()
        
        # Guardar referencia al label del valor
        return valor_label
    
    def create_alerts_section(self, parent):
        """Crea la sección de alertas"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title = self.theme.create_title_label(card, "⚠️ Requieren Atención")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para alertas
        self.alerts_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        self.alerts_frame.pack(fill=tk.X)
    
    def create_charts_section(self, parent):
        """Crea la sección de gráficos"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Título
        title = self.theme.create_title_label(card, "📈 Sesiones por Mes")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para gráfico
        self.chart_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
    
    def create_activity_section(self, parent):
        """Crea la sección de actividad reciente"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 20))
        
        # Título
        title = self.theme.create_title_label(card, "🕐 Actividad Reciente")
        title.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame para actividad
        self.activity_frame = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        self.activity_frame.pack(fill=tk.X)
    
    def load_data(self):
        """Carga datos desde Google Sheets"""
        try:
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("Cargando datos del dashboard...")
            
            # Limpiar caché
            sheets_manager.clear_cache()
            
            # Cargar solicitudes
            data_solicitudes = sheets_manager.get_all_data('Solicitudes')
            if len(data_solicitudes) > 1:
                self.solicitudes = [Solicitud.from_sheet_row(row) for row in data_solicitudes[1:]]
            else:
                self.solicitudes = []
            
            # Cargar sesiones
            data_sesiones = sheets_manager.get_all_data('Sesiones')
            if len(data_sesiones) > 1:
                self.sesiones = [Sesion.from_sheet_row(row) for row in data_sesiones[1:]]
            else:
                self.sesiones = []
            
            logger.info(f"📊 Dashboard: {len(self.solicitudes)} solicitudes, {len(self.sesiones)} sesiones")
            
            # Actualizar UI
            self.update_kpis()
            self.update_alerts()
            self.update_chart()
            self.update_activity()
            
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("✅ Dashboard actualizado")
            
        except Exception as e:
            logger.error(f"Error al cargar datos del dashboard: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def update_kpis(self):
        """Actualiza los KPIs usando el calculador centralizado"""
        # Calcular resumen con calculador centralizado
        resumen = CalculadorEstados.calcular_resumen_general(self.solicitudes, self.sesiones)
        
        # Actualizar valores
        self.kpi_total.config(text=str(resumen['total_solicitudes']))
        self.kpi_pendientes.config(text=str(resumen['pendientes']))
        self.kpi_proceso.config(text=str(resumen['en_proceso']))
        self.kpi_completados.config(text=str(resumen['completados']))
        self.kpi_sesiones_hoy.config(text=str(resumen['sesiones_hoy']))
        self.kpi_atrasados.config(text=str(resumen['atrasados']))
        
        logger.info(f"✅ KPIs actualizados: {resumen['total_solicitudes']} solicitudes, "
                   f"{resumen['pendientes']} pendientes, "
                   f"{resumen['en_proceso']} en proceso, "
                   f"{resumen['completados']} completados")
    
    def update_alerts(self):
        """Actualiza la sección de alertas"""
        # Limpiar
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
        
        # Agrupar sesiones por solicitud
        sesiones_por_solicitud = {}
        for sesion in self.sesiones:
            if sesion.id_solicitud not in sesiones_por_solicitud:
                sesiones_por_solicitud[sesion.id_solicitud] = []
            sesiones_por_solicitud[sesion.id_solicitud].append(sesion)
        
        # Encontrar solicitudes que necesitan atención
        alertas = []
        
        for solicitud in self.solicitudes:
            sesiones = sesiones_por_solicitud.get(solicitud.id_solicitud, [])
            info = CalculadorEstados.calcular_estado_y_progreso(solicitud, sesiones)
            
            if info['necesita_atencion']:
                problema = ""
                if info['estado'] == 'Pendiente' and info['dias_sin_actividad'] > 10:
                    problema = f"Sin sesiones ({info['dias_sin_actividad']} días)"
                elif info['esta_atrasado']:
                    problema = f"{info['dias_sin_actividad']} días sin actividad"
                
                alertas.append({
                    'solicitud': solicitud,
                    'problema': problema,
                    'estado': info['estado']
                })
        
        # Mostrar alertas
        if alertas:
            for alerta in alertas[:5]:  # Máximo 5
                self.create_alert_item(
                    alerta['solicitud'],
                    alerta['problema'],
                    alerta['estado']
                )
        else:
            # Mensaje de todo OK
            tk.Label(
                self.alerts_frame,
                text="✅ No hay servicios que requieran atención inmediata",
                bg=self.theme.COLORS['card_bg'],
                fg='#4CAF50',
                font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
                pady=20
            ).pack()
    
    def create_alert_item(self, solicitud: Solicitud, problema: str, estado: str):
        """Crea un item de alerta"""
        item = tk.Frame(
            self.alerts_frame,
            bg='#FFF3E0',
            relief='solid',
            borderwidth=1
        )
        item.pack(fill=tk.X, pady=5)
        
        content = tk.Frame(item, bg='#FFF3E0')
        content.pack(fill=tk.X, padx=15, pady=10)
        
        # Estado icono
        icono = CalculadorEstados.get_icono_estado(estado)
        tk.Label(
            content,
            text=icono,
            bg='#FFF3E0',
            font=(self.theme.FONTS['family'], 16)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Info
        info_frame = tk.Frame(content, bg='#FFF3E0')
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            info_frame,
            text=f"{solicitud.id_solicitud} - {solicitud.nombre_solicitante}",
            bg='#FFF3E0',
            fg='#333',
            font=(self.theme.FONTS['family'], 10, 'bold'),
            anchor='w'
        ).pack(fill=tk.X)
        
        tk.Label(
            info_frame,
            text=problema,
            bg='#FFF3E0',
            fg='#666',
            font=(self.theme.FONTS['family'], 9),
            anchor='w'
        ).pack(fill=tk.X)
    
    def update_chart(self):
        """Actualiza el gráfico de sesiones"""
        # Limpiar
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        try:
            import matplotlib
            matplotlib.use('Agg')
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.pyplot as plt
            
            # Preparar datos
            # Últimos 6 meses
            hoy = date.today()
            meses = []
            sesiones_realizadas_por_mes = []
            sesiones_planificadas_por_mes = []
            
            for i in range(5, -1, -1):
                mes = hoy.month - i
                anio = hoy.year
                while mes <= 0:
                    mes += 12
                    anio -= 1
                
                meses.append(f"{mes:02d}/{anio}")
                
                # Contar sesiones del mes
                realizadas = 0
                planificadas = 0
                
                for sesion in self.sesiones:
                    if sesion.fecha_sesion.month == mes and sesion.fecha_sesion.year == anio:
                        if sesion.tipo_sesion == "Realizada":
                            realizadas += 1
                        else:
                            planificadas += 1
                
                sesiones_realizadas_por_mes.append(realizadas)
                sesiones_planificadas_por_mes.append(planificadas)
            
            # Crear gráfico
            fig = Figure(figsize=(10, 4), dpi=80)
            ax = fig.add_subplot(111)
            
            x = range(len(meses))
            width = 0.35
            
            # Barras
            ax.bar([i - width/2 for i in x], sesiones_realizadas_por_mes, width, 
                   label='Realizadas', color='#4CAF50')
            ax.bar([i + width/2 for i in x], sesiones_planificadas_por_mes, width,
                   label='Planificadas', color='#2196F3')
            
            ax.set_xlabel('Mes')
            ax.set_ylabel('Número de Sesiones')
            ax.set_xticks(x)
            ax.set_xticklabels(meses)
            ax.legend()
            ax.grid(axis='y', alpha=0.3)
            
            fig.tight_layout()
            
            # Mostrar en tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            logger.error(f"Error al crear gráfico: {e}")
            tk.Label(
                self.chart_frame,
                text="⚠️ Error al generar gráfico",
                bg=self.theme.COLORS['card_bg'],
                fg='#666'
            ).pack(pady=20)
    
    def update_activity(self):
        """Actualiza la actividad reciente"""
        # Limpiar
        for widget in self.activity_frame.winfo_children():
            widget.destroy()
        
        # Últimas 5 sesiones
        sesiones_recientes = sorted(self.sesiones, key=lambda s: s.fecha_sesion, reverse=True)[:5]
        
        if sesiones_recientes:
            for sesion in sesiones_recientes:
                self.create_activity_item(sesion)
        else:
            tk.Label(
                self.activity_frame,
                text="No hay actividad reciente",
                bg=self.theme.COLORS['card_bg'],
                fg='#999',
                pady=20
            ).pack()
    
    def create_activity_item(self, sesion: Sesion):
        """Crea un item de actividad"""
        item = tk.Frame(self.activity_frame, bg=self.theme.COLORS['card_bg'])
        item.pack(fill=tk.X, pady=5)
        
        # Fecha
        fecha_str = sesion.fecha_sesion.strftime("%d/%m/%Y")
        tk.Label(
            item,
            text=fecha_str,
            bg=self.theme.COLORS['card_bg'],
            fg='#666',
            font=(self.theme.FONTS['family'], 9),
            width=12
        ).pack(side=tk.LEFT)
        
        # Tipo
        tipo_color = '#4CAF50' if sesion.tipo_sesion == "Realizada" else '#2196F3'
        tipo_label = tk.Label(
            item,
            text=sesion.tipo_sesion,
            bg=tipo_color,
            fg='white',
            font=(self.theme.FONTS['family'], 8, 'bold'),
            padx=6,
            pady=2
        )
        tipo_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Descripción
        desc = f"{sesion.id_solicitud} - {sesion.servicio}"
        tk.Label(
            item,
            text=desc,
            bg=self.theme.COLORS['card_bg'],
            fg='#333',
            font=(self.theme.FONTS['family'], 9),
            anchor='w'
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
