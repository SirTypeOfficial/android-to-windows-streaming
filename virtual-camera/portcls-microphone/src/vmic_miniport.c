#include "../inc/vmic_common.h"

// WaveRT Miniport interface methods
typedef struct _VMIC_MINIPORT {
    IMiniportWaveRT Miniport;
    LONG RefCount;
    PVMIC_MINIPORT_CONTEXT Context;
} VMIC_MINIPORT, *PVMIC_MINIPORT;

// Forward declarations
NTSTATUS NTAPI VMicMiniportQueryInterface(
    _In_ PMINIPORTWAVERT This,
    _In_ REFIID InterfaceId,
    _Out_ PVOID* Interface
);

ULONG NTAPI VMicMiniportAddRef(
    _In_ PMINIPORTWAVERT This
);

ULONG NTAPI VMicMiniportRelease(
    _In_ PMINIPORTWAVERT This
);

NTSTATUS NTAPI VMicMiniportInit(
    _In_ PMINIPORTWAVERT This,
    _In_ PUNKNOWN UnknownAdapter,
    _In_ PRESOURCELIST ResourceList,
    _In_ PPORTWAVERT Port
);

NTSTATUS NTAPI VMicMiniportGetDescription(
    _In_ PMINIPORTWAVERT This,
    _Out_ PPCFILTER_DESCRIPTOR* FilterDescriptor
);

NTSTATUS NTAPI VMicMiniportNewStream(
    _In_ PMINIPORTWAVERT This,
    _Out_ PMINIPORTWAVERTSTREAM* Stream,
    _In_ PPORTWAVERTSTREAM PortStream,
    _In_ ULONG Pin,
    _In_ BOOLEAN Capture,
    _In_ PKSDATAFORMAT DataFormat
);

// Miniport VTable
static IMiniportWaveRTVtbl VMicMiniportVtbl = {
    VMicMiniportQueryInterface,
    VMicMiniportAddRef,
    VMicMiniportRelease,
    VMicMiniportInit,
    VMicMiniportGetDescription,
    NULL,                           // DataRangeIntersection
    VMicMiniportNewStream,
    NULL,                           // GetDeviceDescription
    NULL                            // SetDeviceChannelVolume (optional)
};

// Create miniport instance
NTSTATUS VMicMiniportCreate(
    _Out_ PUNKNOWN* Unknown,
    _In_ REFCLSID ClassId,
    _In_opt_ PUNKNOWN OuterUnknown,
    _In_ POOL_TYPE PoolType
)
{
    PVMIC_MINIPORT miniport;
    PVMIC_MINIPORT_CONTEXT context;
    NTSTATUS status;

    UNREFERENCED_PARAMETER(ClassId);
    UNREFERENCED_PARAMETER(OuterUnknown);

    KdPrint(("VMic: MiniportCreate called\n"));

    // Allocate miniport
    miniport = (PVMIC_MINIPORT)ExAllocatePoolWithTag(
        PoolType,
        sizeof(VMIC_MINIPORT),
        VMIC_POOL_TAG
    );

    if (miniport == NULL) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(miniport, sizeof(VMIC_MINIPORT));

    // Allocate miniport context
    context = (PVMIC_MINIPORT_CONTEXT)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(VMIC_MINIPORT_CONTEXT),
        VMIC_POOL_TAG
    );

    if (context == NULL) {
        ExFreePoolWithTag(miniport, VMIC_POOL_TAG);
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(context, sizeof(VMIC_MINIPORT_CONTEXT));

    // Create loopback buffer
    status = VMicLoopbackCreate(&context->LoopbackBuffer);
    if (!NT_SUCCESS(status)) {
        ExFreePoolWithTag(context, VMIC_POOL_TAG);
        ExFreePoolWithTag(miniport, VMIC_POOL_TAG);
        return status;
    }

    // Initialize miniport
    miniport->Miniport.lpVtbl = &VMicMiniportVtbl;
    miniport->RefCount = 1;
    miniport->Context = context;
    context->Miniport = (PMINIPORTWAVERT)miniport;

    *Unknown = (PUNKNOWN)miniport;

    KdPrint(("VMic: Miniport created successfully\n"));
    return STATUS_SUCCESS;
}

