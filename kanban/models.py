from enum import StrEnum


class TaskStatus(StrEnum):
    TO_DO = 'to_do'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Task:
    def __init__(self, task_id: int, name: str, description: str | None, status: TaskStatus = TaskStatus.TO_DO):
        self.id = task_id
        self.name = name
        self.description = description
        self.status = status