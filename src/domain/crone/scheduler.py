from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.configs.config import settings
from src.configs.logger_setup import logger
from src.domain.crone.discharge_process import discharge_patients_crone


def start_scheduler() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(discharge_patients_crone, CronTrigger(minute=settings.CRONE_TIME_MINUTE))

    scheduler.start()

    logger.info("Crone started")
