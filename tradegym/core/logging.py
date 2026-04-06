from typing import Dict, Callable
import sys
import logging as _logging
from colorlog import ColoredFormatter
from beautifultable import BeautifulTable


__all__ = [
    'info',
    'warning',
    'error',
    'critical',
    'debug',
    'box',
    'configure_logging',
]


debug = _logging.debug
info = _logging.info
warning = _logging.warning
error = _logging.error
critical = _logging.critical


_LEVEL_LOG: Dict[int, Callable] = {
    _logging.DEBUG: debug,
    _logging.INFO: info,
    _logging.WARNING: warning,
    _logging.ERROR: error,
    _logging.CRITICAL: critical,
}


_DEFAULT_LOG_FORMATTER = ColoredFormatter(
    "%(thin)s%(light_black)s[%(asctime)s.%(msecs)03d]%(reset)s "
    "%(bold)s%(log_color)s%(levelname)-8s%(reset)s "
    "%(thin)s%(cyan)s%(filename)s%(reset)s:%(thin)s%(purple)s%(lineno)d%(reset)s - "
    "%(message_log_color)s%(message)s%(reset)s",
    
    datefmt="%H:%M:%S",
    log_colors={
        'DEBUG': 'light_cyan',
        'INFO': 'light_green',
        'WARNING': 'light_yellow',
        'ERROR': 'light_red',
        'CRITICAL': 'light_red,bg_white',
    },
    secondary_log_colors={
        'message': {
            'DEBUG': 'bold_black',  
            'INFO': 'bold_black',   
            'WARNING': 'bold_black',
            'ERROR': 'bold_red',    
            'CRITICAL': 'bold_red', 
        }
    },
    reset=True,
)


def configure_logging(
    level: int = _logging.INFO,
    formatter: _logging.Formatter = _DEFAULT_LOG_FORMATTER,
):
    handler = _logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    _logging.basicConfig(
        level=level,
        handlers=[handler],
        force=True,
    )


def box(content: str, level: int = _logging.INFO, stacklevel=2):
    table = BeautifulTable()
    table.rows.append([content])
    table.set_style(BeautifulTable.STYLE_BOX_ROUNDED)
    _LEVEL_LOG[level]("\n" + str(table), stacklevel=stacklevel)


configure_logging()