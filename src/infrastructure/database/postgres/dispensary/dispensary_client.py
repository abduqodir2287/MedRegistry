from sqlalchemy import select, delete, update

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


	async def create_table(self) -> None:
		async with self.engine.begin() as conn:
			await conn.run_sync(self.metadata.create_all)


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

			logger.info("Task added to DB")
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

				delete_task = delete(Dispensary).where(Dispensary.id == id)
				result = await session.execute(delete_task)

				await session.commit()

				if result.rowcount > 0:
					return True

	async def update_dispensary_by_id(self, id: int, dispensary: DispensaryModel) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_task = update(Dispensary).where(Dispensary.id == id).values(
					dispensary_name=dispensary.dispensary_name,
					address=dispensary.address
				)

				result = await session.execute(update_task)
				await session.commit()

				if result.rowcount > 0:
					return True


