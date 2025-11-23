"""
Formulario de Sesión - Ventana Modal
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional

from src.models.sesion_real import Sesion
from src.models.solicitud_real import Solicitud
from src.constants_real import TIPOS_SERVICIOS, ESTADOS_SESION
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class FormularioSesion:
    """Formulario para crear/editar sesiones"""
    
    def __init__(self, main_window, sesiones_panel, sesion: Optional[Sesion] = None):
        self.main_window = main_window
        self.sesiones_panel = sesiones_panel
        self.theme = main_window.theme
        self.sesion = sesion
        self.es_edicion = sesion is not None
        
        # Variables de formulario
        self.vars = {}
        
        # Crear ventana
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Editar Sesión" if self.es_edicion else "Nueva Sesión")
        self.window.geometry("700x700")
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
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def build_ui(self):
        """Construye la interfaz del formulario"""
        # Frame principal con scroll
        main_frame = tk.Frame(self.window, bg=self.theme.COLORS['bg_main'])
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
        
        # Empaquetar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Título
        title = self.theme.create_header_label(
            scrollable_frame,
            "✏️ Editar Sesión" if self.es_edicion else "➕ Nueva Sesión"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Secciones del formulario
        self.create_section_identificacion(scrollable_frame)
        self.create_section_servicio(scrollable_frame)
        self.create_section_metricas(scrollable_frame)
        self.create_section_observaciones(scrollable_frame)
        
        # Botones
        self.create_buttons(scrollable_frame)
        
        # Bind scroll
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
    
    def create_section_identificacion(self, parent):
        """Sección de identificación"""
        section = self.create_section_frame(parent, "🆔 Identificación")
        
        # ID Solicitud (selector)
        self.add_combobox_field(
            section, 
            "ID Solicitud: *", 
            "id_solicitud",
            [s.id_solicitud for s in self.sesiones_panel.solicitudes]
        )
        
        # Fecha
        self.add_entry_field(section, "Fecha Sesión (DD/MM/YYYY): *", "fecha_sesion")
        if not self.es_edicion:
            self.vars['fecha_sesion'].insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        # Estado
        self.add_combobox_field(section, "Estado: *", "estado_servicio", ESTADOS_SESION)
    
    def create_section_servicio(self, parent):
        """Sección de servicio"""
        section = self.create_section_frame(parent, "🔬 Servicio")
        
        self.add_combobox_field(section, "Tipo Servicio: *", "servicio_sesion", TIPOS_SERVICIOS)
        self.add_entry_field(section, "Coste Sesión (€): *", "coste_sesion")
    
    def create_section_metricas(self, parent):
        """Sección de métricas"""
        section = self.create_section_frame(parent, "📊 Métricas del Servicio")
        
        self.add_entry_field(section, "Irradiaciones Realizadas:", "irradiaciones_realizadas")
        self.add_entry_field(section, "Dosis Suministrada (Gy):", "dosis_suministrada")
        self.add_entry_field(section, "Tiempo Usado (h):", "tiempo_usado_h")
        self.add_entry_field(section, "Tiempo Dosimetría (meses):", "tiempo_dosimetria_meses")
    
    def create_section_observaciones(self, parent):
        """Sección de observaciones"""
        section = self.create_section_frame(parent, "💬 Observaciones")
        
        row = tk.Frame(section, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.BOTH, expand=True, pady=5)
        
        text_widget = self.theme.create_text(row, height=4)
        text_widget.pack(fill=tk.BOTH, expand=True)
        self.vars['observaciones_sesion'] = text_widget
    
    def create_section_frame(self, parent, title):
        """Crea un frame de sección con título"""
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        title_label = self.theme.create_title_label(card, title)
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        sep = ttk.Separator(card, orient='horizontal')
        sep.pack(fill=tk.X, pady=(0, 10))
        
        return card
    
    def add_entry_field(self, parent, label_text, var_name, width=40):
        """Añade un campo de entrada"""
        row = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text=label_text, bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=25, anchor=tk.W).pack(side=tk.LEFT)
        
        entry = self.theme.create_entry(row, width=width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.vars[var_name] = entry
    
    def add_combobox_field(self, parent, label_text, var_name, values):
        """Añade un combobox"""
        row = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text=label_text, bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=25, anchor=tk.W).pack(side=tk.LEFT)
        
        combo = ttk.Combobox(row, values=values, state='readonly')
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.vars[var_name] = combo
    
    def create_buttons(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Espaciador
        tk.Frame(btn_frame, bg=self.theme.COLORS['bg_main']).pack(side=tk.LEFT, expand=True)
        
        # Botón Cancelar
        btn_cancel = self.theme.create_secondary_button(
            btn_frame,
            "❌ Cancelar",
            self.window.destroy
        )
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        # Botón Guardar
        btn_save = self.theme.create_primary_button(
            btn_frame,
            "✅ Guardar",
            self.guardar
        )
        btn_save.pack(side=tk.LEFT, padx=5)
    
    def cargar_datos(self):
        """Carga los datos de la sesión en el formulario"""
        if not self.sesion:
            return
        
        if 'id_solicitud' in self.vars:
            self.vars['id_solicitud'].set(self.sesion.id_solicitud)
        if 'fecha_sesion' in self.vars:
            self.vars['fecha_sesion'].insert(0, self.sesion.fecha_sesion.strftime("%d/%m/%Y"))
        if 'estado_servicio' in self.vars:
            self.vars['estado_servicio'].set(self.sesion.estado_servicio)
        if 'servicio_sesion' in self.vars:
            self.vars['servicio_sesion'].set(self.sesion.servicio_sesion)
        if 'coste_sesion' in self.vars:
            self.vars['coste_sesion'].insert(0, str(self.sesion.coste_sesion))
        if 'irradiaciones_realizadas' in self.vars:
            self.vars['irradiaciones_realizadas'].insert(0, str(self.sesion.irradiaciones_realizadas))
        if 'dosis_suministrada' in self.vars:
            self.vars['dosis_suministrada'].insert(0, str(self.sesion.dosis_suministrada))
        if 'tiempo_usado_h' in self.vars:
            self.vars['tiempo_usado_h'].insert(0, str(self.sesion.tiempo_usado_h))
        if 'tiempo_dosimetria_meses' in self.vars:
            self.vars['tiempo_dosimetria_meses'].insert(0, str(self.sesion.tiempo_dosimetria_meses))
        if 'observaciones_sesion' in self.vars:
            self.vars['observaciones_sesion'].insert(1.0, self.sesion.observaciones_sesion)
    
    def guardar(self):
        """Guarda la sesión"""
        try:
            # Validar campos obligatorios
            if not self.vars['id_solicitud'].get():
                messagebox.showerror("Error", "El ID de solicitud es obligatorio")
                return
            
            if not self.vars['fecha_sesion'].get():
                messagebox.showerror("Error", "La fecha de sesión es obligatoria")
                return
            
            if not self.vars['servicio_sesion'].get():
                messagebox.showerror("Error", "El tipo de servicio es obligatorio")
                return
            
            # Crear o actualizar sesión
            if self.es_edicion:
                sesion = self.sesion
            else:
                sesion = Sesion()
            
            # Llenar datos
            sesion.id_solicitud = self.vars['id_solicitud'].get()
            
            # Parsear fecha
            fecha_str = self.vars['fecha_sesion'].get()
            try:
                sesion.fecha_sesion = datetime.strptime(fecha_str, "%d/%m/%Y")
            except:
                messagebox.showerror("Error", "Formato de fecha inválido (usa DD/MM/YYYY)")
                return
            
            sesion.estado_servicio = self.vars['estado_servicio'].get()
            sesion.servicio_sesion = self.vars['servicio_sesion'].get()
            sesion.coste_sesion = float(self.vars['coste_sesion'].get() or 0)
            sesion.irradiaciones_realizadas = float(self.vars['irradiaciones_realizadas'].get() or 0)
            sesion.dosis_suministrada = float(self.vars['dosis_suministrada'].get() or 0)
            sesion.tiempo_usado_h = float(self.vars['tiempo_usado_h'].get() or 0)
            sesion.tiempo_dosimetria_meses = float(self.vars['tiempo_dosimetria_meses'].get() or 0)
            sesion.observaciones_sesion = self.vars['observaciones_sesion'].get(1.0, tk.END).strip()
            
            # Validar
            es_valida, mensaje = sesion.validar()
            if not es_valida:
                messagebox.showerror("Error de Validación", mensaje)
                return
            
            # Guardar en Google Sheets
            if self.es_edicion:
                messagebox.showinfo("Info", "Función de actualización pendiente de implementar")
            else:
                row = sesion.to_sheet_row()
                sheets_manager.append_row('Sesiones', row)
            
            # Actualizar lista
            self.sesiones_panel.load_data()
            
            messagebox.showinfo("Éxito", "Sesión guardada correctamente")
            self.window.destroy()
            
        except Exception as e:
            logger.error(f"Error al guardar sesión: {e}")
            messagebox.showerror("Error", f"Error al guardar:\n{e}")
