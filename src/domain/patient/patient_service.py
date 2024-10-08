from typing import Optional
from fastapi import Query, HTTPException, status, Depends

from src.configs.logger_setup import logger
from src.domain.enums import PatientStatus
from src.domain.patient.functions import PatientsFunctions
from src.domain.patient.schema import AllPatients, PatientResponseForPut, PatientModel, PatientResponse, \
	PatientResponseForPost
from src.infrastructure.database.postgres.create_db import dispensary, patient
from src.domain.authorization.auth import get_token
from src.domain.authorization.dependencies import check_user_is_doctor


class PatientsService(PatientsFunctions):

	def __init__(self):
		super().__init__()


	async def get_all_patients_service(
		self, firstname: Optional[str] = Query(None, description="The firstname of the patient"),
		lastname: Optional[str] = Query(None, description="The lastname of the patient"),
		dispensary_id: Optional[int] = Query(None, description="The dispensary id of the patient")
	) -> AllPatients:

		patients_list = await self.get_all_patients_function(firstname, lastname, dispensary_id)
		logger.info("Patients sent from Db")

		return AllPatients(Patients=patients_list)


	async def add_patient_service(
			self, firstname: str = Query(..., description="The firstname of the patient"),
			lastname: str = Query(..., description="The lastname of the patient"),
			dispensary_id: int = Query(..., description="The dispensary id of the patient"),
			room_number: int = Query(..., description="The room number of the patient"),
			bunk_number: int = Query(..., description="The bunk number of the patient"),
			days_of_treatment: int = Query(..., description="How many days should the patient be treated", le=30),
			token: str = Depends(get_token)
	) -> PatientResponseForPost:

		await check_user_is_doctor(dispensary_id, token)

		patient_model = PatientModel(
			firstname=firstname,
			lastname=lastname,
			dispensary_id=dispensary_id,
			room_number=room_number,
			bunk_number=bunk_number,
			days_of_treatment=days_of_treatment
		)

		exist_dispensary = await dispensary.dispensary_exists(dispensary_id)
		if not exist_dispensary:
			logger.warning("Dispensary not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="There is no Dispensary with this id."
			)

		if not await dispensary.select_dispensary_status(dispensary_id):
			logger.warning("Dispensary status is False")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This dispensary is not active right now")

		await self.check_room(room_number)
		await self.check_bunk(dispensary_id, room_number, bunk_number)
		await self.reserve_bunk(dispensary_id, room_number, bunk_number)

		patient_id = await patient.insert_patient(patient_model)

		logger.info("Patient added to DB")

		return PatientResponseForPost(PatientId=patient_id)

	async def get_patient_by_id_service(self, patient_id: int) -> PatientResponse:
		patient_by_id = await self.get_patient_by_id_function(patient_id)

		return patient_by_id


	async def update_patient_service(
		self, patient_id: int, firstname: Optional[str],
		lastname: Optional[str], token: str = Depends(get_token)
) -> PatientResponseForPut:

		patient_by_id = await patient.select_patient_by_id(patient_id)

		if patient_by_id is None:
			logger.warning("Patient not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

		await check_user_is_doctor(patient_by_id.dispensary_id, token)

		if firstname is None and lastname is None:
			logger.warning("Patient did not changed anything")
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You haven't changed anything")

		await patient.update_patient_name_by_id(
			patient_id,
			firstname if firstname is not None else patient_by_id.firstname,
			lastname if lastname is not None else patient_by_id.lastname
		)

		days_left = await self.days_left(patient_by_id.days_of_treatment, patient_by_id.arrival_date)

		logger.info("Patient updated successfully")

		return PatientResponseForPut(
			result="Patients updated successfully",
			id=patient_id,
			firstname=firstname if firstname is not None else patient_by_id.firstname,
			lastname=lastname if lastname is not None else patient_by_id.lastname,
			arrival_date=patient_by_id.arrival_date,
			status=patient_by_id.status,
			dispensary_id=patient_by_id.dispensary_id,
			room_number=patient_by_id.room_number,
			bunk_number=patient_by_id.bunk_number,
			days_left=str(days_left)
		)


	async def update_patient_status_service(
		self, patient_id: int, token: str = Depends(get_token)
	) -> PatientResponseForPut:

		patient_by_id = await patient.select_patient_by_id(patient_id)

		if patient_by_id is None:
			logger.warning("Patient not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

		await check_user_is_doctor(patient_by_id.dispensary_id, token)

		if patient_by_id.status != PatientStatus.discharged:
			logger.warning("the patent is already in the Dispensary")
			raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="the patent is already in the Dispensary")

		days_left = await self.days_left(patient_by_id.days_of_treatment, patient_by_id.arrival_date)

		update = await patient.update_patient_status(patient_id)

		logger.info("Patient updated successfully")

		if update:
			return PatientResponseForPut(
				result="Patients status updated successfully",
				id=patient_id,
				firstname=patient_by_id.firstname,
				lastname=patient_by_id.lastname,
				arrival_date=patient_by_id.arrival_date,
				status=patient_by_id.status,
				dispensary_id=patient_by_id.dispensary_id,
				room_number=patient_by_id.room_number,
				bunk_number=patient_by_id.bunk_number,
				days_left=str(days_left)
			)

