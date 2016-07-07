#!/bin/env perl

use warnings;
use strict;

# Usually pointer arguments are assumed to be return values.
# So here we create a special exception for in/out array arguments
my %inout_array_arguments = ();
$inout_array_arguments{"GetDeviceToAbsoluteTrackingPose"} = ["pTrackedDevicePoseArray","unTrackedDevicePoseArrayCount"];
# print $inout_array_arguments{"GetDeviceToAbsoluteTrackingPose"}[1], "\n";

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

# open my $translated, ">", "translated.py" or die;

my %docstrings = ();

translate_all();

sub translate_all {

    parse_docstrings($cppheader_string);

    write_preamble();

    translate_constants($header_string);

    translate_enums($header_string);

    translate_typedefs($header_string);

    translate_structs($header_string);

    translate_functions($cppheader_string);

}

sub parse_docstrings {
    my $cpp_header_string = shift;

    my $all_comment_regex = 
        '(?:/\*(?:[^*]|(?:\*+[^*/]))*\*+/)|(?://.*)';
        # '\/\*(?:\*[^/]|[^*])*\*\/';
    my $cpp_comment_regex = '(?:\n\s*//[^\n\r]+)+';

    my $doc_comment_regex = '(?:[\n\r]{1,2}[\ \t]*(?:'.${all_comment_regex}.'))+';

    # Class comments as docstrings
    while ($cpp_header_string =~ m!
        (${doc_comment_regex})
        [\n\r]{1,2}[\ \t]*
        (?:class|struct)\s+(\S+) #
        # ( # capture 1
        # (?: # begin multiple comments
        # [\n\r]{1,2}[\ \t]*(?: # comment is first thing on the first line
        # (?:/\*(?:[^*]|(?:\*+[^*/]))*\*+/) # c style comment /* foo */
        # | # "or"
        # (?://.*) # c++ style comment // foo
        # ))+ # multiple comments together
        # ) # end capture 1
        !xg) 
    {
        my $comment = $1;
        my $class_name = $2;

        $class_name = translate_type($class_name);

        $comment = trim_comment($comment);
        $docstrings{$class_name} = $comment;
        # print "$comment\nclass $class_name\n\n\n";
    }

    while ($cpp_header_string =~ m!
        (${doc_comment_regex})
        [\n\r]{1,2}[\ \t]*
        virtual\s+[^(]+\s(\S+)\( # 
        !xg) 
    {
        my $comment = $1;
        my $method_name = $2;

        $comment = trim_comment($comment);
        $method_name =~ s/^\*//;
        $method_name = lcfirst($method_name);

        # print "$comment\n method $method_name\n\n\n";

        $docstrings{$method_name} = $comment;
    }

}

sub trim_comment {
    my $comment = shift;

    $comment =~ s/^\s*//; # trim leading spaces
    $comment =~ s/\s*$//; # trim trailing spaces
    $comment =~ s/[\n\r]+\s*/\n/g; # trim spaces from start of line
    $comment =~ s/^\/+\s?//g; # remove leading slashes
    $comment =~ s/[\n\r]+\/+\s?/\n/g; # remove leading slashes from lines
    $comment =~ s/^\*+\s?//g; # remove leading stars
    $comment =~ s/[\n\r]+\*+\s?/\n/g; # remove leading stars from lines
    $comment =~ s/\/*$//; # remove trailing slashes
    $comment =~ s/\**$//; # remove trailing stars
    $comment =~ s/\n$//; # remove trailing newline
    $comment =~ s/\s*$//; # remove trailing spaces

    return $comment;
}

sub print_docstring
{
    my $key = shift;
    my $indent = shift;

    if (! exists $docstrings{$key}) {
        return; # no docstring for you
    }

    my $comment = $docstrings{$key};
    my @lines = split "\n", $comment;

    if ($#lines > 0) {
        print $indent, '"""', "\n$indent";
        print join "\n$indent", @lines;
        print "\n", $indent, '"""', "\n\n";
    }
    else {
        print $indent, "\"$lines[0]\"\n\n";
    }

}

sub translate_functions {
    my $cppheader_string = shift;

    print <<EOF;

########################
### Expose functions ###
########################

def _checkInitError(error):
    """
    Replace openvr error return code with a python exception
    """
    if error != VRInitError_None:
        shutdown()
        raise OpenVRError("%s (error number %d)" %(getVRInitErrorAsSymbol(error), error))


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
    initInternal(applicationType)
    # Retrieve "System" API
    return VRSystem()


def shutdown():
    """
    unloads vrclient.dll. Any interface pointers from the interface are
    invalid after this point
    """
    shutdownInternal() # OK, this is just like inline definition in openvr.h


EOF

    while ($cppheader_string =~ m!
        # (\n\s*/\*[^\n]* # initial comment line
        # ((?:\n\s*\*[^\n]*\n\s*)* # middle comment lines
        # [^\n]*\*/)?\s* # final comment line
        (\/\*(?:\*[^/]|[^*])*\*\/)?\s*
        \n[\t\ ]*VR_INTERFACE
        ([^;]+)
        ;
        !gx) 
    {
        my $comment = $1;
        my $method_signature = $2;

        # print $method_signature, "\n";
        die $method_signature unless $method_signature =~ m!
        ^\s* # begin with any number of spaces
        (\S.*\S) # return type
        \s* # any number of spaces
        VR_CALLTYPE
        \s+ # one or more spaces
        (\S[^(]+) # function name
        \(\s* # open paren
        (\S[^)]*\S)?
        \s*\) # close paren
        !x;

        my $return_type = $1;
        my $fn_name = $2;
        my $fn_args = $3;

        $fn_args = "" unless defined $fn_args;

        $return_type = translate_type($return_type);
        print "_openvr.$fn_name.restype = $return_type\n";
        print "_openvr.$fn_name.argtypes = [";
        my @arg_types = ();
        my @py_arg_names = ();
        my @arg_names = ();
        my @py_return_val_names = ();
        if ($return_type ne "None") {
            push @py_return_val_names, "result";
        }
        my $error_arg_name = undef;
        foreach my $arg (split ",", $fn_args) {
            die $arg unless $arg =~ m/^\s*(\S.*\S)\s(\S+)\s*$/;
            my $arg_type = $1;
            my $arg_name = $2;

            # Check for pointer * at start of function name
            if ($arg_name =~ m/\*(.*)/) {
                $arg_name = $1;
                $arg_type = "$arg_type *";
            }

            $arg_type = translate_type($arg_type);

            # remove annoying initial "pch", e.g. "pchInterfaceVersion"
            if ($arg_name =~ /^(?:pch|pe)(.*)/) {
                $arg_name = $1;
                $arg_name = lcfirst($arg_name);
            }
            
            # avoid reserved words in argument name
            $arg_name =~ s/^type$/type_/;

            if ($arg_type eq "POINTER\(EVRInitError\)") {
                # Handle error argument specially
                $error_arg_name = $arg_name;
                $arg_name = "byref($arg_name)";
            }
            elsif ($arg_type =~ /^POINTER\(.*\)$/) {
                # Treat pointer arguments as return types
                # TODO: need even more code if this ever happens...
                push @py_return_val_names, $arg_name;
                $arg_name = "byref($arg_name)";
            }
            else {
                push @py_arg_names, $arg_name;
            }

            push @arg_types, $arg_type;
            push @arg_names, $arg_name;
        }
        print join ", ", @arg_types;
        print "]\n";

        my $py_fn_name = $fn_name;
        $py_fn_name =~ s/^VR_//;
        $py_fn_name = lcfirst($py_fn_name);
        print "def $py_fn_name(";
        print join ", ", @py_arg_names;
        print "):\n";

        # Turn the comment into a docstring
        if (defined $comment) {
            $comment =~ s/^\s*\/\**\s*//; # comment open
            $comment =~ s/\s*\*\/\s*//; # comment close
            $comment =~ s/\n\s*\*\s*/\n/g; # comment middle line start
            # print $comment, "\n";
            print "    \"\"\"\n"; # open docstring
            foreach my $comment_line (split "\n", $comment) {
                print "    $comment_line\n";
            }
            print "    \"\"\"\n"; # close docstring
        }

        # Create error object for this function call
        if (defined $error_arg_name) {
            print "    $error_arg_name = EVRInitError()\n";
        }

        print "    "; # indent
        if ($return_type ne "None") { # avoid IDE warning when "result" value is unused
        	print "result = ";
        }
        print "    _openvr.$fn_name(";
        print join ", ", @arg_names;
        print ")\n";

        # Raise exception if error state returned
        if (defined $error_arg_name) {
            print "    _checkInitError(${error_arg_name}.value)\n";
        }
        if ($#py_return_val_names >= 0) {
            print "    return ";
            print join ", ", @py_return_val_names;
            print "\n";
        }

        print "\n\n";

        # print $1, $2, $3, "\n\n";
    }

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
ENUM_VALUE_TYPE = int

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
            print "$item = ENUM_VALUE_TYPE($value)\n"
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
        
        # Special handling of COpenVRContext class
        if ($struct_name =~ m/^COpenVRContext$/) {
        	expose_openvr_context($struct_contents);
        	next;
        }

        # Add special methods to vector classes
        if ($struct_name =~ m/^HmdVector/) {
            $base = "_VectorMixin, $base";
        }
        if ($struct_name =~ m/^HmdMatrix/) {
            $base = "_MatrixMixin, $base";
        }

        print "class $struct_name($base):\n";

        # Maybe include docstring
        print_docstring($struct_name, "    ");

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
                # Iterate over second through nth arguments
                foreach my $arg (split ",", $fn_args0) {
                    die unless $arg =~ m/^\s*(.*\S)\s+(\S+)\s*$/;
                    my $arg_type = $1;
                    my $arg_name = $2;
                    $arg_type = translate_type($arg_type);
                    push @fn_args, $arg_type;
                    # Store inout array argument type for later processing
                    if (exists $inout_array_arguments{$fn_name}) {
                        if ($arg_name eq $inout_array_arguments{$fn_name}[0]) {
                            die $arg_type unless $arg_type =~ /POINTER\((.*)\)/;
                            my $pointee_type = $1;
                            $inout_array_arguments{$fn_name}[2] = $pointee_type;
                        }
                    }

                    # if ($arg_name eq $)
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
            print "class $interface_name(object):\n";
            print_docstring($interface_name, "    ");
            print <<EOF;
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

                    # Hack to reconfigure getDeviceToAbsoluteTrackingPose implementation correct
                    my $array_arg_name = undef;
                    my $array_arg_size = undef;
                    my $array_arg_pointee_type = undef;
                    if (exists $inout_array_arguments{$fn_name}) {
                        $array_arg_name = $inout_array_arguments{$fn_name}[0];
                        $array_arg_size = $inout_array_arguments{$fn_name}[1];
                        $array_arg_pointee_type = $inout_array_arguments{$fn_name}[2];
                    }

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
                        
                        # avoid reserved words in argument name
                        $arg_name =~ s/^type$/type_/;

                        $arg_type = translate_type($arg_type);
                        push @arg_types, $arg_type;
                        if (defined $array_arg_name and $arg_name eq $array_arg_name) {
                            push @internal_arg_names, $arg_name;
                            push @return_arg_names, $arg_name;
                        }
                        # Pointer arguments are assumed to be OUTPUT arguments at this point
                        elsif ($arg_type =~ m/^POINTER\((.*)\)/) {
                            my $pointee_type = $1;
                            push @return_arg_types, $pointee_type;
                            push @internal_arg_names, "byref($arg_name)";
                            # Pointers to primitive types return the .value member
                            if ($pointee_type =~ m/^c_/) {
	                            push @return_arg_names, "${arg_name}.value";
								# print "VALUE ${arg_name}\n";
                            }
                            else {
	                            push @return_arg_names, $arg_name;
                            }
                        }
                        else {
                            push @internal_arg_names, $arg_name;
                            push @call_arg_names, $arg_name;
                        }

                    }
                    # Make the array argument optional and final
                    if (defined $array_arg_name) {
                        push @call_arg_names, "$array_arg_name=None";
                    }

                    $fn_name = lcfirst($fn_name); # first character lower case for python functions

                    print "    def $fn_name(";
                    print join ", ", @call_arg_names;
                    print "):\n";

                    print_docstring($fn_name, "        ");

                    print "        fn = self.function_table.$fn_name\n";
					# Assign local variables for return/out arguments
                    foreach my $ret_name0 (@return_arg_names) {
						my $ret_name = $ret_name0;
                        next if $ret_name =~ m/^result$/;
                        next if defined $array_arg_name and $ret_name eq $array_arg_name; # handled below
                        $ret_name =~ s/\.value$//;
                        print "        $ret_name = ";
                        print shift @return_arg_types;
                        print "()\n";
                    }

                    # Hack to reconfigure getDeviceToAbsoluteTrackingPose implementation correct
                    if (defined $array_arg_name) {
                        print "        if $array_arg_name is None:\n";
                        print "            $array_arg_name = ($array_arg_pointee_type * $array_arg_size)()\n";
                        print "        $array_arg_name = cast($array_arg_name, POINTER($array_arg_pointee_type))\n";
                    }

                    print "        "; # indent
                    if ($return_type !~ m/^void$/) {
                    	# avoid IDE warning when "result"" value is unused
                        print "result = ";
                    }
                    print "fn(";
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

sub expose_openvr_context {
	my $struct_contents = shift;
	my @fields = split('\n', $struct_contents);
	my @context_classes = ();
	foreach my $field (@fields) {
		$field =~ s/^\s*//;
		$field =~ s/\s*$//;
		next unless $field =~ m/\S/;
		# print "# $field #\n";
		# "intptr_t m_pVRChaperoneSetup; // class vr::IVRChaperoneSetup *"
		die $field unless $field =~ m/^intptr_t\s+m_p(VR\S+);/; 
		my $cls_root = $1; # e.g. "VRChaperoneSetup"
		push @context_classes, $cls_root
	}
    # exit(0); # TODO

    print <<EOF;
class COpenVRContext(object):
    def __init__(self):
        self.clear()
        
    def checkClear(self):
        global _vr_token
        if _vr_token != getInitToken():
            self.clear()
            _vr_token = getInitToken()
            
    def clear(self):  
EOF

	# enumerate members to clear in clear method
	foreach my $cls_name (@context_classes) {
		print "        self.m_p$cls_name = None\n";
	}

	# enumerate accessors for each interface class types
	foreach my $cls_name (@context_classes) {
		print <<EOF;

    def $cls_name(self):
        self.checkClear()
        if self.m_p$cls_name is None:
            self.m_p$cls_name = I$cls_name()
        return self.m_p$cls_name
EOF
	}

    print <<EOF;


# Globals for context management
_vr_token = None
_internal_module_context = COpenVRContext()


EOF

	# enumerate global accessors for each interface class type
	foreach my $cls_name (@context_classes) {
		print <<EOF;
def ${cls_name}():
    return _internal_module_context.${cls_name}()

EOF
	}

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
