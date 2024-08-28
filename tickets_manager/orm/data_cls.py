import os
import uuid
import enum

from sqlalchemy import (
    Column, Integer, String, DateTime, Interval, ForeignKey,
    UUID, JSON, TIMESTAMP, func, TypeDecorator, Enum
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from cryptography.fernet import Fernet


class AES:
    __secret_cipher = os.getenv("SECRET_CIPHER")
    _cipher_suite = Fernet(__secret_cipher)
    @classmethod
    def encrypt(cls, value):
        return cls._cipher_suite.encrypt(value.encode()).decode()

    @classmethod
    def decrypt(cls, value):
        return cls._cipher_suite.decrypt(value.encode()).decode()


class EncryptedValue(TypeDecorator):
    impl = String
    cache_ok = False

    def process_bind_param(self, value, dialect):
        return AES.encrypt(value)

    def process_result_value(self, value, dialect):
        return AES.decrypt(value)


class TypeAction(enum.Enum):
    log_in = "log_in"
    open_ticket = "open_ticket"
    change_state = "change_state"
    error = 'error'
    get_tickets = 'get_tickets'

TypeAction_lst = []

class StatusTicket(enum.Enum):
    open = "open"
    processing = "processing"
    closed_success = "closed_success"
    closed_fail = "closed_fail"

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(String(53), primary_key=True)
    access_token = Column(
        EncryptedValue(255)
    )
    dt_token_update = Column(TIMESTAMP(timezone=True))
    expire_in = Column(Interval)
    email = Column(
        EncryptedValue(128),
        unique=True, nullable=False)
    tickets = relationship("Tickets", back_populates="author_user")
    actions = relationship("Actions", back_populates="author_user")


class Tickets(Base):
    __tablename__ = 'tickets'

    guid_ticket = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author = Column(String(53), ForeignKey('users.id'))
    status = Column(
        Enum(StatusTicket),
        # ForeignKey('status_enum.status')
    )

    author_user = relationship("User", back_populates="tickets")
    actions = relationship("Actions", back_populates="ticket")


class Actions(Base):
    __tablename__ = 'actions'

    timestamp = Column(TIMESTAMP(timezone=True), primary_key=True, default=func.now())
    type = Column(
        Enum(TypeAction),
        # ForeignKey('type_enum.type')
    )
    guid_ticket = Column(PG_UUID(as_uuid=True), ForeignKey('tickets.guid_ticket'))
    author = Column(String(53), ForeignKey('users.id'))
    data = Column(JSON)

    author_user = relationship("User", back_populates="actions")
    ticket = relationship("Tickets", back_populates="actions")
