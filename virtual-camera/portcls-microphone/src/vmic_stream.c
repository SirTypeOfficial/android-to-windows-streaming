#include "../inc/vmic_common.h"

// Stream interface methods
typedef struct _VMIC_STREAM {
    IMiniportWaveRTStream Stream;
    LONG RefCount;
    VMIC_STREAM_CONTEXT Context;
} VMIC_STREAM, *PVMIC_STREAM;

// Forward declarations
NTSTATUS NTAPI VMicStreamQueryInterface(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ REFIID InterfaceId,
    _Out_ PVOID* Interface
);

ULONG NTAPI VMicStreamAddRef(
    _In_ PMINIPORTWAVERTSTREAM This
);

ULONG NTAPI VMicStreamRelease(
    _In_ PMINIPORTWAVERTSTREAM This
);

NTSTATUS NTAPI VMicStreamAllocateAudioBuffer(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ ULONG RequestedSize,
    _Out_ PMDL* AudioBufferMdl,
    _Out_ ULONG* ActualSize,
    _Out_ ULONG* OffsetFromFirstPage,
    _Out_ PULONG CacheType
);

VOID NTAPI VMicStreamFreeAudioBuffer(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ PMDL AudioBufferMdl
);

NTSTATUS NTAPI VMicStreamGetPosition(
    _In_ PMINIPORTWAVERTSTREAM This,
    _Out_ PULONGLONG Position
);

NTSTATUS NTAPI VMicStreamSetState(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ KSSTATE State
);

NTSTATUS NTAPI VMicStreamSetFormat(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ PKSDATAFORMAT DataFormat
);

// Stream VTable
static IMiniportWaveRTStreamVtbl VMicStreamVtbl = {
    VMicStreamQueryInterface,
    VMicStreamAddRef,
    VMicStreamRelease,
    VMicStreamAllocateAudioBuffer,
    VMicStreamFreeAudioBuffer,
    NULL,                               // GetClockRegister
    NULL,                               // GetPositionRegister
    VMicStreamGetPosition,
    VMicStreamSetState,
    VMicStreamSetFormat,
    NULL                                // SetNotificationFrequency
};

// Create stream
NTSTATUS VMicStreamCreate(
    _In_ PVMIC_MINIPORT_CONTEXT MiniportContext,
    _In_ BOOLEAN IsCapture,
    _In_ PKSDATAFORMAT DataFormat,
    _Out_ PVMIC_STREAM_CONTEXT* StreamContext
)
{
    PVMIC_STREAM stream;
    PKSDATAFORMAT_WAVEFORMATEX waveFormat;

    KdPrint(("VMic: StreamCreate called\n"));

    // Allocate stream
    stream = (PVMIC_STREAM)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(VMIC_STREAM),
        VMIC_POOL_TAG
    );

    if (stream == NULL) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(stream, sizeof(VMIC_STREAM));

    // Initialize stream
    stream->Stream.lpVtbl = &VMicStreamVtbl;
    stream->RefCount = 1;
    stream->Context.IsCapture = IsCapture;
    stream->Context.State = KSSTATE_STOP;
    stream->Context.LoopbackBuffer = &MiniportContext->LoopbackBuffer;

    // Extract format information
    waveFormat = (PKSDATAFORMAT_WAVEFORMATEX)DataFormat;
    stream->Context.SampleRate = waveFormat->WaveFormatEx.nSamplesPerSec;
    stream->Context.BitsPerSample = waveFormat->WaveFormatEx.wBitsPerSample;
    stream->Context.Channels = waveFormat->WaveFormatEx.nChannels;

    KdPrint(("VMic: Stream format: %d Hz, %d bits, %d channels\n",
        stream->Context.SampleRate,
        stream->Context.BitsPerSample,
        stream->Context.Channels));

    *StreamContext = &stream->Context;

    return STATUS_SUCCESS;
}

// Close stream
VOID VMicStreamClose(
    _In_ PVMIC_STREAM_CONTEXT StreamContext
)
{
    PVMIC_STREAM stream = CONTAINING_RECORD(StreamContext, VMIC_STREAM, Context);

    KdPrint(("VMic: StreamClose called\n"));

    if (stream->Context.Buffer != NULL) {
        ExFreePoolWithTag(stream->Context.Buffer, VMIC_POOL_TAG);
        stream->Context.Buffer = NULL;
    }

    ExFreePoolWithTag(stream, VMIC_POOL_TAG);
}

// IUnknown methods
NTSTATUS NTAPI VMicStreamQueryInterface(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ REFIID InterfaceId,
    _Out_ PVOID* Interface
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;

    if (IsEqualGUID(InterfaceId, &IID_IUnknown) ||
        IsEqualGUID(InterfaceId, &IID_IMiniportWaveRTStream)) {
        *Interface = This;
        VMicStreamAddRef(This);
        return STATUS_SUCCESS;
    }

    *Interface = NULL;
    return STATUS_INVALID_PARAMETER;
}

ULONG NTAPI VMicStreamAddRef(
    _In_ PMINIPORTWAVERTSTREAM This
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;
    return InterlockedIncrement(&stream->RefCount);
}

