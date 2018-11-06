
class TasksService:
    def __init__(self, site):
        self.__site = site

        self.__is_loaded = False

    def load(self):
        self.__is_loaded = True
