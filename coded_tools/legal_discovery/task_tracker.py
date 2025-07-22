import os

from neuro_san.coded_tool import CodedTool


class TaskTracker(CodedTool):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.task_file = "tasks.txt"

    def add_task(self, task: str) -> str:
        """
        Adds a task to the task list.

        :param task: The task to add.
        :return: A message indicating success.
        """
        with open(self.task_file, "a") as f:
            f.write(f"- {task}\\n")
        return f"Task '{task}' added."

    def list_tasks(self) -> str:
        """
        Lists all tasks in the task list.

        :return: A string containing the list of tasks.
        """
        if not os.path.exists(self.task_file):
            return "No tasks found."
        with open(self.task_file, "r") as f:
            return f.read()

    def clear_tasks(self) -> str:
        """
        Clears all tasks from the task list.

        :return: A message indicating success.
        """
        if os.path.exists(self.task_file):
            os.remove(self.task_file)
        return "All tasks cleared."
