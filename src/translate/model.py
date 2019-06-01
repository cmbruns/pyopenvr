import inspect
import re


class Declaration(object):
    def __init__(self, name, docstring=None):
        self.name = name
        self.docstring = docstring

    def __str__(self):
        return f'{self.name}'


class ConstantDeclaration(Declaration):
    def __init__(self, name, value, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.value = value

    def __str__(self):
        docstring = ''
        if self.docstring:
            docstring = f'  # {self.docstring}'
        return f'{self.name} = {self.value}{docstring}'


class Enum(Declaration):
    def __init__(self, name, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.constants = []

    def add_constant(self, constant):
        self.constants.append(constant)

    def __str__(self):
        result = f'{self.name} = ENUM_TYPE'
        for c in self.constants:
            result += f'\n{c}'
        return result


class EnumConstant(Declaration):
    def __init__(self, name, value, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.value = value

    def __str__(self):
        return f'{self.name} = ENUM_VALUE_TYPE({self.value})'


class Struct(Declaration):
    def __init__(self, name, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.fields = []
        self.base = None

    def add_field(self, field):
        self.fields.append(field)

    def __str__(self):
        docstring = ''
        if self.docstring:
            docstring = f'''
                """
                {self.docstring}
                """
            '''
        fields = ''
        for f in self.fields:
            fields = fields + f'''
                     {f}'''
        base = 'ctypes.Structure'
        if self.base is not None:
            base = self.base
        return inspect.cleandoc(f'''
            class {self.name}({base}):{docstring}
                _fields_ = [{fields}
                ]
        ''')


class StructureForwardDeclaration(Declaration):
    def __str__(self):
        return inspect.cleandoc(f'''
            class {self.name}(ctypes.Structure):
                pass
        ''')


class StructField(Declaration):
    def __init__(self, name, type_, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.type = type_

    def __str__(self):
        type_name = ctypes_from_cpp(self.type)
        return f'("{self.name}", {type_name}),'


class Typedef(Declaration):
    def __init__(self, alias, original, docstring=None):
        super().__init__(name=alias, docstring=docstring)
        self.original = original

    def __str__(self):
        orig = ctypes_from_cpp(self.original)
        return f'{self.name} = {orig}'


def ctypes_from_cpp(type_name, bracket=False):
    """
    Convert c++ type name to ctypes type name
    :param type_name:
    :return:
    """
    result = type_name

    # e.g. float[3] -> ctypes.c_float * 3
    m = re.match(r'^([^\d]+\S)\s*\[(\d+)\](.*)$', result)
    if m:
        t = f'{m.group(1)}{m.group(3)}'  # in case there are more dimensions
        t = ctypes_from_cpp(t, bracket=True)
        result = f'{t} * {m.group(2)}'
        if bracket:
            result = f'({result})'  # multiple levels of arrays

    # e.g. uint32_t -> ctypes.c_uint32
    m = re.match(r'^\s*((?:u?int|float)\d*)(?:_t)?\s*$', result)
    if m:
        result = f'ctypes.c_{m.group(1)}'

    return result
