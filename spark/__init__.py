import sys
PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    from spark.spark import GenericParser as GenericParser
    from spark.spark import GenericASTTraversal as GenericASTTraversal
    from spark.ast import AST as AST
    from spark.scanner import GenericScanner as GenericScanner
    from spark.scanner import GenericToken as GenericToken
else:
    from spark import GenericParser as GenericParser
    from spark import GenericASTTraversal as GenericASTTraversal
    from ast import AST as AST
