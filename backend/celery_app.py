from celery import Celery
from app import app


celery = Celery(
    "placement_portal",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery.conf.update(
    timezone="Asia/Kolkata",
    beat_schedule={
        "interview-reminder": {
            "task": "tasks.interview_reminder",
            "schedule": 60.0
        },
        "monthly-placement-report": {
        "task": "tasks.monthly_placement_report",
        "schedule": 2592000.0
        }
    }
)
import tasks