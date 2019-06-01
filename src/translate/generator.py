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
        print('\n', file=file_out)
        # TODO: enums next...
        for declaration in declarations:
            if isinstance(declaration, model.StructureForwardDeclaration):
                continue
            if isinstance(declaration, model.ConstantDeclaration):
                continue
            print(declaration, file=file_out)

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
        ''')
        print(preamble, file=file_out)


def main():
    file_name1 = 'openvr.h'
    file_string1 = pkg_resources.resource_string(__name__, file_name1)
    declarations = Parser().parse_file(file_name=file_name1, file_string=file_string1)
    generator = CTypesGenerator()
    generator.generate(
        declarations=declarations,
        file_out=open('../openvr/__init__.py', 'w'),
    )


if __name__ == '__main__':
    main()
