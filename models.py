from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Movie(Base):
    """Movie model - stores movie information and seating configuration"""
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    rows = Column(Integer, nullable=False)  # Max 26 (A-Z)
    seats_per_row = Column(Integer, nullable=False)  # Max 50
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    seats = relationship("Seat", back_populates="movie", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="movie", cascade="all, delete-orphan")

    @property
    def total_seats(self):
        return self.rows * self.seats_per_row

    @property
    def available_seats_count(self):
        return sum(1 for seat in self.seats if not seat.is_booked)


class Seat(Base):
    """Seat model - represents individual seats in the cinema"""
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    row_letter = Column(String(1), nullable=False)  # A-Z
    seat_number = Column(Integer, nullable=False)  # 1-50
    is_booked = Column(Boolean, default=False)

    # Relationships
    movie = relationship("Movie", back_populates="seats")
    booking_seat = relationship("BookingSeat", back_populates="seat", uselist=False)

    __table_args__ = (
        UniqueConstraint('movie_id', 'row_letter', 'seat_number', name='unique_seat_per_movie'),
    )

    @property
    def seat_label(self):
        return f"{self.row_letter}{self.seat_number}"


class Booking(Base):
    """Booking model - stores booking information"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(String(20), unique=True, nullable=False)  # e.g., GIC0001
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    movie = relationship("Movie", back_populates="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")

    @property
    def seats_display(self):
        """Return formatted seat labels"""
        return ", ".join(sorted([bs.seat.seat_label for bs in self.booking_seats]))


class BookingSeat(Base):
    """Junction table for many-to-many relationship between Booking and Seat"""
    __tablename__ = "booking_seats"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    booking = relationship("Booking", back_populates="booking_seats")
    seat = relationship("Seat", back_populates="booking_seat")

    __table_args__ = (
        UniqueConstraint('booking_id', 'seat_id', name='unique_booking_seat'),
    )
