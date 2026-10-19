import sys
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from zoneinfo import ZoneInfo

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.agent.graph import execute_pipeline

scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.TIMEZONE))

def scheduled_agent_job():
    print(f"APScheduler: Running scheduled hourly Auto-Apply discovery & application job in {settings.TIMEZONE}...")
    try:
        execute_pipeline(user_id=1, trigger_type="scheduled_hourly")
        print("APScheduler: Job completed successfully.")
    except Exception as e:
        print(f"APScheduler Error during scheduled run: {e}")

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            scheduled_agent_job,
            trigger=IntervalTrigger(hours=settings.SCHEDULER_INTERVAL_HOURS),
            id="hourly_auto_apply_job",
            name="Hourly Auto-Apply Job Search and Application",
            replace_existing=True
        )
        scheduler.start()
        print(f"APScheduler started: Running every {settings.SCHEDULER_INTERVAL_HOURS} hour(s) [{settings.TIMEZONE}]")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("APScheduler stopped.")
