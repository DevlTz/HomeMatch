import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def debug_task():
    logger.info("Celery worker está funcionando!")
    return "ok"

# para usar essa taks, chamamos a task junto com .delay()