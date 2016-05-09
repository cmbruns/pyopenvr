project(OpenVrCTests C)

cmake_minimum_required(VERSION 3.5)

# HTC Vive [CMB]
find_path(OPENVR_SDK_PATH
	NAMES 
		headers/openvr.h
	PATHS
		C:/Users/cmbruns/git/openvr
)
find_path(OPENVR_INCLUDE_DIRECTORY
	NAMES
		openvr.h
	PATHS
		${OPENVR_SDK_PATH}/headers
)
find_library(OPENVR_LIBRARY
	NAMES openvr_api
	PATHS "${OPENVR_SDK_PATH}/lib/win32/"
)

include_directories("${OPENVR_INCLUDE_DIRECTORY}")

if(WIN32)
	add_definitions(-D__WIN32)
endif()

add_executable(test_init test_init.c)
target_link_libraries(test_init "${OPENVR_LIBRARY}")

enable_testing()

add_test(test_init test_init)
