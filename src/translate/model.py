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


class FunctionBase(Declaration):
    def __init__(self, name, type_=None, docstring=None):
        super().__init__(name=name, docstring=docstring)
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
        if parameter.name in ('punRequiredBufferSize', ):
            parameter.is_required_count = True  # getRuntimePath()
        self.parameters.append(parameter)

    def annotate_parameters(self):
        for pix, p in enumerate(self.parameters):
            if p.is_output_string():
                len_param = self.parameters[pix + 1]
                len_param.is_count = True
            if p.is_struct_size():
                if pix > 0:
                    sized_param = self.parameters[pix - 1]
                    t = sized_param.type.get_pointee().spelling
                    t = translate_type(t)
                    p.always_value = f'sizeof({t})'

    def ctypes_string(self, in_params=()):
        in_params = list(in_params)
        self.annotate_parameters()
        call_params = []
        out_params = []
        if self.has_return() and not self.raise_error_code():
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
        # Handle output strings
        for pix, p in enumerate(self.parameters):
            if p.is_output_string():
                len_param = self.parameters[pix + 1]
                if len_param.is_struct_size():
                    len_param = self.parameters[pix + 2]
                len_param.is_count = True
                call_params0 = []
                # Treat VR_GetRuntimePath specially...
                initial_buffer_size = 0
                length_is_retval = True
                required_len_param = None
                if len(self.parameters) >= 3 and self.parameters[2].name == 'punRequiredBufferSize':
                    initial_buffer_size = 1
                    length_is_retval = False
                    required_len_param = self.parameters[2]
                if initial_buffer_size > 0:
                    pre_call_statements += f'{p.py_name} = ctypes.create_string_buffer({initial_buffer_size})\n'
                for p2 in self.parameters:
                    if p2 is p:
                        if initial_buffer_size == 0:
                            call_params0.append('None')
                        else:
                            call_params0.append(p2.call_param_name())
                    elif p2 is len_param:
                        call_params0.append(str(initial_buffer_size))
                    elif p2.call_param_name():
                        call_params0.append(p2.call_param_name())
                param_list = ', '.join(call_params0)
                if length_is_retval:
                    pre_call_statements += textwrap.dedent(f'''\
                        {len_param.py_name} = fn({param_list})
                        if {len_param.py_name} == 0:
                            return ''
                        {p.py_name} = ctypes.create_string_buffer({len_param.py_name})
                    ''')
                else:  # getRuntimePath()
                    pre_call_statements += textwrap.dedent(f'''\
                        fn({param_list})
                        {len_param.py_name} = {required_len_param.py_name}.value
                        if {len_param.py_name} == 0:
                            return ''
                        {p.py_name} = ctypes.create_string_buffer({len_param.py_name})
                    ''')
        param_list1 = ', '.join(in_params)
        # pythonically downcase first letter of method name
        result_annotation = ''
        if len(out_params) == 0:
            result_annotation = ' -> None'
        method_string = f'def {self.py_method_name()}({param_list1}){result_annotation}:\n'
        body_string = ''
        if self.docstring:
            body_string += f'"""{self.docstring}"""\n'
        body_string += f'fn = {self.inner_function_name()}\n'
        body_string += pre_call_statements
        param_list2 = ', '.join(call_params)
        if self.raise_error_code():
            body_string += f'error = fn({param_list2})'
        elif self.has_return():
            body_string += f'result = fn({param_list2})'
        else:
            body_string += f'fn({param_list2})'
        if self.raise_error_code():
            error_category = translate_error_category(self.type)
            post_call_statements += f'\n{error_category}.check_error_value(error)'
        body_string += post_call_statements
        if self.py_method_name() == 'pollNextEvent':
            body_string += '\nreturn result != 0'  # Custom return statement
        elif len(out_params) > 0:
            results = ', '.join(out_params)
            body_string += f'\nreturn {results}'
        body_string = textwrap.indent(body_string, ' '*4)
        method_string += body_string
        return method_string

    def has_return(self):
        if self.type.spelling == 'void':
            return False
        for p in self.parameters:
            if p.is_output_string():
                return False
        return True

    def inner_function_name(self):
        return f'self.function_table.{self.py_method_name()}'

    def py_method_name(self):
        n = self.name
        if n.startswith('VR_'):
            n = n[3:]
        return n[0].lower() + n[1:]

    def raise_error_code(self):
        return re.match(r'(?:vr::)?E\S+Error$', self.type.spelling)


