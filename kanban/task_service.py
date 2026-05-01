from enum import StrEnum
from kanban.storage import JsonStorage
from kanban.models import Task, TaskStatus


class TaskServiсe:
    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def create_task(self, user_id: int, name: str, description: str | None = None):
        task = Task(name, description)
        self.storage.add_user_task(user_id, task)
        return task

    def get_tasks(self, user_id: int):
        return self.storage.get_all_tasks(user_id)

    def update_task(
        self,
        user_id: int,
        task_id: int,
        description: str | None = None,
        status: TaskStatus | None = None,
    ):
        task = self.storage.get_task_by_id(user_id, task_id)
        if task is None:
            raise AttributeError(
                "Такого номера задачи не существует."
            )
        if isinstance(description, str):
            task.description = description
        if isinstance(status, TaskStatus):
            task.status = status
        if description is None and status is None:
            raise AttributeError(
                "Description или Status должны быть переданы в функцию"
            )
        self.storage.save_task(user_id, task)
        return task


