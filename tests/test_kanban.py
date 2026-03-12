from kanban.task_service import TaskServise
from kanban.models import Task, TaskStatus


class FakeStorage:
    def __init__(self):
        self.result = {}

    def add_user_task(self, user_id, task):
        self.result = {user_id: task}


class TestTaskServise:
    def test_create_task(self):
        storage = FakeStorage()
        servise = TaskServise(storage)
        servise.create_task(1, 'Zadacha', 'blabla')
        assert 1 in storage.result
        task: Task = storage.result[1]
        assert task.name == 'Zadacha'
        assert task.description == 'blabla'
        assert task.status == TaskStatus.TO_DO