from enum import StrEnum


class TaskStatus(StrEnum):
    TO_DO = 'to_do'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class Task:
    def __init__(self, name: str, description: str | None):
        self.name = name
        self.description = description
        self.status = TaskStatus.TO_DO