import schedule
import threading
import time
from datetime import datetime

class BackupScheduler:
    def __init__(self, job_fn):
        self.job_fn = job_fn
        self.jobs = []
        self.scheduler_thread = None

    def clear(self):
        schedule.clear()
        self.jobs.clear()

    def schedule_once(self, dt: datetime):
        def one_time_job():
            if datetime.now() >= dt:
                self.job_fn()
                return schedule.CancelJob
        self.jobs.append(schedule.every(1).minutes.do(one_time_job))

    def schedule_daily(self, at_time: str):
        self.jobs.append(schedule.every().day.at(at_time).do(self.job_fn))

    def schedule_weekly(self, weekdays: list, at_time: str):
        for day in weekdays:
            self.jobs.append(getattr(schedule.every(), day.lower()).at(at_time).do(self.job_fn))

    def start(self):
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.scheduler_thread = threading.Thread(target=self.run, daemon=True)
            self.scheduler_thread.start()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
