class TaskData:
    def __init__(self, name: str, description=""):
        self.name = name
        self.description = description

        self.ui_card = None

        # Future Fields to setup in future user stories:
        self.priority = "Medium"
        self.due_date = None
        self.assigned_to = None
    
    def __str__(self):
        return self.name