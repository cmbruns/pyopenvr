import os
import shutil

# Copy libraries from openvr project
openvr_path = 'C:/Users/cmbruns2/git/openvr'

this_path = os.path.dirname(os.path.abspath(__file__))
pyopenvr_path = os.path.dirname(this_path)

conversions = {
    'bin/win32/openvr_api.dll': 'openvr/libopenvr_api_32.dll',
    'bin/win64/openvr_api.dll': 'openvr/libopenvr_api_64.dll',
    'bin/osx32/libopenvr_api.dylib': 'openvr/libopenvr_api_32.dylib',
    'bin/linux32/libopenvr_api.so': 'openvr/libopenvr_api_32.so',
    'bin/linux64/libopenvr_api.so': 'openvr/libopenvr_api_64.so',
    'headers/openvr.h': 'translate/openvr.h',
    'headers/openvr_capi.h': 'translate/openvr_capi.h',
}

for olib, polib in conversions.items():
    src = f'{openvr_path}/{olib}'
    dst = os.path.join(pyopenvr_path, polib)
    print(src, dst)
    if not os.path.isfile(src):
        raise Exception(f'File does not exist {src}')
    shutil.copyfile(src, dst)
