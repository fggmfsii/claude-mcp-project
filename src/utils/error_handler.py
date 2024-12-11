import time
import logging
from functools import wraps
from typing import Callable, Any, Dict
from requests.exceptions import RequestException
from ..utils.metrics import MetricsTracker

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self, metrics: MetricsTracker):
        self.metrics = metrics
        self.max_retries = 3
        self.retry_delay = 5  # secunde
        
    def with_retry(self, func: Callable) -> Callable:
        """Decorator pentru reîncercarea funcțiilor eșuate"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(self.max_retries):
                try:
                    result = func(*args, **kwargs)
                    # Înregistrează succes în metrici
                    self.metrics.track_action(
                        func.__name__, 
                        success=True,
                        details={'attempt': attempt + 1}
                    )
                    return result
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} "
                        f"failed for {func.__name__}: {str(e)}"
                    )
                    # Înregistrează eroarea în metrici
                    self.metrics.track_action(
                        func.__name__,
                        success=False,
                        details={
                            'attempt': attempt + 1,
                            'error': str(e)
                        }
                    )
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
            
            raise last_error
        return wrapper
        
    def handle_request_error(self, error: RequestException) -> Dict:
        """Gestionează erorile de request"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        if "429" in error_msg:
            logger.warning("Rate limit reached. Backing off...")
            time.sleep(30)  # Așteaptă 30 secunde
            return {
                "status": "retry",
                "message": "Rate limit reached",
                "wait_time": 30
            }
            
        elif "401" in error_msg or "403" in error_msg:
            logger.error("Authentication error. Cookie-urile ar putea fi expirate.")
            return {
                "status": "fatal",
                "message": "Authentication failed",
                "action": "refresh_cookies"
            }
            
        elif "5" in str(error.response.status_code):
            logger.error(f"Server error: {error_msg}")
            return {
                "status": "retry",
                "message": "Server error",
                "wait_time": 60
            }
            
        else:
            logger.error(f"Unhandled error: {error_type} - {error_msg}")
            return {
                "status": "error",
                "message": error_msg,
                "error_type": error_type
            }
            
    def recover_session(self, instagram_service) -> bool:
        """Încearcă să recupereze sesiunea"""
        try:
            # Reînnoiește cookie-urile
            instagram_service.refresh_cookies()
            
            # Verifică dacă sesiunea e validă
            test_response = instagram_service.test_connection()
            if test_response.ok:
                logger.info("Session recovered successfully")
                return True
                
            logger.error("Failed to recover session")
            return False
            
        except Exception as e:
            logger.error(f"Error during session recovery: {str(e)}")
            return False