"""
Formulario de Solicitud - Ventana Modal con 24 campos
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import Optional
import json

from src.models.solicitud_real import Solicitud
from src.constants_real import (
    TIPOS_SERVICIOS, TIPOS_USUARIO, ESTADOS_SOLICITUD,
    TARIFAS_SERVICIOS, ORGANISMOS_COMUNES, DEPARTAMENTOS_UCM
)
from src.utils.sheets_manager import sheets_manager
from src.utils.logger import logger


class FormularioSolicitud:
    """Formulario para crear/editar solicitudes"""
    
    def __init__(self, main_window, solicitudes_panel, solicitud: Optional[Solicitud] = None, es_nueva: bool = False):
        self.main_window = main_window
        self.solicitudes_panel = solicitudes_panel
        self.theme = main_window.theme
        self.solicitud = solicitud
        # Si es_nueva=True, es una importación desde PDF (nueva solicitud con datos pre-cargados)
        # Si es_nueva=False y solicitud existe, es una edición
        self.es_edicion = solicitud is not None and not es_nueva
        
        # Variables de formulario
        self.vars = {}
        
        # Crear ventana
        self.window = tk.Toplevel(main_window.root)
        self.window.title("Editar Solicitud" if self.es_edicion else "Nueva Solicitud")
        self.window.geometry("900x800")
        self.window.transient(main_window.root)
        self.window.grab_set()
        
        # Centrar ventana
        self.center_window()
        
        # Construir interfaz
        self.build_ui()
        
        # Cargar datos si es edición o importación de PDF
        if self.solicitud:
            self.cargar_datos()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = 900
        height = 800
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
            "✏️ Editar Solicitud" if self.es_edicion else "➕ Nueva Solicitud"
        )
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Secciones del formulario
        self.create_section_identificacion(scrollable_frame)
        self.create_section_solicitante(scrollable_frame)
        self.create_section_servicio(scrollable_frame)
        self.create_section_facturacion(scrollable_frame)
        self.create_section_proyecto(scrollable_frame)
        self.create_section_observaciones(scrollable_frame)
        
        # Botones
        self.create_buttons(scrollable_frame)
        
        # Bind scroll con rueda del ratón (solo en este canvas, no global)
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        
        # Limpiar binding cuando se cierra la ventana
        def on_close():
            canvas.unbind("<MouseWheel>")
            scrollable_frame.unbind("<MouseWheel>")
            self.window.destroy()
        
        self.window.protocol("WM_DELETE_WINDOW", on_close)
    
    def create_section_identificacion(self, parent):
        """Sección de identificación"""
        section = self.create_section_frame(parent, "🆔 Identificación")
        
        # ID (solo lectura si es edición)
        row = tk.Frame(section, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text="ID Solicitud:", bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        if self.es_edicion:
            id_label = tk.Label(row, text=self.solicitud.id_solicitud,
                              bg=self.theme.COLORS['bg_secondary'],
                              fg=self.theme.COLORS['text_primary'], anchor=tk.W)
            id_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        else:
            id_label = tk.Label(row, text="Se generará automáticamente",
                              bg=self.theme.COLORS['bg_secondary'],
                              fg=self.theme.COLORS['text_secondary'], anchor=tk.W)
            id_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Estado
        self.add_combobox_field(section, "Estado:", "estado", ESTADOS_SOLICITUD)
        
        # Fecha (solo lectura)
        row = tk.Frame(section, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text="Fecha Solicitud:", bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        fecha_text = datetime.now().strftime("%d/%m/%Y %H:%M") if not self.es_edicion else \
                     self.solicitud.fecha_solicitud.strftime("%d/%m/%Y %H:%M")
        fecha_label = tk.Label(row, text=fecha_text,
                             bg=self.theme.COLORS['bg_secondary'],
                             fg=self.theme.COLORS['text_primary'], anchor=tk.W)
        fecha_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def create_section_solicitante(self, parent):
        """Sección de datos del solicitante"""
        section = self.create_section_frame(parent, "👤 Datos del Solicitante")
        
        self.add_entry_field(section, "Nombre Completo: *", "nombre_solicitante")
        self.add_entry_field(section, "Email: *", "email")
        self.add_entry_field(section, "Teléfono:", "telefono")
        self.add_combobox_field(section, "Tipo Usuario: *", "tipo_usuario", TIPOS_USUARIO)
        self.add_combobox_field(section, "Organismo/Centro:", "organismo_centro_solicitante", ORGANISMOS_COMUNES)
        self.add_combobox_field(section, "Departamento:", "departamento_solicitante", DEPARTAMENTOS_UCM)
    
    def create_section_servicio(self, parent):
        """Sección de servicio"""
        section = self.create_section_frame(parent, "🔬 Servicio Solicitado")
        
        # Tipo de servicio
        self.add_combobox_field(section, "Tipo Servicio: *", "servicio_solicitado", TIPOS_SERVICIOS,
                               callback=self.on_servicio_change)
        
        # Frame para detalles del servicio (dinámico según tipo)
        self.detalles_frame = tk.Frame(section, bg=self.theme.COLORS['card_bg'])
        self.detalles_frame.pack(fill=tk.X, pady=10)
        
        # Coste estimado (calculado automáticamente)
        row = tk.Frame(section, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text="Coste Estimado:", bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=20, anchor=tk.W,
                font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold')).pack(side=tk.LEFT)
        
        self.vars['coste_label'] = tk.Label(row, text="0.00 €",
                                           bg=self.theme.COLORS['bg_selected'],
                                           fg=self.theme.COLORS['primary'],
                                           anchor=tk.W,
                                           font=(self.theme.FONTS['family'], self.theme.FONTS['size_medium'], 'bold'))
        self.vars['coste_label'].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    
    def create_section_facturacion(self, parent):
        """Sección de facturación"""
        section = self.create_section_frame(parent, "💰 Datos de Facturación")
        
        self.add_entry_field(section, "Organismo/Centro Facturación:", "organismo_centro_facturacion")
        self.add_entry_field(section, "Departamento Facturación:", "departamento_facturacion")
        self.add_entry_field(section, "CIF:", "cif")
        self.add_entry_field(section, "Domicilio Fiscal:", "domicilio_fiscal")
        self.add_entry_field(section, "Código Postal:", "domicilio_postal")
        self.add_entry_field(section, "Oficina Contable:", "oficina_contable")
        self.add_entry_field(section, "Órgano Gestor:", "organo_gestor")
        self.add_entry_field(section, "Centro Gestor:", "centro_gestor")
    
    def create_section_proyecto(self, parent):
        """Sección de proyecto"""
        section = self.create_section_frame(parent, "📊 Proyecto de Investigación")
        
        self.add_entry_field(section, "Investigador Principal:", "investigador_principal")
        self.add_entry_field(section, "Proyecto/PEP:", "proyecto")
        self.add_entry_field(section, "Nº Contabilidad:", "numero_contabilidad")
    
    def create_section_observaciones(self, parent):
        """Sección de observaciones"""
        section = self.create_section_frame(parent, "💬 Observaciones")
        
        row = tk.Frame(section, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.BOTH, expand=True, pady=5)
        
        text_widget = self.theme.create_text(row, height=4)
        text_widget.pack(fill=tk.BOTH, expand=True)
        self.vars['observaciones'] = text_widget
    
    def create_section_frame(self, parent, title):
        """Crea un frame de sección con título"""
        # Card frame
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 15))
        
        # Título de sección
        title_label = self.theme.create_title_label(card, title)
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Separador
        sep = ttk.Separator(card, orient='horizontal')
        sep.pack(fill=tk.X, pady=(0, 10))
        
        return card
    
    def add_entry_field(self, parent, label_text, var_name, width=50):
        """Añade un campo de entrada"""
        row = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text=label_text, bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        entry = self.theme.create_entry(row, width=width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.vars[var_name] = entry
    
    def add_combobox_field(self, parent, label_text, var_name, values, callback=None):
        """Añade un combobox"""
        row = tk.Frame(parent, bg=self.theme.COLORS['card_bg'])
        row.pack(fill=tk.X, pady=5)
        
        tk.Label(row, text=label_text, bg=self.theme.COLORS['card_bg'],
                fg=self.theme.COLORS['text_primary'], width=20, anchor=tk.W).pack(side=tk.LEFT)
        
        combo = ttk.Combobox(row, values=values, state='readonly')
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        if callback:
            combo.bind('<<ComboboxSelected>>', lambda e: callback())
        
        self.vars[var_name] = combo
    
    def on_servicio_change(self):
        """Maneja el cambio de tipo de servicio"""
        # Limpiar frame de detalles
        for widget in self.detalles_frame.winfo_children():
            widget.destroy()
        
        servicio = self.vars['servicio_solicitado'].get()
        
        # Añadir campos específicos según servicio
        if "menor" in servicio.lower() or "< 10" in servicio:
            # Irradiación < 10 Gy
            self.add_entry_field(self.detalles_frame, "Nº Canisters:", "det_canisters")
            
        elif "mayor" in servicio.lower() or "> 10" in servicio:
            # Irradiación > 10 Gy
            self.add_entry_field(self.detalles_frame, "Nº Canisters:", "det_canisters")
            self.add_entry_field(self.detalles_frame, "Dosis por Canister (Gy):", "det_dosis")
            
        elif "dosimétrica" in servicio.lower():
            # Gestión dosimétrica
            self.add_entry_field(self.detalles_frame, "Nº Dosímetros:", "det_dosimetros")
            self.add_entry_field(self.detalles_frame, "Tiempo (meses):", "det_meses")
            
        elif "Contador" in servicio:
            # Contadores
            self.add_entry_field(self.detalles_frame, "Tiempo de uso (horas):", "det_horas")
        
        # Calcular coste
        self.calcular_coste()
    
    def calcular_coste(self):
        """Calcula el coste estimado"""
        try:
            # Crear solicitud temporal para calcular
            temp_sol = Solicitud()
            temp_sol.servicio_solicitado = self.vars['servicio_solicitado'].get()
            temp_sol.tipo_usuario = self.vars['tipo_usuario'].get()
            
            # Extraer detalles del servicio
            detalles = {}
            servicio = temp_sol.servicio_solicitado
            
            if "menor" in servicio.lower() or "< 10" in servicio:
                if 'det_canisters' in self.vars:
                    detalles['canisters'] = int(self.vars['det_canisters'].get() or 0)
                    detalles['irradiaciones'] = 1
                    
            elif "mayor" in servicio.lower() or "> 10" in servicio:
                if 'det_canisters' in self.vars and 'det_dosis' in self.vars:
                    detalles['canisters'] = int(self.vars['det_canisters'].get() or 0)
                    detalles['dosis_por_canister_Gy'] = float(self.vars['det_dosis'].get() or 0)
                    detalles['irradiaciones'] = 1
                    
            elif "dosimétrica" in servicio.lower():
                if 'det_dosimetros' in self.vars and 'det_meses' in self.vars:
                    detalles['dosimetros'] = int(self.vars['det_dosimetros'].get() or 0)
                    detalles['meses'] = int(self.vars['det_meses'].get() or 0)
                    
            elif "Contador" in servicio:
                if 'det_horas' in self.vars:
                    detalles['horas'] = float(self.vars['det_horas'].get() or 0)
            
            temp_sol.detalles_servicio = detalles
            
            # Calcular
            coste = temp_sol.calcular_coste(TARIFAS_SERVICIOS)
            
            # Actualizar label
            if 'coste_label' in self.vars:
                self.vars['coste_label'].config(text=f"{coste:.2f} €")
                
        except Exception as e:
            logger.debug(f"Error al calcular coste: {e}")
    
    def create_buttons(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(fill=tk.X, pady=20)
        
        # Botón Calcular Coste
        btn_calcular = self.theme.create_secondary_button(
            btn_frame,
            "💰 Calcular Coste",
            self.calcular_coste
        )
        btn_calcular.pack(side=tk.LEFT, padx=5)
        
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
        """Carga los datos de la solicitud en el formulario"""
        if not self.solicitud:
            return
        
        # Cargar campos básicos
        if 'estado' in self.vars:
            self.vars['estado'].set(self.solicitud.estado)
        if 'nombre_solicitante' in self.vars:
            self.vars['nombre_solicitante'].insert(0, self.solicitud.nombre_solicitante)
        if 'email' in self.vars:
            self.vars['email'].insert(0, self.solicitud.email)
        if 'telefono' in self.vars:
            self.vars['telefono'].insert(0, self.solicitud.telefono)
        if 'tipo_usuario' in self.vars:
            self.vars['tipo_usuario'].set(self.solicitud.tipo_usuario)
        if 'organismo_centro_solicitante' in self.vars:
            self.vars['organismo_centro_solicitante'].set(self.solicitud.organismo_centro_solicitante)
        if 'departamento_solicitante' in self.vars:
            self.vars['departamento_solicitante'].set(self.solicitud.departamento_solicitante)
        
        # Servicio
        if 'servicio_solicitado' in self.vars:
            self.vars['servicio_solicitado'].set(self.solicitud.servicio_solicitado)
            self.on_servicio_change()
            
            # Cargar detalles del servicio
            detalles = self.solicitud.detalles_servicio
            if 'det_canisters' in self.vars and 'canisters' in detalles:
                self.vars['det_canisters'].insert(0, str(detalles['canisters']))
            if 'det_dosis' in self.vars and 'dosis_por_canister_Gy' in detalles:
                self.vars['det_dosis'].insert(0, str(detalles['dosis_por_canister_Gy']))
            if 'det_dosimetros' in self.vars and 'dosimetros' in detalles:
                self.vars['det_dosimetros'].insert(0, str(detalles['dosimetros']))
            if 'det_meses' in self.vars and 'meses' in detalles:
                self.vars['det_meses'].insert(0, str(detalles['meses']))
            if 'det_horas' in self.vars and 'horas' in detalles:
                self.vars['det_horas'].insert(0, str(detalles['horas']))
        
        # Facturación
        if 'organismo_centro_facturacion' in self.vars:
            self.vars['organismo_centro_facturacion'].insert(0, self.solicitud.organismo_centro_facturacion)
        if 'departamento_facturacion' in self.vars:
            self.vars['departamento_facturacion'].insert(0, self.solicitud.departamento_facturacion)
        if 'cif' in self.vars:
            self.vars['cif'].insert(0, self.solicitud.cif)
        if 'domicilio_fiscal' in self.vars:
            self.vars['domicilio_fiscal'].insert(0, self.solicitud.domicilio_fiscal)
        if 'domicilio_postal' in self.vars:
            self.vars['domicilio_postal'].insert(0, self.solicitud.domicilio_postal)
        if 'oficina_contable' in self.vars:
            self.vars['oficina_contable'].insert(0, self.solicitud.oficina_contable)
        if 'organo_gestor' in self.vars:
            self.vars['organo_gestor'].insert(0, self.solicitud.organo_gestor)
        if 'centro_gestor' in self.vars:
            self.vars['centro_gestor'].insert(0, self.solicitud.centro_gestor)
        
        # Proyecto
        if 'investigador_principal' in self.vars:
            self.vars['investigador_principal'].insert(0, self.solicitud.investigador_principal)
        if 'proyecto' in self.vars:
            self.vars['proyecto'].insert(0, self.solicitud.proyecto)
        if 'numero_contabilidad' in self.vars:
            self.vars['numero_contabilidad'].insert(0, self.solicitud.numero_contabilidad)
        
        # Observaciones
        if 'observaciones' in self.vars:
            self.vars['observaciones'].insert(1.0, self.solicitud.observaciones)
        
        # Actualizar coste
        self.calcular_coste()
    
    def guardar(self):
        """Guarda la solicitud"""
        try:
            # Validar campos obligatorios
            if not self.vars['nombre_solicitante'].get():
                messagebox.showerror("Error", "El nombre del solicitante es obligatorio")
                return
            
            if not self.vars['email'].get():
                messagebox.showerror("Error", "El email es obligatorio")
                return
            
            if not self.vars['servicio_solicitado'].get():
                messagebox.showerror("Error", "El tipo de servicio es obligatorio")
                return
            
            if not self.vars['tipo_usuario'].get():
                messagebox.showerror("Error", "El tipo de usuario es obligatorio")
                return
            
            # Crear o actualizar solicitud
            if self.es_edicion:
                solicitud = self.solicitud
            else:
                # Si ya tenemos una solicitud (ej: desde PDF), usarla
                if self.solicitud:
                    solicitud = self.solicitud
                else:
                    # Solo crear nueva si no hay nada
                    solicitud = Solicitud()
                    solicitud.fecha_solicitud = datetime.now()
            
            # Llenar datos
            solicitud.estado = self.vars['estado'].get()
            solicitud.nombre_solicitante = self.vars['nombre_solicitante'].get()
            solicitud.email = self.vars['email'].get()
            solicitud.telefono = self.vars['telefono'].get()
            solicitud.tipo_usuario = self.vars['tipo_usuario'].get()
            solicitud.organismo_centro_solicitante = self.vars['organismo_centro_solicitante'].get()
            solicitud.departamento_solicitante = self.vars['departamento_solicitante'].get()
            solicitud.servicio_solicitado = self.vars['servicio_solicitado'].get()
            
            # Detalles del servicio
            detalles = {}
            servicio = solicitud.servicio_solicitado
            
            if "menor" in servicio.lower() or "< 10" in servicio:
                if 'det_canisters' in self.vars:
                    detalles['canisters'] = int(self.vars['det_canisters'].get() or 0)
                    detalles['irradiaciones'] = 1
                    
            elif "mayor" in servicio.lower() or "> 10" in servicio:
                if 'det_canisters' in self.vars and 'det_dosis' in self.vars:
                    detalles['canisters'] = int(self.vars['det_canisters'].get() or 0)
                    detalles['dosis_por_canister_Gy'] = float(self.vars['det_dosis'].get() or 0)
                    detalles['irradiaciones'] = 1
                    
            elif "dosimétrica" in servicio.lower():
                if 'det_dosimetros' in self.vars and 'det_meses' in self.vars:
                    detalles['dosimetros'] = int(self.vars['det_dosimetros'].get() or 0)
                    detalles['meses'] = int(self.vars['det_meses'].get() or 0)
                    
            elif "Contador" in servicio:
                if 'det_horas' in self.vars:
                    detalles['horas'] = float(self.vars['det_horas'].get() or 0)
            
            solicitud.detalles_servicio = detalles
            
            # Facturación
            solicitud.organismo_centro_facturacion = self.vars['organismo_centro_facturacion'].get()
            solicitud.departamento_facturacion = self.vars['departamento_facturacion'].get()
            solicitud.cif = self.vars['cif'].get()
            solicitud.domicilio_fiscal = self.vars['domicilio_fiscal'].get()
            solicitud.domicilio_postal = self.vars['domicilio_postal'].get()
            solicitud.oficina_contable = self.vars['oficina_contable'].get()
            solicitud.organo_gestor = self.vars['organo_gestor'].get()
            solicitud.centro_gestor = self.vars['centro_gestor'].get()
            
            # Proyecto
            solicitud.investigador_principal = self.vars['investigador_principal'].get()
            solicitud.proyecto = self.vars['proyecto'].get()
            solicitud.numero_contabilidad = self.vars['numero_contabilidad'].get()
            
            # Observaciones
            solicitud.observaciones = self.vars['observaciones'].get(1.0, tk.END).strip()
            
            # Calcular coste
            solicitud.calcular_coste(TARIFAS_SERVICIOS)
            
            # Validar
            es_valida, mensaje = solicitud.validar()
            if not es_valida:
                messagebox.showerror("Error de Validación", mensaje)
                return
            
            # Guardar en Google Sheets
            try:
                if self.es_edicion:
                    # Actualizar fila existente
                    logger.info(f"📝 Actualizando solicitud: {solicitud.id_solicitud}")
                    row = solicitud.to_sheet_row()
                    logger.info(f"   Fila generada con {len(row)} columnas")
                    
                    # Buscar el índice de la fila en Google Sheets
                    data = sheets_manager.get_all_data('Solicitudes')
                    logger.info(f"   Datos obtenidos: {len(data)} filas")
                    
                    row_index = None
                    
                    for i, data_row in enumerate(data[1:], start=2):  # Empezar desde fila 2
                        if len(data_row) > 0 and data_row[0] == solicitud.id_solicitud:
                            row_index = i
                            logger.info(f"   ✅ Encontrada en fila {row_index}")
                            break
                    
                    if row_index:
                        resultado = sheets_manager.update_row('Solicitudes', row_index, row)
                        if resultado:
                            logger.info(f"✅ Solicitud actualizada correctamente")
                        else:
                            logger.error(f"❌ Error al actualizar en Sheets")
                            raise Exception("No se pudo actualizar en Google Sheets")
                    else:
                        # Si no se encuentra, añadir como nueva
                        logger.warning(f"⚠️ No se encontró la fila para {solicitud.id_solicitud}, añadiendo como nueva")
                        resultado = sheets_manager.append_row('Solicitudes', row)
                        if not resultado:
                            raise Exception("No se pudo añadir en Google Sheets")
                else:
                    # Añadir nueva fila
                    logger.info(f"➕ Añadiendo nueva solicitud: {solicitud.id_solicitud}")
                    row = solicitud.to_sheet_row()
                    logger.info(f"   Fila generada con {len(row)} columnas")
                    
                    resultado = sheets_manager.append_row('Solicitudes', row)
                    if resultado:
                        logger.info(f"✅ Nueva solicitud añadida correctamente")
                    else:
                        logger.error(f"❌ Error al añadir en Sheets")
                        raise Exception("No se pudo añadir en Google Sheets")
                
                # Actualizar lista
                self.solicitudes_panel.load_data()
                
                messagebox.showinfo("Éxito", "Solicitud guardada correctamente")
                self.window.destroy()
                
            except Exception as e_sheets:
                logger.error(f"❌ Error al guardar en Sheets: {e_sheets}")
                messagebox.showerror(
                    "Error al Guardar", 
                    f"La solicitud se validó correctamente pero no se pudo guardar en Google Sheets:\n\n{e_sheets}\n\n"
                    "Verifica:\n"
                    "1. Conexión a Google Sheets\n"
                    "2. Permisos de escritura\n"
                    "3. El Spreadsheet ID en ⚙️ Configuración"
                )
                return
            
        except Exception as e:
            logger.error(f"Error al guardar solicitud: {e}")
            messagebox.showerror("Error", f"Error al guardar:\n{e}")
