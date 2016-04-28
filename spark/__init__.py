import sys
PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    from spark.ast import AST as AST
    from spark.spark import DEFAULT_DEBUG
    from spark.spark import GenericParser as GenericParser
    from spark.spark import GenericASTBuilder as GenericASTBuilder
    from spark.spark import GenericASTTraversalPruningException as GenericASTTraversalPruningException
    from spark.spark import GenericASTTraversal as GenericASTTraversal
    from spark.scanner import GenericScanner as GenericScanner
    from spark.scanner import GenericToken as GenericToken
else:
    from ast import AST as AST
    from spark import DEFAULT_DEBUG
    from spark import GenericParser as GenericParser
    from spark import GenericASTBuilder as GenericASTBuilder
    from spark import GenericASTTraversalPruningException as GenericASTTraversalPruningException
    from spark import GenericASTTraversal as GenericASTTraversal
    from scanner import GenericScanner as GenericScanner
    from scanner import GenericToken as GenericToken
