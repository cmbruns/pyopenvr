#!/bin/env perl

use warnings;
use strict;

my $header_file = "openvr_capi.h";
open my $header_fh, "<", $header_file or die;
my $header_string = do {
    local $/ = undef;
    <$header_fh>;
};
close $header_fh;

my $cppheader_file = "openvr.h";
open my $cppheader_fh, "<", $cppheader_file or die;
my $cppheader_string = do {
    local $/ = undef;
    <$cppheader_fh>;
};
close $cppheader_fh;

open my $translated, ">", "translated.py" or die;

translate_all();

sub translate_all {

    write_preamble();

    translate_constants($header_string);

    translate_enums($header_string);

    translate_typedefs($header_string);

    translate_structs($header_string);

    translate_functions($header_string);

}

sub translate_functions {
    my $header_string = shift;

    print <<EOF;

########################
### Expose functions ###
########################

def _checkInitError(error):
    if error.value != VRInitError_None.value:
        shutdown()
        raise OpenVRError(getInitErrorAsSymbol(error) + str(error))    


_openvr.VR_GetGenericInterface.restype = c_void_p
_openvr.VR_GetGenericInterface.argtypes = [c_char_p, POINTER(EVRInitError)]
def getGenericInterface(interfaceVersion):
    error = EVRInitError()
    ptr = _openvr.VR_GetGenericInterface(interfaceVersion, byref(error))
    _checkInitError(error)
    return ptr


_openvr.VR_GetVRInitErrorAsSymbol.restype = c_char_p
_openvr.VR_GetVRInitErrorAsSymbol.argtypes = [EVRInitError]
def getInitErrorAsSymbol(error):
    return _openvr.VR_GetVRInitErrorAsSymbol(error)


_openvr.VR_InitInternal.restype = c_uint32
_openvr.VR_InitInternal.argtypes = [POINTER(EVRInitError), EVRApplicationType]
# Copying VR_Init inline implementation from https://github.com/ValveSoftware/openvr/blob/master/headers/openvr.h
# and from https://github.com/phr00t/jMonkeyVR/blob/master/src/jmevr/input/OpenVR.java
def init(applicationType):
    """
    Finds the active installation of the VR API and initializes it. The provided path must be absolute
    or relative to the current working directory. These are the local install versions of the equivalent
    functions in steamvr.h and will work without a local Steam install.
    
    This path is to the "root" of the VR API install. That's the directory with
    the "drivers" directory and a platform (i.e. "win32") directory in it, not the directory with the DLL itself.
    """
    eError = EVRInitError()
    _vr_token = _openvr.VR_InitInternal(byref(eError), applicationType)
    _checkInitError(eError)
    # Retrieve "System" API
    return IVRSystem()


_openvr.VR_IsHmdPresent.restype = openvr_bool
_openvr.VR_IsHmdPresent.argtypes = []
def isHmdPresent():
    """
    Returns true if there is an HMD attached. This check is as lightweight as possible and
    can be called outside of VR_Init/VR_Shutdown. It should be used when an application wants
    to know if initializing VR is a possibility but isn't ready to take that step yet.   
    """
    return _openvr.VR_IsHmdPresent()


_openvr.VR_IsInterfaceVersionValid.restype = openvr_bool
_openvr.VR_IsInterfaceVersionValid.argtypes = [c_char_p]
def isInterfaceVersionValid(version):
    return _openvr.VR_IsInterfaceVersionValid(version)


_openvr.VR_IsRuntimeInstalled.restype = openvr_bool
_openvr.VR_IsRuntimeInstalled.argtypes = []
def isRuntimeInstalled():
    """
    Returns true if the OpenVR runtime is installed.
    """
    return _openvr.VR_IsRuntimeInstalled()


_openvr.VR_RuntimePath.restype = c_char_p
_openvr.VR_RuntimePath.argtypes = []
def runtimePath():
    """
    Returns where the OpenVR runtime is installed.
    """
    return _openvr.VR_RuntimePath()


_openvr.VR_ShutdownInternal.restype = None
_openvr.VR_ShutdownInternal.argtypes = []
def shutdown():
    """
    unloads vrclient.dll. Any interface pointers from the interface are
    invalid after this point
    """
    _openvr.VR_ShutdownInternal() # OK, this is just like inline definition in openvr.h


_vr_token = c_uint32()

EOF

}

