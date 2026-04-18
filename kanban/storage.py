import json
import os
from kanban.models import Task


class JsonStorage:
    def __init__(self, path: str):
        self.path = path
    
    def add_user_task(self, user_id: int, task: Task):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
        else: 
            data = {}

        if user_id in data:
            tasks = data[user_id]
            tasks[str(task.status)].append({
                'id': tasks["current_task_id"] + 1,
                'name': task.name,
                'description': task.description,
            })
            tasks["current_task_id"] += 1
            data[user_id] = tasks
        else:
            data[user_id] = {
                "current_task_id": 0,
                "to_do":[],
                "in_progress":[],
                "done": [],
            }
            
            data[user_id][str(task.status)].append({
                'id': 1,
                'name': task.name,
                'description': task.description,
            })
        
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        
    def get_user_current_task_id(self, user_id: int):
        with open(self.path) as f:
            data = json.load(f)
        if user_id in data:
            return data[user_id]["current_task_id"]
        else:
            data[user_id] = {
                "current_task_id": 0,
                "to_do":[],
                "in_progress":[],
                "done": [],
            }
        
    def get_task_by_id(self, user_id, task_id):
        with open(self.path) as f:
            data = json.load(f)
        user = data[str(user_id)]
        for task in user["to_do"]:
            if task["id"] == task_id:
                return Task(task["name"], task["description"], "to_do")
        for task in user["in_progress"]:
            if task["id"] == task_id:
                return Task(task["name"], task["description"], "in_progress")
        for task in user["done"]:
            if task["id"] == task_id:
                return Task(task["name"], task["description"], "done")


    def save_task(self, user_id: int, task_id: int, task: Task):
        with open(self.path) as f:
            data = json.load(f)
        task_data = {
            'id': task_id,
            'name': task.name,
            'description': task.description,
        }
        data[str(user_id)][str(task.status)] = task_data
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

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

