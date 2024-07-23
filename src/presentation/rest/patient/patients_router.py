from typing import Optional

from fastapi import APIRouter, status, Query

from src.domain.patient.patient_service import PatientsService
from src.domain.patient.schema import AllPatients, PatientResponseForPost, PatientResponse

patient_router = APIRouter(prefix="/Patient", tags=["Patients"])

patient_service = PatientsService()


@patient_router.get("", response_model=AllPatients, status_code=status.HTTP_200_OK)
async def get_patients() -> AllPatients:
	return await patient_service.get_all_patients_service()


@patient_router.post("", status_code=status.HTTP_200_OK, response_model=PatientResponseForPost)
async def add_patient(
		firstname: str = Query(..., description="The firstname of the patient"),
		lastname: str = Query(..., description="The lastname of the patient"),
		dispensary_id: int = Query(..., description="The dispensary id of the patient"),
		room_number: int = Query(..., description="The room number of the patient"),
		bunk_number: int = Query(..., description="The bunk number of the patient"),
):
	return await patient_service.add_patient_service(firstname, lastname, dispensary_id, room_number, bunk_number)


@patient_router.get("/{patient_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
async def get_patient_by_id(patient_id: int):
	return await patient_service.get_patient_by_id_service(patient_id)


@patient_router.patch("/{patient_id}", status_code=status.HTTP_200_OK, response_model=PatientResponseForPost)
async def update_patient(
		patient_id: int, firstname: Optional[str] = Query(None, description="The firstname of the patient"),
		lastname: Optional[str] = Query(None, description="The lastname of the patient")
):
	return await patient_service.update_patient_service(patient_id, firstname, lastname)



