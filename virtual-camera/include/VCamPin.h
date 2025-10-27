#pragma once

#include "common.h"
#include "SharedMemory.h"

class CVCamPin : public CSourceStream {
public:
    CVCamPin(HRESULT* phr, CSource* pFilter);
    ~CVCamPin();

    HRESULT FillBuffer(IMediaSample* pSample);
    HRESULT DecideBufferSize(IMemAllocator* pAlloc, ALLOCATOR_PROPERTIES* pRequest);
    HRESULT GetMediaType(int iPosition, CMediaType* pmt);
    HRESULT SetMediaType(const CMediaType* pmt);
    HRESULT CheckMediaType(const CMediaType* pmt);
    
    STDMETHODIMP Notify(IBaseFilter* pSelf, Quality q) {
        return E_NOTIMPL;
    }

private:
    SharedMemory m_sharedMemory;
    REFERENCE_TIME m_rtFrameLength;
    CCritSec m_cSharedState;
    int m_iFrameNumber;
};

