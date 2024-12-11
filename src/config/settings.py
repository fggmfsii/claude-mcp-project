from pathlib import Path
import os

class Config:
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGS_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    
    # Instagram settings
    INSTAGRAM_APP_ID = "936619743392459"
    COOKIES_FILE = "instagram_cookies.json"
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(DATA_DIR / "instagram_bot.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Rate limiting
    MAX_ACTIONS_PER_DAY = {
        "like": 350,
        "comment": 180,
        "follow": 200,
        "unfollow": 200
    }
    
    # Time delays (in seconds)
    MIN_DELAY_BETWEEN_ACTIONS = 3
    MAX_DELAY_BETWEEN_ACTIONS = 10
    
    # Conversation settings
    MAX_INTERACTIONS_PER_CONVERSATION = 5
    CONVERSATION_TIMEOUT_HOURS = 24

    # Dashboard settings
    DASHBOARD_UPDATE_INTERVAL = 30  # seconds
    DASHBOARD_HISTORY_DAYS = 7
    
    # Create required directories
    LOGS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)