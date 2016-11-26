from spark_parser.scanner import  GenericToken
class PythonToken(GenericToken):
    def __init__(self, kind, attr, line, column):
        # self.type = kind # Not working yet
        pass
