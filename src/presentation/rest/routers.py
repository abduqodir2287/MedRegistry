from src.presentation.rest.rooms.rooms_router import room_router
from src.presentation.rest.dispensary.dispensary_router import dispensary_router
from src.presentation.rest.bunk.bunk_router import bunk_router
from src.presentation.rest.users.users_router import users_router
from src.presentation.rest.patient.patients_router import patient_router

all_routers = [
	users_router,
	dispensary_router,
	room_router,
	bunk_router,
	patient_router
]
