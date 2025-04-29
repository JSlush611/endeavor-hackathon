from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os

# Create database directory if it doesn't exist
os.makedirs('db', exist_ok=True)

# Database setup
DATABASE_URL = "sqlite:///db/orders.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    material = Column(String, index=True)
    size = Column(String, index=True)
    length = Column(String)
    coating = Column(String)
    thread_type = Column(String)
    description = Column(String, unique=True)
    unit_price = Column(Float, default=0.0)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    status = Column(String)  # 'processing', 'needs_review', 'completed', 'error'
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    line_items = relationship("LineItem", back_populates="order", cascade="all, delete-orphan")

class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    extracted_text = Column(String)
    matched_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    confidence_score = Column(Float)
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="line_items")
    matched_product = relationship("Product")

# Create all tables
Base.metadata.create_all(bind=engine) 