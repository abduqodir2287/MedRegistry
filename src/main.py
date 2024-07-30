from fastapi import FastAPI, status
from contextlib import asynccontextmanager

from src.presentation.rest.routers import all_routers

@asynccontextmanager
async def lifespan_app(my_app: FastAPI):
	yield


app = FastAPI(lifespan=lifespan_app)


for router in all_routers:
	app.include_router(router)


@app.get("/", status_code=status.HTTP_200_OK)
async def hello():
	return {"Message": "Hello World"}


