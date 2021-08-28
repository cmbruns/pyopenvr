import inspect
import pkg_resources
import textwrap

from translate.parser import Parser
import translate.model as model


class CTypesGenerator(object):
    @staticmethod
    def write_preamble(file_out, version):
        preamble = inspect.cleandoc(f'''
            #!/bin/env python
            
            # Unofficial python bindings for OpenVR API version {".".join([str(v) for v in version])}
            # from https://github.com/cmbruns/pyopenvr
            # based on OpenVR C++ API at https://github.com/ValveSoftware/openvr
            
            import os
            import platform
            import ctypes
            from ctypes import *
            
            from .version import __version__
            import openvr.error_code
            from openvr.error_code import OpenVRError
            
            
            class Pack4Structure(Structure):
                _pack_ = 4
            
            
            if sizeof(c_void_p) != 4 and platform.system() in ('Linux', 'Darwin'):
                PackHackStructure = Pack4Structure
            else:
                PackHackStructure = Structure
            
            ################################################################
            # Load OpenVR shared library, so we can access it using ctypes #
            ################################################################
            
            # Detect 32-bit vs 64-bit python
            # Detect platform
            if sizeof(c_void_p) == 4:
                if platform.system() == 'Windows':
                    _openvr_lib_name = "libopenvr_api_32"
                elif platform.system() == 'Linux':
                    _openvr_lib_name = "libopenvr_api_32.so"
                elif platform.system() == 'Darwin':
                    _openvr_lib_name = "libopenvr_api_32.dylib"    
                else:
                    raise ValueError("Libraries not available for this platform: " + platform.system())
            else:
                if platform.system() == 'Windows':
                    _openvr_lib_name = "libopenvr_api_64"
                elif platform.system() == 'Linux':
                    _openvr_lib_name = "libopenvr_api_64.so"
                elif platform.system() == 'Darwin':
                    _openvr_lib_name = "libopenvr_api_32.dylib"  # Universal 32-bit and 64-bit library.
                else:
                    raise ValueError("Libraries not available for this platform: " + platform.system())
            
            # Load library
            _openvr_lib_path = pkg_resources.resource_filename("openvr", _openvr_lib_name)
            _openvr = ctypes.cdll.LoadLibrary(_openvr_lib_path)
            
            # Function pointer table calling convention
            if platform.system() == 'Windows':
                OPENVR_FNTABLE_CALLTYPE = WINFUNCTYPE  # __stdcall in openvr_capi.h
            else:
                OPENVR_FNTABLE_CALLTYPE = CFUNCTYPE  # __cdecl
            
            
            def byref(arg):
                if arg is None:
                    return None
                else:
                    return ctypes.byref(arg)
        ''')
        print(preamble, file=file_out)

    @staticmethod
    def generate_errors(declarations, file_out):
        print(inspect.cleandoc('''
            ############################################
            # Python exceptions for openvr error codes #
            ############################################


            class OpenVRError(Exception):
                """
                OpenVRError is a custom exception type for when OpenVR functions return a failure code.
                Such a specific exception type allows more precise exception handling that does just raising Exception().
                """
                pass
            
            
            class ErrorCode(OpenVRError):
                error_index = dict()
                is_error = True  # FooError_None classes should override this
            
                @classmethod
                def check_error_value(cls, error_value, message=''):
                    error_class = cls.error_index[int(error_value)]
                    if not error_class.is_error:
                        return
                    raise error_class(error_value, message)
                    
                def __init__(this, error_value, message=''):
                    super().__init__(message)
                    this.error_value = error_value
            
            
            class BufferTooSmallError(ErrorCode):
                pass
        '''), file=file_out)
        for declaration in declarations:
            if not isinstance(declaration, model.EnumDecl):
                continue
            nm = declaration.name
            if nm.startswith('EVR'):
                nm = nm[3:]  # Strip 'EVR'
            elif nm.startswith('E'):
                nm = nm[1:]
            else:
                continue
            if not nm.endswith('Error'):
                continue
            error_category = nm
            # General error_code type category class
            print(textwrap.dedent(f'''\
                
                
                class {error_category}(ErrorCode):
                    error_index = dict()
            '''), file=file_out)
            index = ''
            for c in declaration.constants:
                # particular error_code type class
                error_name = c.name
                if error_name.startswith('VR'):
                    error_name = error_name[2:]
                index += f'\n{error_category}.error_index[{c.value}] = {error_name}'
                is_error = True
                if error_name.endswith('_None'):
                    is_error = False
                if error_name.endswith('_Success'):
                    is_error = False
                base_classes = f'{error_category}'
                if error_name.endswith('BufferTooSmall'):
                    base_classes += ', BufferTooSmallError'
                if is_error:
                    print(textwrap.dedent(f'''\
                        
                        class {error_name}({base_classes}):
                            pass
                    '''), file=file_out)
                else:
                    print(textwrap.dedent(f'''\
                        
                        class {error_name}({base_classes}):
                            is_error = False
                    '''), file=file_out)
            print(index, file=file_out)

    @staticmethod
    def generate(declarations, file_out, version):
        CTypesGenerator.write_preamble(file_out=file_out, version=version)
        for declaration in declarations:
            if isinstance(declaration, model.StructureForwardDeclaration):
                print('\n', file=file_out)
                if declaration.docstring is not None:
                    print(f'# {declaration.docstring}', file=file_out)
                print(declaration, file=file_out)
        print('\n', file=file_out)
        print(inspect.cleandoc('''
            ####################
            # Expose constants #
            ####################
        '''), file=file_out)
        print('', file=file_out)
        for declaration in declarations:
            if isinstance(declaration, model.ConstantDeclaration):
                print(declaration, file=file_out)

        print('', file=file_out)
        print(inspect.cleandoc('''
            #########################
            # Expose enum constants #
            #########################
            
            ENUM_TYPE = c_uint32
            ENUM_VALUE_TYPE = int
        '''), file=file_out)
        print('', file=file_out)
        for declaration in declarations:
            if isinstance(declaration, model.EnumDecl):
                print(declaration, file=file_out)
                print('', file=file_out)

        print('', file=file_out)
        print(inspect.cleandoc('''
            ###################
            # Expose Typedefs #
            ###################
            
            # Use c_ubyte instead of c_char, for better compatibility with Python True/False
            openvr_bool = c_ubyte
        '''), file=file_out)
        print('', file=file_out)
        for declaration in declarations:
            if isinstance(declaration, model.Typedef):
                if len(str(declaration)) > 0:
                    print(declaration, file=file_out)

        print('', file=file_out)
        print(inspect.cleandoc('''
            ##################
            # Expose classes #
            ##################
            
            
            # Methods to include in all openvr vector classes
            class _VectorMixin(object):
                def __init__(self, *args):
                    self._setArray(self._getArray().__class__(*args))
            
                def _getArray(self):
                    return self.v
            
                def _setArray(self, array):
                    self.v[:] = array[:]
            
                def __getitem__(self, key):
                    return self._getArray()[key]
            
                def __len__(self):
                    return len(self._getArray())
            
                def __setitem__(self, key, value):
                    self._getArray()[key] = value
            
                def __str__(self):
                    return str(list(self))
            
            
            class _MatrixMixin(_VectorMixin):
                def _getArray(self):
                    return self.m
            
                def _setArray(self, array):
                    self.m[:] = array[:]
            
                def __str__(self):
                    return str(list(list(e) for e in self))
        '''), file=file_out)
        print('\n', file=file_out)
        for declaration in declarations:
            if isinstance(declaration, model.Struct):
                print(declaration, file=file_out)
                print('\n', file=file_out)

        for declaration in declarations:
            if isinstance(declaration, model.COpenVRContext):
                print(declaration, file=file_out)
                print('', file=file_out)

        for declaration in declarations:
            if isinstance(declaration, model.IVRClass):
                print(declaration, file=file_out)
                print('\n', file=file_out)

        print(inspect.cleandoc('''
            ####################
            # Expose functions #
            ####################
            
            def _checkInterfaceVersion(version_key):
                """
                Replace openvr error return code with a python exception
                """
                if isInterfaceVersionValid(version_key):
                    return
                shutdown()
                error = VRInitError_Init_InterfaceNotFound
                msg = f"The installed SteamVR runtime could not provide API version {version_key} requested by pyopenvr. "\\
                      f"You may need to update SteamVR or use an older version of pyopenvr. "\\
                      f"{getVRInitErrorAsSymbol(error)} (error number {error})."
                raise OpenVRError(msg)
            
            
            # Copying VR_Init inline implementation from https://github.com/ValveSoftware/openvr/blob/master/headers/openvr.h
            # and from https://github.com/phr00t/jMonkeyVR/blob/master/src/jmevr/input/OpenVR.java
            def init(applicationType, pStartupInfo=None):
                """
                Finds the active installation of the VR API and initializes it. The provided path must be absolute
                or relative to the current working directory. These are the local install versions of the equivalent
                functions in steamvr.h and will work without a local Steam install.
                
                This path is to the "root" of the VR API install. That's the directory with
                the "drivers" directory and a platform (i.e. "win32") directory in it, not the directory with the DLL itself.
                """
                initInternal2(applicationType, pStartupInfo)
                # Retrieve "System" API
                return VRSystem()
            
            
            def shutdown():
                """
                unloads vrclient.dll. Any interface pointers from the interface are
                invalid after this point
                """
                shutdownInternal()  # OK, this is just like inline definition in openvr.h
        '''), file=file_out)
        for declaration in declarations:
            if isinstance(declaration, model.Function):
                print('\n', file=file_out)
                print(declaration, file=file_out)

        print('Generate complete')


