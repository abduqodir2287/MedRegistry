from datetime import timedelta, datetime
from typing import Optional
from sqlalchemy import select, update, and_
import pytz

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.domain.enums import PatientStatus
from src.infrastructure.database.postgres.database import Base
from src.infrastructure.database.postgres.models import Patient
from src.domain.patient.schema import PatientModel, PatientResponse


class PatientDb:

	def __init__(self) -> None:
		self.db_url = settings.DATABASE_URL
		self.engine = Base.engine
		self.metadata = Base.metadata
		self.async_session = Base.async_session


	async def select_all_patients(self) -> list:
		async with self.async_session() as session:
			select_patients = select(Patient)

			result = await session.execute(select_patients)

			return result.scalars().all()


	async def select_patients_like(
			self, firstname: Optional[str] = None,
			lastname: Optional[str] = None,
			dispensary_id: Optional[int] = None
	) -> list:
		async with self.async_session() as session:
			select_patients = select(Patient)

			conditions = []

			if firstname is not None:
				conditions.append(Patient.firstname.like(f"%{firstname}%"))

			if lastname is not None:
				conditions.append(Patient.lastname.like(f"%{lastname}%"))

			if dispensary_id is not None:
				conditions.append(Patient.dispensary_id == dispensary_id)

			if conditions:
				select_patients = select_patients.where(and_(*conditions))

			result = await session.execute(select_patients)

			return result.scalars().all()



	async def insert_patient(self, patient_model: PatientModel) -> int:
		async with self.async_session() as session:
			async with session.begin():

				insert_into = Patient(
					firstname=patient_model.firstname,
					lastname=patient_model.lastname,
					dispensary_id=patient_model.dispensary_id,
					room_number=patient_model.room_number,
					bunk_number=patient_model.bunk_number,
					days_of_treatment=patient_model.days_of_treatment
				)
				session.add(insert_into)

			await session.commit()

			await session.refresh(insert_into)

			logger.info("User added to DB")

			return insert_into.id


	async def select_patient_by_id(self, patient_id: int) -> Patient:
		async with self.async_session() as session:
			select_patients = select(Patient).where(Patient.id == patient_id)

			result = await session.execute(select_patients)

			return result.scalars().first()


	async def update_patient_name_by_id(self, patient_id: int, firstname: str, lastname: str) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_dispensary = update(Patient).where(Patient.id == patient_id).values(
					firstname=firstname,
					lastname=lastname
				)

				result = await session.execute(update_dispensary)
				await session.commit()

				if result.rowcount > 0:
					return True


	async def select_patient_by_bunk_number(self, dispensary_id: int, room_number: int, bunk_number: int) -> Patient:
		async with self.async_session() as session:
			select_patients = select(Patient).where(
				Patient.dispensary_id == dispensary_id,
				Patient.room_number == room_number,
				Patient.bunk_number == bunk_number
			)

			result = await session.execute(select_patients)

			return result.scalars().first()

	async def update_patient_status_crone(self, day_of_discharge: datetime) -> list[PatientResponse] | None:
		async with self.async_session() as session:
			async with session.begin():
				local_time = datetime.now()
				term = local_time.astimezone(pytz.utc) - timedelta(days=10)

				result = await session.execute(select(Patient).where(
					Patient.status != PatientStatus.discharged,
					Patient.arrival_date <= term
				))

				patients = result.scalars().all()

				patients_list = []

				for p in patients:
					returned_patient = PatientResponse(
						id=p.id,
						firstname=p.firstname,
						lastname=p.lastname,
						status=p.status,
						arrival_date=p.arrival_date,
						dispensary_id=p.dispensary_id,
						room_number=p.room_number,
						bunk_number=p.bunk_number
					)

					patients_list.append(returned_patient)

				for patient in patients:
					patient.status = PatientStatus.discharged
					logger.info(f"Patient with id {patient.id} discharged")

				await session.commit()

				return patients_list

	async def discharge_patient(self, patient_id: int):
		async with self.async_session() as session:
			async with session.begin():
				update_patient = update(Patient).where(Patient.id == patient_id).values(
					status=PatientStatus.discharged
				)

				result = await session.execute(update_patient)
				await session.commit()

				if result.rowcount > 0:
					return True


	async def update_patient_status(self, patient_id: int) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_patient = update(Patient).where(Patient.id == patient_id).values(
					status=PatientStatus.on_treatment
				)

				result = await session.execute(update_patient)
				await session.commit()

				if result.rowcount > 0:
					return True


