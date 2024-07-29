from datetime import datetime
from enum import Enum
from pydantic import BaseModel

class PatientStatus(str, Enum):
	on_treatment = "on_treatment"
	discharged = "discharged"


class PatientModel(BaseModel):
	firstname: str
	lastname: str
	dispensary_id: int
	room_number: int
	bunk_number: int


class PatientResponse(BaseModel):
	id: int
	firstname: str
	lastname: str
	arrival_date: datetime
	status: PatientStatus = "on_treatment"
	dispensary_id: int
	room_number: int
	bunk_number: int

class PatientResponseForPut(BaseModel):
	result: str = "Patient added successfully"
	id: int
	firstname: str
	lastname: str
	arrival_date: datetime
	status: PatientStatus = "on_treatment"
	dispensary_id: int
	room_number: int
	bunk_number: int


class PatientResponseForPost(BaseModel):
	PatientId: int


class AllPatients(BaseModel):
	Patients: list[PatientResponse]

