#include "openvr_capi.h"
#include <stdio.h>

__declspec(dllimport) bool VR_IsHmdPresent();

int main() 
{
    printf("Hello\n");
	if (VR_IsHmdPresent()) {
		return 0;
	}
    return 1;
}
