"""
Tema Microsoft 365 para la aplicación GestionIRC
Colores, fuentes y estilos profesionales
"""
import tkinter as tk
from tkinter import ttk


class Microsoft365Theme:
    """Tema visual Microsoft 365"""
    
    # Colores principales
    COLORS = {
        # Primarios
        'primary': '#0078D4',        # Azul Microsoft
        'primary_dark': '#005A9E',   # Azul oscuro
        'primary_light': '#50E6FF',  # Azul claro
        
        # Backgrounds
        'bg_main': '#FFFFFF',        # Blanco
        'bg_secondary': '#F3F2F1',   # Gris muy claro
        'bg_tertiary': '#FAF9F8',    # Gris ultra claro
        'bg_hover': '#EDEBE9',       # Gris hover
        'bg_selected': '#DEECF9',    # Azul muy claro
        
        # Textos
        'text_primary': '#323130',   # Negro suave
        'text_secondary': '#605E5C', # Gris texto
        'text_tertiary': '#8A8886',  # Gris claro
        'text_white': '#FFFFFF',     # Blanco
        
        # Bordes
        'border': '#EDEBE9',         # Gris borde
        'border_focus': '#0078D4',   # Azul foco
        
        # Estados
        'success': '#107C10',        # Verde
        'warning': '#FFB900',        # Amarillo
        'error': '#D13438',          # Rojo
        'info': '#00B7C3',           # Cian
        
        # Cards y sombras
        'card_bg': '#FFFFFF',
        'shadow': '#00000020',
    }
    
    # Fuentes
    FONTS = {
        'family': 'Segoe UI',
        'size_small': 9,
        'size_normal': 10,
        'size_medium': 11,
        'size_large': 12,
        'size_title': 14,
        'size_header': 16,
    }
    
    @classmethod
    def apply_theme(cls, root):
        """Aplica el tema a la ventana principal"""
        style = ttk.Style()
        
        # Configurar tema base
        available_themes = style.theme_names()
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        
        # === CONFIGURACIÓN GENERAL ===
        root.configure(bg=cls.COLORS['bg_main'])
        
        # === LABELS ===
        style.configure('TLabel',
            background=cls.COLORS['bg_main'],
            foreground=cls.COLORS['text_primary'],
            font=(cls.FONTS['family'], cls.FONTS['size_normal'])
        )
        
        style.configure('Title.TLabel',
            font=(cls.FONTS['family'], cls.FONTS['size_title'], 'bold'),
            foreground=cls.COLORS['text_primary']
        )
        
        style.configure('Header.TLabel',
            font=(cls.FONTS['family'], cls.FONTS['size_header'], 'bold'),
            foreground=cls.COLORS['primary']
        )
        
        style.configure('Secondary.TLabel',
            foreground=cls.COLORS['text_secondary'],
            font=(cls.FONTS['family'], cls.FONTS['size_small'])
        )
        
        # === BUTTONS ===
        style.configure('TButton',
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            borderwidth=1,
            relief='flat',
            padding=(12, 6)
        )
        
        style.map('TButton',
            background=[
                ('active', cls.COLORS['bg_hover']),
                ('!active', cls.COLORS['bg_secondary'])
            ],
            foreground=[('!active', cls.COLORS['text_primary'])]
        )
        
        # Botón primario
        style.configure('Primary.TButton',
            font=(cls.FONTS['family'], cls.FONTS['size_normal'], 'bold'),
            padding=(12, 6)
        )
        
        style.map('Primary.TButton',
            background=[
                ('active', cls.COLORS['primary_dark']),
                ('!active', cls.COLORS['primary'])
            ],
            foreground=[('!active', cls.COLORS['text_white'])]
        )
        
        # Botón secundario
        style.configure('Secondary.TButton',
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            padding=(12, 6)
        )
        
        # Botón de éxito
        style.configure('Success.TButton',
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            padding=(12, 6)
        )
        
        style.map('Success.TButton',
            background=[
                ('active', '#0E6A0E'),
                ('!active', cls.COLORS['success'])
            ],
            foreground=[('!active', cls.COLORS['text_white'])]
        )
        
        # === FRAMES ===
        style.configure('TFrame',
            background=cls.COLORS['bg_main']
        )
        
        style.configure('Card.TFrame',
            background=cls.COLORS['card_bg'],
            relief='flat',
            borderwidth=1
        )
        
        style.configure('Secondary.TFrame',
            background=cls.COLORS['bg_secondary']
        )
        
        # === NOTEBOOK (Pestañas) ===
        style.configure('TNotebook',
            background=cls.COLORS['bg_main'],
            borderwidth=0
        )
        
        style.configure('TNotebook.Tab',
            background=cls.COLORS['bg_secondary'],
            foreground=cls.COLORS['text_primary'],
            padding=(20, 8),
            font=(cls.FONTS['family'], cls.FONTS['size_normal'])
        )
        
        style.map('TNotebook.Tab',
            background=[
                ('selected', cls.COLORS['bg_main']),
                ('active', cls.COLORS['bg_hover'])
            ],
            foreground=[
                ('selected', cls.COLORS['primary']),
                ('!selected', cls.COLORS['text_secondary'])
            ]
        )
        
        # === TREEVIEW ===
        style.configure('Treeview',
            background=cls.COLORS['bg_main'],
            foreground=cls.COLORS['text_primary'],
            fieldbackground=cls.COLORS['bg_main'],
            borderwidth=0,
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            rowheight=28
        )
        
        style.configure('Treeview.Heading',
            background=cls.COLORS['bg_secondary'],
            foreground=cls.COLORS['text_primary'],
            borderwidth=1,
            relief='flat',
            font=(cls.FONTS['family'], cls.FONTS['size_normal'], 'bold')
        )
        
        style.map('Treeview',
            background=[('selected', cls.COLORS['bg_selected'])],
            foreground=[('selected', cls.COLORS['text_primary'])]
        )
        
        style.map('Treeview.Heading',
            background=[('active', cls.COLORS['bg_hover'])]
        )
        
        # === ENTRY ===
        style.configure('TEntry',
            fieldbackground=cls.COLORS['bg_main'],
            foreground=cls.COLORS['text_primary'],
            borderwidth=1,
            relief='solid',
            padding=8,
            font=(cls.FONTS['family'], cls.FONTS['size_normal'])
        )
        
        # === COMBOBOX ===
        style.configure('TCombobox',
            fieldbackground=cls.COLORS['bg_main'],
            background=cls.COLORS['bg_main'],
            foreground=cls.COLORS['text_primary'],
            borderwidth=1,
            relief='solid',
            padding=8,
            font=(cls.FONTS['family'], cls.FONTS['size_normal'])
        )
        
        # === SCROLLBAR ===
        style.configure('Vertical.TScrollbar',
            background=cls.COLORS['bg_secondary'],
            troughcolor=cls.COLORS['bg_tertiary'],
            borderwidth=0,
            arrowsize=14
        )
        
        # === PROGRESSBAR ===
        style.configure('TProgressbar',
            background=cls.COLORS['primary'],
            troughcolor=cls.COLORS['bg_secondary'],
            borderwidth=0,
            thickness=4
        )
        
        # === SEPARATOR ===
        style.configure('TSeparator',
            background=cls.COLORS['border']
        )
        
        return style
    
    @classmethod
    def create_card_frame(cls, parent, **kwargs):
        """Crea un frame tipo card con sombra y bordes redondeados"""
        frame = tk.Frame(
            parent,
            bg=cls.COLORS['card_bg'],
            relief='flat',
            bd=0,
            **kwargs
        )
        # Padding interno
        frame.configure(padx=20, pady=20)
        return frame
    
    @classmethod
    def create_title_label(cls, parent, text, **kwargs):
        """Crea un label de título"""
        return tk.Label(
            parent,
            text=text,
            font=(cls.FONTS['family'], cls.FONTS['size_title'], 'bold'),
            fg=cls.COLORS['text_primary'],
            bg=cls.COLORS['bg_main'],
            **kwargs
        )
    
    @classmethod
    def create_header_label(cls, parent, text, **kwargs):
        """Crea un label de encabezado"""
        return tk.Label(
            parent,
            text=text,
            font=(cls.FONTS['family'], cls.FONTS['size_header'], 'bold'),
            fg=cls.COLORS['primary'],
            bg=cls.COLORS['bg_main'],
            **kwargs
        )
    
    @classmethod
    def create_primary_button(cls, parent, text, command, **kwargs):
        """Crea un botón primario"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=cls.COLORS['primary'],
            fg=cls.COLORS['text_white'],
            font=(cls.FONTS['family'], cls.FONTS['size_normal'], 'bold'),
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground=cls.COLORS['primary_dark'],
            activeforeground=cls.COLORS['text_white'],
            **kwargs
        )
    
    @classmethod
    def create_secondary_button(cls, parent, text, command, **kwargs):
        """Crea un botón secundario"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=cls.COLORS['bg_secondary'],
            fg=cls.COLORS['text_primary'],
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            relief='flat',
            bd=1,
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground=cls.COLORS['bg_hover'],
            **kwargs
        )
    
    @classmethod
    def create_success_button(cls, parent, text, command, **kwargs):
        """Crea un botón de éxito"""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=cls.COLORS['success'],
            fg=cls.COLORS['text_white'],
            font=(cls.FONTS['family'], cls.FONTS['size_normal'], 'bold'),
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            activebackground='#0E6A0E',
            activeforeground=cls.COLORS['text_white'],
            **kwargs
        )
    
    @classmethod
    def create_entry(cls, parent, **kwargs):
        """Crea un campo de entrada con estilo"""
        entry = tk.Entry(
            parent,
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            bg=cls.COLORS['bg_main'],
            fg=cls.COLORS['text_primary'],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=cls.COLORS['border'],
            highlightcolor=cls.COLORS['primary'],
            **kwargs
        )
        return entry
    
    @classmethod
    def create_text(cls, parent, **kwargs):
        """Crea un widget Text con estilo"""
        text = tk.Text(
            parent,
            font=(cls.FONTS['family'], cls.FONTS['size_normal']),
            bg=cls.COLORS['bg_main'],
            fg=cls.COLORS['text_primary'],
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightbackground=cls.COLORS['border'],
            highlightcolor=cls.COLORS['primary'],
            wrap=tk.WORD,
            **kwargs
        )
        return text
