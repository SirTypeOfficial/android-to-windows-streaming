#pragma once

#include <ntddk.h>
#include <windef.h>
#include <portcls.h>
#include <ksmedia.h>
#include <ntstrsafe.h>

// GUID for Virtual Microphone Device
// {F7C3A5D2-8E4B-4A1C-9F2D-6E7A8B9C0D1E}
DEFINE_GUIDSTRUCT("F7C3A5D2-8E4B-4A1C-9F2D-6E7A8B9C0D1E", VMIC_DEVICE_GUID);
#define VMIC_DEVICE_GUID_DEFINE DEFINE_GUIDNAMED(VMIC_DEVICE_GUID)

// Pool tags
#define VMIC_POOL_TAG 'cmiV'

// Audio format defaults
#define VMIC_DEFAULT_SAMPLE_RATE 48000
#define VMIC_DEFAULT_BITS_PER_SAMPLE 16
#define VMIC_DEFAULT_CHANNELS 2

// Supported sample rates
static const ULONG g_SupportedSampleRates[] = { 44100, 48000 };
#define VMIC_NUM_SAMPLE_RATES (sizeof(g_SupportedSampleRates) / sizeof(ULONG))

// Supported bit depths
static const ULONG g_SupportedBitDepths[] = { 16, 24 };
#define VMIC_NUM_BIT_DEPTHS (sizeof(g_SupportedBitDepths) / sizeof(ULONG))

// Buffer configuration
#define VMIC_BUFFER_SIZE (48000 * 2 * 2)  // 1 second at 48kHz stereo 16-bit
#define VMIC_NUM_BUFFERS 4

// Pin IDs
typedef enum {
    VMIC_PIN_RENDER_SINK = 0,
    VMIC_PIN_CAPTURE_SOURCE,
    VMIC_PIN_COUNT
} VMIC_PIN_ID;

// Node IDs
typedef enum {
    VMIC_NODE_LOOPBACK = 0,
    VMIC_NODE_COUNT
} VMIC_NODE_ID;

// Adapter context
typedef struct _VMIC_ADAPTER_CONTEXT {
    PDEVICE_OBJECT PhysicalDeviceObject;
    PDEVICE_OBJECT FunctionalDeviceObject;
    PADAPTERCOMMON AdapterCommon;
    BOOLEAN PoweredUp;
} VMIC_ADAPTER_CONTEXT, *PVMIC_ADAPTER_CONTEXT;

// Loopback buffer structure
typedef struct _VMIC_LOOPBACK_BUFFER {
    PUCHAR Buffer;
    ULONG Size;
    ULONG WritePosition;
    ULONG ReadPosition;
    KSPIN_LOCK Lock;
    BOOLEAN Initialized;
} VMIC_LOOPBACK_BUFFER, *PVMIC_LOOPBACK_BUFFER;

// Stream context for both render and capture
typedef struct _VMIC_STREAM_CONTEXT {
    PPORTWAVERTSTREAM PortStream;
    BOOLEAN IsCapture;
    ULONG SampleRate;
    ULONG BitsPerSample;
    ULONG Channels;
    ULONG BufferSize;
    PUCHAR Buffer;
    ULONG CurrentPosition;
    KSSTATE State;
    PVMIC_LOOPBACK_BUFFER LoopbackBuffer;
} VMIC_STREAM_CONTEXT, *PVMIC_STREAM_CONTEXT;

// Miniport context
typedef struct _VMIC_MINIPORT_CONTEXT {
    PMINIPORTWAVERT Miniport;
    VMIC_LOOPBACK_BUFFER LoopbackBuffer;
    PVMIC_STREAM_CONTEXT RenderStream;
    PVMIC_STREAM_CONTEXT CaptureStream;
} VMIC_MINIPORT_CONTEXT, *PVMIC_MINIPORT_CONTEXT;

// Forward declarations
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
);

NTSTATUS VMicAddDevice(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PDEVICE_OBJECT PhysicalDeviceObject
);

VOID VMicUnload(
    _In_ PDRIVER_OBJECT DriverObject
);

NTSTATUS VMicDispatchPnp(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

NTSTATUS VMicDispatchPower(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
);

// Topology functions
extern const PCFILTER_DESCRIPTOR VMicFilterDescriptor;

// WaveRT Miniport functions
NTSTATUS VMicMiniportCreate(
    _Out_ PUNKNOWN* Unknown,
    _In_ REFCLSID ClassId,
    _In_opt_ PUNKNOWN OuterUnknown,
    _In_ POOL_TYPE PoolType
);

// Stream functions
NTSTATUS VMicStreamCreate(
    _In_ PVMIC_MINIPORT_CONTEXT MiniportContext,
    _In_ BOOLEAN IsCapture,
    _In_ PKSDATAFORMAT DataFormat,
    _Out_ PVMIC_STREAM_CONTEXT* StreamContext
);

VOID VMicStreamClose(
    _In_ PVMIC_STREAM_CONTEXT StreamContext
);

NTSTATUS VMicStreamSetState(
    _In_ PVMIC_STREAM_CONTEXT StreamContext,
    _In_ KSSTATE NewState
);

NTSTATUS VMicStreamGetPosition(
    _In_ PVMIC_STREAM_CONTEXT StreamContext,
    _Out_ PULONGLONG Position
);

// Loopback buffer functions
NTSTATUS VMicLoopbackCreate(
    _Out_ PVMIC_LOOPBACK_BUFFER* LoopbackBuffer
);

VOID VMicLoopbackDestroy(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer
);

NTSTATUS VMicLoopbackWrite(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer,
    _In_ PUCHAR Data,
    _In_ ULONG Length
);

NTSTATUS VMicLoopbackRead(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer,
    _Out_ PUCHAR Data,
    _In_ ULONG Length
);

ULONG VMicLoopbackGetAvailableData(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer
);

ULONG VMicLoopbackGetAvailableSpace(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer
);

