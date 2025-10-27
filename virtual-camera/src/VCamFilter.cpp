#include "VCamFilter.h"

CVCamFilter::CVCamFilter(LPUNKNOWN pUnk, HRESULT* phr)
    : CSource(NAME("Virtual Camera Filter"), pUnk, CLSID_VirtualCamera)
{
    CVCamPin* pPin = new CVCamPin(phr, this);
    if (pPin == nullptr)
    {
        if (phr)
            *phr = E_OUTOFMEMORY;
    }
}

CUnknown* WINAPI CVCamFilter::CreateInstance(LPUNKNOWN pUnk, HRESULT* phr)
{
    CVCamFilter* pFilter = new CVCamFilter(pUnk, phr);
    if (pFilter == nullptr)
    {
        if (phr)
            *phr = E_OUTOFMEMORY;
    }
    return pFilter;
}

