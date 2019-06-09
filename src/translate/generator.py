import inspect
import pkg_resources

from translate.parser import Parser
import translate.model as model


class CTypesGenerator(object):
    @staticmethod
    def generate(declarations, file_out):
        CTypesGenerator.write_preamble(file_out=file_out)
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
            
            
            class OpenVRError(RuntimeError):
                """
                OpenVRError is a custom exception type for when OpenVR functions return a failure code.
                Such a specific exception type allows more precise exception handling that does just raising Exception().
                """
                pass
            
            
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
                print('\n', file=file_out)

        for declaration in declarations:
            if isinstance(declaration, model.IVRClass):
                print(declaration, file=file_out)
                print('\n', file=file_out)

        print('\n', file=file_out)
        print(inspect.cleandoc('''
            ########################
            ### Expose functions ###
            ########################
            
            def _checkInitError(error):
                """
                Replace openvr error return code with a python exception
                """
                if error != VRInitError_None:
                    shutdown()
                    raise OpenVRError("%s (error number %d)" % (getVRInitErrorAsSymbol(error), error))
            
            
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
                shutdownInternal() # OK, this is just like inline definition in openvr.h
        '''), file=file_out)
        print('\n', file=file_out)
        for declaration in declarations:
            if isinstance(declaration, model.Function):
                print(declaration, file=file_out)
                print('\n', file=file_out)
        print('Generate complete')


    @staticmethod
    def write_preamble(file_out):
        preamble = inspect.cleandoc('''
            #!/bin/env python
            
            # Python bindings for OpenVR API version 1.0.11
            # from https://github.com/ValveSoftware/openvr
            # Created Jan 1, 2018 Christopher Bruns
            
            import os
            import platform
            import ctypes
            from ctypes import *
            
            from .version import __version__
            
            
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
            if platform.system() == 'Windows':
                # Add current directory to PATH, so we can load the DLL from right here.
                os.environ['PATH'] += os.pathsep + os.path.dirname(__file__)
            else:
                _openvr_lib_name = os.path.join(os.path.dirname(__file__), _openvr_lib_name)
            
            _openvr = cdll.LoadLibrary(_openvr_lib_name)
            
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


def main():
    file_name1 = 'openvr.h'
    file_string1 = pkg_resources.resource_string(__name__, file_name1)
    declarations = Parser().parse_file(file_name=file_name1, file_string=file_string1)
    generator = CTypesGenerator()
    generator.generate(
        declarations=declarations,
        file_out=open('../openvr/__init__.py', 'w', newline=None),
    )


if __name__ == '__main__':
    main()
