from datetime import datetime
from pydantic import BaseModel

from src.domain.enums import PatientStatus


class PatientModel(BaseModel):
	firstname: str
	lastname: str
	dispensary_id: int
	room_number: int
	bunk_number: int
	days_of_treatment: int


class PatientResponse(BaseModel):
	id: int
	firstname: str
	lastname: str
	arrival_date: datetime
	status: PatientStatus = PatientStatus.on_treatment
	dispensary_id: int
	room_number: int
	bunk_number: int
	days_left: str


class PatientResponseForPut(BaseModel):
	result: str = "Patient added successfully"
	id: int
	firstname: str
	lastname: str
	arrival_date: datetime
	status: PatientStatus = PatientStatus.on_treatment
	dispensary_id: int
	room_number: int
	bunk_number: int
	days_left: str


class PatientResponseForPost(BaseModel):
	PatientId: int


class AllPatients(BaseModel):
	Patients: list[PatientResponse]

class PatientDischarge(BaseModel):
	id: int
	firstname: str
	lastname: str
	arrival_date: datetime
	dispensary_id: int
	room_number: int
	bunk_number: int
	discharge_date: datetime

