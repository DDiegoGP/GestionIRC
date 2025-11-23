"""
Sistema de Logging para Gestión IRC
"""
import logging
import logging.handlers
from pathlib import Path
import colorlog
from config import LOG_CONFIG, LOGS_DIR


def setup_logger(name: str = 'GestionIRC') -> logging.Logger:
    """
    Configura el sistema de logging.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicados
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_CONFIG['LEVEL'])
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_CONFIG['FILE'],
        maxBytes=LOG_CONFIG['MAX_BYTES'],
        backupCount=LOG_CONFIG['BACKUP_COUNT'],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_CONFIG['FORMAT'])
    file_handler.setFormatter(file_formatter)
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(color_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Logger global
logger = setup_logger()
