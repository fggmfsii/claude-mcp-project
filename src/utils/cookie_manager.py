import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class CookieManager:
    def __init__(self):
        self.required_cookies = {'sessionid', 'csrftoken', 'ds_user_id'}
        
    def load_cookies(self, cookie_file: str) -> List[Dict]:
        """
        Încarcă și validează cookie-urile din fișier
        """
        try:
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
                
            if self.validate_cookies(cookies):
                logger.info(f"Successfully loaded {len(cookies)} cookies")
                return cookies
            else:
                raise ValueError("Invalid cookies")
                
        except FileNotFoundError:
            logger.error(f"Cookie file not found: {cookie_file}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in cookie file: {cookie_file}")
            raise

    def validate_cookies(self, cookies: List[Dict]) -> bool:
        """
        Verifică validitatea cookie-urilor
        """
        if not cookies:
            logger.error("Empty cookies list")
            return False

        # Verifică cookie-urile necesare
        cookie_names = {cookie['name'] for cookie in cookies}
        missing = self.required_cookies - cookie_names
        
        if missing:
            logger.error(f"Missing required cookies: {missing}")
            return False

        # Verifică expirarea
        for cookie in cookies:
            if 'expirationDate' in cookie:
                expiry = datetime.fromtimestamp(cookie['expirationDate'])
                if expiry < datetime.now():
                    logger.warning(f"Cookie {cookie['name']} has expired")
                    return False

        return True

    def get_cookie_value(self, cookies: List[Dict], name: str) -> Optional[str]:
        """
        Returnează valoarea unui cookie specific
        """
        for cookie in cookies:
            if cookie['name'] == name:
                return cookie['value']
        return None

    def get_headers(self, cookies: List[Dict]) -> Dict:
        """
        Generează headers pentru request-uri
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-IG-App-ID': '936619743392459',
            'X-ASBD-ID': '198387',
            'X-IG-WWW-Claim': '0',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://www.instagram.com/',
            'X-CSRFToken': self.get_cookie_value(cookies, 'csrftoken')
        }