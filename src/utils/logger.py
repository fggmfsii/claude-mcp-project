import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

class CustomLogger:
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurare logger principal
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Format pentru logging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler pentru fișierul general
        general_handler = RotatingFileHandler(
            self.log_dir / "general.log",
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
        )
        general_handler.setLevel(logging.INFO)
        general_handler.setFormatter(formatter)
        
        # Handler pentru erori
        error_handler = RotatingFileHandler(
            self.log_dir / "errors.log",
            maxBytes=5*1024*1024,
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        
        # Handler pentru debug
        debug_handler = RotatingFileHandler(
            self.log_dir / "debug.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        
        # Handler pentru consolă
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Adaugă handlere la logger
        self.logger.addHandler(general_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(console_handler)
        
    def log_action(self, action_type: str, status: str, details: dict = None):
        """Logger specializat pentru acțiuni"""
        msg = f"Action: {action_type} - Status: {status}"
        if details:
            msg += f" - Details: {details}"
            
        if status == "success":
            self.logger.info(msg)
        elif status == "error":
            self.logger.error(msg)
        else:
            self.logger.debug(msg)
            
    def log_request(self, method: str, url: str, status_code: int, 
                   response_time: float):
        """Logger specializat pentru request-uri"""
        msg = f"Request: {method} {url} - Status: {status_code} - Time: {response_time:.2f}s"
        
        if status_code >= 500:
            self.logger.error(msg)
        elif status_code >= 400:
            self.logger.warning(msg)
        else:
            self.logger.info(msg)
            
    def log_error(self, error: Exception, context: dict = None):
        """Logger specializat pentru erori"""
        msg = f"Error: {str(error)}"
        if context:
            msg += f" - Context: {context}"
            
        self.logger.exception(msg)
        
    def create_session_log(self):
        """Creează un nou fișier de log pentru sesiunea curentă"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_log = self.log_dir / f"session_{timestamp}.log"
        
        handler = logging.FileHandler(session_log)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        self.logger.addHandler(handler)
        return session_log
        
    def clean_old_logs(self, days: int = 7):
        """Șterge logurile mai vechi de X zile"""
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in self.log_dir.glob("*.log.*"):
            if log_file.stat().st_mtime < cutoff.timestamp():
                log_file.unlink()