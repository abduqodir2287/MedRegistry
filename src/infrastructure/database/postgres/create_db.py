from src.infrastructure.database.postgres.dispensary.dispensary_client import DispensaryDb
from src.infrastructure.database.postgres.room.room_client import RoomDb
from src.infrastructure.database.postgres.bunk.bunk_client import BunkDb
from src.infrastructure.database.postgres.patient.patient_client import PatientDb
from src.infrastructure.database.postgres.users.users_client import UsersDb

dispensary = DispensaryDb()
room = RoomDb()
bunk = BunkDb()
users = UsersDb()
patient = PatientDb()
