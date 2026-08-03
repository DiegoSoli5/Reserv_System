from .database import Base
from sqlalchemy import String, Text, select, ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30),unique=True)
    password: Mapped[str]
    role: Mapped[str] = mapped_column(nullable=True, default="client")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    bookings: Mapped[List["Booking"]] = relationship(back_populates="client", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship(back_populates="client", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str]
    total_tickets: Mapped[int]
    avaliable_tickets: Mapped[int]
    price: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    # cascade="all, delete-orphan"
    #if an admin wants to delete a event, this step will delete all the orphan - bookings
    bookings: Mapped[List["Booking"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    client: Mapped["Client"] = relationship(back_populates="events")
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id",ondelete="CASCADE"))

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    total_price: Mapped[float]
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    client: Mapped["Client"] = relationship(back_populates="bookings")
    event: Mapped["Event"] = relationship(back_populates="bookings")