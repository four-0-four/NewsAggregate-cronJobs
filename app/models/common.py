from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.sql import func
from ..config.database import Base

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(30), nullable=False)
    fileName = Column(String(255), nullable=False)
    fileExtension = Column(String(20), nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())


class NewsCorporations(Base):
    __tablename__ = "newsCorporations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    parent = Column(String(100))
    url = Column(String(300))
    logo = Column(String(300))
    language = Column(String(100))
    location = Column(String(100))

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    parent_id = Column(Integer, nullable=False)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())