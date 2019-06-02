"""
Parses translate header files to create a model of the code to be generated
"""

import inspect
import pkg_resources

from clang.cindex import Index, CursorKind

import translate.model as model


def clean_comment(cursor):
    docstring = cursor.raw_comment
    if docstring is None:
        return docstring
    docstring = inspect.cleandoc(docstring)
    docstring = docstring.replace('\r', '')
    if docstring.startswith('//'):
        docstring = docstring.replace('//', '  ')
    elif docstring.startswith('/**'):
        docstring = docstring.replace('/**', '   ')
        docstring = docstring.replace('**/', '   ')
        docstring.replace('\n  *', '\n   ')
        docstring = docstring.replace('*/', '  ')
        docstring = docstring.replace('\n*', '\n ')
    elif docstring.startswith('/*'):
        docstring = docstring.replace('/*', '  ')
        docstring = docstring.replace('*/', '  ')
        docstring = docstring.replace('\n *', '\n  ')
        docstring = docstring.replace('\n*', '\n ')
    else:
        assert False
    docstring = inspect.cleandoc(docstring.strip())
    # flank multi-line comments with newlines
    if '\n' in docstring:
        docstring = f'\n{docstring}\n'
    return docstring


class Parser(object):
    def __init__(self):
        self.items = []

    def parse_enum(self, cursor):
        name = cursor.spelling
        enum = model.Enum(name=name)
        next_value = 0
        index = dict()
        for child in cursor.get_children():
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                values = list(child.get_children())
                if len(values) > 0:
                    value = self.parse_literal(values[0])
                else:
                    value = str(next_value)
                enum_const = model.EnumConstant(name=child.spelling, value=value)
                enum.add_constant(enum_const)
                int_val = next_value
                if str(value) in index:
                    int_val = index[str(value)]  # reference to another enum value, e.g. 'k_EButton_Axis0'
                else:
                    try:
                        int_val = int(eval(str(value)))
                    except:
                        pass  # I give up
                index[str(child.spelling)] = int_val
                next_value = int_val + 1
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
        print(f'*** WARNING *** skipping function declaration {cursor.spelling}(...)')

    def parse_literal(self, cursor):
        value = ''.join([str(t.spelling) for t in cursor.get_tokens()])
        if cursor.kind == CursorKind.STRING_LITERAL:
            value = 'b' + value  # Ensure byte string for compatibility
        return value

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
                print(f'*** WARNING *** skipping class declaration {child.spelling}(...)')
            elif child.kind == CursorKind.CXX_METHOD:
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
        children = list(cursor.get_children())
        alias = cursor.spelling
        if len(children) == 1:
            original = children[0].spelling
            item = model.Typedef(alias=alias, original=original, docstring=cursor.brief_comment)
            self.items.append(item)

    def parse_unexposed_decl(self, cursor):
        for child in cursor.get_children():
            if child.kind == CursorKind.FUNCTION_DECL:
                self.parse_function(child)
            else:
                self.report_unparsed(child)

    def parse_var_decl(self, cursor):
        for child in cursor.get_children():
            if child.kind == CursorKind.UNEXPOSED_EXPR:
                value_cursor = list(child.get_children())[0]
                value = self.parse_literal(value_cursor)
                comment = cursor.brief_comment
                if comment is not None and comment.startswith('---'):
                    comment = None
                item = model.ConstantDeclaration(
                    name=cursor.spelling,
                    value=value,
                    docstring=comment,
                )
                self.items.append(item)

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
