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


class TaskServise:
    def __init__(self, storage: JsonStorage):
        self.storage = storage

    def create_task(self, user_id: int, name: str, description: str | None = None):
        storage.get_user_current_task_id(user_id)
        task = Task(name, description)
        storage.add_user_task(user_id, task)



# {
#     "123":{
#         "current_task_id": 3
#         "to_do":[...]
#         "in_progres":[{'id':2, 'name':'abhs', 'description': 'сделать что-то'}]
#         "done": [...]
#     }
# }