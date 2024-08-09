from datetime import datetime
import pytz

from src.domain.crone.pdf_create import create_patient_discharge_pdf
from src.domain.dispensary.schema import DispensaryModel
from src.infrastructure.database.postgres.create_db import patient, dispensary
from src.domain.patient.schema import PatientDischarge


async def discharge_crone() -> None:
    discharged_patients = await patient.update_patient_status_crone()
    local_time = datetime.now()
    utc = local_time.astimezone(pytz.utc)

    if discharged_patients:
        for get_patient in discharged_patients:
            get_dispensary = await dispensary.select_dispensary_by_id(get_patient.dispensary_id)

            patient_model = PatientDischarge(
                id=get_patient.id,
                firstname=get_patient.firstname,
                lastname=get_patient.lastname,
                arrival_date=get_patient.arrival_date,
                dispensary_id=get_patient.dispensary_id,
                room_number=get_patient.room_number,
                bunk_number=get_patient.bunk_number,
                discharge_date=utc
            )

            dispensary_model = DispensaryModel(
                dispensary_name=get_dispensary.dispensary_name,
                address=get_dispensary.address
            )

            create_patient_discharge_pdf(
	            get_patient.firstname + "_" + get_patient.lastname,
	            patient_model, dispensary_model
            )

