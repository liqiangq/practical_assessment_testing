from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from app.db import Base


class TokenMapping(Base):
    __tablename__ = "token_mapping"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), nullable=False, unique=True, index=True)
    account_number = Column(String(128), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        UniqueConstraint("token", name="uq_token"),
        UniqueConstraint("account_number", name="uq_account_number"),
    )
