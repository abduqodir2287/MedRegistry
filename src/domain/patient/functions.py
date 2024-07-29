from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
import json

from src.configs.logger_setup import logger
from src.domain.patient.schema import PatientResponse, PatientStatus, PatientModel
from src.domain.bunk.schema import BunkResponse, BunkStatus
from src.infrastructure.database.postgres.create_db import patient, bunk, room
from src.infrastructure.database.redis.client import RedisClient
from src.configs.config import settings

class PatientsFunctions:

	def __init__(self):
		self.redis_client = RedisClient(settings.REDIS_PATIENTS)
		self.redis_bunk_client = RedisClient(settings.REDIS_BUNK)


	@staticmethod
	async def get_all_patients_function() -> list:
		all_patients = await patient.select_all_patients()
		patients_list = []

		for patients in all_patients:
			returned_patients = PatientResponse(
				id=patients.id,
				firstname=patients.firstname,
				lastname=patients.lastname,
				arrival_date=patients.arrival_date,
				status=patients.status,
				dispensary_id=patients.dispensary_id,
				room_number=patients.room_number,
				bunk_number=patients.bunk_number
			)

			patients_list.append(returned_patients)

		return patients_list


	async def get_patients_redis(self) -> list:
		keys = self.redis_client.get_keys()
		patients_list = []

		for key in keys:
			returned_patient = self.redis_client.get(key)

			patients_list.append(json.loads(returned_patient))

		logger.info("Patients sent from Redis")

		return patients_list


	async def add_patient_redis(self, patient_id: int, arrival_date: datetime, patient_model: PatientModel) -> None:
		bunk_by_number = await bunk.select_bunk_by_number(
			patient_model.dispensary_id, patient_model.room_number, patient_model.bunk_number)

		redis_bunk_model = BunkResponse(
			id=bunk_by_number.id,
			bunk_status=BunkStatus("busy"),
			bunk_number=patient_model.bunk_number,
			room_number=patient_model.bunk_number,
			dispensary_id=patient_model.dispensary_id
		)

		self.redis_bunk_client.set(bunk_by_number.id, json.dumps(jsonable_encoder(redis_bunk_model)))

		model_patient = PatientResponse(
			id=patient_id,
			firstname=patient_model.firstname,
			lastname=patient_model.lastname,
			arrival_date=arrival_date,
			dispensary_id=patient_model.dispensary_id,
			room_number=patient_model.room_number,
			bunk_number=patient_model.bunk_number
		)

		self.redis_client.set(patient_id, json.dumps(jsonable_encoder(model_patient)))


	@staticmethod
	async def check_bunk(dispensary_id: int, room_number: int, bunk_number: int) -> bool:
		check = await bunk.select_bunk_by_number(dispensary_id, room_number, bunk_number)

		if check is None:
			logger.warning("Bunk not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Bunk with this number in this room not found in this dispensary"
			)

		return True

	@staticmethod
	async def check_room(room_number: int) -> bool:
		exist_room = await room.room_exists(room_number)

		if not exist_room:
			logger.warning("Room not found")
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="There is no Room with this id."
			)

		return True


	@staticmethod
	async def reserve_bunk(dispensary_id: int, room_number: int, bunk_number: int) -> bool | None:
		bunk_by_number = await bunk.select_bunk_by_number(dispensary_id, room_number, bunk_number)
		booking = await bunk.update_bunk_status(dispensary_id, room_number, bunk_number)

		busy = BunkStatus("busy")
		not_available = BunkStatus("not_available")

		if bunk_by_number:
			if bunk_by_number.bunk_status == busy:
				logger.warning("Bunk already reserved")
				raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bunk already reserved")

			if bunk_by_number.bunk_status == not_available:
				logger.warning("Bunk not available")
				raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Bunk not available")

			if booking:
				logger.info("Bunk booking")
				return True


	@staticmethod
	async def get_patient_by_id_function(patient_id: int) -> PatientResponse:
		patient_by_id = await patient.select_patient_by_id(patient_id)

		if patient_by_id is None:
			logger.info("Patient not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient with this id not found")

		logger.info("Patient sent from DB")

		return PatientResponse(
			id=patient_by_id.id,
			firstname=patient_by_id.firstname,
			lastname=patient_by_id.lastname,
			arrival_date=patient_by_id.arrival_date,
			status=patient_by_id.status,
			dispensary_id=patient_by_id.dispensary_id,
			room_number=patient_by_id.room_number,
			bunk_number=patient_by_id.bunk_number
		)


	async def get_patient_by_id_redis(self, patient_id: int) -> PatientResponse:
		patient_by_id = self.redis_client.get(patient_id)

		if patient_by_id is None:
			logger.warning("Patient not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

		logger.info("Patient sent from Redis")
		return json.loads(patient_by_id)


	async def update_patient_redis(
			self, patient_id: int, firstname: str,
			lastname: str, arrival_date: datetime,
			patient_status: PatientStatus, dispensary_id: int,
			room_number: int, bunk_number: int
	) -> None:

		patient_model = PatientResponse(
			id=patient_id,
			firstname=firstname,
			lastname=lastname,
			arrival_date=arrival_date,
			status=patient_status,
			dispensary_id=dispensary_id,
			room_number=room_number,
			bunk_number=bunk_number
		)

		self.redis_client.set(patient_id, json.dumps(jsonable_encoder(patient_model)))


