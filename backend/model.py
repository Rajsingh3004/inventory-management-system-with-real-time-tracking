from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    quantity = Column(Integer)
    price = Column(Integer)
    # Relationships
    requests = relationship("Request", backref="item", cascade="all, delete-orphan")
    sales = relationship("Sale", backref="item", cascade="all, delete-orphan")

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)
    reqitem_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"))
    quantity = Column(Integer)
    price = Column(Integer)
    status = Column(String(100), default="pending")

class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer)
    # FIX: Yahan ForeignKey add karna zaroori hai taaki Item.sales kaam kare
    reqitem_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"))
    quantity = Column(Integer)
    price = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    week_number = Column(Integer, default=lambda: datetime.now().isocalendar()[1])

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    password = Column(String(100))
    role = Column(String(100))