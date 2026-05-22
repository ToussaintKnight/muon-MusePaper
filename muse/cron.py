"""Cron scheduler for automated daily runs."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Callable, Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class MuseCron:
    """Schedules and manages Muse's daily briefing runs."""

    def __init__(self, run_callback: Callable, timezone: str = "Asia/Shanghai"):
        self.run_callback = run_callback
        self.scheduler = AsyncIOScheduler(timezone=timezone)
        self._job_id = "muse_daily_briefing"

    def start(self) -> None:
        """Start the scheduler if not already running."""
        if not self.scheduler.running:
            self.scheduler.start()

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()

    def schedule_daily(self, hour: int = 5, minute: int = 30) -> bool:
        """Schedule the daily briefing at the given time."""
        self._remove_existing()
        self.scheduler.add_job(
            self.run_callback,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=self._job_id,
            replace_existing=True,
            name="Muse Daily Briefing",
        )
        return True

    def _remove_existing(self) -> None:
        try:
            self.scheduler.remove_job(self._job_id)
        except Exception:
            pass

    def get_next_run(self) -> Optional[datetime]:
        """Return the next scheduled run time."""
        job = self.scheduler.get_job(self._job_id)
        return job.next_run_time if job else None

    def is_scheduled(self) -> bool:
        """Check if the daily job is currently scheduled."""
        return self.scheduler.get_job(self._job_id) is not None
