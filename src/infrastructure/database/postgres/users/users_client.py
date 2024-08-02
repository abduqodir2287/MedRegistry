from typing import Optional
from sqlalchemy import select, delete, update, and_

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.infrastructure.database.postgres.database import Base
from src.infrastructure.database.postgres.models import User
from src.domain.users.schema import UserModel
from src.domain.enums import UserRole


class UsersDb:

	def __init__(self) -> None:
		self.db_url = settings.DATABASE_URL
		self.engine = Base.engine
		self.metadata = Base.metadata
		self.async_session = Base.async_session

	async def select_all_users(self) -> list:
		async with self.async_session() as session:
			select_tasks = select(User)

			result = await session.execute(select_tasks)

			return result.scalars().all()


	async def insert_user(self, user_model: UserModel) -> int:
		async with self.async_session() as session:
			async with session.begin():
				insert_into = User(
					firstname=user_model.firstname.capitalize(),
					lastname=user_model.lastname.capitalize(),
					password=user_model.password,
					job_title=user_model.job_title.capitalize() if user_model.job_title is not None else None,
					dispensary_id=user_model.dispensary_id
				)
				session.add(insert_into)

			await session.commit()

			await session.refresh(insert_into)
			user_id = insert_into.id

			logger.info("User added to DB")
			return user_id


	async def delete_user_by_id(self, user_id: int) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				delete_user = delete(User).where(User.id == user_id)
				result = await session.execute(delete_user)

				await session.commit()

				if result.rowcount > 0:
					return True

	async def select_user_by_id(self, user_id: int) -> User:
		async with self.async_session() as session:
			select_users = select(User).where(User.id == user_id)

			result = await session.execute(select_users)

			return result.scalars().first()

	async def update_user_role(self, user_id: int, role: UserRole) -> bool | None:
		async with self.async_session() as session:
			async with session.begin():
				update_user = update(User).where(User.id == user_id).values(
					role=role
				)

				result = await session.execute(update_user)
				await session.commit()

				if result.rowcount > 0:
					return True


	async def select_user_by_name(self, firstname: int, lastname: int, dispensary_id: int) -> User:
		async with self.async_session() as session:
			select_users = select(User).where(
				User.firstname == firstname,
				User.lastname == lastname,
				User.dispensary_id == dispensary_id
			)

			result = await session.execute(select_users)

			return result.scalars().first()


	async def create_user_superadmin(self, firstname: str, lastname: str, password: str, dispensary_id: int) -> int:
		async with self.async_session() as session:
			async with session.begin():
				insert_into = User(
					firstname=firstname.capitalize(),
					lastname=lastname.capitalize(),
					password=password,
					role="superadmin",
					job_title="superadmin",
					dispensary_id=dispensary_id
				)
				session.add(insert_into)

			await session.commit()

			await session.refresh(insert_into)
			user_id = insert_into.id

			logger.info("User added to DB")
			return user_id


	async def select_users_like(
			self, firstname: Optional[str] = None,
			lastname: Optional[str] = None,
			role: Optional[UserRole] = None,
			dispensary_id: Optional[int] = None
	) -> list:
		async with self.async_session() as session:
			select_patients = select(User)

			conditions = []

			if firstname is not None:
				conditions.append(User.firstname.like(f"%{firstname}%"))

			if lastname is not None:
				conditions.append(User.lastname.like(f"%{lastname}%"))

			if role is not None:
				conditions.append(User.role == role)

			if dispensary_id is not None:
				conditions.append(User.dispensary_id == dispensary_id)

			if conditions:
				select_patients = select_patients.where(and_(*conditions))

			result = await session.execute(select_patients)

			return result.scalars().all()