sub translate_constants
{
    print <<EOF;

########################
### Expose constants ###
########################

EOF
    my $header_string = shift;
    while ($header_string =~ m/
        \nstatic\sconst\s(?:[^\n]+)\s(\S+)\s=\s(\S+);
        /xg) 
    {
        my $var = $1;
        my $val = $2;

        # explicit byte strings, for compatibility with python 3
        $val =~ s/^"/b"/;

        print "$var = $val\n";
    }
}

sub write_preamble
{
    print <<EOF;
#!/bin/env python

# Python bindings for OpenVR API version 0.9.20
# from https://github.com/ValveSoftware/openvr
# Created May 7, 2016 Christopher Bruns

import os
import platform
import ctypes
from ctypes import *

from .version import __version__

####################################################################
### Load OpenVR shared library, so we can access it using ctypes ###
####################################################################

# Detect 32-bit vs 64-bit python
if sizeof(c_void_p) == 4:
    _openvr_lib_name = "openvr_api_32"
else:
    _openvr_lib_name = "openvr_api_64"

# Add current directory to PATH, so we can load the DLL from right here.
os.environ['PATH'] += os.pathsep + os.path.dirname(__file__)
_openvr = cdll.LoadLibrary(_openvr_lib_name)

# Function pointer table calling convention
if platform.system() == 'Windows':
    OPENVR_FNTABLE_CALLTYPE = WINFUNCTYPE # __stdcall in openvr_capi.h
else:
    OPENVR_FNTABLE_CALLTYPE = CFUNCTYPE # __cdecl

EOF
}

sub translate_typedefs {
    my $header_string = shift;
    print <<EOF;

#######################
### Expose Typedefs ###
#######################

# Use c_ubyte instead of c_char, for better compatibility with Python True/False
openvr_bool = c_ubyte

EOF
    while ($header_string =~ m/
        typedef\s+ # typedef keyword
        (\S[^;{}]*\S) # existing type name
        \s+(\S+) # new type name
        \s*;
        /gx)
    {
        my $original_type = $1;
        my $new_type = $2;

        if ($new_type =~ m/^bool$/) {
            next; # skip bool definition, in favor of hard-coded version above
        }

        $original_type = translate_type($original_type);
        print "$new_type = $original_type\n";
    }
}

sub translate_enums {
    my $header_string = shift;

    print <<EOF;

#############################
### Expose enum constants ###
#############################

ENUM_TYPE = c_uint32

EOF

    # First pass - sanity check total enum count
    my $enum_count = 0;
    while ($header_string =~ m/typedef enum/g) {
        $enum_count += 1;
    }
    # print $enum_count, "\n";

    # Second pass - full parse of enums
    my $enum_count2 = 0;
    while ($header_string =~ m/
        typedef\s+enum
        \s+
        (\S+)
        \s*
        {\s*
        ([^}]*)
        }\s*
        [^;]*
        ;
        /gx) 
    {
        my $enum_name1 = $1;
        my $enum_values = $2;

        print "$enum_name1 = ENUM_TYPE\n";

        my @vals = split "\n", $enum_values;
        foreach my $val (@vals) {
            $val =~ s/,\s*$//; # remove trailing comma
            $val =~ s/^\s*//; # remove leading space
            $val =~ s/\s*$//; # remove trailing space
            die $val unless $val =~ m/(\S+) = (\S+)/;
            my $item = $1;
            my $value = $2;
            if ($enum_name1 !~ /EVRNotificationStyle|VROverlayFlags|VROverlayInputMethod|ChaperoneCalibrationState|EChaperoneConfigFile/) 
            {
            	$item =~ s/^${enum_name1}_//; # strip outer enum name from value
            }
            print "$item = ENUM_TYPE($value)\n"
        }
        print "\n";

        $enum_count2 += 1;
    }
    # print $enum_count2, "\n";

}

