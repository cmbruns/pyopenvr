from clang.cindex import TypeKind
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
        self._count_parameter_names = set()

    def __str__(self):
        return self.ctypes_string()

    def add_parameter(self, parameter):
        # Tag count parameters
        m = parameter.is_array()
        if m:
            self._count_parameter_names.add(m.group(1))
        if parameter.name in self._count_parameter_names:
            parameter.is_count = True
        self.parameters.append(parameter)

    def ctypes_fntable_string(self):
        method_name = self.name[0].lower() + self.name[1:]
        param_list = [translate_type(self.type), ]
        for p in self.parameters:
            param_list.append(translate_type(p.type.spelling))
        params = ', '.join(param_list)
        result = f'("{method_name}", OPENVR_FNTABLE_CALLTYPE({params})),'
        return result

    def ctypes_string(self):
        in_params = ['self']
        call_params = []
        out_params = []
        if self.type != 'void':
            out_params.append('result')
        pre_call_statements = ''
        post_call_statements = ''
        for p in self.parameters:
            if p.input_param_name():
                in_params.append(p.input_param_name())
            if p.call_param_name():
                call_params.append(p.call_param_name())
            if p.return_param_name():
                out_params.append(p.return_param_name())
            pre_call_statements += p.pre_call_block()
            post_call_statements += p.post_call_block()
        param_list1 = ', '.join(in_params)
        # pythonically downcase first letter of method name
        method_name = self.name[0].lower() + self.name[1:]
        method_string = f'def {method_name}({param_list1}):\n'
        body_string = ''
        if self.docstring:
            body_string += f'"""{self.docstring}"""\n\n'
        body_string += f'fn = self.function_table.{method_name}\n'
        body_string += pre_call_statements
        param_list2 = ', '.join(call_params)
        if self.type == 'void':
            body_string += f'fn({param_list2})\n'
        else:
            body_string += f'result = fn({param_list2})\n'
        body_string += post_call_statements
        if len(out_params) > 0:
            results = ', '.join(out_params)
            body_string += f'return {results}\n'
        body_string = textwrap.indent(body_string, ' '*4)
        method_string += body_string
        return method_string


class Parameter(Declaration):
    def __init__(self, name, type_, default_value=None, docstring=None, annotation=None):
        super().__init__(name=name, docstring=docstring)
        self.type = type_
        self.default_value = default_value
        self.annotation = annotation
        self.is_count = False

    def is_array(self):
        if not self.annotation:
            return False
        return re.match(r'array_count:(\S+);', self.annotation)

    def is_output(self):
        if self.is_count:
            return False
        if not self.type.kind == TypeKind.POINTER:
            return False
        pt = self.type.get_pointee()
        if pt.is_const_qualified():
            return False
        return True

    def is_input(self):
        if self.is_count:
            return False
        elif self.is_array():
            return True
        elif not self.is_output():
            return True
        else:
            return False  # TODO:

    def pre_call_block(self):
        m = self.is_array()
        if m:
            result = ''
            count_param = m.group(1)
            element_t = translate_type(self.type.get_pointee().spelling)
            if re.match(r'^unTrackedDevice.*Count$', count_param):
                result += textwrap.dedent(f'''\
                    if {self.name} is None:
                        {count_param} = k_unMaxTrackedDeviceCount
                        {self.name} = ({element_t} * {count_param})()
                        {self.name}Arg = byref({self.name}[0])
                    ''')
            else:
                result += textwrap.dedent(f'''\
                if {self.name} is None:
                    {count_param} = 0
                    {self.name}Arg = None
                ''')
            result += textwrap.dedent(f'''\
                else:
                    {count_param} = len({self.name})
                    {self.name}Arg = byref({self.name}[0])
                ''')
            return result
        elif self.is_count:
            return ''
        elif not self.is_input():
            t = translate_type(self.type.get_pointee().spelling)
            return f'{self.name} = {t}()\n'
        else:
            return ''

    def post_call_block(self):
        return ''

    def input_param_name(self):
        if not self.is_input():
            return None
        return self.name

    def call_param_name(self):
        if self.is_array():
            return f'{self.name}Arg'
        elif self.is_count:
            return self.name
        elif self.is_output():
            return f'byref({self.name})'
        else:
            return self.name

    def return_param_name(self):
        if not self.is_output():
            return None
        result = self.name
        pt = translate_type(self.type.get_pointee().spelling)
        if pt.startswith('c_'):
            result += '.value'
        return result


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
