from enum import StrEnum
from kanban.storage import JsonStorage
from kanban.models import Task, TaskStatus


class TaskServise:
    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def create_task(self, user_id: int, name: str, description: str | None = None):
        task = Task(name, description)
        self.storage.add_user_task(user_id, task)
        return task
    
    def update_task(self, user_id: int, task_id: int, description: str | None = None, status: TaskStatus | None = None):
        task = self.storage.get_task_by_id(user_id, task_id)
        if isinstance(description, str):
            task.description = description
        if isinstance(status, TaskStatus):
            task.status = status
        if description is None and status is None:
            raise AttributeError('Description или Status должны быть переданы в функцию')
        self.storage.save_task(user_id, task_id, task)
        return task





# {
#     "123":{
#         "current_task_id": 3
#         "to_do":[...]
#         "in_progres":[{'id':2, 'name':'abhs', 'description': 'сделать что-то'}]
#         "done": [...]
#     }
# }