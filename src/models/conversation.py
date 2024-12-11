from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from .db import Base

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    post_shortcode = Column(String(100), unique=True, nullable=False)
    post_content = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    interaction_count = Column(Integer, default=0)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship('Interaction', back_populates='conversation')