// IUnknown methods
NTSTATUS NTAPI VMicMiniportQueryInterface(
    _In_ PMINIPORTWAVERT This,
    _In_ REFIID InterfaceId,
    _Out_ PVOID* Interface
)
{
    PVMIC_MINIPORT miniport = (PVMIC_MINIPORT)This;

    if (IsEqualGUID(InterfaceId, &IID_IUnknown) ||
        IsEqualGUID(InterfaceId, &IID_IMiniport) ||
        IsEqualGUID(InterfaceId, &IID_IMiniportWaveRT)) {
        *Interface = This;
        VMicMiniportAddRef(This);
        return STATUS_SUCCESS;
    }

    *Interface = NULL;
    return STATUS_INVALID_PARAMETER;
}

ULONG NTAPI VMicMiniportAddRef(
    _In_ PMINIPORTWAVERT This
)
{
    PVMIC_MINIPORT miniport = (PVMIC_MINIPORT)This;
    return InterlockedIncrement(&miniport->RefCount);
}

ULONG NTAPI VMicMiniportRelease(
    _In_ PMINIPORTWAVERT This
)
{
    PVMIC_MINIPORT miniport = (PVMIC_MINIPORT)This;
    LONG refCount;

    refCount = InterlockedDecrement(&miniport->RefCount);

    if (refCount == 0) {
        if (miniport->Context != NULL) {
            if (miniport->Context->LoopbackBuffer.Initialized) {
                VMicLoopbackDestroy(&miniport->Context->LoopbackBuffer);
            }
            ExFreePoolWithTag(miniport->Context, VMIC_POOL_TAG);
        }
        ExFreePoolWithTag(miniport, VMIC_POOL_TAG);
    }

    return refCount;
}

// IMiniportWaveRT methods
NTSTATUS NTAPI VMicMiniportInit(
    _In_ PMINIPORTWAVERT This,
    _In_ PUNKNOWN UnknownAdapter,
    _In_ PRESOURCELIST ResourceList,
    _In_ PPORTWAVERT Port
)
{
    UNREFERENCED_PARAMETER(This);
    UNREFERENCED_PARAMETER(UnknownAdapter);
    UNREFERENCED_PARAMETER(ResourceList);
    UNREFERENCED_PARAMETER(Port);

    KdPrint(("VMic: MiniportInit called\n"));

    return STATUS_SUCCESS;
}

NTSTATUS NTAPI VMicMiniportGetDescription(
    _In_ PMINIPORTWAVERT This,
    _Out_ PPCFILTER_DESCRIPTOR* FilterDescriptor
)
{
    UNREFERENCED_PARAMETER(This);

    KdPrint(("VMic: MiniportGetDescription called\n"));

    *FilterDescriptor = (PPCFILTER_DESCRIPTOR)&VMicFilterDescriptor;

    return STATUS_SUCCESS;
}

NTSTATUS NTAPI VMicMiniportNewStream(
    _In_ PMINIPORTWAVERT This,
    _Out_ PMINIPORTWAVERTSTREAM* Stream,
    _In_ PPORTWAVERTSTREAM PortStream,
    _In_ ULONG Pin,
    _In_ BOOLEAN Capture,
    _In_ PKSDATAFORMAT DataFormat
)
{
    PVMIC_MINIPORT miniport = (PVMIC_MINIPORT)This;
    PVMIC_STREAM_CONTEXT streamContext;
    NTSTATUS status;

    KdPrint(("VMic: MiniportNewStream called (Pin=%d, Capture=%d)\n", Pin, Capture));

    // Validate pin
    if (Pin >= VMIC_PIN_COUNT) {
        return STATUS_INVALID_PARAMETER;
    }

    // Create stream
    status = VMicStreamCreate(
        miniport->Context,
        Capture,
        DataFormat,
        &streamContext
    );

    if (!NT_SUCCESS(status)) {
        KdPrint(("VMic: Failed to create stream: 0x%08X\n", status));
        return status;
    }

    streamContext->PortStream = PortStream;

    // Store stream reference
    if (Capture) {
        miniport->Context->CaptureStream = streamContext;
    }
    else {
        miniport->Context->RenderStream = streamContext;
    }

    *Stream = (PMINIPORTWAVERTSTREAM)streamContext;

    KdPrint(("VMic: Stream created successfully\n"));
    return STATUS_SUCCESS;
}

