#pragma once

#include <windows.h>
#include <streams.h>
#include <initguid.h>

// {E7B6A5B1-9F3C-4D2E-8A1B-5C3D4E5F6A7B}
DEFINE_GUID(CLSID_VirtualCamera,
    0xe7b6a5b1, 0x9f3c, 0x4d2e, 0x8a, 0x1b, 0x5c, 0x3d, 0x4e, 0x5f, 0x6a, 0x7b);

#define VCAM_WIDTH 1920
#define VCAM_HEIGHT 1080
#define VCAM_FPS 30
#define VCAM_BPP 24

#define SHARED_MEMORY_NAME L"VirtualCameraSharedMemory"
#define SHARED_MEMORY_SIZE (VCAM_WIDTH * VCAM_HEIGHT * 3)

extern "C" {
    BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD dwReason, LPVOID lpReserved);
}

