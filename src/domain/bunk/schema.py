from pydantic import BaseModel
from enum import Enum

from src.domain.patient.schema import PatientResponse


class BunkStatus(str, Enum):
	available = "available"
	busy = "busy"
	not_available = "not_available"


class BunkModel(BaseModel):
	dispensary_id: int
	room_number: int
	bunk_number: int

class BunkResponse(BaseModel):
	id: int
	bunk_status: BunkStatus = "available"
	dispensary_id: int
	room_number: int
	bunk_number: int


class BunkResponseForGet(BaseModel):
	id: int
	bunk_status: BunkStatus = "available"
	dispensary_id: int
	room_number: int
	bunk_number: int
	patient: PatientResponse | None


class BunkResponseForPut(BaseModel):
	result: str = "Bunk Added"
	id: int
	bunk_status: BunkStatus = "available"
	dispensary_id: int
	room_number: int
	bunk_number: int

class BunkResponseForPost(BaseModel):
	BunkId: int

class AllBunks(BaseModel):
	Bunks: list[BunkResponseForGet]

class AvailableBunks(BaseModel):
	Bunks: list[BunkResponse]

