import sys
from spark_parser.version import VERSION

__version__ = 'SPARK-%s Python2 and Python3 compatible' % VERSION

PYTHON3 = (sys.version_info >= (3, 0))

if PYTHON3:
    from spark_parser.ast import AST as AST
    from spark_parser.spark import DEFAULT_DEBUG
    from spark_parser.spark import GenericParser as GenericParser
    from spark_parser.spark import GenericASTBuilder as GenericASTBuilder
    from spark_parser.spark import GenericASTTraversalPruningException as GenericASTTraversalPruningException
    from spark_parser.spark import GenericASTTraversal as GenericASTTraversal
    from spark_parser.scanner import GenericScanner as GenericScanner
    from spark_parser.scanner import GenericToken as GenericToken
else:
    from ast import AST as AST
    from spark import DEFAULT_DEBUG
    from spark import GenericParser as GenericParser
    from spark import GenericASTBuilder as GenericASTBuilder
    from spark import GenericASTTraversalPruningException as GenericASTTraversalPruningException
    from spark import GenericASTTraversal as GenericASTTraversal
    from scanner import GenericScanner as GenericScanner
    from scanner import GenericToken as GenericToken
