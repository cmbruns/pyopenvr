#!/bin/env perl

use warnings;
use strict;

my $header_file = "openvr_capi.h";

open my $header_fh, "<", $header_file or die;
open my $translated, ">", "translated.py" or die;

translate_all();

sub translate_all {
	my $header_string = do {
	    local $/ = undef;
	    <$header_fh>;
	};

	# print $header_string;

	write_preamble();

	translate_constants($header_string);

	translate_enums($header_string);

	translate_typedefs($header_string);

	translate_structs($header_string);

	translate_functions($header_string);

	# TODO: translate interface classes
}

sub translate_functions {
	my $header_string = shift;

	print <<EOF;

########################
### Expose functions ###
########################

def _checkInitError(error):
    if error.value != EVRInitError_VRInitError_None.value:
        shutdown()
        raise OpenVRError(getInitErrorAsSymbol(error) + str(error))    

EOF

	# TODO:
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
import ctypes
from ctypes import *

####################################################################
### Load OpenVR shared library, so we can access it using ctypes ###
####################################################################

# Add current directory to PATH, so we can load the DLL from right here.
os.environ['PATH'] = os.path.dirname(__file__) + ';' + os.environ['PATH']
_openvr_windll = windll.openvr_api
_openvr_cdll = cdll.openvr_api
_openvr = _openvr_cdll

EOF
}

sub translate_typedefs {
	my $header_string = shift;
	print <<EOF;

#######################
### Expose Typedefs ###
#######################

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

		$new_type =~ s/^bool$/openvr_bool/;

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

		$struct_or_union = ucfirst($struct_or_union);
		if ($struct_or_union eq "Struct") {
			$struct_or_union = "Structure";
		}

		$struct_name = translate_type($struct_name);

		print "class $struct_name($struct_or_union):\n";
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
				print "        (\"$fn_name\", WINFUNCTYPE(";
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
