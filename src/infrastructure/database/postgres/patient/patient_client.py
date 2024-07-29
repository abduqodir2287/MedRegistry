from sqlalchemy import select, update

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.infrastructure.database.postgres.database import Base
from src.infrastructure.database.postgres.models import Patient
from src.domain.patient.schema import PatientModel


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


	async def insert_patient(self, patient_model: PatientModel) -> tuple:
		async with self.async_session() as session:
			async with session.begin():

				insert_into = Patient(
					firstname=patient_model.firstname,
					lastname=patient_model.lastname,
					dispensary_id=patient_model.dispensary_id,
					room_number=patient_model.room_number,
					bunk_number=patient_model.bunk_number
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