ULONG NTAPI VMicStreamRelease(
    _In_ PMINIPORTWAVERTSTREAM This
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;
    LONG refCount;

    refCount = InterlockedDecrement(&stream->RefCount);

    if (refCount == 0) {
        VMicStreamClose(&stream->Context);
    }

    return refCount;
}

// IMiniportWaveRTStream methods
NTSTATUS NTAPI VMicStreamAllocateAudioBuffer(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ ULONG RequestedSize,
    _Out_ PMDL* AudioBufferMdl,
    _Out_ ULONG* ActualSize,
    _Out_ ULONG* OffsetFromFirstPage,
    _Out_ PULONG CacheType
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;
    PUCHAR buffer;
    PMDL mdl;

    KdPrint(("VMic: AllocateAudioBuffer called (size=%d)\n", RequestedSize));

    // Allocate buffer
    buffer = (PUCHAR)ExAllocatePoolWithTag(
        NonPagedPool,
        RequestedSize,
        VMIC_POOL_TAG
    );

    if (buffer == NULL) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(buffer, RequestedSize);

    // Create MDL
    mdl = IoAllocateMdl(buffer, RequestedSize, FALSE, FALSE, NULL);
    if (mdl == NULL) {
        ExFreePoolWithTag(buffer, VMIC_POOL_TAG);
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    MmBuildMdlForNonPagedPool(mdl);

    // Store buffer information
    stream->Context.Buffer = buffer;
    stream->Context.BufferSize = RequestedSize;
    stream->Context.CurrentPosition = 0;

    *AudioBufferMdl = mdl;
    *ActualSize = RequestedSize;
    *OffsetFromFirstPage = 0;
    *CacheType = MmCached;

    KdPrint(("VMic: Audio buffer allocated successfully\n"));
    return STATUS_SUCCESS;
}

VOID NTAPI VMicStreamFreeAudioBuffer(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ PMDL AudioBufferMdl
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;

    KdPrint(("VMic: FreeAudioBuffer called\n"));

    if (AudioBufferMdl != NULL) {
        if (stream->Context.Buffer != NULL) {
            ExFreePoolWithTag(stream->Context.Buffer, VMIC_POOL_TAG);
            stream->Context.Buffer = NULL;
        }
        IoFreeMdl(AudioBufferMdl);
    }
}

NTSTATUS NTAPI VMicStreamGetPosition(
    _In_ PMINIPORTWAVERTSTREAM This,
    _Out_ PULONGLONG Position
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;

    *Position = stream->Context.CurrentPosition;

    return STATUS_SUCCESS;
}

NTSTATUS NTAPI VMicStreamSetState(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ KSSTATE State
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;

    KdPrint(("VMic: SetState called (from %d to %d)\n", stream->Context.State, State));

    // Handle state transition
    if (State == KSSTATE_RUN && stream->Context.State != KSSTATE_RUN) {
        // Starting playback/capture
        KdPrint(("VMic: Starting %s\n", stream->Context.IsCapture ? "capture" : "render"));
        stream->Context.CurrentPosition = 0;

        // If this is render stream, start writing to loopback
        // If this is capture stream, start reading from loopback
    }
    else if (stream->Context.State == KSSTATE_RUN && State != KSSTATE_RUN) {
        // Stopping playback/capture
        KdPrint(("VMic: Stopping %s\n", stream->Context.IsCapture ? "capture" : "render"));
    }

    stream->Context.State = State;

    return VMicStreamSetState(&stream->Context, State);
}

NTSTATUS NTAPI VMicStreamSetFormat(
    _In_ PMINIPORTWAVERTSTREAM This,
    _In_ PKSDATAFORMAT DataFormat
)
{
    PVMIC_STREAM stream = (PVMIC_STREAM)This;
    PKSDATAFORMAT_WAVEFORMATEX waveFormat;

    UNREFERENCED_PARAMETER(stream);
    UNREFERENCED_PARAMETER(DataFormat);

    KdPrint(("VMic: SetFormat called\n"));

    waveFormat = (PKSDATAFORMAT_WAVEFORMATEX)DataFormat;

    // Update format
    stream->Context.SampleRate = waveFormat->WaveFormatEx.nSamplesPerSec;
    stream->Context.BitsPerSample = waveFormat->WaveFormatEx.wBitsPerSample;
    stream->Context.Channels = waveFormat->WaveFormatEx.nChannels;

    return STATUS_SUCCESS;
}

// Stream state management
NTSTATUS VMicStreamSetState(
    _In_ PVMIC_STREAM_CONTEXT StreamContext,
    _In_ KSSTATE NewState
)
{
    UNREFERENCED_PARAMETER(StreamContext);
    UNREFERENCED_PARAMETER(NewState);

    // State management logic
    return STATUS_SUCCESS;
}

NTSTATUS VMicStreamGetPosition(
    _In_ PVMIC_STREAM_CONTEXT StreamContext,
    _Out_ PULONGLONG Position
)
{
    *Position = StreamContext->CurrentPosition;
    return STATUS_SUCCESS;
}

