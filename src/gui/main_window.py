"""
Ventana Principal del Sistema de Gestión IRC - Tema Microsoft 365
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import APP_CONFIG, UI_CONFIG
from src.utils.logger import logger
from src.utils.sheets_manager import sheets_manager
from src.gui.theme import Microsoft365Theme
from src.gui.dashboard_sincronizado import DashboardSincronizado as DashboardPanel
from src.gui.solicitudes_real import SolicitudesRealPanel
from src.gui.sesiones_mejorado import SesionesPanelMejorado as SesionesPanel
from src.gui.busqueda import BusquedaPanel
from src.gui.informes import InformesPanel


class MainWindow:
    """Ventana principal de la aplicación con tema Microsoft 365"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.apply_theme()
        self.check_authentication()
        
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title(f"{APP_CONFIG['NOMBRE']} v{APP_CONFIG['VERSION']}")
        
        # Tamaño más grande para mejor visualización
        width = 1400
        height = 900
        
        # Centrar ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(1200, 700)
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def apply_theme(self):
        """Aplica el tema Microsoft 365"""
        self.theme = Microsoft365Theme()
        self.style = self.theme.apply_theme(self.root)
        
        # Configurar colores de fondo
        self.root.configure(bg=self.theme.COLORS['bg_main'])
        
    def check_authentication(self):
        """Verifica la autenticación con Google Sheets"""
        logger.info("Verificando autenticación...")
        
        if not sheets_manager.is_authenticated():
            response = messagebox.askyesno(
                "Configuración Necesaria",
                "No se detectó autenticación con Google Sheets.\n\n"
                "¿Deseas configurar las credenciales ahora?"
            )
            
            if response:
                self.show_config_dialog()
            else:
                messagebox.showinfo(
                    "Modo Exploración",
                    "La aplicación se abrirá en modo exploración.\n"
                    "Algunas funciones estarán limitadas."
                )
                logger.warning("Usuario canceló configuración - Modo offline")
        else:
            logger.info("✅ Autenticación verificada correctamente")
        
        # Construir interfaz
        self.build_interface()
        
    def show_config_dialog(self):
        """Muestra diálogo de configuración completo"""
        from src.gui.dialogo_configuracion import DialogoConfiguracion
        
        try:
            DialogoConfiguracion(self.root, self)
        except Exception as e:
            logger.error(f"Error al abrir configuración: {e}")
            # Fallback al método antiguo
            self._show_old_config_dialog()
    
    def _show_old_config_dialog(self):
        """Método antiguo de configuración (fallback)"""
        from tkinter import filedialog
        
        # Pedir archivo de credenciales
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de credenciales",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                sheets_manager.set_credentials(file_path)
                spreadsheet_id = self.ask_spreadsheet_id()
                
                if spreadsheet_id:
                    sheets_manager.set_spreadsheet_id(spreadsheet_id)
                    messagebox.showinfo("Éxito", "Configuración completada correctamente")
                    logger.info("✅ Configuración de Google Sheets completada")
                else:
                    messagebox.showwarning("Advertencia", "No se configuró el ID del spreadsheet")
            except Exception as e:
                messagebox.showerror("Error", f"Error al configurar credenciales:\n{e}")
                logger.error(f"Error en configuración: {e}")
        
    def ask_spreadsheet_id(self):
        """Pide el ID del spreadsheet"""
        dialog = tk.Toplevel(self.root)
        dialog.title("ID de Google Sheets")
        dialog.geometry("500x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centrar diálogo
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (250)
        y = (dialog.winfo_screenheight() // 2) - (100)
        dialog.geometry(f"+{x}+{y}")
        
        # Contenido
        frame = tk.Frame(dialog, bg=self.theme.COLORS['bg_main'], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = self.theme.create_title_label(
            frame,
            "Introduce el ID de tu Google Sheets:"
        )
        label.pack(pady=(0, 10))
        
        entry = self.theme.create_entry(frame, width=50)
        entry.pack(pady=10, fill=tk.X)
        entry.focus()
        
        result = {'id': None}
        
        def on_ok():
            result['id'] = entry.get().strip()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Botones
        btn_frame = tk.Frame(dialog, bg=self.theme.COLORS['bg_main'])
        btn_frame.pack(pady=10)
        
        btn_ok = self.theme.create_primary_button(btn_frame, "Aceptar", on_ok)
        btn_ok.pack(side=tk.LEFT, padx=5)
        
        btn_cancel = self.theme.create_secondary_button(btn_frame, "Cancelar", on_cancel)
        btn_cancel.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        entry.bind('<Return>', lambda e: on_ok())
        
        dialog.wait_window()
        return result['id']
        
    def build_interface(self):
        """Construye la interfaz principal"""
        # Frame principal con fondo
        main_frame = tk.Frame(self.root, bg=self.theme.COLORS['bg_main'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Barra superior
        self.create_header(main_frame)
        
        # Contenido principal
        content_frame = tk.Frame(main_frame, bg=self.theme.COLORS['bg_main'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear paneles
        self.create_panels()
        
        # Barra de estado
        self.create_statusbar(main_frame)
        
        logger.info("✅ Interfaz construida correctamente")
        
    def create_header(self, parent):
        """Crea la barra superior"""
        header = tk.Frame(parent, bg=self.theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Contenedor con padding
        container = tk.Frame(header, bg=self.theme.COLORS['primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=0)
        
        # Título
        title_label = tk.Label(
            container,
            text=f"🏛️ {APP_CONFIG['NOMBRE']}",
            font=(self.theme.FONTS['family'], 18, 'bold'),
            fg=self.theme.COLORS['text_white'],
            bg=self.theme.COLORS['primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Versión
        version_label = tk.Label(
            container,
            text=f"v{APP_CONFIG['VERSION']}",
            font=(self.theme.FONTS['family'], 10),
            fg=self.theme.COLORS['primary_light'],
            bg=self.theme.COLORS['primary']
        )
        version_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botones de la derecha
        btn_frame = tk.Frame(container, bg=self.theme.COLORS['primary'])
        btn_frame.pack(side=tk.RIGHT)
        
        # Botón de configuración
        config_btn = tk.Button(
            btn_frame,
            text="⚙️ Configuración",
            command=self.show_config_dialog,
            bg=self.theme.COLORS['primary_dark'],
            fg=self.theme.COLORS['text_white'],
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_normal']),
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        config_btn.pack(side=tk.RIGHT, padx=5)
        
    def create_panels(self):
        """Crea los paneles de la aplicación"""
        try:
            # Dashboard
            dashboard_frame = tk.Frame(self.notebook, bg=self.theme.COLORS['bg_main'])
            self.dashboard = DashboardPanel(dashboard_frame, self)
            self.notebook.add(dashboard_frame, text="📊 Dashboard")
            
            # Solicitudes (versión real con 24 campos)
            solicitudes_frame = tk.Frame(self.notebook, bg=self.theme.COLORS['bg_main'])
            self.solicitudes = SolicitudesRealPanel(solicitudes_frame, self)
            self.notebook.add(solicitudes_frame, text="📋 Solicitudes")
            
            # Sesiones
            sesiones_frame = tk.Frame(self.notebook, bg=self.theme.COLORS['bg_main'])
            self.sesiones = SesionesPanel(sesiones_frame, self)
            self.notebook.add(sesiones_frame, text="🔬 Sesiones")
            
            # Búsqueda
            busqueda_frame = tk.Frame(self.notebook, bg=self.theme.COLORS['bg_main'])
            self.busqueda = BusquedaPanel(busqueda_frame, self)
            self.notebook.add(busqueda_frame, text="🔍 Búsqueda")
            
            # Informes
            informes_frame = tk.Frame(self.notebook, bg=self.theme.COLORS['bg_main'])
            self.informes = InformesPanel(informes_frame, self)
            self.notebook.add(informes_frame, text="📄 Informes")
            
        except Exception as e:
            logger.error(f"Error al crear paneles: {e}")
            messagebox.showerror("Error", f"Error al crear paneles:\n{e}")
        
    def create_statusbar(self, parent):
        """Crea la barra de estado"""
        statusbar_frame = tk.Frame(parent, bg=self.theme.COLORS['bg_secondary'], height=30)
        statusbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        statusbar_frame.pack_propagate(False)
        
        self.statusbar = tk.Label(
            statusbar_frame,
            text="✅ Listo",
            font=(self.theme.FONTS['family'], self.theme.FONTS['size_small']),
            fg=self.theme.COLORS['text_secondary'],
            bg=self.theme.COLORS['bg_secondary'],
            anchor=tk.W,
            padx=20
        )
        self.statusbar.pack(fill=tk.BOTH, expand=True)
        
    def update_status(self, message: str):
        """Actualiza el mensaje de la barra de estado"""
        if hasattr(self, 'statusbar'):
            self.statusbar.config(text=message)
            self.root.update_idletasks()
        
    def refresh_all(self):
        """Refresca todos los paneles"""
        try:
            if hasattr(self, 'dashboard'):
                self.dashboard.load_data()
            if hasattr(self, 'solicitudes'):
                self.solicitudes.load_data()
            if hasattr(self, 'sesiones'):
                self.sesiones.load_data()
            self.update_status("✅ Datos actualizados")
        except Exception as e:
            logger.error(f"Error al refrescar: {e}")
            self.update_status(f"❌ Error: {e}")
        
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Deseas cerrar la aplicación?"):
            logger.info("Cerrando aplicación...")
            self.root.quit()
            self.root.destroy()
            import sys
            sys.exit(0)
        
    def run(self):
        """Inicia la aplicación"""
        logger.info("Iniciando aplicación...")
        self.root.mainloop()
