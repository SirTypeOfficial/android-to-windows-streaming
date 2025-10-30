#pragma once

#include <ntddk.h>
#include <windef.h>
#include <ks.h>
#include <ksmedia.h>
#include <ntstrsafe.h>

// GUID for Virtual Camera Device
// {E7B6A5B1-9F3C-4D2E-8A1B-5C3D4E5F6A7B}
DEFINE_GUIDSTRUCT("E7B6A5B1-9F3C-4D2E-8A1B-5C3D4E5F6A7B", VCAM_DEVICE_GUID);
#define VCAM_DEVICE_GUID_DEFINE DEFINE_GUIDNAMED(VCAM_DEVICE_GUID)

// Device and driver tags
#define VCAM_POOL_TAG 'macV'
#define VCAM_DEVICE_NAME L"\\Device\\VirtualCamera"
#define VCAM_SYMBOLIC_LINK L"\\DosDevices\\VirtualCamera"

// Video format constants
#define VCAM_DEFAULT_WIDTH 1920
#define VCAM_DEFAULT_HEIGHT 1080
#define VCAM_DEFAULT_FPS 30

// Supported resolutions
typedef struct _VCAM_RESOLUTION {
    ULONG Width;
    ULONG Height;
} VCAM_RESOLUTION;

static const VCAM_RESOLUTION g_SupportedResolutions[] = {
    { 640, 480 },      // VGA
    { 1280, 720 },     // 720p HD
    { 1920, 1080 }     // 1080p FHD
};

#define VCAM_NUM_RESOLUTIONS (sizeof(g_SupportedResolutions) / sizeof(VCAM_RESOLUTION))

// Frame rates
static const ULONG g_SupportedFrameRates[] = { 30, 60 };
#define VCAM_NUM_FRAMERATES (sizeof(g_SupportedFrameRates) / sizeof(ULONG))

// IOCTL codes
#define IOCTL_VCAM_SEND_FRAME \
    CTL_CODE(FILE_DEVICE_VIDEO, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)

#define IOCTL_VCAM_GET_STATUS \
    CTL_CODE(FILE_DEVICE_VIDEO, 0x801, METHOD_BUFFERED, FILE_READ_ACCESS)

#define IOCTL_VCAM_SET_FORMAT \
    CTL_CODE(FILE_DEVICE_VIDEO, 0x802, METHOD_BUFFERED, FILE_WRITE_ACCESS)

// IOCTL structures
typedef struct _VCAM_FRAME_HEADER {
    ULONG Width;
    ULONG Height;
    ULONG Format;      // GUID index
    ULONG BufferSize;
    LARGE_INTEGER Timestamp;
} VCAM_FRAME_HEADER, *PVCAM_FRAME_HEADER;

typedef struct _VCAM_STATUS {
    BOOLEAN IsStreaming;
    ULONG CurrentWidth;
    ULONG CurrentHeight;
    ULONG CurrentFormat;
    ULONG FramesDelivered;
} VCAM_STATUS, *PVCAM_STATUS;

// Circular buffer for frames
#define VCAM_FRAME_BUFFER_COUNT 5

typedef struct _VCAM_FRAME_BUFFER {
    PUCHAR Data;
    ULONG Size;
    LARGE_INTEGER Timestamp;
    BOOLEAN Valid;
} VCAM_FRAME_BUFFER, *PVCAM_FRAME_BUFFER;

// Device extension
typedef struct _VCAM_DEVICE_EXTENSION {
    PKSDEVICE KsDevice;
    KSPIN_LOCK BufferLock;
    VCAM_FRAME_BUFFER FrameBuffers[VCAM_FRAME_BUFFER_COUNT];
    ULONG CurrentWriteIndex;
    ULONG CurrentReadIndex;
    ULONG TotalFramesReceived;
} VCAM_DEVICE_EXTENSION, *PVCAM_DEVICE_EXTENSION;

// Pin context
typedef struct _VCAM_PIN_CONTEXT {
    PKSPIN Pin;
    ULONG Width;
    ULONG Height;
    GUID Format;
    ULONG FrameRate;
    ULONGLONG FrameNumber;
    LARGE_INTEGER StartTime;
    KSSTATE PreviousState;
} VCAM_PIN_CONTEXT, *PVCAM_PIN_CONTEXT;

// Function declarations
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
);

NTSTATUS VCamDeviceAdd(
    _In_ PKSDEVICE Device
);

NTSTATUS VCamDeviceStart(
    _In_ PKSDEVICE Device,
    _In_ PIRP Irp,
    _In_opt_ PCM_RESOURCE_LIST TranslatedResourceList,
    _In_opt_ PCM_RESOURCE_LIST UntranslatedResourceList
);

VOID VCamDeviceStop(
    _In_ PKSDEVICE Device,
    _In_ PIRP Irp
);

NTSTATUS VCamDispatchCreate(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

NTSTATUS VCamDispatchClose(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

NTSTATUS VCamDispatchIoControl(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

// Filter functions
extern const KSFILTER_DESCRIPTOR VCamFilterDescriptor;

// Pin functions
NTSTATUS VCamPinCreate(
    _In_ PKSPIN Pin,
    _In_ PIRP Irp
);

NTSTATUS VCamPinClose(
    _In_ PKSPIN Pin,
    _In_ PIRP Irp
);

NTSTATUS VCamPinSetDeviceState(
    _In_ PKSPIN Pin,
    _In_ KSSTATE ToState,
    _In_ KSSTATE FromState
);

NTSTATUS VCamPinProcess(
    _In_ PKSPIN Pin
);

NTSTATUS VCamPinIntersectHandler(
    _In_ PVOID Context,
    _In_ PIRP Irp,
    _In_ PKSP_PIN Pin,
    _In_ PKSDATARANGE CallerDataRange,
    _In_ PKSDATARANGE DescriptorDataRange,
    _In_ ULONG BufferSize,
    _Out_opt_ PVOID Data,
    _Out_ PULONG DataSize
);

// Format functions
extern const PKSDATARANGE VCamPinDataRanges[];
extern const ULONG VCamPinDataRangesCount;

NTSTATUS VCamValidateFormat(
    _In_ const KS_DATAFORMAT_VIDEOINFOHEADER* Format
);

// Buffer management
NTSTATUS VCamAllocateFrameBuffers(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension
);

VOID VCamFreeFrameBuffers(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension
);

NTSTATUS VCamStoreFrame(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension,
    _In_ PVCAM_FRAME_HEADER Header,
    _In_ PUCHAR FrameData
);

NTSTATUS VCamGetFrame(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension,
    _Out_ PVCAM_FRAME_BUFFER* FrameBuffer
);

