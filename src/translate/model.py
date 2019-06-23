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


class Function(Declaration):
    def __init__(self, name, type_=None, docstring=None):
        super().__init__(name=name, docstring=docstring)
        self.type = type_
        self.parameters = []

    def __str__(self):
        py_name = self.name
        if py_name.startswith('VR_'):
            py_name = py_name[3:]
        py_name = py_name[0].lower() + py_name[1:]
        docstring = ''
        if self.docstring:
            docstring = f'\n"""{self.docstring}"""'
            docstring = textwrap.indent(docstring, ' '*20)
        params = []
        call_params = []
        param_types = []
        error_param = None
        for p in self.parameters:
            if p.is_error():
                error_param = p
            else:
                n = p.name
                if p.default_value:
                    n += f'={p.default_value}'
                params.append(n)
            if p.type.kind == TypeKind.POINTER:
                pt = p.type.get_pointee()
                if pt.is_const_qualified():
                    call_params.append(p.name)
                else:
                    call_params.append(f'byref({p.name})')
            else:
                call_params.append(p.name)
            param_types.append(translate_type(p.type.spelling))
        restype = translate_type(self.type.spelling)
        args = ', '.join(params)
        call_args = ', '.join(call_params)
        arg_types = ', '.join(param_types)
        if error_param is None:
            method_string = f'''
                _openvr.{self.name}.restype = {restype}
                _openvr.{self.name}.argtypes = [{arg_types}]
                def {py_name}({args}):{docstring}
                    result = _openvr.{self.name}({call_args})
                    return result
            '''
        else:
            etype = translate_type(error_param.type.get_pointee().spelling)
            method_string = f'''
                _openvr.{self.name}.restype = {restype}
                _openvr.{self.name}.argtypes = [{arg_types}]
                def {py_name}({args}):{docstring}
                    {error_param.name} = {etype}()
                    result = _openvr.{self.name}({call_args})
                    _checkInitError({error_param.name}.value)
                    return result
            '''
        return inspect.cleandoc(method_string)

    def add_parameter(self, parameter):
        self.parameters.append(parameter)


class Method(Declaration):
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
        self.parameters.append(parameter)

    def ctypes_fntable_string(self):
        method_name = self.name[0].lower() + self.name[1:]
        param_list = [translate_type(self.type), ]
        for p in self.parameters:
            param_list.append(translate_type(p.type.spelling))
        params = ', '.join(param_list)
        result = f'("{method_name}", OPENVR_FNTABLE_CALLTYPE({params})),'
        return result

    def has_return(self):
        if self.type == 'void':
            return False
        for p in self.parameters:
            if p.is_output_string():
                return False
        return True

    def ctypes_string(self):
        in_params = ['self']
        call_params = []
        out_params = []
        if self.has_return() and not self.raise_error_code():
            out_params.append('result')
        pre_call_statements = ''
        post_call_statements = ''
        # Annotate count params just in time
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
                for p2 in self.parameters:
                    if p2 is p:
                        call_params0.append('None')
                    elif p2 is len_param:
                        call_params0.append('0')
                    elif p2.call_param_name():
                        call_params0.append(p2.call_param_name())
                param_list = ', '.join(call_params0)
                pre_call_statements += textwrap.dedent(f'''\
                    {len_param.name} = fn({param_list})
                    if {len_param.name} == 0:
                        return b''
                    {p.name} = ctypes.create_string_buffer({len_param.name})
                ''')
        param_list1 = ', '.join(in_params)
        # pythonically downcase first letter of method name
        method_name = self.name[0].lower() + self.name[1:]
        result_annotation = ''
        if len(out_params) == 0:
            result_annotation = ' -> None'
        method_string = f'def {method_name}({param_list1}){result_annotation}:\n'
        body_string = ''
        if self.docstring:
            body_string += f'"""{self.docstring}"""\n\n'
        body_string += f'fn = self.function_table.{method_name}\n'
        body_string += pre_call_statements
        param_list2 = ', '.join(call_params)
        if self.raise_error_code():
            body_string += f'error_code = fn({param_list2})\n'
        elif self.has_return():
            body_string += f'result = fn({param_list2})\n'
        else:
            body_string += f'fn({param_list2})\n'
        if self.raise_error_code():
            message = f'{translate_type(self.type)}({{error_code}})'
            post_call_statements += textwrap.dedent(f'''\
                if error_code != 0:
                    raise OpenVRError(f'{message}')
            ''')
        body_string += post_call_statements
        if method_name == 'pollNextEvent':
            body_string += 'return result != 0\n'  # Custom return statement
        elif len(out_params) > 0:
            results = ', '.join(out_params)
            body_string += f'return {results}\n'
        body_string = textwrap.indent(body_string, ' '*4)
        method_string += body_string
        return method_string

    def raise_error_code(self):
        if re.match(r'(?:vr::)?EVRRenderModelError$', self.type):
            return False  # Need the non-zero error code in this case
        return re.match(r'(?:vr::)?E\S+Error$', self.type)


