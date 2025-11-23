# Soluciones a Problemas Identificados - App IRC

## Fecha: 18 de Noviembre 2025

---

## 1. CONFIGURACIÓN DE PLANTILLA PDF NO VISIBLE

### Problema
La generación de PDF funciona, pero no se ve dónde configurar la plantilla en la ventana de Configuración.

### Solución
Agregar en `ConfigWindow` (o ventana de configuración):

```python
def create_config_widgets(self):
    # ... código existente para Google Sheets ...
    
    # NUEVA SECCIÓN: Plantilla PDF
    ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)
    
    pdf_frame = ttk.LabelFrame(self.main_frame, text="📄 Plantilla PDF", padding=10)
    pdf_frame.pack(fill='x', padx=10, pady=5)
    
    # Mostrar plantilla actual
    current_template = self.config.get('pdf_template_path', 'No configurada')
    ttk.Label(pdf_frame, text=f"Plantilla actual: {current_template}").pack(anchor='w')
    
    # Botón para seleccionar nueva plantilla
    btn_frame = ttk.Frame(pdf_frame)
    btn_frame.pack(fill='x', pady=5)
    
    ttk.Button(
        btn_frame,
        text="📁 Seleccionar Plantilla PDF",
        command=self.select_pdf_template
    ).pack(side='left', padx=5)
    
    ttk.Button(
        btn_frame,
        text="📋 Usar Plantilla por Defecto",
        command=self.use_default_template
    ).pack(side='left', padx=5)

def select_pdf_template(self):
    """Permite al usuario seleccionar una plantilla PDF personalizada"""
    from tkinter import filedialog
    
    file_path = filedialog.askopenfilename(
        title="Seleccionar Plantilla PDF",
        filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
    )
    
    if file_path:
        self.config['pdf_template_path'] = file_path
        self.save_config()
        messagebox.showinfo("Éxito", "Plantilla PDF configurada correctamente")
        self.refresh_display()

def use_default_template(self):
    """Establece la plantilla por defecto del sistema"""
    # Ruta a la plantilla incluida en la aplicación
    default_template = os.path.join(
        os.path.dirname(__file__), 
        'resources', 
        'plantilla_solicitud_default.pdf'
    )
    
    if os.path.exists(default_template):
        self.config['pdf_template_path'] = default_template
        self.save_config()
        messagebox.showinfo("Éxito", "Usando plantilla por defecto")
        self.refresh_display()
    else:
        messagebox.showwarning(
            "Aviso", 
            "No se encontró la plantilla por defecto. La generación de PDF usará formato simple."
        )
        self.config['pdf_template_path'] = None
        self.save_config()
```

---