sub translate_structs {
    my $header_string = shift;

    print <<EOF;

######################
### Expose classes ###
######################

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


EOF
    # sanity check total struct count
    my $struct_count = 0;
    while ($header_string =~ m/\b(?:struct|union)\b/g)
    {
        $struct_count += 1;
    }
    # print $struct_count, "\n";

    # Second pass actually parses the struct
    my $struct_count2 = 0;
    while ($header_string =~ m/
        (?<=\n) # beginning of a line
        (?:\s*typedef\s+)? # optional "typedef"
        \s*\b(struct|union)\b\s+ # struct or union
        (\b\S+\b)? # (initial) name of struct
        \s*{ # open brace
        ([^}]*) # struct contents
        }\s* # close brace
        (\S+)? # typedefed name
        \s*;
        /gx)
    {
        $struct_count2 += 1;
        # print $1, "\n";

        my $struct_or_union = $1;
        my $struct_name = $2;
        my $struct_contents = $3;

        $struct_name = $4 unless defined $struct_name;

        my $base = $struct_or_union;

        $base = ucfirst($base);
        if ($base eq "Struct") {
            $base = "Structure";
        }

        $struct_name = translate_type($struct_name);

        # Add special methods to vector classes
        if ($struct_name =~ m/^HmdVector/) {
            $base = "_VectorMixin, $base";
        }
        if ($struct_name =~ m/^HmdMatrix/) {
            $base = "_MatrixMixin, $base";
        }

        print "class $struct_name($base):\n";
        print "    _fields_ = [\n";
        my @fields = split('\n', $struct_contents);
        # print $#fields, "\n";
        foreach my $field (@fields) {
            # TODO: For now I'm ignoring everything that's not a function pointer
            if ($field =~ m/OPENVR_FNTABLE_CALLTYPE/) 
            { # this member is a function pointer
                die unless $field =~ m/
                    ^\s*
                    (\S.*\S) # return type
                    \s*\(OPENVR_FNTABLE_CALLTYPE\s+\*
                    (\w+) # function name
                    \)\(
                    ([^)]*) # function arguments
                    \)
                    /x;

                my $return_type = $1;
                my $fn_name = $2;
                my $fn_args0 = $3;

                my @fn_args = ();
                # "first" argument is the return type
                push @fn_args, translate_type($return_type);
                foreach my $arg (split ",", $fn_args0) {
                    $arg =~ s/\s+\S+\s*$//;
                    push @fn_args, translate_type($arg);
                }

                $fn_name = lcfirst($fn_name); # first character lower case for python functions
                print "        (\"$fn_name\", OPENVR_FNTABLE_CALLTYPE(";
                print join ", ", @fn_args;
                print ")),\n";
            }
            else { # not a function pointer
                # print $field, "\n";
                $field =~ s/;.*$//; # remove trailing semicolon and comment
                $field =~ s!//.*!!; # remove pure comment line
                $field =~ s/^\s*//; # remove leading space
                $field =~ s/\s*$//; # remove trailing space
                next unless $field =~ m/\S/;
                die $field unless $field =~ m/^(\S.*\S)\s+(\S+)$/;
                my $type = $1;
                my $name = $2;

                $type = translate_type($type);

                # Process square brackets for array types
                # A) Outer final set of square brackets
                if ( $name =~ /
                    (.*) # actual name
                    \[([^\]]+)\] # something in brackets
                $/x ) 
                {
                    $name = $1;
                    $type = "$type * $2";
                }
                # B) Inner initial set of square brackets (for 2D arrays)
                if ( $name =~ /
                    (.*) # actual name
                    \[([^\]]+)\] # something in brackets
                $/x ) 
                {
                    $name = $1;
                    $type = "($type) * $2";
                }

                print "        (\"$name\", $type),\n"
            }
        }
        print "    ]\n\n\n";

        # Create a SECOND class definition for the foo_FnTable structs,
        # this time with a user-quality interface

        if ($struct_name =~ m/^(\S+)_FnTable$/) 
        {
            my $interface_name = $1;

            # Create special interface class, e.g. IVRSystem, based on IVRSystem_FnTable
            print <<EOF;
class $interface_name(object):
    def __init__(self):
        version_key = ${interface_name}_Version
        if not isInterfaceVersionValid(version_key):
            _checkInitError(VRInitError_Init_InterfaceNotFound)
        # Thank you lukexi https://github.com/lukexi/openvr-hs/blob/master/cbits/openvr_capi_helper.c#L9
        fn_key = b"FnTable:" + version_key
        fn_type = $struct_name
        fn_table_ptr = cast(getGenericInterface(fn_key), POINTER(fn_type))
        if fn_table_ptr is None:
            raise OpenVRError("Error retrieving VR API for $interface_name")
        self.function_table = fn_table_ptr.contents

EOF

            foreach my $field (@fields) {
                # TODO: For now I'm ignoring everything that's not a function pointer
                if ($field =~ m/OPENVR_FNTABLE_CALLTYPE/) 
                { # this member is a function pointer
                    die unless $field =~ m/
                        ^\s*
                        (\S.*\S) # return type
                        \s*\(OPENVR_FNTABLE_CALLTYPE\s+\*
                        (\w+) # function name
                        \)\(
                        ([^)]*) # function arguments
                        \)
                        /x;

                    my $return_type = $1;
                    my $fn_name = $2;
                    my $fn_args0 = $3;

                    my @arg_types = ();
                    my @call_arg_names = ("self",);
                    my @internal_arg_names = ();
                    my @return_arg_names = ();
                    my @return_arg_types = ();
                    # "first" argument is the return type
                    push @arg_types, translate_type($return_type);

                    if ($return_type !~ m/^void$/) {
                        push @return_arg_names, "result";
                    }


                    foreach my $arg (split ",", $fn_args0) {
                        die unless $arg =~ m/^\s*(.*)\s+(\S+)\s*$/;
                        my $arg_type = $1;
                        my $arg_name = $2;

                        $arg_type = translate_type($arg_type);
                        push @arg_types, $arg_type;
                        if ($arg_type =~ m/^POINTER\((.*)\)/) {
                            my $pointee_type = $1;
                            push @return_arg_types, $pointee_type;
                            push @internal_arg_names, "byref($arg_name)";
                            push @return_arg_names, $arg_name;
                        }
                        else {
                            push @internal_arg_names, $arg_name;
                            push @call_arg_names, $arg_name;
                        }
                    }

                    $fn_name = lcfirst($fn_name); # first character lower case for python functions

                    print "    def $fn_name(";
                    print join ", ", @call_arg_names;
                    print "):\n";
                    print "        fn = self.function_table.$fn_name\n";
                    foreach my $ret_name (@return_arg_names) {
                        next if $ret_name =~ m/^result$/;
                        print "        $ret_name = ";
                        print shift @return_arg_types;
                        print "()\n";
                    }
                    print "        result = fn(";
                    print join ", ", @internal_arg_names;
                    print ")\n";
                    if ($#return_arg_names >= 0) {
                        print "        return ";
                        print join ", ", @return_arg_names;
                        print "\n";
                    }
                    print "\n";
                }
            }

            print "\n\n";
        }

    }
    # print $struct_count2, "\n";    
}