class Parameter(Declaration):
    def __init__(self, name, type_, default_value=None, docstring=None, annotation=None):
        if name == 'type':
            name = 'type_'
        super().__init__(name=name, docstring=docstring)
        self.type = type_
        self.always_value = None
        self.default_value = default_value
        self.annotation = annotation
        self.is_count = False
        if self.is_input_string():
            if self.name.startswith('pch'):
                self.name = self.name[3:]
                self.name = self.name[0].lower() + self.name[1:]

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
        if not self.type.kind == TypeKind.POINTER:
            return False
        pt = self.type.get_pointee()
        if pt.is_const_qualified():
            return False
        if pt.kind == TypeKind.VOID:
            return False
        return True

    def is_input(self):
        if self.is_count:
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
        if not self.type.kind in (TypeKind.TYPEDEF, ):
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
            element_t = translate_type(self.type.get_pointee().spelling)
            is_pose_array = False
            if re.match(r'^unTrackedDevice.*Count$', count_param):
                is_pose_array = True
            if re.match(r'^un\S+PoseArrayCount$', count_param):
                is_pose_array = True
            if is_pose_array:
                result += textwrap.dedent(f'''\
                    if {self.name} is None:
                        {count_param} = 0
                        {self.name}Arg = None
                    elif isinstance({self.name}, ctypes.Array):
                        {count_param} = len({self.name})
                        {self.name}Arg = byref({self.name}[0])
                    else:
                        {count_param} = k_unMaxTrackedDeviceCount
                        {self.name} = ({element_t} * {count_param})()
                        {self.name}Arg = byref({self.name}[0])
                    ''')
            else:
                result += textwrap.dedent(f'''\
                if {self.name} is None:
                    {count_param} = 0
                    {self.name}Arg = None
                else:
                    {count_param} = len({self.name})
                    {self.name}Arg = byref({self.name}[0])
                ''')
            return result
        elif self.is_output_string():
            return ''
        elif self.is_count:
            return ''
        elif self.always_value is not None:
            return f'{self.name} = {self.always_value}\n'
        elif not self.is_input():
            t = translate_type(self.type.get_pointee().spelling)
            return f'{self.name} = {t}()\n'
        else:
            return ''

    def post_call_block(self):
        result = ''
        if self.is_error():
            result += textwrap.dedent(f'''\
                if {self.name}.value != 0:
                    raise OpenVRError(str({self.name}))
            ''')
        if self.is_output() and self.type.kind == TypeKind.POINTER:
            pt = self.type.get_pointee()
            if pt.kind == TypeKind.POINTER:
                pt2 = pt.get_pointee()
                if pt2.spelling.endswith('_t'):
                    n = self.name
                    result += textwrap.dedent(f'''\
                        if {n}:
                            {n} = {n}.contents
                        else:
                            {n} = None
                    ''')
        return result

    def input_param_name(self):
        if not self.is_input():
            return None
        n = self.name
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
            return f'{self.name}Arg'
        elif self.is_count:
            return self.name
        elif self.is_input_string():
            return f"bytes({self.name}, encoding='utf-8')"
        elif self.is_output_string():
            return self.name
        elif self.is_output():
            return f'byref({self.name})'
        elif self.type.kind == TypeKind.POINTER:
            ptk = self.type.get_pointee().kind
            if ptk == TypeKind.CHAR_S:
                return self.name
            else:
                return f'byref({self.name})'
        else:
            return self.name

    def return_param_name(self):
        if self.is_error():
            return None
        if self.is_output_string():
            return f"bytes({self.name}.value).decode('utf-8')"
        if not self.is_output():
            return None
        result = self.name
        pt = translate_type(self.type.get_pointee().spelling)
        if pt.startswith('c_'):
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
