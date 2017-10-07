from spark_parser.scanner import  GenericToken
class PythonToken(GenericToken):
    def __init__(self, kind, attr, line, column):
        self.kind = kind
        self.attr = attr
        self.line = line
        self.column = column

    def __str__(self):
        return 'L%d.%d: %s: %r' % (self.line, self.column, self.kind, self.attr)
