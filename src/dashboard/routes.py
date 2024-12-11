from flask import Blueprint, jsonify, render_template
from ..models.db import SessionLocal
from ..models.conversation import Conversation
from ..utils.metrics import MetricsTracker
from datetime import datetime, timedelta

dashboard = Blueprint('dashboard', __name__)
metrics = MetricsTracker()

@dashboard.route('/')
def index():
    return render_template('dashboard/index.html')

@dashboard.route('/api/dashboard/stats')
def get_stats():
    session = SessionLocal()
    try:
        # Calculează statisticile
        stats = calculate_stats(session)
        return jsonify(stats)
    finally:
        session.close()

def calculate_stats(session):
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Statistici de bază
    daily_stats = metrics.get_daily_stats()
    
    # Conversații active
    active_conversations = session.query(Conversation).filter(
        Conversation.is_active == True,
        Conversation.last_interaction >= today
    ).count()
    
    # Rate de succes/eroare
    success_rate = metrics.get_success_rate()
    error_rate = 100 - success_rate if success_rate > 0 else 0
    
    # Date pentru graficul de activitate
    activity_data = get_activity_data(session, now)
    
    # Date pentru graficul de erori
    error_data = get_error_distribution()
    
    # Activitate recentă
    recent_activity = get_recent_activity(session)
    
    return {
        "total_interactions": sum(daily_stats.values()),
        "success_rate": round(success_rate, 2),
        "error_rate": round(error_rate, 2),
        "active_conversations": active_conversations,
        "activity_data": activity_data,
        "error_data": error_data,
        "recent_activity": recent_activity
    }

def get_activity_data(session, now):
    # Ultimele 24 ore de activitate
    data = []
    for i in range(24):
        time = now - timedelta(hours=i)
        interactions = session.query(Conversation).filter(
            Conversation.last_interaction >= time,
            Conversation.last_interaction < time + timedelta(hours=1)
        ).count()
        data.append({
            "hour": time.strftime("%H:00"),
            "interactions": interactions
        })
    return data[::-1]  # Inversează pentru ordine cronologică

def get_error_distribution():
    # Distribuția erorilor pe categorii
    return {
        "rate_limit": metrics.daily_stats.get("rate_limit_errors", 0),
        "network": metrics.daily_stats.get("network_errors", 0),
        "authentication": metrics.daily_stats.get("auth_errors", 0),
        "other": metrics.daily_stats.get("other_errors", 0)
    }

def get_recent_activity(session):
    # Ultimele 50 de interacțiuni
    recent = session.query(Conversation).order_by(
        Conversation.last_interaction.desc()
    ).limit(50).all()
    
    return [{
        "time": conv.last_interaction.strftime("%H:%M:%S"),
        "action": conv.last_action,
        "status": "success" if conv.is_active else "error",
        "details": f"Post: {conv.post_shortcode}"
    } for conv in recent]