class COpenVRContext(Declaration):
    def __init__(self, name, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.vr_member_names = []
        self.vr_method_names = []

    def __str__(self):
        docstring = ''
        if self.docstring:
            docstring = textwrap.indent(f'\n"""{self.docstring}"""\n', ' '*16)
        name = translate_type(self.name)
        class_string = textwrap.dedent(f'''\
            class {name}(object):{docstring}
                def __init__(self):
        ''')
        for m in self.vr_member_names:
            class_string += ' '*8 + f'self.{m} = None\n'
        class_string += textwrap.indent(textwrap.dedent(f'''\
                
                def checkClear(self):
                    global _vr_token
                    if _vr_token != getInitToken():
                        self.clear()
                        _vr_token = getInitToken()
                        
                def clear(self):  
        '''), ' '*4)
        for m in self.vr_member_names:
            class_string += ' '*8 + f'self.{m} = None\n'
        class_string += '\n'
        for m in self.vr_method_names:
            method_string = textwrap.dedent(f'''\
                def {m}(self):
                    self.checkClear()
                    if self.m_p{m} is None:
                        self.m_p{m} = I{m}()
                    return self.m_p{m}
                              
            ''')
            class_string += textwrap.indent(method_string, ' '*4)
        class_string += textwrap.dedent(f'''\
            
            # Globals for context management
            _vr_token = None
            _internal_module_context = COpenVRContext()
        ''')
        for m in self.vr_method_names:
            method_string = textwrap.dedent(f'''\
                
                
                def {m}():
                    return _internal_module_context.{m}()
            ''')
            class_string += method_string
        return class_string

    def add_vr_member_name(self, name):
        self.vr_member_names.append(name)

    def add_vr_method_name(self, name):
        self.vr_method_names.append(name)


class IVRClass(Declaration):
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
                methods += textwrap.indent(str(method), 16*' ') + '\n\n'
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
                    fn_key = 'FnTable:' + version_key
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


class Function(FunctionBase):
    def inner_function_name(self):
        return f'_openvr.{self.name}'

    def ctypes_string(self):
        restype = translate_type(self.type.spelling)
        param_types = []
        for p in self.parameters:
            param_types.append(translate_type(p.type.spelling))
        arg_types = ', '.join(param_types)
        result = textwrap.dedent(f'''\
                _openvr.{self.name}.restype = {restype}
                _openvr.{self.name}.argtypes = [{arg_types}]


        ''')
        result += super().ctypes_string()
        return result


class Method(FunctionBase):
    def ctypes_fntable_string(self):
        method_name = self.name[0].lower() + self.name[1:]
        param_list = [translate_type(self.type.spelling), ]
        for p in self.parameters:
            param_list.append(translate_type(p.type.spelling))
        params = ', '.join(param_list)
        result = f'("{method_name}", OPENVR_FNTABLE_CALLTYPE({params})),'
        return result

    def ctypes_string(self):
        return super().ctypes_string(in_params=['self', ])


class Parameter(Declaration):
    def __init__(self, name, type_, default_value=None, docstring=None, annotation=None):
        super().__init__(name=name, docstring=docstring)
        self.type = type_
        self.always_value = None
        self.default_value = default_value
        self.annotation = annotation
        self.is_count = False
        self.is_required_count = False
        self.py_name = self.get_py_name(self.name)

    @staticmethod
    def get_py_name(c_name):
        result = c_name
        match = re.match(r'^[a-z]{1,5}([A-Z].*)$', result)
        if match:  # strip initial hungarian prefix
            n = match.group(1)
            result = n[0].lower() + n[1:]  # convert first character to lower case
        if result in ('bytes', 'from', 'property', 'type'):  # avoid python keywords
            result += '_'
        return result

    def is_array(self):
        if not self.annotation:
            return False
        return re.match(r'array_count:(\S+);', self.annotation)

    def is_error(self):
        if self.type.kind != TypeKind.POINTER:
            return False
        t = translate_type(self.type.get_pointee().spelling)
        if re.match(r'^(vr::)?E\S+Error$', t):
            return True
        return False

    def is_input_string(self):
        if not self.type.kind == TypeKind.POINTER:
            return False
        pt = self.type.get_pointee()
        if not pt.is_const_qualified():
            return False
        return pt.kind == TypeKind.CHAR_S

    def is_float(self):
        return self.type.kind in (
            TypeKind.FLOAT,
            TypeKind.DOUBLE,
            TypeKind.LONGDOUBLE,
            TypeKind.FLOAT128,
        )

    def is_int(self):
        return self.type.kind in (
            TypeKind.USHORT,
            TypeKind.UINT,
            TypeKind.ULONG,
            TypeKind.ULONGLONG,
            TypeKind.UINT128,
            TypeKind.SHORT,
            TypeKind.INT,
            TypeKind.LONG,
            TypeKind.LONGLONG,
            TypeKind.INT128,
        )

    def is_output_string(self):
        if not self.annotation:
            return False
        return str(self.annotation) == 'out_string: ;'

    def is_output(self):
        if self.is_count:
            return False
        if self.is_required_count:
            return False
        if not self.type.kind == TypeKind.POINTER:
            return False
        pt = self.type.get_pointee()
        if pt.is_const_qualified():
            return False
        if pt.kind == TypeKind.VOID:
            return False
        if pt.kind == TypeKind.POINTER:
            return True  # pointer to pointer
        if pt.spelling == 'vr::RenderModel_t':  # IVRRenderModels.freeRenderModel()
            return False
        if pt.spelling == 'vr::RenderModel_TextureMap_t':  # IVRRenderModels.freeTexture()
            return False
        return True

    def is_input(self):
        if self.is_count:
            return False
        if self.is_required_count:
            return False
        elif self.is_array():
            return True
        elif self.name == 'pEvent':
            return True
        elif self.always_value is not None:
            return False
        elif not self.is_output():
            return True
        else:
            return False  # TODO:

    def is_struct_size(self):
        if self.is_count:
            return False
        if self.type.kind not in (TypeKind.TYPEDEF, ):
            return False
        if self.name.startswith('unSizeOf'):
            return True
        if self.name in ('uncbVREvent', ):
            return True
        if not self.name.endswith('Size'):
            return False
        if self.default_value is not None:
            return False
        if self.name.endswith('BufferSize'):
            return False
        if self.name.endswith('CompressedSize'):
            return False
        if self.name.endswith('ElementSize'):
            return False
        return True

    def pre_call_block(self):
        m = self.is_array()
        if m:
            result = ''
            count_param = m.group(1)
            count_param = self.get_py_name(count_param)
            element_t = translate_type(self.type.get_pointee().spelling)
            is_pose_array = False
            if re.match(r'^trackedDevice.*Count$', count_param):
                is_pose_array = True
            if re.match(r'^\S+PoseArrayCount$', count_param):
                is_pose_array = True
            default_length = 1
            if is_pose_array:
                default_length = 'k_unMaxTrackedDeviceCount'
            result += textwrap.dedent(f'''\
                if {self.py_name} is None:
                    {count_param} = 0
                    {self.py_name}Arg = None
                elif isinstance({self.py_name}, ctypes.Array):
                    {count_param} = len({self.py_name})
                    {self.py_name}Arg = byref({self.py_name}[0])
                else:
                    {count_param} = {default_length}
                    {self.py_name} = ({element_t} * {count_param})()
                    {self.py_name}Arg = byref({self.py_name}[0])
                ''')
            return result
        elif self.is_output_string():
            return ''
        elif self.is_count:
            return ''
        elif self.always_value is not None:
            return f'{self.py_name} = {self.always_value}\n'
        elif not self.is_input():
            t = translate_type(self.type.get_pointee().spelling)
            return f'{self.py_name} = {t}()\n'
        elif self.is_input_string():
            result = textwrap.dedent(f'''\
                if {self.py_name} is not None:
                    {self.py_name} = bytes({self.py_name}, encoding='utf-8')
            ''')
            return result
        else:
            return ''

    def post_call_block(self):
        result = ''
        if self.is_error():
            assert self.type.kind == TypeKind.POINTER
            pt = self.type.get_pointee()
            error_category = translate_error_category(pt)
            result += f'\n{error_category}.check_error_value({self.py_name}.value)'
        if self.is_output() and self.type.kind == TypeKind.POINTER:
            pt = self.type.get_pointee()
            if pt.kind == TypeKind.POINTER:
                pt2 = pt.get_pointee()
                if pt2.spelling.endswith('_t'):
                    n = self.py_name
                    result += textwrap.dedent(f'''\
                        
                        if {n}:
                            {n} = {n}.contents
                        else:
                            {n} = None''')
        return result

    def input_param_name(self):
        if not self.is_input():
            return None
        n = self.py_name
        if self.is_input_string():
            n = f'{n}: str'
        elif self.is_int():
            n = f'{n}: int'
        elif self.is_float():
            n = f'{n}: float'
        if self.default_value:
            n = f'{n}={self.default_value}'
        return n

    def call_param_name(self):
        if self.is_array():
            return f'{self.py_name}Arg'
        elif self.is_count:
            return self.py_name
        elif self.is_output_string():
            return self.py_name
        elif self.is_output():
            return f'byref({self.py_name})'
        elif self.type.kind == TypeKind.POINTER:
            ptk = self.type.get_pointee().kind
            if ptk == TypeKind.CHAR_S:
                return self.py_name
            else:
                return f'byref({self.py_name})'
        else:
            return self.py_name

    def return_param_name(self):
        if self.is_error():
            return None
        if self.is_output_string():
            return f"bytes({self.py_name}.value).decode('utf-8')"
        if not self.is_output():
            return None
        result = self.py_name
        pt0 = self.type.get_pointee()
        extract_value = False
        if pt0.kind == TypeKind.TYPEDEF and pt0.spelling.endswith('Handle_t'):
            extract_value = True
        pt = translate_type(pt0.spelling)
        if pt.startswith('c_'):
            extract_value = True
        if extract_value:
            result += '.value'
        return result


class Struct(Declaration):
    def __init__(self, name, docstring=None):
        if name == 'vr::VRControllerState001_t':
            name = 'VRControllerState_t'
        super().__init__(name=name, docstring=docstring)
        self.fields = []
        self.base = None
        if name == 'VRControllerState_t':
            self.base = 'PackHackStructure'
        if name == 'vr::VREvent_t':
            self.base = 'PackHackStructure'

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
        if self.name == orig:
            return ''
        return f'{self.name} = {orig}'


def translate_error_category(type_):
    error_category = type_.spelling
    assert error_category.endswith('Error')
    if error_category.startswith('vr::EVR'):
        error_category = error_category[7:]
    elif error_category.startswith('vr::E'):
        error_category = error_category[5:]
    else:
        assert False
    return f'openvr.error_code.{error_category}'


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
    result = re.sub(r'\bunion\s+', '', result)
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

    m = re.match(r'^([^*]+\S)\s*[*&](.*)$', result)
    while m:  # # HmdStruct* -> POINTER(HmdStruct)
        pointee_type = translate_type(m.group(1))
        result = f'POINTER({pointee_type}){m.group(2)}'
        m = re.match(r'^([^*]+\S)\s*[*&](.*)$', result)

    # translate pointer type "ptr"
    m = re.match(r'^([^*]+)ptr(?:_t)?(.*)$', result)
    while m:  # uintptr_t -> POINTER(c_uint)
        pointee_type = translate_type(m.group(1))
        result = f'POINTER({pointee_type}){m.group(2)}'
        m = re.match(r'^([^*]+)ptr(?:_t)?(.*)$', result)

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
