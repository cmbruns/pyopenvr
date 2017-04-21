#!/bin/env python

# file hello_glfw.py

import numpy
import time
import collections
from numpy.linalg import inv, norm
import itertools
from textwrap import dedent
from ctypes import cast, c_float, c_void_p, sizeof

from OpenGL.GL import *  # @UnusedWildImport # this comment squelches an IDE warning
# from OpenGL.GL import GL_FLOAT, GL_ELEMENT_ARRAY_BUFFER, GL_FRAGMENT_SHADER, GL_TRIANGLES, GL_UNSIGNED_INT, GL_VERTEX_SHADER
# from OpenGL.GL import glUniformMatrix4fv, glUseProgram, glVertexAttribPointer, glDrawElements, glBindVertexArray, glGenVertexArrays, glEnableVertexAttribArray, glDeleteVertexArrays
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.arrays import vbo

import glfw
import openvr

from openvr.glframework.glfw_app import GlfwApp
from openvr.gl_renderer import OpenVrGlRenderer
from openvr.tracked_devices_actor import TrackedDevicesActor
from openvr.glframework.glmatrix import pack
import openvr.glframework.glmatrix as glmatrix


"""
glfw programming example with colored mouse brain scene that can be closed by pressing ESCAPE.
"""


def Vec3(xyz):
    return numpy.array(xyz[0:3], dtype=numpy.float32)


