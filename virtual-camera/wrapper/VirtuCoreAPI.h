#pragma once

#ifndef VIRTUCORE_API_H
#define VIRTUCORE_API_H

#include <Windows.h>
#include <stdint.h>

#ifdef VIRTUCORE_EXPORTS
#define VIRTUCORE_API __declspec(dllexport)
#else
#define VIRTUCORE_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif

// ================================
// Camera API
// ================================

typedef void* VCAM_HANDLE;

typedef enum {
    VCAM_FORMAT_RGB24 = 0,
    VCAM_FORMAT_NV12 = 1,
    VCAM_FORMAT_YUY2 = 2
} VCAM_FORMAT;

typedef struct {
    BOOL IsStreaming;
    UINT32 Width;
    UINT32 Height;
    VCAM_FORMAT Format;
    UINT32 FramesDelivered;
} VCAM_STATUS;

/**
 * باز کردن اتصال به درایور دوربین مجازی
 * @return Handle به درایور یا NULL در صورت خطا
 */
VIRTUCORE_API VCAM_HANDLE VirtuCore_OpenCamera(void);

/**
 * بستن اتصال به درایور دوربین
 * @param handle Handle دریافتی از OpenCamera
 */
VIRTUCORE_API void VirtuCore_CloseCamera(VCAM_HANDLE handle);

/**
 * ارسال یک فریم تصویر به درایور
 * @param handle Handle دوربین
 * @param buffer بافر حاوی داده تصویر
 * @param width عرض فریم
 * @param height ارتفاع فریم
 * @param format فرمت تصویر (RGB24, NV12, YUY2)
 * @return TRUE در صورت موفقیت، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_SendFrame(
    VCAM_HANDLE handle,
    const BYTE* buffer,
    UINT32 width,
    UINT32 height,
    VCAM_FORMAT format
);

/**
 * دریافت وضعیت درایور دوربین
 * @param handle Handle دوربین
 * @param status پوینتر به ساختار وضعیت
 * @return TRUE در صورت موفقیت، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_GetCameraStatus(
    VCAM_HANDLE handle,
    VCAM_STATUS* status
);

/**
 * تنظیم فرمت دوربین
 * @param handle Handle دوربین
 * @param width عرض فریم
 * @param height ارتفاع فریم  
 * @param format فرمت تصویر
 * @return TRUE در صورت موفقیت، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_SetCameraFormat(
    VCAM_HANDLE handle,
    UINT32 width,
    UINT32 height,
    VCAM_FORMAT format
);

/**
 * بررسی نصب درایور دوربین
 * @return TRUE اگر درایور نصب باشد، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_IsCameraDriverInstalled(void);

// ================================
// Microphone API
// ================================

typedef void* VMIC_HANDLE;

typedef enum {
    VMIC_FORMAT_PCM16 = 0,
    VMIC_FORMAT_PCM24 = 1
} VMIC_FORMAT;

typedef struct {
    UINT32 SampleRate;
    UINT32 Channels;
    VMIC_FORMAT Format;
} VMIC_CONFIG;

/**
 * باز کردن اتصال به درایور میکروفون مجازی
 * @param config کانفیگ میکروفون (sample rate, channels, format)
 * @return Handle به درایور یا NULL در صورت خطا
 */
VIRTUCORE_API VMIC_HANDLE VirtuCore_OpenMicrophone(const VMIC_CONFIG* config);

/**
 * بستن اتصال به درایور میکروفون
 * @param handle Handle دریافتی از OpenMicrophone
 */
VIRTUCORE_API void VirtuCore_CloseMicrophone(VMIC_HANDLE handle);

/**
 * ارسال داده صوتی به میکروفون مجازی
 * @param handle Handle میکروفون
 * @param buffer بافر حاوی sample های صوتی
 * @param sizeBytes اندازه بافر به byte
 * @return TRUE در صورت موفقیت، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_SendAudio(
    VMIC_HANDLE handle,
    const BYTE* buffer,
    UINT32 sizeBytes
);

/**
 * دریافت اطلاعات میکروفون
 * @param handle Handle میکروفون
 * @param config پوینتر به ساختار کانفیگ
 * @return TRUE در صورت موفقیت، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_GetMicrophoneInfo(
    VMIC_HANDLE handle,
    VMIC_CONFIG* config
);

/**
 * بررسی نصب درایور میکروفون
 * @return TRUE اگر درایور نصب باشد، FALSE در غیر این صورت
 */
VIRTUCORE_API BOOL VirtuCore_IsMicrophoneDriverInstalled(void);

// ================================
// Error Handling
// ================================

/**
 * دریافت کد آخرین خطا
 * @return کد خطای Win32
 */
VIRTUCORE_API DWORD VirtuCore_GetLastError(void);

/**
 * دریافت توضیحات آخرین خطا
 * @param buffer بافر برای ذخیره پیام خطا
 * @param bufferSize اندازه بافر
 * @return تعداد کاراکترهای کپی شده
 */
VIRTUCORE_API UINT32 VirtuCore_GetLastErrorMessage(
    WCHAR* buffer,
    UINT32 bufferSize
);

// ================================
// Version Info
// ================================

typedef struct {
    UINT32 Major;
    UINT32 Minor;
    UINT32 Patch;
    const char* BuildDate;
} VIRTUCORE_VERSION;

/**
 * دریافت اطلاعات نسخه DLL
 * @return ساختار حاوی اطلاعات نسخه
 */
VIRTUCORE_API const VIRTUCORE_VERSION* VirtuCore_GetVersion(void);

#ifdef __cplusplus
}
#endif

#endif // VIRTUCORE_API_H

