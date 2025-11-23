"""
Diálogo de Configuración
Permite cambiar BD y plantilla PDF
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

from src.utils.config_manager import config_manager
from src.utils.sheets_manager import sheets_manager


class DialogoConfiguracion:
    """Diálogo para configurar BD y plantilla PDF"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.theme = main_window.theme
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Configuración")
        self.window.geometry("650x700")  # Aumentado para mostrar todo
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrar
        self.center_window()
        
        # Construir interfaz
        self.build_ui()
        
        # Cargar configuración actual
        self.load_current_config()
    
    def center_window(self):
        """Centra la ventana"""
        self.window.update_idletasks()
        width = 650
        height = 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def build_ui(self):
        """Construye la interfaz"""
        # Frame principal con padding
        main_frame = tk.Frame(self.window, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = self.theme.create_header_label(main_frame, "⚙️ Configuración")
        title.pack(anchor=tk.W, pady=(0, 20))
        
        # Sección Base de Datos
        self.create_bd_section(main_frame)
        
        # Separador
        separator = tk.Frame(main_frame, height=2, bg=self.theme.COLORS['border'])
        separator.pack(fill=tk.X, pady=20)
        
        # Sección Plantilla PDF
        self.create_pdf_section(main_frame)
        
        # Espaciador
        tk.Frame(main_frame, height=20, bg=self.theme.COLORS['bg_main']).pack()
        
        # Botones
        self.create_buttons(main_frame)
    
    def create_bd_section(self, parent):
        """Crea la sección de configuración de BD"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title = self.theme.create_title_label(card, "🗄️ Base de Datos (Google Sheets)")
        title.pack(anchor=tk.W, pady=(0, 15))
        
        # Spreadsheet ID actual
        row1 = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="Spreadsheet ID actual:",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.current_id_label = tk.Label(
            row1,
            text="",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal'], 'bold'),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['primary']
        )
        self.current_id_label.pack(anchor=tk.W)
        
        # Nuevo Spreadsheet ID
        row2 = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        row2.pack(fill=tk.X, pady=(15, 5))
        
        tk.Label(
            row2,
            text="Nuevo Spreadsheet ID:",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.new_id_entry = self.theme.create_entry(row2)
        self.new_id_entry.pack(fill=tk.X)
        
        # Botón cambiar BD
        btn_cambiar_bd = self.theme.create_primary_button(
            card,
            "🔄 Cambiar Base de Datos",
            self.cambiar_bd
        )
        btn_cambiar_bd.pack(pady=(10, 0))
        
        # Info
        info_text = "Introduce el ID del nuevo spreadsheet de Google Sheets"
        tk.Label(
            card,
            text=info_text,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_tertiary'],
            wraplength=500
        ).pack(pady=(10, 0))
    
    def create_pdf_section(self, parent):
        """Crea la sección de configuración de plantilla PDF"""
        # Card
        card = self.theme.create_card_frame(parent)
        card.pack(fill=tk.X, pady=(10, 0))
        
        # Título
        title = self.theme.create_title_label(card, "📄 Plantilla PDF")
        title.pack(anchor=tk.W, pady=(0, 15))
        
        # Ruta actual
        row1 = tk.Frame(card, bg=self.theme.COLORS['card_bg'])
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(
            row1,
            text="Plantilla actual:",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_secondary']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.current_pdf_label = tk.Label(
            row1,
            text="",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_primary'],
            wraplength=500,
            justify=tk.LEFT
        )
        self.current_pdf_label.pack(anchor=tk.W)
        
        # Estado
        self.pdf_status_label = tk.Label(
            row1,
            text="",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_tertiary']
        )
        self.pdf_status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Botón seleccionar
        btn_seleccionar = self.theme.create_secondary_button(
            card,
            "📁 Seleccionar Plantilla PDF",
            self.seleccionar_plantilla
        )
        btn_seleccionar.pack(pady=(15, 0))
        
        # Info
        info_text = "Selecciona el archivo anexo_III_2025_V8.pdf (formulario en blanco)"
        tk.Label(
            card,
            text=info_text,
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            bg=self.theme.COLORS['card_bg'],
            fg=self.theme.COLORS['text_tertiary'],
            wraplength=500
        ).pack(pady=(10, 0))
    
    def create_buttons(self, parent):
        """Crea los botones de acción"""
        btn_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Espaciador
        tk.Frame(btn_frame, bg=self.theme.COLORS['bg_main']).pack(side=tk.LEFT, expand=True)
        
        # Botón Cerrar
        btn_close = self.theme.create_secondary_button(
            btn_frame,
            "Cerrar",
            self.window.destroy
        )
        btn_close.pack(side=tk.LEFT)
    
    def load_current_config(self):
        """Carga la configuración actual"""
        # Spreadsheet ID
        current_id = config_manager.get_spreadsheet_id()
        if current_id:
            self.current_id_label.config(text=current_id)
        else:
            self.current_id_label.config(text="(No configurado)")
        
        # Plantilla PDF
        current_pdf = config_manager.get_plantilla_pdf()
        self.current_pdf_label.config(text=current_pdf)
        
        # Verificar si existe
        if Path(current_pdf).exists():
            self.pdf_status_label.config(
                text="✅ Archivo encontrado",
                fg=self.theme.COLORS['success']
            )
        else:
            self.pdf_status_label.config(
                text="❌ Archivo no encontrado",
                fg=self.theme.COLORS['error']
            )
    
    def cambiar_bd(self):
        """Cambia la base de datos"""
        new_id = self.new_id_entry.get().strip()
        
        if not new_id:
            messagebox.showwarning(
                "Advertencia",
                "Introduce un Spreadsheet ID válido"
            )
            return
        
        # Confirmar
        if not messagebox.askyesno(
            "Confirmar Cambio",
            f"¿Cambiar a la nueva base de datos?\n\n"
            f"Nuevo ID: {new_id}\n\n"
            "La aplicación se reconectará."
        ):
            return
        
        try:
            # Guardar nuevo ID
            config_manager.set_spreadsheet_id(new_id)
            
            # Reconectar sheets_manager
            sheets_manager.spreadsheet_id = new_id
            sheets_manager.clear_cache()
            
            # Actualizar display
            self.current_id_label.config(text=new_id)
            self.new_id_entry.delete(0, tk.END)
            
            messagebox.showinfo(
                "Éxito",
                "Base de datos cambiada correctamente.\n\n"
                "Actualiza los datos en cada panel."
            )
            
            # Notificar a la ventana principal
            if hasattr(self.main_window, 'update_status'):
                self.main_window.update_status("✅ Base de datos cambiada")
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al cambiar la base de datos:\n{e}"
            )
    
    def seleccionar_plantilla(self):
        """Selecciona la plantilla PDF"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar Plantilla PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=Path.cwd() / "formularios"
        )
        
        if not filepath:
            return  # Usuario canceló
        
        # Verificar que es un PDF
        if not filepath.lower().endswith('.pdf'):
            messagebox.showwarning(
                "Advertencia",
                "Selecciona un archivo PDF"
            )
            return
        
        # Guardar configuración
        config_manager.set_plantilla_pdf(filepath)
        
        # Actualizar display
        self.current_pdf_label.config(text=filepath)
        self.pdf_status_label.config(
            text="✅ Archivo encontrado",
            fg=self.theme.COLORS['success']
        )
        
        messagebox.showinfo(
            "Éxito",
            "Plantilla PDF configurada correctamente"
        )
