from parcels.grid import Grid
from parcels.field import Field
from parcels.particle import ParticleType
import ast


class Node(ast.AST):
    """Base class for intermediate representation nodes"""

    _fields = ['children']

    def __init__(self):
        self.children = []

    def __repr__(self):
        if hasattr(self, 'children'):
            body = [str(c) for c in self.children]
            return "<%s: %s>" % (type(self).__name__, body)
        else:
            return "<%s>" % type(self).__name__


class Root(Node):
    """Root node for a tree of IR nodes describing a kernel"""

    def __init__(self, name, nodes):
        self.name = name
        self.children = nodes

    def __repr__(self):
        return '\n'.join([str(s) for s in self.children])


class Constant(Node):
    """Constant numerical value"""

    def __init__(self, value):
        self.value = value


class Variable(Node):
    """Scalar variable with optional type"""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<%s %s>" % (type(self).__name__, self.name)


class Assign(Node):
    """Basic variable assignment"""

    _fields = ['target', 'expr']

    def __init__(self, target, expr, op='='):
        self.target = target
        self.expr = expr
        self.op = op

    def __repr__(self):
        body = [str(c) for c in self.children]
        return "<%s %s: %s>" % (type(self).__name__, self.op, body)

    @property
    def children(self):
        return [self.target, self.expr]


class BinaryOperator(Node):
    """Binary arithmetic operator"""

    def __init__(self, expr1, expr2, op):
        self.children = [expr1, expr2]
        self.op = op


class GridIntrinsic(Node):
    """Intrinsic node representing `grid`"""

    def __init__(self, grid):
        assert(isinstance(grid, Grid))
        self.grid = grid

    def __getattr__(self, attr):
        field = getattr(self.grid, attr)
        return FieldIntrinsic(field)


class FieldIntrinsic(Node):
    """Intrinsic node representing field instances"""

    def __init__(self, field):
        assert(isinstance(field, Field))
        self.field = field


class ParticleIntrinsic(Node):
    """Intrinsic node representing `particle`"""

    def __init__(self, ptype):
        assert(isinstance(ptype, ParticleType))
        self.ptype = ptype

    def __getattr__(self, attr):
        assert(attr in [v.name for v in self.ptype.variables])
        return Variable(name='particle->%s' % attr)


class FieldEvalIntrinsic(Node):
    """Intrinsic node representing a field evaluation call"""

    _fields = ['args']

    def __init__(self, field, args, var=None):
        self.field = field
        self.args = args
        self.var = var or Variable('_TMP')

    def __repr__(self):
        return 'FIELD_EVAL:%s %s:' % (self.field.name, self.args)