class Query:
    def __init__(self, contents, query_string):
        self.__query_string = query_string
        self.__results = () if len(contents) == 0 else contents

    def __bool__(self):
        return True if len(self.__results) > 0 else False

    def __len__(self):
        return len(self.__results)

    @property
    def count(self):
        return len(self)

    @property
    def results(self):
        return self.__results

    @property
    def query_string(self):
        return self.__query_string
