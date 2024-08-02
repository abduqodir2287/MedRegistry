from enum import Enum


class BunkStatus(str, Enum):
	available = "available"
	busy = "busy"
	not_available = "not_available"


class PatientStatus(str, Enum):
	on_treatment = "on_treatment"
	discharged = "discharged"


class RoomStatus(str, Enum):
	available = "available"
	busy = "busy"
	not_available = "not_available"


class UserRole(str, Enum):
	user = "user"
	doctor = "doctor"
	superadmin = "superadmin"

