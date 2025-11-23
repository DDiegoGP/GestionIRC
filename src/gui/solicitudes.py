"""
Panel de Gestión de Solicitudes
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pdfplumber

from src.utils.sheets_manager import sheets_manager
from src.models.solicitud import Solicitud
from src.constants import TIPOS_SERVICIOS, TIPOS_USUARIO, ESTADOS_SOLICITUD, DEPARTAMENTOS_UCM, TARIFAS_SERVICIOS
from src.utils.logger import logger


class SolicitudesPanel:
    """Panel para gestionar solicitudes"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.solicitudes = []
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Configura la interfaz"""
        # Frame principal dividido
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Lista
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Botones de acción
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="➕ Nueva Solicitud", 
                  command=self.nueva_solicitud).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Desde PDF", 
                  command=self.cargar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Editar", 
                  command=self.editar_solicitud).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Eliminar", 
                  command=self.eliminar_solicitud).pack(side=tk.LEFT, padx=5)
        
        # Tabla de solicitudes
        self.tree = ttk.Treeview(left_frame, columns=('ID', 'Nombre', 'Servicio', 'Estado', 'Fecha'),
                                show='headings', height=20)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Nombre', text='Nombre')
        self.tree.heading('Servicio', text='Servicio')
        self.tree.heading('Estado', text='Estado')
        self.tree.heading('Fecha', text='Fecha')
        
        self.tree.column('ID', width=80)
        self.tree.column('Nombre', width=150)
        self.tree.column('Servicio', width=200)
        self.tree.column('Estado', width=100)
        self.tree.column('Fecha', width=100)
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Panel derecho - Detalles
        right_frame = ttk.LabelFrame(top_frame, text="📋 Detalles", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        self.details_text = tk.Text(right_frame, width=40, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind selección
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
    
    def load_data(self):
        """Carga las solicitudes"""
        try:
            data = sheets_manager.get_all_data('Solicitudes')
            self.solicitudes = [Solicitud.from_sheet_row(row) for row in data[1:]] if len(data) > 1 else []
            self.update_tree()
        except Exception as e:
            logger.error(f"Error al cargar solicitudes: {e}")
            self.solicitudes = []
            self.update_tree()
            # Mostrar mensaje en detalles
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, "⚠️ Sin conexión a Google Sheets\n\n")
            self.details_text.insert(tk.END, "Configura las credenciales desde el menú Configuración\n")
            self.details_text.insert(tk.END, "para cargar las solicitudes.")
    
    def update_tree(self):
        """Actualiza la tabla"""
        self.tree.delete(*self.tree.get_children())
        for sol in self.solicitudes:
            fecha = sol.fecha_solicitud.strftime("%d/%m/%Y") if sol.fecha_solicitud else ""
            self.tree.insert('', tk.END, values=(
                sol.id,
                sol.nombre_completo,
                sol.tipo_servicio,
                sol.estado,
                fecha
            ))
    
    def on_select(self, event):
        """Maneja la selección de una solicitud"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            sol_id = item['values'][0]
            solicitud = next((s for s in self.solicitudes if s.id == sol_id), None)
            
            if solicitud:
                self.show_details(solicitud)
    
    def show_details(self, solicitud):
        """Muestra los detalles de una solicitud"""
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, f"""
Número: {solicitud.numero_solicitud}

SOLICITANTE:
Nombre: {solicitud.nombre_completo}
Email: {solicitud.email}
Teléfono: {solicitud.telefono}
Departamento: {solicitud.departamento}

SERVICIO:
Tipo Usuario: {solicitud.tipo_usuario}
Tipo Servicio: {solicitud.tipo_servicio}
Descripción: {solicitud.descripcion}

ESTADO:
Estado: {solicitud.estado}
Prioridad: {solicitud.prioridad}
Fecha Solicitud: {solicitud.fecha_solicitud.strftime("%d/%m/%Y %H:%M")}

COSTES:
Coste Calculado: {solicitud.coste_calculado:.2f} €
Facturada: {'Sí' if solicitud.facturada else 'No'}
        """)
    
    def nueva_solicitud(self):
        """Abre el formulario para nueva solicitud"""
        FormularioSolicitud(self.parent, self, None)
    
    def editar_solicitud(self):
        """Edita la solicitud seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecciona una solicitud")
            return
        
        item = self.tree.item(selection[0])
        sol_id = item['values'][0]
        solicitud = next((s for s in self.solicitudes if s.id == sol_id), None)
        
        if solicitud:
            FormularioSolicitud(self.parent, self, solicitud)
    
    def eliminar_solicitud(self):
        """Elimina la solicitud seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecciona una solicitud")
            return
        
        if messagebox.askyesno("Confirmar", "¿Eliminar esta solicitud?"):
            # Implementar eliminación
            messagebox.showinfo("Info", "Función en desarrollo")
    
    def cargar_pdf(self):
        """Carga una solicitud desde PDF"""
        filename = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if filename:
            try:
                solicitud = self.extraer_datos_pdf(filename)
                FormularioSolicitud(self.parent, self, solicitud)
            except Exception as e:
                messagebox.showerror("Error", f"Error al leer PDF: {e}")
    
    def extraer_datos_pdf(self, pdf_path):
        """Extrae datos de un PDF de solicitud"""
        solicitud = Solicitud()
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                texto = ""
                for page in pdf.pages:
                    texto += page.extract_text()
                
                # Aquí implementar extracción de campos
                # Por ahora solo creamos una solicitud vacía
                
        except Exception as e:
            logger.error(f"Error al extraer PDF: {e}")
        
        return solicitud
    
    def guardar_solicitud(self, solicitud):
        """Guarda o actualiza una solicitud"""
        try:
            # Calcular coste
            solicitud.calcular_coste(TARIFAS_SERVICIOS)
            
            # Validar
            es_valida, mensaje = solicitud.validar()
            if not es_valida:
                messagebox.showerror("Error", mensaje)
                return False
            
            # Guardar en Sheets
            row = solicitud.to_sheet_row()
            sheets_manager.append_rows('Solicitudes', [row])
            
            messagebox.showinfo("Éxito", "Solicitud guardada correctamente")
            self.refresh()
            return True
            
        except Exception as e:
            logger.error(f"Error al guardar solicitud: {e}")
            messagebox.showerror("Error", f"Error al guardar: {e}")
            return False
    
    def refresh(self):
        """Refresca los datos"""
        self.load_data()


