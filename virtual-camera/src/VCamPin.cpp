#include "VCamPin.h"
#include <dvdmedia.h>

CVCamPin::CVCamPin(HRESULT* phr, CSource* pFilter)
    : CSourceStream(NAME("Virtual Camera Pin"), phr, pFilter, L"Output")
    , m_iFrameNumber(0)
{
    m_rtFrameLength = UNITS / VCAM_FPS;
    
    if (!m_sharedMemory.Open(SHARED_MEMORY_NAME, SHARED_MEMORY_SIZE))
    {
        *phr = E_FAIL;
    }
}

CVCamPin::~CVCamPin()
{
    m_sharedMemory.Close();
}

HRESULT CVCamPin::FillBuffer(IMediaSample* pSample)
{
    BYTE* pData;
    HRESULT hr = pSample->GetPointer(&pData);
    if (FAILED(hr))
    {
        return hr;
    }

    long lDataLen = pSample->GetSize();
    
    if (m_sharedMemory.IsValid())
    {
        if (!m_sharedMemory.ReadFrame(pData, lDataLen))
        {
            ZeroMemory(pData, lDataLen);
        }
    }
    else
    {
        ZeroMemory(pData, lDataLen);
    }

    REFERENCE_TIME rtStart = m_iFrameNumber * m_rtFrameLength;
    REFERENCE_TIME rtStop = rtStart + m_rtFrameLength;
    
    pSample->SetTime(&rtStart, &rtStop);
    pSample->SetSyncPoint(TRUE);
    
    m_iFrameNumber++;
    
    return S_OK;
}

HRESULT CVCamPin::DecideBufferSize(IMemAllocator* pAlloc, ALLOCATOR_PROPERTIES* pRequest)
{
    CAutoLock cAutoLock(m_pFilter->pStateLock());
    
    HRESULT hr;
    ALLOCATOR_PROPERTIES Actual;

    pRequest->cBuffers = 1;
    pRequest->cbBuffer = VCAM_WIDTH * VCAM_HEIGHT * 3;

    hr = pAlloc->SetProperties(pRequest, &Actual);
    if (FAILED(hr))
    {
        return hr;
    }

    if (Actual.cbBuffer < pRequest->cbBuffer)
    {
        return E_FAIL;
    }

    return S_OK;
}

HRESULT CVCamPin::GetMediaType(int iPosition, CMediaType* pmt)
{
    if (iPosition < 0)
    {
        return E_INVALIDARG;
    }

    if (iPosition > 0)
    {
        return VFW_S_NO_MORE_ITEMS;
    }

    VIDEOINFO* pvi = (VIDEOINFO*)pmt->AllocFormatBuffer(sizeof(VIDEOINFO));
    if (pvi == nullptr)
    {
        return E_OUTOFMEMORY;
    }

    ZeroMemory(pvi, sizeof(VIDEOINFO));

    pvi->bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    pvi->bmiHeader.biWidth = VCAM_WIDTH;
    pvi->bmiHeader.biHeight = VCAM_HEIGHT;
    pvi->bmiHeader.biPlanes = 1;
    pvi->bmiHeader.biBitCount = VCAM_BPP;
    pvi->bmiHeader.biCompression = BI_RGB;
    pvi->bmiHeader.biSizeImage = GetBitmapSize(&pvi->bmiHeader);
    
    pvi->AvgTimePerFrame = m_rtFrameLength;

    pmt->SetType(&MEDIATYPE_Video);
    pmt->SetFormatType(&FORMAT_VideoInfo);
    pmt->SetTemporalCompression(FALSE);
    pmt->SetSubtype(&MEDIASUBTYPE_RGB24);
    pmt->SetSampleSize(pvi->bmiHeader.biSizeImage);

    return S_OK;
}

HRESULT CVCamPin::SetMediaType(const CMediaType* pmt)
{
    HRESULT hr = CSourceStream::SetMediaType(pmt);
    return hr;
}

HRESULT CVCamPin::CheckMediaType(const CMediaType* pmt)
{
    if (*pmt->Type() != MEDIATYPE_Video)
    {
        return E_INVALIDARG;
    }

    if (*pmt->Subtype() != MEDIASUBTYPE_RGB24)
    {
        return E_INVALIDARG;
    }

    if (*pmt->FormatType() != FORMAT_VideoInfo)
    {
        return E_INVALIDARG;
    }

    VIDEOINFO* pvi = (VIDEOINFO*)pmt->Format();
    if (pvi == nullptr)
    {
        return E_INVALIDARG;
    }

    if (pvi->bmiHeader.biWidth != VCAM_WIDTH || 
        abs(pvi->bmiHeader.biHeight) != VCAM_HEIGHT)
    {
        return E_INVALIDARG;
    }

    return S_OK;
}

