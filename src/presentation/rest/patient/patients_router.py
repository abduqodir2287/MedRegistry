from typing import Optional
from fastapi import APIRouter, status, Query, Depends

from src.domain.authorization.auth import get_token
from src.domain.patient.patient_service import PatientsService
from src.domain.patient.schema import AllPatients, PatientResponseForPut, PatientResponse, PatientResponseForPost

patient_router = APIRouter(prefix="/Patient", tags=["Patients"])

patient_service = PatientsService()


@patient_router.get("", response_model=AllPatients, status_code=status.HTTP_200_OK)
async def get_patients(
		firstname: Optional[str] = Query(None, description="The firstname of the patient"),
		lastname: Optional[str] = Query(None, description="The lastname of the patient"),
		dispensary_id: Optional[int] = Query(None, description="The dispensary id of the patient")
) -> AllPatients:
	return await patient_service.get_all_patients_service(firstname, lastname, dispensary_id)


@patient_router.post("", status_code=status.HTTP_201_CREATED, response_model=PatientResponseForPost)
async def add_patient(
		firstname: str = Query(..., description="The firstname of the patient"),
		lastname: str = Query(..., description="The lastname of the patient"),
		dispensary_id: int = Query(..., description="The dispensary id of the patient"),
		room_number: int = Query(..., description="The room number of the patient"),
		bunk_number: int = Query(..., description="The bunk number of the patient"),
		days_of_treatment: int = Query(..., description="How many days should the patient be treated", le=30),
		token: str = Depends(get_token)
) -> PatientResponseForPost:
	return await patient_service.add_patient_service(
		firstname, lastname, dispensary_id, room_number, bunk_number, days_of_treatment, token)


@patient_router.get("/{patient_id}", response_model=PatientResponse, status_code=status.HTTP_200_OK)
async def get_patient_by_id(patient_id: int) -> PatientResponse:
	return await patient_service.get_patient_by_id_service(patient_id)


@patient_router.patch("/{patient_id}", status_code=status.HTTP_200_OK, response_model=PatientResponseForPut)
async def update_patient(
		patient_id: int, firstname: Optional[str] = Query(None, description="The firstname of the patient"),
		lastname: Optional[str] = Query(None, description="The lastname of the patient"),
		token: str = Depends(get_token)
) -> PatientResponseForPut:
	return await patient_service.update_patient_service(patient_id, firstname, lastname, token)


@patient_router.patch("/comeback/{patient_id}", status_code=status.HTTP_200_OK, response_model=PatientResponseForPut)
async def comeback_patient(
		patient_id: int, token: str = Depends(get_token)
) -> PatientResponseForPut:
	return await patient_service.update_patient_status_service(patient_id, token)


