from enum import StrEnum
from kanban.storage import JsonStorage
from kanban.models import Task


class TaskServise:
    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def create_task(self, user_id: int, name: str, description: str | None = None):
        task = Task(name, description)
        self.storage.add_user_task(user_id, task)


# {
#     "123":{
#         "current_task_id": 3
#         "to_do":[...]
#         "in_progres":[{'id':2, 'name':'abhs', 'description': 'сделать что-то'}]
#         "done": [...]
#     }
# }