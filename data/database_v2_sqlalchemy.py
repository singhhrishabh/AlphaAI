"""
AlphaAI — Database Layer (V2 - SQLAlchemy / PostgreSQL)
Ready to migrate the backend to support multi-tenant YC-tier scale.
"""
import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

logger = logging.getLogger("alphaai.data.db_v2")

# Uses DATABASE_URL from environment for managed PostgreSQL (e.g., Supabase / Neon)
# Fallback to local sqlite for backwards compat
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/alphaai.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    """Multi-tenant User Table (YC requirement)"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    risk_profile = Column(String, default="moderate")

class Stock(Base):
    __tablename__ = "stocks"
    symbol = Column(String, primary_key=True, index=True)
    name = Column(String)
    sector = Column(String)
    market_cap = Column(Float)
    added_at = Column(DateTime, default=datetime.utcnow)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    signal = Column(String)
    confidence = Column(Float)
    reasoning = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Core PostgreSQL/SQLAlchemy schema initialized.")

if __name__ == "__main__":
    init_db()
