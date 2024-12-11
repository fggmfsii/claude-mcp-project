import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List
from pathlib import Path

class MetricsTracker:
    def __init__(self, metrics_file: str = "metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()
        self.daily_stats = {
            'likes': 0,
            'comments': 0,
            'follows': 0,
            'unfollows': 0,
            'errors': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }
        
    def _load_metrics(self) -> Dict:
        try:
            if Path(self.metrics_file).exists():
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logging.error(f"Error loading metrics: {e}")
            return {}
            
    def save_metrics(self):
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving metrics: {e}")

    def track_action(self, action_type: str, success: bool, details: Dict = None):
        timestamp = datetime.now().isoformat()
        
        if action_type not in self.metrics:
            self.metrics[action_type] = []
            
        action_data = {
            'timestamp': timestamp,
            'success': success,
            'details': details or {}
        }
        
        self.metrics[action_type].append(action_data)
        
        # Actualizează statisticile zilnice
        if success:
            if action_type in self.daily_stats:
                self.daily_stats[action_type] += 1
            self.daily_stats['successful_requests'] += 1
        else:
            self.daily_stats['failed_requests'] += 1
            if not success:
                self.daily_stats['errors'] += 1

    def get_daily_stats(self) -> Dict:
        return self.daily_stats

    def get_success_rate(self, action_type: str = None) -> float:
        total = self.daily_stats['successful_requests'] + self.daily_stats['failed_requests']
        if total == 0:
            return 0.0
        return (self.daily_stats['successful_requests'] / total) * 100

    def reset_daily_stats(self):
        for key in self.daily_stats:
            self.daily_stats[key] = 0