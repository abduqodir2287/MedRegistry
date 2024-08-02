from sqlalchemy import select, update, exists, func

from src.configs.config import settings
from src.infrastructure.database.postgres.database import Base
from src.infrastructure.database.postgres.models import Bunk
from src.domain.bunk.schema import BunkModel
from src.domain.enums import BunkStatus
from src.configs.logger_setup import logger


class BunkDb:
	def __init__(self) -> None:
		self.db_url = settings.DATABASE_URL
		self.engine = Base.engine
		self.metadata = Base.metadata
		self.async_session = Base.async_session


	async def insert_bunk(self, bunk_model: BunkModel) -> int:
		async with self.async_session() as session:
			async with session.begin():
				insert_into = Bunk(
					bunk_number=bunk_model.bunk_number,
					room_number=bunk_model.room_number,
					dispensary_id=bunk_model.dispensary_id
				)
				session.add(insert_into)
			await session.commit()

			await session.refresh(insert_into)
			bunk_id = insert_into.id

			logger.info("Task added to DB")
			return bunk_id


	async def select_all_bunks(self) -> list:
		async with self.async_session() as session:
			select_bunks = select(Bunk)

			result = await session.execute(select_bunks)

			return result.scalars().all()

	async def select_bunk_by_id(self, id: int) -> Bunk:
		async with self.async_session() as session:
			result = await session.execute(select(Bunk).where(Bunk.id == id))
			task = result.scalars().first()

			if task:
				return task

	async def select_bunk_by_number(self, dispensary_id: int, room_number: int, bunk_number: int) -> Bunk:
		async with self.async_session() as session:
			result = await session.execute(
				select(Bunk).where(
					Bunk.dispensary_id == dispensary_id,
					Bunk.room_number == room_number,
					Bunk.bunk_number == bunk_number
				)
			)

			task = result.scalars().first()

			if task:
				return task


	async def select_bunks_by_room_number(self, dispensary_id: int, room_number: int) -> Bunk:
		async with self.async_session() as session:
			result = await session.execute(
				select(Bunk).where(
					Bunk.dispensary_id == dispensary_id,
					Bunk.room_number == room_number
				)
			)

			return result.scalars().all()


	async def select_available_bunks(self) -> Bunk:
		async with self.async_session() as session:
			result = await session.execute(
				select(Bunk).where(
					Bunk.bunk_status == BunkStatus.available
				)
			)

			return result.scalars().all()


	async def select_available_bunks_by_id(self, dispensary_id: int) -> Bunk:
		async with self.async_session() as session:
			result = await session.execute(
				select(Bunk).where(
					Bunk.dispensary_id == dispensary_id,
					Bunk.bunk_status == BunkStatus.available
				)
			)

			return result.scalars().all()


	async def update_bunk_by_id(self, id: int, bunk_status: BunkStatus) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_bunk = update(Bunk).where(Bunk.id == id).values(
					bunk_status=bunk_status
				)

				result = await session.execute(update_bunk)
				await session.commit()

				if result.rowcount > 0:
					return True

	async def update_bunk_status(self, dispensary_id: int, room_number: int, bunk_number: int) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_bunk = update(Bunk).where(
					Bunk.dispensary_id == dispensary_id,
					Bunk.room_number == room_number,
					Bunk.bunk_number == bunk_number).values(
					bunk_status=BunkStatus.busy
				)

				result = await session.execute(update_bunk)
				await session.commit()

				if result.rowcount > 0:
					return True


	async def bunk_exists(self, bunk_id: int) -> bool:
		async with self.async_session() as session:
			exist = select(exists().where(Bunk.id == bunk_id))
			result = await session.execute(exist)
			return result.scalar()


	async def free_bunks_by_dispensary_id(self, dispensary_id: int) -> int | str:
		async with self.async_session() as session:
			stmt = select(func.count(Bunk.id)).where(
				Bunk.dispensary_id == dispensary_id, Bunk.bunk_status == BunkStatus.available
			)

			result = await session.execute(stmt)
			task = result.scalar_one_or_none()

			if task:
				return task

			return "There is not a single free bed at this dispensary yet"

