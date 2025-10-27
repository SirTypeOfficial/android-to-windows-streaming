#include "common.h"
#include "VCamFilter.h"

const AMOVIESETUP_MEDIATYPE AMSMediaTypesVCam = {
    &MEDIATYPE_Video,
    &MEDIASUBTYPE_RGB24
};

const AMOVIESETUP_PIN AMSPinVCam = {
    L"Output",
    FALSE,
    TRUE,
    FALSE,
    FALSE,
    &CLSID_NULL,
    nullptr,
    1,
    &AMSMediaTypesVCam
};

const AMOVIESETUP_FILTER AMSFilterVCam = {
    &CLSID_VirtualCamera,
    L"Android Virtual Camera",
    MERIT_DO_NOT_USE,
    1,
    &AMSPinVCam
};

CFactoryTemplate g_Templates[] = {
    {
        L"Android Virtual Camera",
        &CLSID_VirtualCamera,
        CVCamFilter::CreateInstance,
        nullptr,
        &AMSFilterVCam
    }
};

int g_cTemplates = sizeof(g_Templates) / sizeof(g_Templates[0]);

STDAPI DllRegisterServer()
{
    return AMovieDllRegisterServer2(TRUE);
}

STDAPI DllUnregisterServer()
{
    return AMovieDllRegisterServer2(FALSE);
}

extern "C" BOOL WINAPI DllEntryPoint(HINSTANCE, ULONG, LPVOID);

BOOL APIENTRY DllMain(HANDLE hModule, DWORD dwReason, LPVOID lpReserved)
{
    return DllEntryPoint((HINSTANCE)(hModule), dwReason, lpReserved);
}

