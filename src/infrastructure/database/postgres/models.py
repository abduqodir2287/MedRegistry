from sqlalchemy import Column, Integer, Text, ForeignKey, func, TIMESTAMP, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from src.infrastructure.database.postgres.database import Base


class Dispensary(Base):
    __tablename__ = "drug_dispensary"
    id = Column(Integer, primary_key=True)
    dispensary_name = Column(Text, nullable=False)
    address = Column(Text)

    rooms = relationship("Room", order_by="Room.id", back_populates="dispensary")
    users = relationship("Users", order_by="Users.id", back_populates="dispensary")
    # patients = relationship("Patient", order_by="Patient.id", back_populates="dispensary")


class Room(Base):
    __tablename__ = "room"
    id = Column(Integer, primary_key=True)
    room_status = Column(Text, default="available")
    room_number = Column(Integer, nullable=False)
    dispensary_id = Column(Integer, ForeignKey("drug_dispensary.id"))

    __table_args__ = (
        UniqueConstraint('room_number', 'dispensary_id', name='uix_room_number_dispensary_id'),
    )

    dispensary = relationship("Dispensary", back_populates="rooms")
    bunks = relationship("Bunk", order_by="Bunk.id", back_populates="room")
    # patients = relationship("Patient", order_by="Patient.id", back_populates="room")


class Bunk(Base):
    __tablename__ = 'bunk'

    id = Column(Integer, primary_key=True, index=True)
    bunk_status = Column(Text, default="available")
    bunk_number = Column(Integer, nullable=False)
    room_number = Column(Integer, nullable=False)
    dispensary_id = Column(Integer, nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(['room_number', 'dispensary_id'], ['room.room_number', 'room.dispensary_id']),
    )

    room = relationship('Room',
                        primaryjoin="and_(Bunk.room_number==Room.room_number, Bunk.dispensary_id==Room.dispensary_id)")
    # patients = relationship("Patient", order_by="Patient.id", back_populates="bunk")



class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    firstname = Column(Text, nullable=False)
    lastname = Column(Text, nullable=False)
    job_title = Column(Text, nullable=True)
    role = Column(Text, default="user")
    dispensary_id = Column(Integer, ForeignKey("drug_dispensary.id"))

    dispensary = relationship("Dispensary", back_populates="users")



