import schedule
from neuro_san.coded_tool import CodedTool


class CaseManagementTools(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.jobs = []

    def schedule_task(self, task, interval, unit):
        """
        Schedules a task to run at a specified interval.

        :param task: The function to run.
        :param interval: The interval at which to run the task.
        :param unit: The unit of the interval (e.g., "seconds", "minutes", "hours", "days", "weeks").
        """
        job = schedule.every(interval)
        if unit == "seconds":
            job.seconds.do(task)
        elif unit == "minutes":
            job.minutes.do(task)
        elif unit == "hours":
            job.hours.do(task)
        elif unit == "days":
            job.days.do(task)
        elif unit == "weeks":
            job.weeks.do(task)
        self.jobs.append(job)

    def run_pending(self):
        """
        Runs all pending scheduled tasks.
        """
        schedule.run_pending()

    def get_scheduled_tasks(self) -> list:
        """
        Returns a list of all scheduled tasks.

        :return: A list of scheduled tasks.
        """
        return schedule.get_jobs()

    def cancel_task(self, job):
        """
        Cancels a scheduled task.

        :param job: The job to cancel.
        """
        schedule.cancel_job(job)
