from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class KeyboardShortcut(Base):
    __tablename__ = 'keyboard_shortcuts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    keyboard_shortcut = Column(Text)
    time = Column(DateTime)  # Changed from Date to DateTime
