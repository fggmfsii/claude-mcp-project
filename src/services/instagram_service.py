import requests
import logging
import re
from typing import Optional, Dict
from ..utils.cookie_manager import CookieManager

logger = logging.getLogger(__name__)

class InstagramService:
    def __init__(self, cookie_file: str):
        self.cookie_manager = CookieManager()
        self.cookies = self.cookie_manager.load_cookies(cookie_file)
        self.session = requests.Session()
        self.headers = self.cookie_manager.get_headers(self.cookies)
        
        # Setup session
        for cookie in self.cookies:
            self.session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain='.instagram.com'
            )

    def get_media_id(self, shortcode: str) -> Optional[str]:
        url = f'https://www.instagram.com/p/{shortcode}/'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                match = re.search(r'"media_id":"(\d+)"', response.text)
                if match:
                    return match.group(1)
            logger.error(f'Failed to get media_id for {shortcode}')
        except Exception as e:
            logger.error(f'Error getting media_id: {str(e)}')
        return None

    def like_post(self, shortcode: str) -> Dict:
        media_id = self.get_media_id(shortcode)
        if not media_id:
            return {"error": "Media ID not found"}

        like_url = f'https://www.instagram.com/web/likes/{media_id}/like/'
        try:
            response = self.session.post(
                like_url,
                headers=self.headers,
                data={'surface': 'www_feed'}
            )
            return response.json() if response.status_code == 200 else {"error": "Failed to like"}
        except Exception as e:
            logger.error(f'Error liking post: {str(e)}')
            return {"error": str(e)}

    def comment_on_post(self, shortcode: str, text: str) -> Dict:
        media_id = self.get_media_id(shortcode)
        if not media_id:
            return {"error": "Media ID not found"}

        comment_url = f'https://www.instagram.com/web/comments/{media_id}/add/'
        try:
            response = self.session.post(
                comment_url,
                headers=self.headers,
                data={'comment_text': text}
            )
            return response.json() if response.status_code == 200 else {"error": f"Failed to comment: {response.status_code}"}
        except Exception as e:
            logger.error(f'Error commenting on post: {str(e)}')
            return {"error": str(e)}"