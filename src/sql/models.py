from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import declarative_base, relationship

from config import amount as amount_data
from src.service.service_tools import correct_time, generate_users_password

Base = declarative_base()


class AdminApp(Base):
    __tablename__ = "admins_app"
    id = Column(type_=Integer, primary_key=True)
    login = Column(type_=String, unique=True, nullable=False)
    password = Column(type_=String, unique=True, nullable=False)
    status = Column(type_=Boolean, nullable=False, default=True)
    info = Column(type_=String, nullable=True, default=None)

    __table_args__ = (
        CheckConstraint(func.length(login).between(3, 20), name="login_length_range"),
        CheckConstraint(func.length(password).between(8, 32), name="password_length_range"),
    )


class User(Base):
    __tablename__ = "users"
    id = Column(type_=Integer, primary_key=True)
    telegram_id = Column(type_=BigInteger, nullable=False, unique=True)
    first_name = Column(type_=String, nullable=False)
    last_name = Column(type_=String, nullable=True, default=None)
    username = Column(type_=String, nullable=True, default=None)
    language_code = Column(type_=String(3), nullable=True, default=None)
    created_at = Column(type_=DateTime, nullable=False, default=correct_time)
    phone_number = Column(type_=String(30), nullable=True, default=None)
    birthday = Column(type_=Date, nullable=True, default=None)
    status = Column(type_=Boolean, nullable=False, default=False)
    info = Column(type_=String, nullable=True, default=None)
    user_login = relationship("UserLogin", back_populates="user")
    user_chat = relationship("UserChat", back_populates="user")
    chats = relationship("Chat", back_populates="user")
    holidays = relationship("Holiday", back_populates="user")
    report = relationship("Report", back_populates="user")


class UserLogin(Base):
    __tablename__ = "user_login"
    id = Column(type_=Integer, primary_key=True)
    user_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), unique=True, nullable=False)
    password = Column(type_=String(30), nullable=True, default=generate_users_password)
    user = relationship("User", back_populates="user_login")


class UserChat(Base):
    __tablename__ = "user_chat"
    id = Column(type_=Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), unique=False, nullable=False)
    user_telegram_id = Column(BigInteger, ForeignKey("users.telegram_id"), unique=False, nullable=False)
    status = Column(type_=Boolean, nullable=False, default=True)
    updated_at = Column(type_=DateTime, nullable=False, default=correct_time)
    chat = relationship("Chat", back_populates="user_chat")
    user = relationship("User", back_populates="user_chat")


class Chat(Base):
    __tablename__ = "chats"
    id = Column(type_=Integer, primary_key=True)
    chat_id = Column(type_=BigInteger, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(type_=String(length=16), nullable=False)
    status = Column(type_=Boolean, nullable=False, default=False)
    created_at = Column(type_=DateTime, nullable=False, default=correct_time)
    user = relationship("User", back_populates="chats")
    user_chat = relationship("UserChat", back_populates="chat")
    holidays = relationship("Holiday", back_populates="chat")
    report = relationship("Report", back_populates="chat")


class Holiday(Base):
    __tablename__ = "holidays"
    id = Column(type_=Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    info = Column(type_=String, nullable=True, default=None)
    date_event = Column(type_=Date, nullable=False)
    amount = Column(type_=Integer, nullable=False, default=amount_data)  # 500 (int)
    status = Column(type_=Boolean, nullable=False, default=False)
    created_at = Column(type_=DateTime, nullable=False, default=correct_time)
    user = relationship("User", back_populates="holidays")
    chat = relationship("Chat", back_populates="holidays")
    report = relationship("Report", back_populates="holidays")


class Report(Base):
    __tablename__ = "report"
    id = Column(type_=Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    holiday_id = Column(Integer, ForeignKey("holidays.id"), nullable=False)
    status = Column(type_=Boolean, nullable=False, default=False)
    user = relationship("User", back_populates="report")
    chat = relationship("Chat", back_populates="report")
    holidays = relationship("Holiday", back_populates="report")


class SystemData(Base):
    __tablename__ = "system_data"
    id = Column(type_=Integer, primary_key=True)
    title = Column(type_=String(30), nullable=False, unique=True)
    data_digital = Column(type_=BigInteger, nullable=True, default=None)
    data_text = Column(type_=String, nullable=True, default=None)
    data_status = Column(type_=Boolean, nullable=True, default=None)
