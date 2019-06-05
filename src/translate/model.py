import enum
import inspect
import re
import textwrap


class Declaration(object):
    def __init__(self, name, docstring=None):
        self.name = name
        self.docstring = docstring

    def __str__(self):
        return f'{self.name}'


class Class(Declaration):
    def __init__(self, name, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.base = 'object'
        self.methods = []

    def __str__(self):
        docstring = ''
        if self.docstring:
            docstring = textwrap.indent(f'\n"""{self.docstring}"""\n', ' '*16)
        name = translate_type(self.name)
        methods = 'pass'
        fn_table_methods = ''
        if len(self.methods) > 0:
            methods = '\n'
            for method in self.methods:
                methods += textwrap.indent(str(method), 16*' ') + '\n'
                fn_table_methods += '\n' + ' '*20 + f'{method.ctypes_fntable_string()}'
        return inspect.cleandoc(f'''
            class {name}_FnTable(Structure):
                _fields_ = [{fn_table_methods}
                ]
        

            class {name}({self.base}):{docstring}
                def __init__(self):
                    version_key = {name}_Version
                    if not isInterfaceVersionValid(version_key):
                        _checkInitError(VRInitError_Init_InterfaceNotFound)
                    fn_key = b"FnTable:" + version_key
                    fn_type = {name}_FnTable
                    fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
                    if fn_table_ptr is None:
                        raise OpenVRError("Error retrieving VR API for {name}")
                    self.function_table = fn_table_ptr.contents\n{methods}
        ''')

    def add_method(self, method):
        self.methods.append(method)


class ConstantDeclaration(Declaration):
    def __init__(self, name, value, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.value = value

    def __str__(self):
        docstring = ''
        if self.docstring:
            docstring = f'  # {self.docstring}'
        return f'{self.name} = {self.value}{docstring}'


class EnumDecl(Declaration):
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


class Method(Declaration):
    def __init__(self, name, type_=None, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.name = name
        self.type = type_
        self.parameters = []

    def __str__(self):
        return self.ctypes_string()

    def add_parameter(self, parameter):
        self.parameters.append(parameter)

    def ctypes_fntable_string(self):
        method_name = self.name[0].lower() + self.name[1:]
        param_list = [translate_type(self.type), ]
        for p in self.parameters:
            param_list.append(translate_type(p.type))
        params = ', '.join(param_list)
        result = f'("{method_name}", OPENVR_FNTABLE_CALLTYPE({params})),'
        return result

    def ctypes_string(self):
        docstring = ''
        if self.docstring:
            docstring = f'\n"""{self.docstring}"""\n'
        all_params = []
        in_params = ['self']
        out_params = []
        for p in self.parameters:
            # is this an output parameter?
            if p.in_out == Parameter.INOUT.OUTPUT:
                out_params.append(p)
                all_params.append(f'byref({p.name})')
            else:
                in_params.append(p.name)
                all_params.append(p.name)
        param_list1 = ', '.join(in_params)
        param_list2 = ', '.join(all_params)
        # pythonically downcase first letter of method name
        method_name = self.name[0].lower() + self.name[1:]
        if len(out_params) == 0:  # simple case: no output parameters
            docstring = textwrap.indent(docstring, ' '*16)
            return inspect.cleandoc(f'''
            def {method_name}({param_list1}):{docstring}
                fn = self.function_table.{method_name}
                result = fn({param_list2})
                return result
            ''') + '\n'
        result_list = []
        fn_call = f'fn({param_list2})'
        if not self.type == 'void':
            result_list.append('result')
            fn_call = f'result = fn({param_list2})'
        out_decls = []
        for op in out_params:
            t = translate_type(op.type[:-1])
            out_decls.append(f'{op.name} = {t}()')
            # Pointers to primitive types return the .value member
            s = op.name
            t = translate_type(op.type)
            if t.startswith('POINTER(c_'):
                s += '.value'
            result_list.append(s)
        od = '\n' + '\n'.join(out_decls)
        od = textwrap.indent(od, ' '*12)
        docstring = textwrap.indent(docstring, ' '*12)
        results = ', '.join(result_list)
        return inspect.cleandoc(f'''
        def {method_name}({param_list1}):{docstring}
            fn = self.function_table.{method_name}{od}
            {fn_call}
            return {results}
        ''') + '\n'


class Parameter(Declaration):
    # @enum.Enum.unique
    class INOUT(enum.Enum):
        INPUT = enum.auto()
        OUTPUT = enum.auto()
        ARRAY_COUNT = enum.auto()
        ARRAY_OUTPUT = enum.auto()

    def __init__(self, name, type_, in_out=INOUT.INPUT, default_value=None, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.type = type_
        self.in_out = in_out
        self.default_value = default_value


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
            docstring = textwrap.indent(f'\n"""{self.docstring}"""\n', ' '*16)
        fields = ''
        for f in self.fields:
            fields = fields + f'''
                    {f}'''
        name = translate_type(self.name)
        base = 'Structure'
        if self.base is not None:
            base = translate_type(self.base)
        if name.startswith('HmdMatrix'):
            base = f'_MatrixMixin, {base}'
        if name.startswith('HmdVector'):
            base = f'_VectorMixin, {base}'
        return inspect.cleandoc(f'''
            class {name}({base}):{docstring}
                _fields_ = [{fields}
                ]
        ''')


class StructureForwardDeclaration(Declaration):
    def __str__(self):
        return inspect.cleandoc(f'''
            class {self.name}(Structure):
                pass
        ''')


class StructField(Declaration):
    def __init__(self, name, type_, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.type = type_

    def __str__(self):
        type_name = translate_type(self.type)
        return f'("{self.name}", {type_name}),'


class Typedef(Declaration):
    def __init__(self, alias, original, docstring=None):
        super().__init__(name=alias, docstring=docstring)
        self.original = original

    def __str__(self):
        orig = translate_type(self.original)
        return f'{self.name} = {orig}'


def translate_type(type_name, bracket=False):
    """
    Convert c++ type name to ctypes type name
    # TODO: move to ctypes generator
    """
    # trim space characters
    result = type_name.strip()
    result = re.sub(r'\bconst\s+', '', result)
    result = re.sub(r'\s+const\b', '', result)
    result = re.sub(r'\bstruct\s+', '', result)
    result = re.sub(r'\benum\s+', '', result)
    # no implicit int
    if result == 'unsigned':
        result = 'unsigned int'
    # abbreviate type for ctypes
    result = re.sub(r'8_t\b', '8', result)
    result = re.sub(r'16_t\b', '16', result)
    result = re.sub(r'32_t\b', '32', result)
    result = re.sub(r'64_t\b', '64', result)
    result = re.sub(r'\bunsigned\s+', 'u', result)  # unsigned int -> uint
    if re.match(r'^\s*(?:const\s+)?char\s*\*\s*$', result):
        result = 'c_char_p'
    result = re.sub(r'\blong\s+long\b', 'longlong', result)
    # prepend 'c_' for ctypes
    if re.match(r'^(float|u?int|double|u?char|u?short|u?long)', result):
        result = f'c_{result}'
    # remove leading "VR_"
    result = re.sub(r'\bVR_', '', result)

    m = re.match(r'^([^\*]+\S)\s*[\*&](.*)$', result)
    while m:  # # HmdStruct* -> POINTER(HmdStruct)
        pointee_type = translate_type(m.group(1))
        result = f'POINTER({pointee_type}){m.group(2)}'
        m = re.match(r'^([^\*]+\S)\s*[\*&](.*)$', result)

    # translate pointer type "ptr"
    m = re.match(r'^([^\*]+)ptr(?:_t)?(.*)$', result)
    while m:  # uintptr_t -> POINTER(c_uint)
        pointee_type = translate_type(m.group(1))
        result = f'POINTER({pointee_type}){m.group(2)}'
        m = re.match(r'^([^\*]+)ptr(?:_t)?(.*)$', result)

    if result == 'void':
        result = 'None'
    if result == 'POINTER(None)':
        result = 'c_void_p'
    result = re.sub(r'\bbool\b', 'openvr_bool', result)

    # e.g. vr::HmdMatrix34_t -> HmdMatrix34_t
    if result.startswith('vr::'):
        result = result[4:]

    # e.g. float[3] -> c_float * 3
    m = re.match(r'^([^\[]+\S)\s*\[(\d+)\](.*)$', result)
    if m:
        t = f'{m.group(1)}{m.group(3)}'  # in case there are more dimensions
        t = translate_type(t, bracket=True)
        result = f'{t} * {m.group(2)}'
        if bracket:
            result = f'({result})'  # multiple levels of arrays

    return result
