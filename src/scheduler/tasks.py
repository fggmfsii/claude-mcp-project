from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime
import logging

from ..models.db import SessionLocal
from ..services.instagram_service import InstagramService
from ..services.feed_service import FeedService
from ..services.gemini_service import GeminiService
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class TaskManager:
    def __init__(self, cookie_file: str, gemini_api_key: str):
        self.cookie_file = cookie_file
        self.gemini_api_key = gemini_api_key
        self.rate_limiter = RateLimiter()
        self.scheduler = None
        
    def init_services(self):
        """Inițializează serviciile necesare"""
        instagram_service = InstagramService(self.cookie_file)
        gemini_service = GeminiService(self.gemini_api_key)
        feed_service = FeedService(instagram_service, gemini_service)
        return instagram_service, gemini_service, feed_service
        
    def process_feed(self):
        """Task pentru procesarea feed-ului"""
        try:
            instagram, gemini, feed = self.init_services()
            session = SessionLocal()
            
            results = feed.process_feed(session)
            logger.info(f"Processed {len(results)} posts from feed")
            
            for result in results:
                if result['status'] == 'new' and 'action' in result:
                    action = result['action']
                    if action['action'] in ['like', 'both']:
                        self._perform_action('like', instagram, result['post'])
                    if action['action'] in ['comment', 'both']:
                        self._perform_action('comment', instagram, result['post'], 
                                          text=action['response'])
                        
            session.close()
        except Exception as e:
            logger.error(f"Error in process_feed task: {str(e)}")
            
    def _perform_action(self, action_type: str, instagram: InstagramService, 
                       post: dict, **kwargs):
        """Execută o acțiune cu respectarea rate limiting"""
        if not self.rate_limiter.can_perform_action(action_type):
            logger.warning(f"Rate limit reached for {action_type}")
            return
            
        try:
            self.rate_limiter.wait_if_needed(action_type)
            
            if action_type == 'like':
                result = instagram.like_post(post['shortcode'])
            elif action_type == 'comment':
                result = instagram.comment_on_post(post['shortcode'], 
                                                kwargs.get('text', 'Great! ✨'))
                
            if 'error' not in result:
                self.rate_limiter.log_action(action_type)
                logger.info(f"Successfully performed {action_type} on {post['shortcode']}")
            else:
                logger.error(f"Failed to perform {action_type}: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error performing {action_type}: {str(e)}")
    
    def start(self):
        """Pornește sistemul de task-uri programate"""
        try:
            jobstores = {
                'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
            }
            
            self.scheduler = BackgroundScheduler(jobstores=jobstores)
            
            # Adaugă task-urile programate
            self.scheduler.add_job(
                self.process_feed,
                'interval',
                minutes=5,
                id='process_feed'
            )
            
            self.scheduler.start()
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise