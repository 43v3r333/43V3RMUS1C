"""
System models: SystemLog
"""
from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON

from app.models.base import BaseModel


class SystemLog(BaseModel):
    """System log model for application logging"""
    
    __tablename__ = "system_logs"
    
    level = Column(String(20), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    
    # Logger context
    logger_name = Column(String(100), nullable=True)
    module = Column(String(100), nullable=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # Request context
    request_id = Column(String(100), nullable=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional data
    extra_data = Column(JSON, nullable=True)
    stack_trace = Column(Text, nullable=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self) -> str:
        return f"<SystemLog(id={self.id}, level={self.level}, message={self.message[:50]})>"