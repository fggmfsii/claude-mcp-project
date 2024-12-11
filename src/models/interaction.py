from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Interaction(Base):
    __tablename__ = 'interactions'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    type = Column(String(20), nullable=False)  # comment, like, mention
    content = Column(Text, nullable=True)
    user_id = Column(String(50), nullable=True) 
    direction = Column(String(10), nullable=False)  # incoming/outgoing
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship('Conversation', back_populates='interactions')