# TODO - subdivide this example into
# * mesh
# * actor
# * material
# * lighting
class ObjMesh(object):
    def __init__(self, file_stream=None):
        "Create a mesh object from a file stream"
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.triangles = []
        if file_stream is not None:
            self.load_file_stream(file_stream)
        self.vao = 0
        self.vertexPositions = None
        self.indexPositions = None
        # self.init_gl()
        self.model_matrix =glmatrix.identity()

    def _parse_line(self, line):
        fields = line.split()
        if not fields:
            return # skip empty lines
        key = fields[0]
        if key.startswith('#'):
            return # skip comment lines
        if key == 'v':
            self._parse_vertex(fields)
        elif key == 'vn':
            self._parse_normal(fields)
        elif key == 'vt':
            self._parse_texcoord(fields)
        elif key == 'f':
            self._parse_face(fields)
        else:
            raise "Unrecognized data line starting with '%s'" % key

    def _parse_vertex(self, fields):
        x, y, z = map(float, fields[1:4])
        if len(fields) > 4:
            w = float(fields[4])
        else:
            w = 1.0
        v = (x/w, y/w, z/w)
        self.vertices.append( v )
        # print(v)

    def _parse_normal(self, fields):
        self.normals.append( map(float, fields[1:4]) )

    def _parse_face(self, fields):
        face = []
        for v in fields[1:]:
            w = v.split('/')
            face.append(int(w[0]))
        for triangle in range(len(face) - 2):
            self.triangles.append([i-1 for i in face[triangle:triangle+3]])

    def init_gl(self):
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        # flatten vector arrays
        idx = [item for sublist in self.triangles for item in sublist]
        floats_per_vertex = 3
        # Is there one normal per vertex? If so, pack them together
        use_normals = False
        if len(self.vertices) == len(self.normals):
            use_normals = True
            floats_per_vertex += 3
            # flatten list
            vtx = list(itertools.chain.from_iterable(zip(self.vertices, self.normals)))
            # flatten again, because the structure was three levels deep
            vtx = list(itertools.chain.from_iterable(vtx))
        else:
            vtx = [item for v in self.vertices for item in v]
        # print(vtx)
        self.vertexPositions = vbo.VBO(
            numpy.array(vtx, dtype=numpy.float32))
        self.indexPositions = vbo.VBO(
            numpy.array(idx, dtype=numpy.uint32), 
            target=GL_ELEMENT_ARRAY_BUFFER)
        self.vertexPositions.bind()
        self.indexPositions.bind()
        # Triangle vertices
        glEnableVertexAttribArray(0)
        fsize = sizeof(c_float)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, floats_per_vertex * fsize, cast(0 * fsize, c_void_p))
        if use_normals:
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, False, floats_per_vertex * fsize, cast(3 * fsize, c_void_p))
        glBindVertexArray(0)
        # 
        vertex_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 212
            
            layout(location = 0) in vec3 in_Position;
            layout(location = 1) in vec3 in_Normal;
            
            layout(location = 0) uniform mat4 projectionMatrix = mat4(1);
            layout(location = 4) uniform mat4 modelMatrix = mat4(1);
            layout(location = 8) uniform mat4 viewMatrix = mat4(1);

            const mat4 scale = mat4(mat3(0.0001)); // convert micrometers to millimeters

            out vec3 normal;
            
            void main() {
              gl_Position = projectionMatrix * viewMatrix * modelMatrix * scale * vec4(in_Position, 1.0);
              mat3 normalMatrix = transpose(inverse(mat3(modelMatrix * scale)));
              normal = normalize(normalMatrix * in_Normal);
            }
            """), 
            GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
            """\
            #version 450 core
            #line 233

            in vec3 normal;
            out vec4 fragColor;
            
            void main() {
              // fragColor = vec4(0.1, 0.8, 0.1, 1.0);
              vec3 norm_color = 0.5 * (normalize(normal) + vec3(1));
              fragColor = vec4(norm_color, 1);
            }
            """), 
            GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader)

    def display_gl(self, modelview, projection):
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        
        # TODO: Adjust modelview matrix
        # modelview0 = self.model_matrix * modelview
        # modelview0 = numpy.asarray(numpy.matrix(modelview0, dtype=numpy.float32))
        # print(modelview0[3,0])
        
        glUniformMatrix4fv(4, 1, False, pack(self.model_matrix))
        glUniformMatrix4fv(8, 1, False, pack(modelview))
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indexPositions), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def dispose_gl(self):
        glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0
        if self.vertexPositions is not None:
            self.vertexPositions.delete()
            self.indexPositions.delete()     

    def load_file_stream(self, file_stream):
        for line in file_stream:
            self._parse_line(line)


class ControllerState(object):
    def __init__(self, name):
        self.name = name
        self.is_dragging = False
        self.device_index = None
        self.current_pose = None
        self.previous_pose = None
        
    def check_drag(self, poses):
        if self.device_index is None:
            return
        self.current_pose = poses[self.device_index]
        is_good_drag = True # start optimistic
        if not self.is_dragging:
            is_good_drag = False
            self.previous_pose = None
        if self.previous_pose is None:
            is_good_drag = False
        elif not self.previous_pose.bPoseIsValid:
            is_good_drag = False
        if not self.current_pose.bPoseIsValid:
            is_good_drag = False
        if is_good_drag:
            X0 = self.previous_pose.mDeviceToAbsoluteTracking
            X1 = self.current_pose.mDeviceToAbsoluteTracking
            # Translation only, for now
            dx = X1.m[0][3] - X0.m[0][3]
            dy = X1.m[1][3] - X0.m[1][3]
            dz = X1.m[2][3] - X0.m[2][3]
            # print("%+7.4f, %+7.4f, %+7.4f" % (dx, dy, dz))
            result = Vec3( (dx, dy, dz,) )
        else:
            result = None
        # Create a COPY of the current pose for comparison next time
        self.previous_pose = openvr.TrackedDevicePose_t(self.current_pose.mDeviceToAbsoluteTracking)
        self.previous_pose.bPoseIsValid = self.current_pose.bPoseIsValid
        return result
    

class ProceduralNoiseShader(object):
    def __init__(self):
        self.fragment_shader = compileShader(dedent(
                """\
                #version 450 core
                #line 320
                
                //
                // Description : Array and textureless GLSL 2D simplex noise function.
                //      Author : Ian McEwan, Ashima Arts.
                //  Maintainer : stegu
                //     Lastmod : 20110822 (ijm)
                //     License : Copyright (C) 2011 Ashima Arts. All rights reserved.
                //               Distributed under the MIT License. See LICENSE file.
                //               https://github.com/ashima/webgl-noise
                //               https://github.com/stegu/webgl-noise
                // 
                
                vec3 mod289(vec3 x) {
                  return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec2 mod289(vec2 x) {
                  return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec3 permute(vec3 x) {
                  return mod289(((x*34.0)+1.0)*x);
                }
                
                vec4 mod289(vec4 x) {
                  return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec4 permute(vec4 x) {
                     return mod289(((x*34.0)+1.0)*x);
                }
                
                vec4 taylorInvSqrt(vec4 r)
                {
                  return 1.79284291400159 - 0.85373472095314 * r;
                }
                
                float snoise(vec3 v)
                  { 
                  const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
                  const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
                
                // First corner
                  vec3 i  = floor(v + dot(v, C.yyy) );
                  vec3 x0 =   v - i + dot(i, C.xxx) ;
                
                // Other corners
                  vec3 g = step(x0.yzx, x0.xyz);
                  vec3 l = 1.0 - g;
                  vec3 i1 = min( g.xyz, l.zxy );
                  vec3 i2 = max( g.xyz, l.zxy );
                
                  //   x0 = x0 - 0.0 + 0.0 * C.xxx;
                  //   x1 = x0 - i1  + 1.0 * C.xxx;
                  //   x2 = x0 - i2  + 2.0 * C.xxx;
                  //   x3 = x0 - 1.0 + 3.0 * C.xxx;
                  vec3 x1 = x0 - i1 + C.xxx;
                  vec3 x2 = x0 - i2 + C.yyy; // 2.0*C.x = 1/3 = C.y
                  vec3 x3 = x0 - D.yyy;      // -1.0+3.0*C.x = -0.5 = -D.y
                
                // Permutations
                  i = mod289(i); 
                  vec4 p = permute( permute( permute( 
                             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
                           + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) 
                           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
                
                // Gradients: 7x7 points over a square, mapped onto an octahedron.
                // The ring size 17*17 = 289 is close to a multiple of 49 (49*6 = 294)
                  float n_ = 0.142857142857; // 1.0/7.0
                  vec3  ns = n_ * D.wyz - D.xzx;
                
                  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);  //  mod(p,7*7)
                
                  vec4 x_ = floor(j * ns.z);
                  vec4 y_ = floor(j - 7.0 * x_ );    // mod(j,N)
                
                  vec4 x = x_ *ns.x + ns.yyyy;
                  vec4 y = y_ *ns.x + ns.yyyy;
                  vec4 h = 1.0 - abs(x) - abs(y);
                
                  vec4 b0 = vec4( x.xy, y.xy );
                  vec4 b1 = vec4( x.zw, y.zw );
                
                  //vec4 s0 = vec4(lessThan(b0,0.0))*2.0 - 1.0;
                  //vec4 s1 = vec4(lessThan(b1,0.0))*2.0 - 1.0;
                  vec4 s0 = floor(b0)*2.0 + 1.0;
                  vec4 s1 = floor(b1)*2.0 + 1.0;
                  vec4 sh = -step(h, vec4(0.0));
                
                  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
                  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
                
                  vec3 p0 = vec3(a0.xy,h.x);
                  vec3 p1 = vec3(a0.zw,h.y);
                  vec3 p2 = vec3(a1.xy,h.z);
                  vec3 p3 = vec3(a1.zw,h.w);
                
                //Normalise gradients
                  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
                  p0 *= norm.x;
                  p1 *= norm.y;
                  p2 *= norm.z;
                  p3 *= norm.w;
                
                // Mix final noise value
                  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
                  m = m * m;
                  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), 
                                                dot(p2,x2), dot(p3,x3) ) );
                }

                float snoise(vec2 v)
                  {
                  const vec4 C = vec4(0.211324865405187,  // (3.0-sqrt(3.0))/6.0
                                      0.366025403784439,  // 0.5*(sqrt(3.0)-1.0)
                                     -0.577350269189626,  // -1.0 + 2.0 * C.x
                                      0.024390243902439); // 1.0 / 41.0
                // First corner
                  vec2 i  = floor(v + dot(v, C.yy) );
                  vec2 x0 = v -   i + dot(i, C.xx);
                
                // Other corners
                  vec2 i1;
                  //i1.x = step( x0.y, x0.x ); // x0.x > x0.y ? 1.0 : 0.0
                  //i1.y = 1.0 - i1.x;
                  i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
                  // x0 = x0 - 0.0 + 0.0 * C.xx ;
                  // x1 = x0 - i1 + 1.0 * C.xx ;
                  // x2 = x0 - 1.0 + 2.0 * C.xx ;
                  vec4 x12 = x0.xyxy + C.xxzz;
                  x12.xy -= i1;
                
                // Permutations
                  i = mod289(i); // Avoid truncation effects in permutation
                  vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 ))
                        + i.x + vec3(0.0, i1.x, 1.0 ));
                
                  vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
                  m = m*m ;
                  m = m*m ;
                
                // Gradients: 41 points uniformly over a line, mapped onto a diamond.
                // The ring size 17*17 = 289 is close to a multiple of 41 (41*7 = 287)
                
                  vec3 x = 2.0 * fract(p * C.www) - 1.0;
                  vec3 h = abs(x) - 0.5;
                  vec3 ox = floor(x + 0.5);
                  vec3 a0 = x - ox;
                
                // Normalise gradients implicitly by scaling m
                // Approximation of: m *= inversesqrt( a0*a0 + h*h );
                  m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
                
                // Compute final noise value at P
                  vec3 g;
                  g.x  = a0.x  * x0.x  + h.x  * x0.y;
                  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
                  return 130.0 * dot(m, g);
                }
                
                float fractal_noise(vec2 texCoord, int nlevels) {
                    if (nlevels < 1) 
                        return 0.0;
                    const float w = 0.5;
                    float result = 0;
                    for (int n = 1; n < nlevels + 1; ++n) {
                        result += pow(w, n) * snoise(n * texCoord);
                    }
                    return result;
                }

                float fractal_noise(vec3 texCoord, int nlevels) {
                    if (nlevels < 1) 
                        return 0.0;
                    const float w = 0.5;
                    float result = 0;
                    for (int n = 1; n < nlevels + 1; ++n) {
                        result += pow(w, n) * snoise(n * texCoord);
                    }
                    return result;
                }

                float filtered_noise(in vec2 texCoord, in float detail) {
                    // Figure out how many spots we might need to sample
                    vec2 dxv = vec2(dFdx(texCoord.x), dFdy(texCoord.x));
                    vec2 dyv = vec2(dFdx(texCoord.y) + dFdy(texCoord.y));
                    float dx = length(dxv);
                    float dy = length(dyv);
                    // How many samples are needed in each direction?
                    const int MaxSamples = 10;
                    int sx = 1 + clamp( int( detail*dx ), 0, MaxSamples-1 );
                    int sy = 1 + clamp( int( detail*dy ), 0, MaxSamples-1 );
                    float dt = length(vec2(dx, dy));
                    if (dt > 5)
                        // return -1.0;
                        return fractal_noise(texCoord, 0); // stuff really far away is just a blurry grey
                    else if (dt <= 0.1) {
                        // return 1.0;
                        return fractal_noise(texCoord, 5); // close stuff gets one exact sample
                    }
                    else if (dt <= 0.3) {
                        // return 1.0;
                        return fractal_noise(texCoord, 3); // close stuff gets one exact sample
                    }
                    else if (dt <= 0.7) {
                        // return 1.0;
                        return fractal_noise(texCoord, 1); // close stuff gets one exact sample
                    }
                    else {
                        // TODO: Multisample here
                        float result = 0.0;
                        vec2 dv = vec2(dx, dy);
                        for (int x = 0; x < sx; ++x) {
                            for (int y = 0; y < sy; ++y) {
                                vec2 tc = texCoord + dv*vec2(x, y)/vec2(sx, sy) - 0.5*dv;
                                result += fractal_noise(tc, 1);
                            }
                        }
                        // return 1.0;
                        return result / (sx*sy);
                        // return fractal_noise(texCoord, 1); // needs filtering
                    }
                }
                """), 
            GL_FRAGMENT_SHADER)


class FloorActor(object):
    "Floor plane with procedural texture for context"
    def __init__(self):
        self.shader = 0
        self.vao = 0
        
    def init_gl(self):
        vertex_shader = compileShader(dedent(
                """
                #version 450 core
                #line 563
                
                layout(location = 0) uniform mat4 Projection = mat4(1);
                layout(location = 4) uniform mat4 ModelView = mat4(1);
                
                const vec3 FLOOR_QUAD[4] = vec3[4](
                    vec3(-1, 0, -1),
                    vec3(-1, 0, +1),
                    vec3(+1, 0, +1),
                    vec3(+1, 0, -1)
                );
                
                const int FLOOR_INDICES[6] = int[6](
                    2, 1, 0,
                    0, 3, 2
                );
                
                out vec2 texCoord;
                
                void main() {
                    int vertexIndex = FLOOR_INDICES[gl_VertexID];
                    vec3 v = FLOOR_QUAD[vertexIndex];
                    const float scale = 50; // meters per side
                    texCoord = scale * v.xz;
                    gl_Position = Projection * ModelView * vec4(scale * v, 1);
                }
                """
                ), GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
                """\
                #version 450 core
                #line 594

                in vec2 texCoord; // Floor texture coordinate in meters
                out vec4 FragColor;
                
                float filtered_noise(in vec2 texCoord, in float detail);

                void main() 
                {
                    // shift texture coordinate so origin artifact is probably far away,
                    // and shift intensity from range [-1,1] to range [0,1]
                    float noise = 0.50 * (filtered_noise(texCoord * 2 + vec2(10, 10), 8) + 1.0);
                    // interpolate final color between brown and green
                    const vec3 color1 = vec3(0.25, 0.3, 0.15); // green
                    const vec3 color2 = vec3(0.05, 0.05, 0.0); // dark brown
                    vec3 color = mix(color2, color1, noise);
                    FragColor = vec4(color, 1.0);
                }
                """), 
            GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader, ProceduralNoiseShader().fragment_shader)
        #
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        glEnable(GL_DEPTH_TEST)

    def display_gl(self, modelview, projection):
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        self.shader = 0
        glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0


class SkyActor(object):
    "Sky sphere with procedural texture for context"
    def __init__(self):
        self.shader = 0
        self.vao = 0
        
    def init_gl(self):
        vertex_shader = compileShader(dedent(
                """
                #version 450 core
                #line 644
                
                layout(location = 0) uniform mat4 Projection = mat4(1);
                layout(location = 4) uniform mat4 ViewMatrix = mat4(1);
                
                const vec4 SCREEN_QUAD[4] = vec4[4](
                    vec4(-1, -1, 0, 1),
                    vec4(-1, +1, 0, 1),
                    vec4(+1, +1, 0, 1),
                    vec4(+1, -1, 0, 1));
                
                const int SCREEN_INDICES[6] = int[6](
                    0, 1, 2,
                    0, 3, 2
                );
                
                out mat4 dirFromNdc;
                out vec4 ndc;
                
                void main() {
                    int vertexIndex = SCREEN_INDICES[gl_VertexID];
                    vec4 v = SCREEN_QUAD[vertexIndex];
                    gl_Position = v;
                    dirFromNdc = mat4(inverse(mat3(ViewMatrix))) * inverse(Projection);
                    ndc = v;
                }
                """
                ), GL_VERTEX_SHADER)
        fragment_shader = compileShader(dedent(
                """\
                #version 450 core
                #line 674

                in mat4 dirFromNdc;
                in vec4 ndc;
                // in vec3 view_direction; // Floor texture coordinate in meters
                out vec4 FragColor;
                
                // float filtered_noise(in vec2 texCoord, in float detail);
                float fractal_noise(vec3 texCoord, int nlevels);


                void main() 
                {
                    vec4 d = dirFromNdc*ndc;                    
                    vec3 view_dir = normalize(d.xyz/d.w);
                    vec3 zenith_color = vec3(0.2, 0.2, 1.0); // deep blue
                    vec3 horizon_color = vec3(0.80, 0.80, 1.0); // pale blue
                    vec3 sky_color = mix(horizon_color, zenith_color, view_dir.y);
                    vec3 cloud_color = vec3(1);
                    float noise = 0.5 * fractal_noise(2 * view_dir, 4) + 0.5;
                    noise = clamp( 0.7 * noise + 0.4 , 0, 1);
                    vec3 color = mix(cloud_color, sky_color, noise);
                    // color = 0.5*ndc.xyz/ndc.w + vec3(0.5);
                    FragColor = vec4(color, 1.0);
                    // FragColor = vec4 (1.0, 0.8, 0.8, 1.0); // pink
                }
                """), 
            GL_FRAGMENT_SHADER)
        self.shader = compileProgram(vertex_shader, fragment_shader, ProceduralNoiseShader().fragment_shader)
        #
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        glEnable(GL_DEPTH_TEST)

    def display_gl(self, modelview, projection):
        glDisable(GL_DEPTH_TEST)
        glUseProgram(self.shader)
        glUniformMatrix4fv(0, 1, False, projection)
        glUniformMatrix4fv(4, 1, False, modelview)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 6)
    
    def dispose_gl(self):
        glDeleteProgram(self.shader)
        self.shader = 0
        glDeleteVertexArrays(1, (self.vao,))
        self.vao = 0


class SpatialInteractor(object):
    "Composite interactor consisting of both controllers plus maybe other inputs"
    
    def __init__(self):
        self.translation_history = collections.deque() # array of translation increments
        self.max_history_size = 100
        self.left_controller = ControllerState("left controller")
        self.right_controller = ControllerState("right controller")
        self.is_dragging = self.left_controller.is_dragging or self.right_controller.is_dragging
        self.velocity_damping = 1.5 # meters per second per second
        self.speed = 0.0 # meters per second inertial velocity
        self.min_velocity = 0.01 # meters per second

    def update_controller_states(self):
        new_event = openvr.VREvent_t()
        while openvr.VRSystem().pollNextEvent(new_event):
            self._check_controller_drag(new_event)
        now_is_dragging = self.left_controller.is_dragging or self.right_controller.is_dragging
        
        xform = self._compute_controllers_transform()
        if xform is not None:
            obj.model_matrix *= xform
        
        # Check for drag begin/end
        if self.is_dragging and not now_is_dragging:
            # print ("drag released!")
            # maybe record velocity
            self._begin_inertial_coast()
        elif now_is_dragging and not self.is_dragging:
            # print ("drag started!")
            self.translation_history.clear()
            self.speed = 0.0
        elif now_is_dragging: # continued drag
            pass
        else: # not dragging, so maybe slow inertial coasting
            if self.speed > 0:
                dt = time.time() - self.previous_update_time
                dv = dt * self.velocity_damping
                self.speed -= dv
                if self.speed < 0: # stay positive
                    self.speed = 0.0
                elif self.speed < self.min_velocity: # static friction takes over at the very end
                    self.speed = 0.0
                else:
                    # print ("speed = %.3f meters per second" % self.speed)
                    dx = self.speed * dt * self.direction
                    obj.model_matrix *=glmatrix.translate(dx)
        self.previous_update_time = time.time()
                
        # Remember drag state
        self.is_dragging = now_is_dragging

    def _begin_inertial_coast(self):
        history_size = len(self.translation_history)
        if history_size < 10: # ~100 ms too short a drag to throw
            self.translation_history.clear()
            return
        history_size = min(history_size - 1, 50) # No more than ~500 ms history
        t1 = self.translation_history[-1][1]
        dx = Vec3([0,0,0])
        for i in range(history_size):
            x, t0 = self.translation_history[-i]
            dx += x
        dt = t1 - t0
        velocity = dx/dt;
        self.speed = norm(velocity)
        self.direction = velocity / self.speed;
        # print("direction = ", self.direction)
        # print("speed = ", self.speed, " meters per second")
        self.translation_history.clear()

    def _check_controller_drag(self, event):
        dix = event.trackedDeviceIndex
        device_class = openvr.VRSystem().getTrackedDeviceClass(dix)
        # We only want to watch controller events
        if device_class != openvr.TrackedDeviceClass_Controller:
            return
        bix = event.data.controller.button
        # Pay attention to trigger presses only
        if bix != openvr.k_EButton_SteamVR_Trigger:
            return
        role = openvr.VRSystem().getControllerRoleForTrackedDeviceIndex(dix)
        if role == openvr.TrackedControllerRole_RightHand:
            controller = self.right_controller
            # print("  right controller trigger %s" % action)
        else:
            controller = self.left_controller
            # print("  left controller trigger %s" % action)
        controller.device_index = dix
        t = event.eventType
        # "Touch" event happens earlier than "Press" event,
        # so allow a light touch for grabbing here
        if t == openvr.VREvent_ButtonTouch:
            controller.is_dragging = True
        elif t == openvr.VREvent_ButtonUntouch:
            controller.is_dragging = False

    def _compute_controllers_transform(self):
        tx1 = self.right_controller.check_drag(renderer.poses)
        tx2 = self.left_controller.check_drag(renderer.poses)
        result =glmatrix.identity()
        translation = None
        if tx1 is None and tx2 is None:
            result = None # No dragging this time
        elif tx1 is not None and tx2 is not None:
            # TODO - combined transform
            # Translate to average of two translations
            translation = 0.5 * (tx1 + tx2)
            # obj.model_matrix *= tx
            # TODO - scale
            mat_left = self.left_controller.current_pose.mDeviceToAbsoluteTracking.m
            mat_right = self.right_controller.current_pose.mDeviceToAbsoluteTracking.m
            pos_left = numpy.array([mat_left[i][3] for i in range(3)])
            pos_right = numpy.array([mat_right[i][3] for i in range(3)])
            between = pos_left - pos_right
            mag1 = numpy.dot(between, between)
            #
            dpos_left = tx2
            dpos_right = tx1
            between0 = between - dpos_left + dpos_right
            mag0 = numpy.dot(between0, between0)
            if mag0 > 0:
                scale = pow(mag1/mag0, 0.5)
                # print("%0.6f" % scale)
                ts = glmatrix.scale(scale)
                orig = 0.5 * (pos_left + pos_right - 0.5 * dpos_left - 0.5 * dpos_right)
                to = glmatrix.translate(orig)
                ts = to.I * ts * to
                result *= ts
            #
            result *= glmatrix.translate(translation)
        elif tx1 is not None:
            translation = tx1
            result *= glmatrix.translate(tx1)
        else:
            translation = tx2
            result *= glmatrix.translate(tx2)

        if translation is not None:
            # Remember translation history
            time_stamp = time.time()
            self.translation_history.append( (translation, time_stamp,) )
            while len(self.translation_history) > self.max_history_size:
                self.translation_history.popleft()
        
        return result

if __name__ == "__main__":
    obj = ObjMesh(open("root_997.obj", 'r'))
    # invert up/down, so brain is dorsal-up
    obj.model_matrix *= ((1,0,0,0),
                         (0,-1,0,0),
                         (0,0,-1,0),
                         (-0.5,1.5,0.5,1),
                         )
    # obj = ObjMesh(open("AIv6b_699.obj", 'r'))
    renderer = OpenVrGlRenderer(multisample=2)
    renderer.append(SkyActor())
    # renderer.append(ColorCubeActor())
    controllers = TrackedDevicesActor(renderer.poses)
    controllers.show_controllers_only = True
    renderer.append(controllers)
    renderer.append(obj)
    renderer.append(FloorActor())
    interactor = SpatialInteractor()
    with GlfwApp(renderer, "mouse brain") as glfwApp:
        while not glfw.window_should_close(glfwApp.window):
            glfwApp.render_scene()
            # Update controller drag state when buttons are pushed
            interactor.update_controller_states()
            # update_scene_geometry(interactor)

