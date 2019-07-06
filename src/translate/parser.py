"""
Parses translate header files to create a model of the code to be generated
"""

import inspect
import pkg_resources

from clang.cindex import CursorKind, Index, TypeKind

import translate.model as model


def clean_comment(cursor):
    docstring = cursor.raw_comment
    if docstring is None:
        return docstring
    docstring = docstring.replace('\r', '')
    docstring = docstring.replace('\t', '   ')  # doc for IVRSystem::GetTimeSinceLastVsync has a tab
    docstring = inspect.cleandoc(docstring)
    if docstring.startswith('//'):
        docstring = docstring.replace('//', '  ')
    elif docstring.startswith('/**'):
        docstring = docstring.replace('/**', '   ')
        docstring = docstring.replace('**/', '   ')
        docstring.replace('\n  *', '\n   ')
        docstring = docstring.replace('*/', '  ')
        # docstring = docstring.replace('\n*\t', '\n   ')
        docstring = docstring.replace('\n*', '\n ')
    elif docstring.startswith('/*'):
        docstring = docstring.replace('/*', '  ')
        docstring = docstring.replace('*/', '  ')
        docstring = docstring.replace('\n *', '\n  ')
        docstring = docstring.replace('\n*', '\n ')
    else:
        assert False
    docstring = inspect.cleandoc(docstring.strip())
    docstring = docstring.replace('\\', '\\\\')  # Replace single backslash with double
    # flank multi-line comments with newlines
    if '\n' in docstring:
        docstring = f'\n{docstring}\n'
    return docstring


