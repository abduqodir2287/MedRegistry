from pydantic import BaseModel

class DispensaryModel(BaseModel):
	dispensary_name: str
	address: str

class DispensaryResponse(BaseModel):
	id: int
	dispensary_name: str
	address: str

class DispensaryResponseForPost(BaseModel):
	result: str = "Task updated"
	id: int
	dispensary_name: str
	address: str


class AllDispensaries(BaseModel):
	Dispensaries: list[DispensaryResponse]
