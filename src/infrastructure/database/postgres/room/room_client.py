from sqlalchemy import select, delete, exists

from src.configs.config import settings
from src.infrastructure.database.postgres.database import Base
from src.infrastructure.database.postgres.models import Room
from src.domain.room.schema import RoomModel
from src.configs.logger_setup import logger


class RoomDb:
	def __init__(self) -> None:
		self.db_url = settings.DATABASE_URL
		self.engine = Base.engine
		self.metadata = Base.metadata
		self.async_session = Base.async_session


	async def insert_room(self, room_model: RoomModel) -> int:
		async with self.async_session() as session:
			async with session.begin():
				insert_into = Room(
					room_number=room_model.room_number,
					dispensary_id=room_model.dispensary_id
				)
				session.add(insert_into)
			await session.commit()

			await session.refresh(insert_into)
			room_id = insert_into.id

			logger.info("Task added to DB")
			return room_id


	async def select_all_rooms(self) -> list:
		async with self.async_session() as session:
			select_tasks = select(Room)

			result = await session.execute(select_tasks)

			return result.scalars().all()


	async def select_room_by_id(self, id: int) -> tuple:
		async with self.async_session() as session:
			result = await session.execute(select(Room).where(Room.id == id))
			task = result.scalars().first()

			if task:
				return task


	async def delete_room_by_id(self, id: int) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				delete_room = delete(Room).where(Room.id == id)
				result = await session.execute(delete_room)

				await session.commit()

				if result.rowcount > 0:
					return True


	async def room_exists(self, room_number: int) -> bool:
		async with self.async_session() as session:
			exist = select(exists().where(Room.room_number == room_number))
			result = await session.execute(exist)
			return result.scalar()

	async def select_room_by_number(self, room_number: int, dispensary_id: int) -> Room:
		async with self.async_session() as session:
			result = await session.execute(select(Room).where(
				Room.room_number == room_number,
				Room.dispensary_id == dispensary_id)
			)

			return result.scalars().first()

	async def check_room_exists(self, room_number: int, dispensary_id: int) -> bool:
		async with self.async_session() as session:
			exist = select(exists().where(Room.room_number == room_number, Room.dispensary_id == dispensary_id))
			result = await session.execute(exist)
			return result.scalar()

	async def get_rooms_by_dispensary_id(self, dispensary_id: int) -> list:
		async with self.async_session() as session:
			result = await session.execute(select(Room).where(Room.dispensary_id == dispensary_id))
			task = result.scalars().all()

			if task:
				return task

