from sqlalchemy import Column, Integer, Text, ForeignKey, func, TIMESTAMP

from src.infrastructure.database.postgres.database import Base

class Dispensary(Base):
	__tablename__ = "drug_dispensary"
	id = Column(Integer, primary_key=True)
	dispensary_name = Column(Text, nullable=False)
	address = Column(Text)


class Room(Base):
	__tablename__ = "room"
	id = Column(Integer, primary_key=True)
	room_status = Column(Text, default="available")
	room_number = Column(Integer, nullable=False)
	dispensary_id = Column(Integer, ForeignKey("drug_dispensary.id"))


class Bunk(Base):
	__tablename__ = "bunks"
	id = Column(Integer, primary_key=True)
	bunk_status = Column(Text, default="available")
	bunk_number = Column(Integer)
	dispensary_id = Column(Integer, ForeignKey("drug_dispensary.id"))
	room_number = Column(Integer, ForeignKey("room.id"))


class Users(Base):
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	firstname = Column(Text)
	lastname = Column(Text)
	job_title = Column(Text, nullable=False)
	role = Column(Text, default="user")
	dispensary_id = Column(Integer, ForeignKey("drug_dispensary.id"))


class Patient(Base):
	__tablename__ = "patient"
	id = Column(Integer, primary_key=True)
	firstname = Column(Text)
	lastname = Column(Text)
	patient_status = Column(Text)
	arrival_date = Column(TIMESTAMP, server_default=func.now())
	dispensary_id = Column(Integer, ForeignKey("drug_dispensary.id"))
	room_number = Column(Integer, ForeignKey("room.id"))
	bunk_number = Column(Integer, ForeignKey("bunks.id"))

