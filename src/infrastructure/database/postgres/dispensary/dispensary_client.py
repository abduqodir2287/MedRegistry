from typing import Optional

from sqlalchemy import select, delete, update, exists, and_

from src.configs.config import settings
from src.infrastructure.database.postgres.database import Base
from src.infrastructure.database.postgres.models import Dispensary
from src.domain.dispensary.schema import DispensaryModel
from src.configs.logger_setup import logger


class DispensaryDb:
	def __init__(self) -> None:
		self.db_url = settings.DATABASE_URL
		self.engine = Base.engine
		self.metadata = Base.metadata
		self.async_session = Base.async_session


	async def insert_dispensary(self, dispensary: DispensaryModel) -> tuple:
		async with self.async_session() as session:
			async with session.begin():
				insert_into = Dispensary(
					dispensary_name=dispensary.dispensary_name,
					address=dispensary.address
				)
				session.add(insert_into)
			await session.commit()

			await session.refresh(insert_into)
			dispensary_id = insert_into.id

			logger.info("Dispensary added to DB")
			return dispensary_id


	async def select_all_dispensaries(self) -> list:
		async with self.async_session() as session:
			select_tasks = select(Dispensary)

			result = await session.execute(select_tasks)

			return result.scalars().all()


	async def select_dispensary_by_id(self, id: int) -> Dispensary:
		async with self.async_session() as session:
			result = await session.execute(select(Dispensary).where(Dispensary.id == id))
			task = result.scalars().first()

			if task:
				return task


	async def delete_dispensary_by_id(self, id: int) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():

				delete_dispensary = delete(Dispensary).where(Dispensary.id == id)
				result = await session.execute(delete_dispensary)

				await session.commit()

				if result.rowcount > 0:
					return True


	async def update_dispensary_by_id(self, id: int, dispensary: DispensaryModel) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_dispensary = update(Dispensary).where(Dispensary.id == id).values(
					dispensary_name=dispensary.dispensary_name,
					address=dispensary.address
				)

				result = await session.execute(update_dispensary)
				await session.commit()

				if result.rowcount > 0:
					return True


	async def dispensary_exists(self, dispensary_id: int) -> bool:
		async with self.async_session() as session:
			exist = select(exists().where(Dispensary.id == dispensary_id))
			result = await session.execute(exist)
			return result.scalar()


	async def update_dispensary_status(self, dispensary_id: int, active_status: bool) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_dispensary = update(Dispensary).where(Dispensary.id == dispensary_id).values(
					active=active_status
				)

				result = await session.execute(update_dispensary)
				await session.commit()

				if result.rowcount > 0:
					return True

	async def select_dispensary_status(self, dispensary_id: int) -> bool | None:
		async with self.async_session() as session:
			result = await session.execute(select(Dispensary).where(Dispensary.id == dispensary_id))
			task = result.scalars().first()

			if task:
				return task.active


	async def select_dispensary_like(
			self, dispensary_id: Optional[int] = None,
			dispensary_name: Optional[str] = None,
			address: Optional[str] = None
	) -> list:
		async with self.async_session() as session:
			select_patients = select(Dispensary)

			conditions = []

			if dispensary_id is not None:
				conditions.append(Dispensary.id == dispensary_id)

			if dispensary_name is not None:
				conditions.append(Dispensary.dispensary_name.like(f"%{dispensary_name}%"))

			if address is not None:
				conditions.append(Dispensary.address.like(f"%{address}%"))

			if conditions:
				select_patients = select_patients.where(and_(*conditions))

			result = await session.execute(select_patients)

			return result.scalars().all()


