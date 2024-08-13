from datetime import datetime

from src.configs.logger_setup import logger
from src.domain.crone.pdf_create import create_patient_discharge_pdf
from src.domain.dispensary.schema import DispensaryModel
from src.infrastructure.database.postgres.create_db import patient, dispensary
from src.domain.patient.schema import PatientDischarge
from src.domain.patient.functions import PatientsFunctions

service = PatientsFunctions()

async def discharge_patients_crone() -> None:
    all_patients = await patient.select_all_patients()

    current_time = datetime.now()

    for p in all_patients:
        term = await service.day_of_discharge(p.days_of_treatment, p.arrival_date)

        if current_time >= term:
            await patient.discharge_patient(p.id)
            get_dispensary = await dispensary.select_dispensary_by_id(p.dispensary_id)

            patient_model = PatientDischarge(
                id=p.id,
                firstname=p.firstname,
                lastname=p.lastname,
                arrival_date=p.arrival_date,
                dispensary_id=p.dispensary_id,
                room_number=p.room_number,
                bunk_number=p.bunk_number,
                discharge_date=term
            )

            dispensary_model = DispensaryModel(
                dispensary_name=get_dispensary.dispensary_name,
                address=get_dispensary.address
            )

            create_patient_discharge_pdf(
                f"{p.firstname}_{p.lastname}",
                patient_model, dispensary_model
            )

            logger.info("Crone checked")