sub translate_type {
    my $type = shift;
    # trim space characters
    $type =~ s/^\s*//;
    $type =~ s/\s*$//;
    # remove const
    $type =~ s/\bconst\s+//g;
    $type =~ s/\s+const\b//g;
    # remove struct
    $type =~ s/\bstruct\s+//g;
    # no implicit int
    $type = "unsigned int" if $type =~ m/^\bunsigned\b$/;
    # abbreviate type
    $type =~ s/8_t\b/8/g; # 
    $type =~ s/16_t\b/16/g; # 
    $type =~ s/32_t\b/32/g; # int32_t => int32
    $type =~ s/64_t\b/64/g; # 
    $type =~ s/\bunsigned\s+/u/g; # unsigned int => uint
    # translate to ctypes type name
    # C strings
    if ($type =~ m/^\s*(?:const\s+)?char\s*\*\s*$/) {
        $type = "c_char_p"; # strings
    }
    $type =~ s/\blong\s+long\b/longlong/;
    if ($type =~ m/^(float|u?int|double|u?char|u?short|u?long)/) {
        $type = "c_$type";
    }
    # remove leading "ovr" or "ovr_"
    if ($type =~ m/^ovr_?(.*)$/) {
        $type = ucfirst($1); # capitalize first letter of types
    }
    # remove leading "VR_"
    $type =~ s/\bVR_//g;
    # $type =~ s/\bVR//g;

    # translate pointer type "*"
    while ($type =~ m/^([^\*]+\S)\s*\*(.*)$/) { # HmdStruct* -> POINTER(HmdStruct)
       $type = "POINTER($1)$2";
    }
    # translate pointer type "ptr"
    while ($type =~ m/^([^\*]+)ptr(?:_t)?(.*)$/) { # uintptr_t -> POINTER(c_uint)
       $type = "POINTER($1)$2";
    }
    # strip "enum"
    $type =~ s/^enum\s+//;

    if ($type =~ /^void$/) {
        $type = "None";
    }

    $type =~ s/\bPOINTER\(void\)/c_void_p/g;

    $type =~ s/\bbool\b/openvr_bool/g;

    return $type;
}
