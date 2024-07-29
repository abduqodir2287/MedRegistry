from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status

from src.configs.logger_setup import logger
from src.infrastructure.database.postgres.create_db import users
from src.domain.authorization.auth import decode_access_token, get_token
from src.infrastructure.database.postgres.models import User


async def check_user_is_superadmin(token: str = Depends(get_token)) -> User:
	payload = decode_access_token(token)

	expire = payload.get("exp")
	if not expire:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

	expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
	if expire_time < datetime.now(timezone.utc):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')

	user_id = payload.get("sub")
	if not user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

	user_by_id = await users.select_user_by_id(int(user_id))
	if not user_by_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

	if user_by_id.role != "superadmin":
		logger.warning("User are not superadmin")
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights!")

	return user_by_id


async def check_user_is_doctor(dispensary_id: int, token: str = Depends(get_token)) -> User:
	payload = decode_access_token(token)

	expire = payload.get("exp")
	if not expire:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

	expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
	if expire_time < datetime.now(timezone.utc):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired')

	user_id = payload.get("sub")
	if not user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

	user_by_id = await users.select_user_by_id(int(user_id))
	if not user_by_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

	if user_by_id.role == "user":
		logger.warning("User are not superadmin or doctor")
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights!")

	if user_by_id.role == "doctor":
		if user_by_id.dispensary_id != dispensary_id:
			logger.warning("There is no such doctor at this dispensary")
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="There is no such doctor at this dispensary")

	return user_by_id

