import json
import os
from kanban.models import Task, TaskStatus


class JsonStorage:
    def __init__(self, path: str):
        self.path = path
    
    def add_user_task(self, user_id: int, task: Task) -> None:
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
        else: 
            data = {}

        if user_id not in data:
            data[user_id] = {
                "tasks": [],
                "current_task_id": 0,
            }
        
        tasks = data[user_id]
        tasks["current_task_id"] += 1
        tasks["tasks"].append({
            'id': tasks["current_task_id"],
            'name': task.name,
            'description': task.description,
            'status': TaskStatus.TO_DO.value,
        })
        data[user_id] = tasks
            
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        
    def get_user_current_task_id(self, user_id: int) -> int | None:
        with open(self.path) as f:
            data = json.load(f)

        if user_id in data:
            return data[user_id]["current_task_id"]
        
        
    def get_task_by_id(self, user_id: int, task_id: int) -> Task:
        with open(self.path) as f:
            data = json.load(f)

        user = data[str(user_id)]
        for task in user["tasks"]:
            if task["id"] == task_id:
                return Task(task["task_id"], task["name"], task["description"], task["status"])

    def save_task(self, user_id: int, task: Task):
        with open(self.path) as f:
            data = json.load(f)
       
        task_data = {
            'id': task.id,
            'name': task.name,
            'description': task.description,
            'status': task.status,
        }
        
        if user_id not in data:
            data[user_id] = {
                "tasks": [],
                "current_task_id": 0,
            }
        user = data[user_id]
        for i, element in enumerate(user["tasks"]):
            if element["id"] == task.id:
                user["tasks"][i] = task_data
                break
        else:
            user["tasks"].append(task_data)

        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_all_tasks(self, user_id) -> dict | None:
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
        else:
            return None
        
        if user_id in data:
            return data[user_id]
        else: 
            return None




# file =
# {
#     "321": ...
#     "123":{
#         "tasks": [
#               {'id': 1, 'name': 'qsd', 'description': 'asd', 'status': 'to_do'},
#               {...}, 
#               {...}
#               {'id': 4}
#         ]
#         "current_task_id": 3
#     }
#     "789": ...
# }



# file =
# {
#     "321": ...
#     "123":{
#         "current_task_id": 3
#         "to_do":['id':2, 'name':'abhs', 'description': 'сделать что-то'}]
#         "in_progres":[{'id':2, 'name':'abhs', 'description': 'сделать что-то'}]
#         "done": [...]
#     }
#     "789": ...
# }
