from pydantic import BaseModel

from src.domain.patient.schema import PatientResponse
from src.domain.enums import BunkStatus


class BunkModel(BaseModel):
	dispensary_id: int
	room_number: int
	bunk_number: int

class BunkResponse(BaseModel):
	id: int
	bunk_status: BunkStatus = BunkStatus.available
	dispensary_id: int
	room_number: int
	bunk_number: int


class BunkResponseForGet(BaseModel):
	id: int
	bunk_status: BunkStatus = BunkStatus.available
	dispensary_id: int
	room_number: int
	bunk_number: int
	patient: PatientResponse | None


class BunkResponseForPut(BaseModel):
	result: str = "Bunk Added"
	id: int
	bunk_status: BunkStatus = BunkStatus.available
	dispensary_id: int
	room_number: int
	bunk_number: int

class BunkResponseForPost(BaseModel):
	BunkId: int

class AllBunks(BaseModel):
	Bunks: list[BunkResponseForGet]

class AvailableBunks(BaseModel):
	Bunks: list[BunkResponse]

