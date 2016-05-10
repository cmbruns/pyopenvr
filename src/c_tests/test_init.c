#include "openvr_capi.h"
#include <stdio.h>

extern __declspec(dllimport) bool VR_IsHmdPresent();
extern __declspec(dllimport) bool VR_IsRuntimeInstalled();
extern __declspec(dllimport) intptr_t VR_InitInternal(EVRInitError *peError, EVRApplicationType eType);
extern __declspec(dllimport) bool VR_IsInterfaceVersionValid(const char *pchInterfaceVersion);
extern __declspec(dllimport) intptr_t VR_GetGenericInterface(const char *pchInterfaceVersion, EVRInitError *peError);

int main() 
{
	EVRInitError eError;
	struct VR_IVRSystem_FnTable * systemFunctions;
	
	printf("Hello\n");

	if ( ! VR_IsHmdPresent() )
		return 1; // report failure
	if ( ! VR_IsRuntimeInstalled() )
		return 1;
	uint32_t vrToken = VR_InitInternal(&eError, EVRApplicationType_VRApplication_Scene);
	if ( eError != EVRInitError_VRInitError_None )
		return 1;
	if ( ! VR_IsInterfaceVersionValid(IVRSystem_Version) )
		return 1;

	char fnTableName[128];
	int result1 = sprintf(fnTableName, "FnTable:%s", IVRSystem_Version);
	systemFunctions = (struct VR_IVRSystem_FnTable *)
		VR_GetGenericInterface(fnTableName, &eError);

	if (eError != EVRInitError_VRInitError_None)
		return 1;
	if (systemFunctions == NULL)
		return 1;
	bool result2 = systemFunctions->IsDisplayOnDesktop();
	if (result2)
		printf("Display is on desktop\n");
	else
		printf("Display is NOT on desktop\n");

    return 0; // success!
}
