#pragma once

#include "common.h"
#include "VCamPin.h"

class CVCamFilter : public CSource {
public:
    static CUnknown* WINAPI CreateInstance(LPUNKNOWN pUnk, HRESULT* phr);

private:
    CVCamFilter(LPUNKNOWN pUnk, HRESULT* phr);
};

