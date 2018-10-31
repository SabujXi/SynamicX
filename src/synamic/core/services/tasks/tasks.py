
class TasksService:
    def __init__(self, site):
        self.__site = site

    def load(self):
        self.__is_loaded = True
