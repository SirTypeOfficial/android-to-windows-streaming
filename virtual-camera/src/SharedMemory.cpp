#include "SharedMemory.h"

SharedMemory::SharedMemory()
    : m_hMapFile(nullptr)
    , m_pBuffer(nullptr)
    , m_size(0)
{
}

SharedMemory::~SharedMemory()
{
    Close();
}

bool SharedMemory::Open(const wchar_t* name, size_t size)
{
    Close();

    m_hMapFile = CreateFileMappingW(
        INVALID_HANDLE_VALUE,
        nullptr,
        PAGE_READWRITE,
        0,
        static_cast<DWORD>(size),
        name
    );

    if (m_hMapFile == nullptr)
    {
        return false;
    }

    m_pBuffer = MapViewOfFile(
        m_hMapFile,
        FILE_MAP_READ,
        0,
        0,
        size
    );

    if (m_pBuffer == nullptr)
    {
        CloseHandle(m_hMapFile);
        m_hMapFile = nullptr;
        return false;
    }

    m_size = size;
    return true;
}

void SharedMemory::Close()
{
    if (m_pBuffer != nullptr)
    {
        UnmapViewOfFile(m_pBuffer);
        m_pBuffer = nullptr;
    }

    if (m_hMapFile != nullptr)
    {
        CloseHandle(m_hMapFile);
        m_hMapFile = nullptr;
    }

    m_size = 0;
}

bool SharedMemory::ReadFrame(BYTE* buffer, size_t bufferSize)
{
    if (!IsValid() || buffer == nullptr || bufferSize < m_size)
    {
        return false;
    }

    memcpy(buffer, m_pBuffer, m_size);
    return true;
}

