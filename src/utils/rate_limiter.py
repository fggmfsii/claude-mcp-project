import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.limits = {
            'like': {'max': 350, 'per_hour': 50},
            'comment': {'max': 180, 'per_hour': 20},
            'follow': {'max': 200, 'per_hour': 30},
            'unfollow': {'max': 200, 'per_hour': 30},
        }
        self.actions = {action: [] for action in self.limits.keys()}
        
    def can_perform_action(self, action_type: str) -> bool:
        if action_type not in self.limits:
            return False
            
        now = datetime.now()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hour_ago = now - timedelta(hours=1)
        
        # Curăță acțiunile vechi
        self.actions[action_type] = [
            timestamp for timestamp in self.actions[action_type]
            if timestamp > day_start
        ]
        
        # Verifică limitele
        daily_count = len(self.actions[action_type])
        hourly_count = len([
            timestamp for timestamp in self.actions[action_type]
            if timestamp > hour_ago
        ])
        
        if (daily_count >= self.limits[action_type]['max'] or
            hourly_count >= self.limits[action_type]['per_hour']):
            logger.warning(f"Rate limit reached for {action_type}")
            return False
            
        return True
        
    def log_action(self, action_type: str):
        """Înregistrează o acțiune nouă"""
        if action_type in self.limits:
            self.actions[action_type].append(datetime.now())
            
    def get_delay(self, action_type: str) -> float:
        """Calculează timpul de așteptare între acțiuni"""
        if action_type == 'like':
            return 6.0  # ~600 pe zi
        elif action_type == 'comment':
            return 12.0  # ~300 pe zi
        elif action_type in ['follow', 'unfollow']:
            return 10.0  # ~400 pe zi
        return 5.0  # delay implicit

    def wait_if_needed(self, action_type: str):
        """Așteaptă dacă este necesară o pauză între acțiuni"""
        time.sleep(self.get_delay(action_type))