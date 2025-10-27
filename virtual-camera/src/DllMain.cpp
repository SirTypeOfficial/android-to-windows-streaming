#include "common.h"

HINSTANCE g_hInst = nullptr;

BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID lpReserved)
{
    switch (dwReason)
    {
    case DLL_PROCESS_ATTACH:
        g_hInst = hInstance;
        DisableThreadLibraryCalls(hInstance);
        break;
    
    case DLL_PROCESS_DETACH:
        break;
    }
    
    return TRUE;
}

