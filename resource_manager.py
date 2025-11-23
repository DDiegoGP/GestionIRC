"""
Módulo para manejar recursos gráficos (logos, iconos)
en la aplicación IRC - Compatible con desarrollo y ejecutable empaquetado
"""

import os
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class ResourceManager:
    """
    Gestor de recursos gráficos para la aplicación
    Maneja rutas tanto en desarrollo como en ejecutable empaquetado
    """
    
    def __init__(self):
        self.base_path = self._get_base_path()
        self.logo_image = None
        self.logo_header = None
        self.logo_splash = None
    
    def _get_base_path(self):
        """
        Obtiene el path base correcto tanto en desarrollo como en ejecutable
        """
        if getattr(sys, 'frozen', False):
            # Si es ejecutable empaquetado (PyInstaller)
            if hasattr(sys, '_MEIPASS'):
                # Directorio temporal de PyInstaller
                return sys._MEIPASS
            else:
                # Directorio del ejecutable
                return os.path.dirname(sys.executable)
        else:
            # Modo desarrollo
            return os.path.dirname(os.path.abspath(__file__))
    
    def get_resource_path(self, relative_path):
        """
        Construye la ruta completa a un recurso
        
        Args:
            relative_path: Ruta relativa al recurso (ej: 'resources/logo.png')
            
        Returns:
            str: Ruta absoluta al recurso
        """
        return os.path.join(self.base_path, relative_path)
    
    def setup_window_icon(self, window):
        """
        Establece el icono de la ventana
        
        Args:
            window: Ventana tkinter (root o Toplevel)
        """
        icon_path = self.get_resource_path('resources/irc_icon.ico')
        
        if os.path.exists(icon_path):
            try:
                window.iconbitmap(icon_path)
                return True
            except Exception as e:
                print(f"⚠️  No se pudo establecer el icono: {e}")
                return False
        else:
            print(f"⚠️  No se encontró el icono en: {icon_path}")
            return False
    
    def load_logo_header(self, max_width=200, max_height=80):
        """
        Carga el logo para el header de la aplicación
        
        Args:
            max_width: Ancho máximo en píxeles
            max_height: Alto máximo en píxeles
            
        Returns:
            ImageTk.PhotoImage o None si hay error
        """
        # Intentar cargar logo pre-redimensionado
        logo_path = self.get_resource_path('resources/irc_logo_header.png')
        
        # Si no existe, intentar con el logo original
        if not os.path.exists(logo_path):
            logo_path = self.get_resource_path('resources/irc_logo.png')
        
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                
                # Redimensionar manteniendo aspecto
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convertir para tkinter
                self.logo_header = ImageTk.PhotoImage(img)
                return self.logo_header
                
            except Exception as e:
                print(f"⚠️  Error cargando logo header: {e}")
                return None
        else:
            print(f"⚠️  No se encontró el logo en: {logo_path}")
            return None
    
    def load_logo_splash(self, max_width=400, max_height=200):
        """
        Carga el logo para la pantalla de splash
        
        Args:
            max_width: Ancho máximo en píxeles
            max_height: Alto máximo en píxeles
            
        Returns:
            ImageTk.PhotoImage o None si hay error
        """
        # Intentar cargar logo pre-redimensionado
        logo_path = self.get_resource_path('resources/irc_logo_splash.png')
        
        # Si no existe, intentar con el logo original
        if not os.path.exists(logo_path):
            logo_path = self.get_resource_path('resources/irc_logo.png')
        
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                
                # Redimensionar manteniendo aspecto
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Convertir para tkinter
                self.logo_splash = ImageTk.PhotoImage(img)
                return self.logo_splash
                
            except Exception as e:
                print(f"⚠️  Error cargando logo splash: {e}")
                return None
        else:
            print(f"⚠️  No se encontró el logo en: {logo_path}")
            return None
    
    def create_header_frame(self, parent, title="Gestión de Solicitudes IRC", subtitle="Instalación Radiactiva de Categoría"):
        """
        Crea un frame de header completo con logo y título
        
        Args:
            parent: Widget padre
            title: Título principal
            subtitle: Subtítulo
            
        Returns:
            ttk.Frame con el header
        """
        header_frame = ttk.Frame(parent)
        
        # Cargar logo
        logo = self.load_logo_header()
        
        if logo:
            # Frame para el logo
            logo_frame = ttk.Frame(header_frame)
            logo_frame.pack(side='left', padx=20, pady=10)
            
            logo_label = ttk.Label(logo_frame, image=logo)
            logo_label.image = logo  # Mantener referencia
            logo_label.pack()
        
        # Frame para texto
        text_frame = ttk.Frame(header_frame)
        text_frame.pack(side='left', fill='both', expand=True, pady=10)
        
        # Título
        title_label = ttk.Label(
            text_frame,
            text=title,
            font=('Arial', 16, 'bold')
        )
        title_label.pack(anchor='w')
        
        # Subtítulo
        if subtitle:
            subtitle_label = ttk.Label(
                text_frame,
                text=subtitle,
                font=('Arial', 10),
                foreground='gray'
            )
            subtitle_label.pack(anchor='w', pady=(2, 0))
        
        # Línea separadora
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=(0, 10))
        
        return header_frame
    
    def create_splash_screen(self, root, app_name="Gestión IRC", app_version="1.0"):
        """
        Crea una pantalla de splash
        
        Args:
            root: Ventana principal (oculta durante el splash)
            app_name: Nombre de la aplicación
            app_version: Versión
            
        Returns:
            Toplevel window del splash
        """
        # Crear ventana de splash
        splash = tk.Toplevel(root)
        splash.title("")
        
        # Sin bordes
        splash.overrideredirect(True)
        
        # Tamaño
        width = 500
        height = 300
        
        # Centrar en pantalla
        screen_width = splash.winfo_screenwidth()
        screen_height = splash.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        splash.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ttk.Frame(splash, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Logo
        logo = self.load_logo_splash()
        if logo:
            logo_label = ttk.Label(main_frame, image=logo)
            logo_label.image = logo  # Mantener referencia
            logo_label.pack(pady=20)
        
        # Nombre de la app
        ttk.Label(
            main_frame,
            text=app_name,
            font=('Arial', 18, 'bold')
        ).pack(pady=10)
        
        # Versión
        ttk.Label(
            main_frame,
            text=f"Versión {app_version}",
            font=('Arial', 10),
            foreground='gray'
        ).pack()
        
        # Barra de progreso
        progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        progress.pack(pady=20)
        progress.start(10)
        
        # Mensaje
        status_label = ttk.Label(
            main_frame,
            text="Iniciando...",
            font=('Arial', 9),
            foreground='gray'
        )
        status_label.pack()
        
        splash.update()
        
        return splash, status_label
    
    def close_splash(self, splash, delay=1000):
        """
        Cierra la pantalla de splash después de un delay
        
        Args:
            splash: Ventana del splash
            delay: Milisegundos antes de cerrar
        """
        splash.after(delay, splash.destroy)


# =============== EJEMPLO DE USO ===============

def ejemplo_uso():
    """
    Ejemplo de cómo usar el ResourceManager en tu aplicación
    """
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("App IRC")
    root.geometry("900x600")
    
    # Crear gestor de recursos
    res_manager = ResourceManager()
    
    # Establecer icono de la ventana
    res_manager.setup_window_icon(root)
    
    # Crear header con logo
    header = res_manager.create_header_frame(
        root,
        title="Gestión de Solicitudes IRC",
        subtitle="Instalación Radiactiva de Categoría"
    )
    header.pack(fill='x')
    
    # Contenido de ejemplo
    content_frame = ttk.Frame(root, padding=20)
    content_frame.pack(fill='both', expand=True)
    
    ttk.Label(
        content_frame,
        text="Contenido de la aplicación aquí...",
        font=('Arial', 12)
    ).pack(pady=50)
    
    # Iniciar aplicación
    root.mainloop()


def ejemplo_splash():
    """
    Ejemplo de uso del splash screen
    """
    
    # Crear ventana principal (oculta inicialmente)
    root = tk.Tk()
    root.withdraw()  # Ocultar
    
    # Crear gestor de recursos
    res_manager = ResourceManager()
    
    # Mostrar splash
    splash, status_label = res_manager.create_splash_screen(
        root,
        app_name="Gestión IRC",
        app_version="1.0.0"
    )
    
    # Simular carga de recursos
    def cargar_recursos():
        import time
        
        # Simular diferentes pasos de carga
        pasos = [
            "Cargando configuración...",
            "Conectando con Google Sheets...",
            "Inicializando interfaz...",
            "¡Listo!"
        ]
        
        for paso in pasos:
            status_label.config(text=paso)
            splash.update()
            time.sleep(0.5)
        
        # Cerrar splash y mostrar ventana principal
        splash.destroy()
        root.deiconify()
        
        # Configurar ventana principal
        root.title("Gestión IRC")
        root.geometry("900x600")
        res_manager.setup_window_icon(root)
        
        # Crear header
        header = res_manager.create_header_frame(root)
        header.pack(fill='x')
        
        # Contenido
        content = ttk.Frame(root, padding=20)
        content.pack(fill='both', expand=True)
        
        ttk.Label(
            content,
            text="¡Aplicación cargada!",
            font=('Arial', 14)
        ).pack(pady=50)
    
    # Cargar recursos después de mostrar splash
    root.after(100, cargar_recursos)
    
    # Iniciar aplicación
    root.mainloop()


if __name__ == "__main__":
    print("ResourceManager - Gestor de Recursos Gráficos")
    print()
    print("Selecciona un ejemplo:")
    print("1. Ejemplo básico (solo header con logo)")
    print("2. Ejemplo con splash screen")
    print()
    
    opcion = input("Opción (1 o 2): ").strip()
    
    if opcion == "1":
        ejemplo_uso()
    elif opcion == "2":
        ejemplo_splash()
    else:
        print("Opción no válida")
