"""
Export Scheduler
Automated and scheduled terrain generation and exports
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from pydantic import BaseModel
import asyncio


class ScheduleFrequency(str, Enum):
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ScheduledJob(BaseModel):
    id: str
    name: str
    frequency: ScheduleFrequency
    next_run: datetime
    last_run: Optional[datetime] = None
    enabled: bool = True
    config: Dict
    user_id: str
    created_at: datetime


class ExportScheduler:
    """Manages scheduled terrain generation and exports"""
    
    def __init__(self):
        self.jobs: Dict[str, ScheduledJob] = {}
        self.running = False
    
    def schedule_export(
        self,
        user_id: str,
        name: str,
        bbox: tuple,
        export_format: str,
        frequency: ScheduleFrequency,
        start_time: datetime,
        options: Dict = None
    ) -> ScheduledJob:
        """Schedule a recurring export job"""
        
        job = ScheduledJob(
            id=f"job_{datetime.now().timestamp()}",
            name=name,
            frequency=frequency,
            next_run=start_time,
            config={
                "bbox": bbox,
                "format": export_format,
                "options": options or {}
            },
            user_id=user_id,
            created_at=datetime.now()
        )
        
        self.jobs[job.id] = job
        return job
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            return True
        return False
    
    def pause_job(self, job_id: str):
        """Pause a job without deleting it"""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = False
    
    def resume_job(self, job_id: str):
        """Resume a paused job"""
        if job_id in self.jobs:
            self.jobs[job_id].enabled = True
    
    def get_user_jobs(self, user_id: str) -> List[ScheduledJob]:
        """Get all jobs for a user"""
        return [job for job in self.jobs.values() if job.user_id == user_id]
    
    async def run(self):
        """Main scheduler loop"""
        self.running = True
        
        while self.running:
            await self._check_and_run_jobs()
            await asyncio.sleep(60)  # Check every minute
    
    async def _check_and_run_jobs(self):
        """Check for jobs that need to run"""
        now = datetime.now()
        
        for job in list(self.jobs.values()):
            if not job.enabled:
                continue
            
            if job.next_run <= now:
                await self._execute_job(job)
                self._schedule_next_run(job)
    
    async def _execute_job(self, job: ScheduledJob):
        """Execute a scheduled job"""
        print(f"Executing job {job.name} for user {job.user_id}")
        
        # This would call the actual terrain generation/export
        # For now, just log
        job.last_run = datetime.now()
    
    def _schedule_next_run(self, job: ScheduledJob):
        """Calculate next run time based on frequency"""
        now = datetime.now()
        
        if job.frequency == ScheduleFrequency.ONCE:
            job.enabled = False
            return
        elif job.frequency == ScheduleFrequency.DAILY:
            job.next_run = now + timedelta(days=1)
        elif job.frequency == ScheduleFrequency.WEEKLY:
            job.next_run = now + timedelta(weeks=1)
        elif job.frequency == ScheduleFrequency.MONTHLY:
            job.next_run = now + timedelta(days=30)
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False


# Global scheduler instance
scheduler = ExportScheduler()
