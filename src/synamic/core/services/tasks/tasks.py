
class TasksService:
    def __init__(self, synamic):
        self.__synamic = synamic

    def load(self):
        self.__is_loaded = True
