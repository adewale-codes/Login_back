from sqlalchemy import Column, Integer, String, DateTime, text
from db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)

    l1_hash = Column(String(255), nullable=False)
    l2_hash = Column(String(255), nullable=False)
    l3_hash = Column(String(255), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP")
    )