class Parser(object):
    def __init__(self):
        self.items = []

    def parse_copenvrcontext(self, cursor):
        name = cursor.type.spelling
        class_ = model.COpenVRContext(name=name, docstring=clean_comment(cursor))
        for child in cursor.get_children():
            if child.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                continue  # no such thing in python
            elif child.kind == CursorKind.CONSTRUCTOR:
                continue  # I will translate this manually
            elif child.kind == CursorKind.CXX_METHOD:
                if child.spelling == 'Clear':
                    continue  # I will translate this manually
                elif child.spelling == 'CheckClear':
                    continue  # I will translate this manually
                elif child.spelling.startswith('VR'):
                    class_.add_vr_method_name(child.spelling)
                else:
                    self.report_unparsed(child)
            elif child.kind == CursorKind.FIELD_DECL:
                if child.spelling.startswith('m_pVR'):
                    class_.add_vr_member_name(child.spelling)
                else:
                    self.report_unparsed(child)
            else:
                self.report_unparsed(child)
        return class_

    def parse_ivrclass(self, cursor):
        name = cursor.type.spelling
        class_ = model.IVRClass(name=name, docstring=clean_comment(cursor))
        for child in cursor.get_children():
            if child.kind == CursorKind.CXX_METHOD:
                method = self.parse_method(child)
                class_.add_method(method)
            elif child.kind == CursorKind.CXX_ACCESS_SPEC_DECL:
                continue  # no such thing in python
            elif child.kind == CursorKind.FIELD_DECL:
                print(f'*** WARNING *** skipping class member {cursor.spelling}::{child.spelling}')
                continue
            else:
                self.report_unparsed(child)
        return class_

    def parse_enum(self, cursor):
        name = cursor.spelling
        enum = model.EnumDecl(name=name)
        for child in cursor.get_children():
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                value1 = child.enum_value
                enum_const = model.EnumConstant(name=child.spelling, value=value1)
                enum.add_constant(enum_const)
            else:
                self.report_unparsed(child)
        self.items.append(enum)

    def parse_field(self, cursor):
        name = cursor.spelling
        field_type = cursor.type.spelling
        return model.StructField(name=name, type_=field_type)

    def parse_file(self, file_name, file_string):
        index = Index.create()
        translation_unit = index.parse(
            path=file_name,
            unsaved_files=((file_name, file_string),),
            args=[
                '-fparse-all-comments',  # we want even non-Doxygen comments
                '-x',
                'c++',  # TODO: for openvr.h only
                '-DAPI_GEN',  # get annotations for output parameters
            ])
        self.parse_translation_unit(cursor=translation_unit.cursor)
        return self.items

    def parse_function(self, cursor):
        name = cursor.spelling
        is_c_function = False
        if name.startswith('VR_'):
            for child in cursor.get_children():
                if child.kind == CursorKind.DLLIMPORT_ATTR:
                    is_c_function = True
        if is_c_function:
            restype = cursor.result_type
            function_ = model.Function(name=name, type_=restype, docstring=clean_comment(cursor))
            for child in cursor.get_children():
                if child.kind == CursorKind.DLLIMPORT_ATTR:
                    pass  # OK
                elif child.kind == CursorKind.PARM_DECL:
                    parameter = self.parse_parameter(child)
                    if parameter is not None:
                        function_.add_parameter(parameter)
                elif child.kind == CursorKind.TYPE_REF:
                    pass  # presumably the return type
                else:
                    self.report_unparsed(child)
            self.items.append(function_)
            return
        param_count = 0
        for child in cursor.get_children():
            if child.kind == CursorKind.PARM_DECL:
                param_count += 1
        is_ivr_instance_function = False
        if name.startswith('VR') and param_count == 0:
            rt = cursor.result_type
            if rt.kind == TypeKind.POINTER:
                pt = rt.get_pointee()
                if pt.spelling.startswith('vr::IVR'):
                    is_ivr_instance_function = True
        if is_ivr_instance_function:
            pass  # OK - we generate these from COpenVRContext
        elif cursor.spelling == 'VR_Init':
            pass  # OK - we manually generate this one
        elif cursor.spelling == 'VR_Shutdown':
            pass  # OK - we manually generate this one
        else:
            print(f'*** WARNING *** skipping function declaration {cursor.spelling}(...)')

    def parse_literal(self, cursor):
        value = ''.join([str(t.spelling) for t in cursor.get_tokens()])
        if cursor.kind == CursorKind.STRING_LITERAL:
            value = "'" + value[1:-1] + "'"  # prefer single quotes
            # value = 'b' + value  # Ensure byte string for compatibility
        return value

    def parse_method(self, cursor):
        name = cursor.spelling
        method = model.Method(name=name, type_=cursor.result_type, docstring=clean_comment(cursor))
        for child in cursor.get_children():
            if child.kind == CursorKind.PARM_DECL:
                parameter = self.parse_parameter(child)
                if parameter is not None:
                    method.add_parameter(parameter)
            elif child.kind == CursorKind.TYPE_REF:
                pass  # OK, probably the return type we already got
            elif child.kind == CursorKind.NAMESPACE_REF:
                pass  # OK, return type is probably namespace qualified
            else:
                self.report_unparsed(child)
        return method

    def parse_parameter(self, cursor):
        name = cursor.spelling
        default_value = None
        annotation = None
        for child in cursor.get_children():
            if child.kind == CursorKind.TYPE_REF:
                pass  # OK, we expect one of these
            elif child.kind == CursorKind.UNEXPOSED_EXPR:
                for gc in child.get_children():
                    if gc.kind == CursorKind.CXX_NULL_PTR_LITERAL_EXPR:
                        default_value = 'None'
                    elif gc.kind == CursorKind.INTEGER_LITERAL:
                        val = self.parse_literal(gc)
                        if val.endswith('L'):
                            val = val[:-1]
                        if cursor.type.kind == TypeKind.POINTER and int(val) == 0:
                            default_value = 'None'
                        else:
                            default_value = f'{int(val)}'
                    elif len(gc.spelling) > 0:
                        default_value = gc.spelling
                    elif gc.kind == CursorKind.CXX_UNARY_EXPR:
                        # default value is some expression
                        # so jam the tokens together, and hope it's interpretable by python
                        # unPrimitiveSize = sizeof( VROverlayIntersectionMaskPrimitive_t )
                        tokens = ''.join([t.spelling for t in gc.get_tokens()])
                        default_value = tokens
                    else:
                        self.report_unparsed(gc)
            elif child.kind == CursorKind.CXX_BOOL_LITERAL_EXPR:
                bool_val = str(next(child.get_tokens()).spelling)
                default_value = str(bool_val == 'true')
            elif child.kind == CursorKind.ANNOTATE_ATTR:
                annotation = child.spelling
            elif child.kind == CursorKind.DECL_REF_EXPR:
                default_value = child.spelling
            elif child.kind == CursorKind.NAMESPACE_REF:
                pass  # probably on the parameter type
            else:
                self.report_unparsed(child)
        parameter = model.Parameter(
            name=name,
            type_=cursor.type,
            docstring=clean_comment(cursor),
            default_value=default_value,
            annotation=annotation,
        )
        return parameter

    def parse_namespace(self, cursor):
        assert str(cursor.spelling) == 'vr'
        for child in cursor.get_children():
            if child.kind == CursorKind.VAR_DECL:
                self.parse_var_decl(child)
            elif child.kind == CursorKind.TYPEDEF_DECL:
                self.parse_typedef(child)
            elif child.kind == CursorKind.STRUCT_DECL:
                self.items.append(self.parse_struct(child))
            elif child.kind == CursorKind.UNION_DECL:
                union = self.parse_struct(child)
                union.base = 'Union'
                self.items.append(union)
            elif child.kind == CursorKind.ENUM_DECL:
                self.parse_enum(child)
            elif child.kind == CursorKind.FUNCTION_DECL:
                self.parse_function(child)
            elif child.kind == CursorKind.UNEXPOSED_DECL:
                self.parse_unexposed_decl(child)
            elif child.kind == CursorKind.CLASS_DECL:
                if child.spelling.startswith('IVR'):
                    self.items.append(self.parse_ivrclass(child))
                elif child.spelling.startswith('COpenVRContext'):
                    self.items.append(self.parse_copenvrcontext(child))
                else:
                    print(f'*** WARNING *** skipping class {child.spelling}(...)')
            elif child.kind == CursorKind.CXX_METHOD:
                cn = child.semantic_parent.spelling
                mn = child.spelling
                if cn == 'COpenVRContext' and mn == 'Clear':
                    pass  # OK - we manually wrap this one
                else:
                    print(f'*** WARNING *** skipping class method implementation {child.spelling}(...)')
            else:
                self.report_unparsed(child)

    def parse_struct(self, cursor):
        name = cursor.type.spelling
        struct = model.Struct(name=name, docstring=clean_comment(cursor))
        for child in cursor.get_children():
            if child.kind == CursorKind.FIELD_DECL:
                field = self.parse_field(child)
                struct.add_field(field)
            elif child.kind == CursorKind.CXX_BASE_SPECIFIER:
                struct.base = child.spelling
            elif child.kind == CursorKind.CONSTRUCTOR:
                print(f'*** WARNING *** skipping constructor for struct {cursor.spelling}')
            else:
                self.report_unparsed(child)
        return struct

    def parse_struct_decl(self, cursor):
        item = model.StructureForwardDeclaration(
            name=cursor.spelling,
            docstring=cursor.brief_comment,
        )
        self.items.append(item)

    def parse_translation_unit(self, cursor):
        tu_file_name = str(cursor.spelling)
        for child in cursor.get_children():
            # Skip external declarations
            child_file_name = str(child.location.file)
            if not child_file_name == tu_file_name:
                continue
            if child.kind == CursorKind.STRUCT_DECL:
                # Parse forward declarations
                self.parse_struct_decl(child)
            elif child.kind == CursorKind.NAMESPACE:
                self.parse_namespace(child)
            else:
                self.report_unparsed(child)

    def parse_typedef(self, cursor):
        alias = cursor.spelling
        original = cursor.underlying_typedef_type.spelling
        if str(original).endswith('VRControllerState001_t'):
            return
        item = model.Typedef(alias=alias, original=original, docstring=cursor.brief_comment)
        self.items.append(item)

    def parse_unexposed_decl(self, cursor):
        for child in cursor.get_children():
            if child.kind == CursorKind.FUNCTION_DECL:
                self.parse_function(child)
            else:
                self.report_unparsed(child)

    def parse_var_decl(self, cursor):
        comment = cursor.brief_comment
        if comment is not None and comment.startswith('---'):
            comment = None
        for child in cursor.get_children():
            if child.kind == CursorKind.UNEXPOSED_EXPR:
                value_cursor = list(child.get_children())[0]
                value = self.parse_literal(value_cursor)
                item = model.ConstantDeclaration(
                    name=cursor.spelling,
                    value=value,
                    docstring=comment,
                )
                self.items.append(item)
            elif child.kind == CursorKind.TYPE_REF:
                pass  # OK
            elif child.kind == CursorKind.INTEGER_LITERAL:
                value = self.parse_literal(child)
                item = model.ConstantDeclaration(
                    name=cursor.spelling,
                    value=value,
                    docstring=comment,
                )
                self.items.append(item)
            elif child.kind == CursorKind.UNARY_OPERATOR:
                # Presumable a minus sign
                value = self.parse_literal(child)
                item = model.ConstantDeclaration(
                    name=cursor.spelling,
                    value=value,
                    docstring=comment,
                )
                self.items.append(item)
            else:
                self.report_unparsed(child)

    def report_unparsed(self, cursor, indent=0):
        print(' '*indent, 'UNPARSED: ', cursor.kind, cursor.spelling, cursor.location)
        for child in cursor.get_children():
            self.report_unparsed(child, indent + 2)


if __name__ == '__main__':
    file_name1 = 'openvr.h'
    file_string1 = pkg_resources.resource_string(__name__, file_name1)
    model = Parser().parse_file(file_name=file_name1, file_string=file_string1)
    bDump = True
    if bDump:
        for declaration in model:
            print(declaration)
