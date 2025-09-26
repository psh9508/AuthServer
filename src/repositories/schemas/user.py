from sqlalchemy import UUID, Column, Integer, String, LargeBinary, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, server_default=func.gen_random_uuid())
    login_id = Column(String(255), unique=True, nullable=False)
    password = Column(LargeBinary, nullable=False)
    salt = Column(String(32), nullable=False)
    email_verified = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<User(id={self.id}, login_id='{self.login_id}')>"