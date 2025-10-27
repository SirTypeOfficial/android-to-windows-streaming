#pragma once

#include "common.h"

class SharedMemory {
public:
    SharedMemory();
    ~SharedMemory();

    bool Open(const wchar_t* name, size_t size);
    void Close();
    
    bool ReadFrame(BYTE* buffer, size_t bufferSize);
    bool IsValid() const { return m_hMapFile != nullptr && m_pBuffer != nullptr; }

private:
    HANDLE m_hMapFile;
    LPVOID m_pBuffer;
    size_t m_size;
};

