import json

from kanban.models import Task


class JsonStorage:
    def __init__(self, path: str):
        self.path = path
    
    def add_user_task(self, user_id: int, task: Task):
        with open(self.path) as f:
            data = json.load(f)

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

