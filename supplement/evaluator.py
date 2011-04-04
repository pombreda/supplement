import ast

from .objects import create_object

def get_name(name, scope):
    project = scope.project

    while scope:
        try:
            return scope[name]
        except KeyError:
            scope = scope.parent

    return project.get_module('__builtin__')[name]

def infer(string, scope):
    tree = ast.parse(string, '<string>', 'eval')
    return Evaluator().process(tree, scope)

class Evaluator(ast.NodeVisitor):
    def name_op(self):
        name = self.stack.pop()
        self.stack.append(get_name(name, self.scope))

    def attr_op(self):
        obj = self.stack.pop()
        attr = self.stack.pop()
        self.stack.append(obj[attr])

    def visit_Name(self, node):
        self.ops.append(self.name_op)
        self.stack.append(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        self.ops.append(self.attr_op)
        self.stack.append(node.attr)
        self.generic_visit(node)

    def visit_Load(self, node):
        self.ops.pop()()

    def visit_Str(self, node):
        self.stack.append(create_object(self.scope, node.s))

    def visit_Num(self, node):
        self.stack.append(create_object(self.scope, node.n))

    def visit_List(self, node):
        self.stack.append(create_object(self.scope, []))

    def visit_Tuple(self, node):
        self.stack.append(create_object(self.scope, ()))

    def visit_Dict(self, node):
        self.stack.append(create_object(self.scope, {}))

    def process(self, tree, scope):
        self.level = 0
        self.scope = scope
        self.ops = []
        self.stack = []
        self.generic_visit(tree)

        return self.stack[-1]

    def default(self, node):
        print '  ' * self.level, type(node), vars(node)
        self.level += 1
        self.generic_visit(node)
        self.level -= 1

    def __getattr__(self, name):
        if name in ('_attrs'):
            return object.__getattr__(self, name)

        return self.default
