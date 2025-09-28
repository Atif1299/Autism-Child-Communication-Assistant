from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    school_name = Column(String)
    home_location = Column(String)
    gender = Column(String) # Added gender field

    conversations = relationship("Conversation", back_populates="child")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    user_message = Column(Text)
    agent_message = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    child = relationship("Child", back_populates="conversations")
