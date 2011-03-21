import sys
import types

from supplement.module import Module
from supplement.project import Project

def create_module(project, name, source):
    code = compile(source, '<string>', 'exec')
    module = types.ModuleType(name)
    sys.modules[name] = module

    exec code in module.__dict__

    m = TestModule(project, module)
    m.source = source
    module.__file__ = name + '.py'

    project.module_provider.cache[name] = m

    return m

class TestModule(Module):
    def get_source(self):
        return self.source


def pytest_funcarg__project(request):
    p = Project('.')
    p.create_module = types.MethodType(create_module, p, Project)
    return p

def cleantabs(text):
    lines = text.splitlines()
    if not lines[0].strip():
        lines = lines[1:]

    toremove = 999
    for l in lines:
        stripped = l.strip()
        if stripped:
            toremove = min(toremove, len(l) - len(stripped))

    if toremove < 999:
        return '\n'.join(l[toremove:] for l in lines)
    else:
        return '\n'.join(lines)
