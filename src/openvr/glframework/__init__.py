import inspect
import textwrap


def shader_string(body, glsl_version='450 core'):
    """
    Call this method from a function that defines a literal shader string as the "body" argument.
    Dresses up a shader string in three ways:
        1) Insert #version at the top
        2) Insert #line number declaration
        3) un-indents
    The line number information can help debug glsl compile errors.
    The version string needs to be the very first characters in the shader,
    which can be distracting, requiring backslashes or other tricks.
    The unindenting allows you to type the shader code at a pleasing indent level
    in your python method, while still creating an unindented GLSL string at the end.
    """
    line_count = len(body.split('\n'))
    line_number = inspect.currentframe().f_back.f_lineno + 1 - line_count
    return """\
#version %s
%s
""" % (glsl_version, shader_substring(body, stack_frame=2))


def shader_substring(body, stack_frame=1):
    """
    Call this method from a function that defines a literal shader string as the "body" argument.
    Dresses up a shader string in two ways:
        1) Insert #line number declaration
        2) un-indents
    The line number information can help debug glsl compile errors.
    The unindenting allows you to type the shader code at a pleasing indent level
    in your python method, while still creating an unindented GLSL string at the end.
    """
    line_count = len(body.splitlines(True))
    line_number = inspect.stack()[stack_frame][2] + 1 - line_count
    return """\
#line %d
%s
""" % (line_number, textwrap.dedent(body))


if __name__ == "__main__":
    # Test example
    def vertex_shader():
        return shader_string("""
            layout(location = 0) in vec3 in_Position;
            layout(location = 1) in vec3 in_Normal;

            layout(location = 0) uniform mat4 projection = mat4(1);
            layout(location = 1) uniform mat4 model_view = mat4(1);

            out vec3 normal;

            void main() 
            {
                gl_Position = projection * model_view * vec4(in_Position, 1.0);
                mat4 normal_matrix = transpose(inverse(model_view));
                normal = normalize((normal_matrix * vec4(in_Normal, 0)).xyz);
            }        
            """)
    print(vertex_shader())
