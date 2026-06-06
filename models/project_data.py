class ProjectData:
    def __init__(self, name: str):
        self.name = name
        self.backlog_tasks = []
        self.active_tasks = []
        self.finished_tasks = []

    def add_task(self, column, task):
        getattr(self, column).append(task)
