from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from src.configs.logger_setup import logger
from src.presentation.rest.routers import all_routers
from src.domain.crone.scheduler import start_scheduler
from src.infrastructure.database.postgres.create_db import dispensary, users

@asynccontextmanager
async def lifespan_app(my_app: FastAPI):
	start_scheduler()
	await dispensary.create_first_dispensary()
	await users.create_user_superadmin()
	yield
	logger.info("Bye Bye!!")


app = FastAPI(lifespan=lifespan_app)


for router in all_routers:
	app.include_router(router)


@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
	return {"Message": "Hello World"}


