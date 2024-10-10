from sqlalchemy import String, Integer, BigInteger, Column, Boolean, Date, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import declarative_base, relationship
from datetime import date, datetime
from src.service.service_tools import correct_time, generate_users_password

Base = declarative_base()


class AdminApp(Base):
    __tablename__ = "admins_app"
    id: int = Column(type_=Integer, primary_key=True)
    login: str = Column(type_=String, unique=True, nullable=False)
    password: str = Column(type_=String, unique=True, nullable=False)
    status: bool = Column(type_=Boolean, nullable=False, default=True)
    info: str = Column(type_=String, nullable=True, default=None)

    __table_args__ = (
        CheckConstraint(func.length(login).between(3, 20), name='login_length_range'),
        CheckConstraint(func.length(password).between(8, 32), name='password_length_range')
    )


class User(Base):
    __tablename__ = "users"
    id: int = Column(type_=Integer, primary_key=True)
    telegram_id: int = Column(type_=BigInteger, nullable=False, unique=True)
    first_name: str = Column(type_=String, nullable=False)
    last_name: str = Column(type_=String, nullable=True, default=None)
    username: str = Column(type_=String, nullable=True, default=None)
    language_code: str = Column(type_=String(3), nullable=True, default=None)
    created_at: datetime = Column(type_=DateTime, nullable=False, default=correct_time)
    phone_number: str = Column(type_=String(30), nullable=True, default=None)
    birthday: date = Column(type_=Date, nullable=True, default=None)
    status: bool = Column(type_=Boolean, nullable=False, default=False)
    info: str = Column(type_=String, nullable=True, default=None)
    user_login = relationship("UserLogin", back_populates="user")
    user_chat = relationship("UserChat", back_populates="user")
    chats = relationship("Chat", back_populates="user")
    holidays = relationship("Holiday", back_populates="user")
    report = relationship("Report", back_populates="user")


class UserLogin(Base):
    __tablename__ = "user_login"
    id: int = Column(type_=Integer, primary_key=True)
    user_telegram_id: int = Column(BigInteger, ForeignKey('users.telegram_id'), unique=True, nullable=False)
    password: str = Column(type_=String(30), nullable=True, default=generate_users_password)
    user = relationship("User", back_populates="user_login")


class UserChat(Base):
    __tablename__ = "user_chat"
    id: int = Column(type_=Integer, primary_key=True)
    chat_id: int = Column(Integer, ForeignKey('chats.id'), unique=False, nullable=False)
    user_telegram_id: int = Column(BigInteger, ForeignKey('users.telegram_id'), unique=False, nullable=False)
    status: bool = Column(type_=Boolean, nullable=False, default=True)
    updated_at: datetime = Column(type_=DateTime, nullable=False, default=correct_time)
    chat = relationship("Chat", back_populates="user_chat")
    user = relationship("User", back_populates="user_chat")


class Chat(Base):
    __tablename__ = "chats"
    id: int = Column(type_=Integer, primary_key=True)
    chat_id: int = Column(type_=BigInteger, nullable=False, unique=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False)
    card_number: str = Column(type_=String(length=16), nullable=False)
    status: bool = Column(type_=Boolean, nullable=False, default=False)
    created_at: datetime = Column(type_=DateTime, nullable=False, default=correct_time)
    user = relationship("User", back_populates="chats")
    user_chat = relationship("UserChat", back_populates="chat")
    holidays = relationship("Holiday", back_populates="chat")
    report = relationship("Report", back_populates="chat")


class Holiday(Base):
    __tablename__ = "holidays"
    id: int = Column(type_=Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    chat_id: int = Column(Integer, ForeignKey('chats.id'), nullable=False)
    info: str = Column(type_=String, nullable=False)
    date_event: date = Column(type_=Date, nullable=False)
    amount: int = Column(type_=Integer, nullable=False, default=500)
    status: bool = Column(type_=Boolean, nullable=False, default=False)
    created_at: datetime = Column(type_=DateTime, nullable=False, default=correct_time)
    user = relationship("User", back_populates="holidays")
    chat = relationship("Chat", back_populates="holidays")
    report = relationship("Report", back_populates="holidays")


class Report(Base):
    __tablename__ = "report"
    id: int = Column(type_=Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    chat_id: int = Column(Integer, ForeignKey('chats.id'), nullable=False)
    holiday_id: int = Column(Integer, ForeignKey('holidays.id'), nullable=False)
    status: bool = Column(type_=Boolean, nullable=False, default=False)
    user = relationship("User", back_populates="report")
    chat = relationship("Chat", back_populates="report")
    holidays = relationship("Holiday", back_populates="report")