def get_version(declarations):
    version = [0, 0, 0]
    for declaration in declarations:
        if isinstance(declaration, model.ConstantDeclaration):
            n = declaration.name
            if not n.startswith('k_nSteamVRVersion'):
                continue
            if n.endswith('Major'):
                version[0] = int(declaration.value)
            elif n.endswith('Minor'):
                version[1] = int(declaration.value)
            elif n.endswith('Build'):
                version[2] = int(declaration.value)
            else:
                assert False
    return tuple(version)


def main(sub_version=1):
    file_name1 = 'openvr.h'
    file_string1 = pkg_resources.resource_string(__name__, file_name1)
    declarations = Parser().parse_file(file_name=file_name1, file_string=file_string1)
    version = get_version(declarations)
    patch_version = str(version[2]).zfill(2) + str(sub_version).zfill(2)
    py_version = (version[0], version[1], patch_version)
    write_version(
        file_out=open('../openvr/version.py', 'w'),
        version=py_version,
    )
    generator = CTypesGenerator()
    generator.generate(
        declarations=declarations,
        file_out=open('../openvr/__init__.py', 'w', newline=None),
        version=version,
    )
    generator.generate_errors(
        declarations=declarations,
        file_out=open('../openvr/error_code/__init__.py', 'w', newline=None),
    )


def write_version(version, file_out):
    print(inspect.cleandoc(f"""
    # Store the version here so:
    # 1) we don't load dependencies by storing it in __init__.py
    # 2) we can import it in setup.py for the same reason
    # 3) we can import it into your module module
    # http://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package

    __version__ = '{".".join([str(v) for v in version])}'
    """), file=file_out)


if __name__ == '__main__':
    # Increase sub_version for additional python-only releases within a single openvr version
    main(sub_version=1)
