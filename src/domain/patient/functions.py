from datetime import datetime, timedelta
from typing import Optional

import pytz
from fastapi import HTTPException, status

from src.configs.logger_setup import logger
from src.domain.patient.schema import PatientResponse
from src.domain.enums import BunkStatus
from src.infrastructure.database.postgres.create_db import patient, bunk, room
from src.infrastructure.database.redis.client import RedisClient
from src.configs.config import settings

class PatientsFunctions:

	def __init__(self):
		self.redis_client = RedisClient(settings.REDIS_PATIENTS)
		self.redis_bunk_client = RedisClient(settings.REDIS_BUNK)

	async def get_all_patients_function(
			self, firstname: Optional[str] = None, lastname: Optional[str] = None,
			dispensary_id: Optional[int] = None
	) -> list[PatientResponse]:
		all_patients = await patient.select_patients_like(firstname, lastname, dispensary_id)
		patients_list = []

		for patients in all_patients:
			days_left = await self.days_left(patients.days_of_treatment, patients.arrival_date)

			returned_patients = PatientResponse(
				id=patients.id,
				firstname=patients.firstname,
				lastname=patients.lastname,
				arrival_date=patients.arrival_date,
				status=patients.status,
				dispensary_id=patients.dispensary_id,
				room_number=patients.room_number,
				bunk_number=patients.bunk_number,
				days_left=str(days_left)
			)

			patients_list.append(returned_patients)

		return patients_list


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

		busy = BunkStatus.busy
		not_available = BunkStatus.not_available

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


	async def get_patient_by_id_function(self, patient_id: int) -> PatientResponse:
		patient_by_id = await patient.select_patient_by_id(patient_id)

		if patient_by_id is None:
			logger.info("Patient not found")
			raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient with this id not found")

		days_left = await self.days_left(patient_by_id.days_of_treatment, patient_by_id.arrival_date)

		logger.info("Patient sent from DB")

		return PatientResponse(
			id=patient_by_id.id,
			firstname=patient_by_id.firstname,
			lastname=patient_by_id.lastname,
			arrival_date=patient_by_id.arrival_date,
			status=patient_by_id.status,
			dispensary_id=patient_by_id.dispensary_id,
			room_number=patient_by_id.room_number,
			bunk_number=patient_by_id.bunk_number,
			days_left=str(days_left)
		)


	@staticmethod
	async def days_left(day: int, arrival_date: datetime) -> timedelta:

		tashkent_tz = pytz.timezone('Asia/Tashkent')
		patient_tashkent_time = arrival_date.astimezone(tashkent_tz)

		today = datetime.now()
		arrival_day = patient_tashkent_time.day + day

		day_of_discharge = datetime(
			patient_tashkent_time.year, patient_tashkent_time.month, arrival_day,
			hour=patient_tashkent_time.hour, minute=patient_tashkent_time.minute,
			second=patient_tashkent_time.second
		)

		result = day_of_discharge - today

		return result

	@staticmethod
	async def day_of_discharge(day: int, arrival_date: datetime) -> datetime:

		tashkent_tz = pytz.timezone('Asia/Tashkent')
		patient_tashkent_time = arrival_date.astimezone(tashkent_tz)

		arrival_day = patient_tashkent_time.day + day

		day_of_discharge = datetime(
			patient_tashkent_time.year, patient_tashkent_time.month, arrival_day,
			hour=patient_tashkent_time.hour, minute=patient_tashkent_time.minute,
			second=patient_tashkent_time.second
		)

		return day_of_discharge


	@staticmethod
	async def minute_of_discharge(minute: int, arrival_date: datetime) -> datetime:

		tashkent_tz = pytz.timezone('Asia/Tashkent')
		patient_tashkent_time = arrival_date.astimezone(tashkent_tz)

		arrival_minute = patient_tashkent_time.minute + minute

		day_of_discharge = datetime(
			patient_tashkent_time.year, patient_tashkent_time.month, patient_tashkent_time.day,
			hour=patient_tashkent_time.hour, minute=arrival_minute,
			second=patient_tashkent_time.second
		)

		return day_of_discharge



