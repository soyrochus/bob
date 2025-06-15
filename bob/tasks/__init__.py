# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT


class TaskManager:
    """
    Base class for task managers. Subclasses should implement required methods.
    """
    def add_task(self, task):
        raise NotImplementedError

    def get_task(self, task_id):
        raise NotImplementedError

    def remove_task(self, task_id):
        raise NotImplementedError

    def list_tasks(self):
        raise NotImplementedError