class FormularioSolicitud:
    """Diálogo para crear/editar solicitud"""
    
    def __init__(self, parent, panel, solicitud=None):
        self.panel = panel
        self.solicitud = solicitud or Solicitud()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nueva Solicitud" if not solicitud else "Editar Solicitud")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_form()
        
        if solicitud:
            self.load_data()
    
    def setup_form(self):
        """Configura el formulario"""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas con scroll
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        self.form_frame = ttk.Frame(canvas)
        
        self.form_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.form_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Campos del formulario
        self.campos = {}
        
        # Datos personales
        ttk.Label(self.form_frame, text="DATOS DEL SOLICITANTE", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        self.add_field("Nombre *:", "nombre", 1)
        self.add_field("Apellidos *:", "apellidos", 2)
        self.add_field("Email *:", "email", 3)
        self.add_field("Teléfono:", "telefono", 4)
        
        self.add_combobox("Departamento *:", "departamento", DEPARTAMENTOS_UCM, 5)
        
        # Servicio
        ttk.Label(self.form_frame, text="SERVICIO", font=('Arial', 10, 'bold')).grid(
            row=6, column=0, columnspan=2, pady=10, sticky='w')
        
        self.add_combobox("Tipo Usuario *:", "tipo_usuario", TIPOS_USUARIO, 7)
        self.add_combobox("Tipo Servicio *:", "tipo_servicio", TIPOS_SERVICIOS, 8)
        
        self.add_field("Descripción:", "descripcion", 9, height=3)
        self.add_field("Observaciones:", "observaciones", 10, height=3)
        
        # Parámetros específicos
        self.add_field("Dosis (Gy):", "dosis_gy", 11)
        self.add_field("Horas de uso:", "horas_uso", 12)
        
        # Estado
        self.add_combobox("Estado:", "estado", ESTADOS_SOLICITUD, 13)
        
        # Botones
        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.grid(row=14, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="💾 Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_field(self, label, key, row, height=1):
        """Añade un campo de texto"""
        ttk.Label(self.form_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)
        
        if height > 1:
            widget = tk.Text(self.form_frame, height=height, width=40)
        else:
            widget = ttk.Entry(self.form_frame, width=40)
        
        widget.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.campos[key] = widget
    
    def add_combobox(self, label, key, values, row):
        """Añade un combobox"""
        ttk.Label(self.form_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)
        
        widget = ttk.Combobox(self.form_frame, values=values, width=37, state='readonly')
        widget.grid(row=row, column=1, sticky='ew', pady=5, padx=(10, 0))
        self.campos[key] = widget
    
    def load_data(self):
        """Carga los datos de la solicitud"""
        for key, widget in self.campos.items():
            value = getattr(self.solicitud, key, "")
            if isinstance(widget, tk.Text):
                widget.insert(1.0, value)
            elif isinstance(widget, ttk.Entry):
                widget.insert(0, str(value) if value else "")
            elif isinstance(widget, ttk.Combobox):
                widget.set(value)
    
    def guardar(self):
        """Guarda la solicitud"""
        for key, widget in self.campos.items():
            if isinstance(widget, tk.Text):
                value = widget.get(1.0, tk.END).strip()
            elif isinstance(widget, (ttk.Entry, ttk.Combobox)):
                value = widget.get().strip()
            
            # Conversión de tipos
            if key in ['dosis_gy', 'horas_uso']:
                value = float(value) if value else None
            
            setattr(self.solicitud, key, value)
        
        if self.panel.guardar_solicitud(self.solicitud):
            self.dialog.destroy()
