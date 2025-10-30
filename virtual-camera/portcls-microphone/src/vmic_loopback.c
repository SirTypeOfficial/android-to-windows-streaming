#include "../inc/vmic_common.h"

// Create loopback buffer
NTSTATUS VMicLoopbackCreate(
    _Out_ PVMIC_LOOPBACK_BUFFER* LoopbackBuffer
)
{
    PVMIC_LOOPBACK_BUFFER buffer;

    KdPrint(("VMic: LoopbackCreate called\n"));

    buffer = (PVMIC_LOOPBACK_BUFFER)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(VMIC_LOOPBACK_BUFFER),
        VMIC_POOL_TAG
    );

    if (buffer == NULL) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(buffer, sizeof(VMIC_LOOPBACK_BUFFER));

    // Allocate buffer memory
    buffer->Buffer = (PUCHAR)ExAllocatePoolWithTag(
        NonPagedPool,
        VMIC_BUFFER_SIZE,
        VMIC_POOL_TAG
    );

    if (buffer->Buffer == NULL) {
        ExFreePoolWithTag(buffer, VMIC_POOL_TAG);
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(buffer->Buffer, VMIC_BUFFER_SIZE);

    // Initialize buffer
    buffer->Size = VMIC_BUFFER_SIZE;
    buffer->WritePosition = 0;
    buffer->ReadPosition = 0;
    KeInitializeSpinLock(&buffer->Lock);
    buffer->Initialized = TRUE;

    *LoopbackBuffer = buffer;

    KdPrint(("VMic: Loopback buffer created (size=%d)\n", VMIC_BUFFER_SIZE));
    return STATUS_SUCCESS;
}

// Destroy loopback buffer
VOID VMicLoopbackDestroy(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer
)
{
    KdPrint(("VMic: LoopbackDestroy called\n"));

    if (LoopbackBuffer == NULL) {
        return;
    }

    if (LoopbackBuffer->Buffer != NULL) {
        ExFreePoolWithTag(LoopbackBuffer->Buffer, VMIC_POOL_TAG);
        LoopbackBuffer->Buffer = NULL;
    }

    LoopbackBuffer->Initialized = FALSE;
}

// Write data to loopback buffer
NTSTATUS VMicLoopbackWrite(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer,
    _In_ PUCHAR Data,
    _In_ ULONG Length
)
{
    KIRQL oldIrql;
    ULONG availableSpace;
    ULONG bytesToEnd;
    ULONG firstChunk;
    ULONG secondChunk;

    if (!LoopbackBuffer->Initialized || Data == NULL || Length == 0) {
        return STATUS_INVALID_PARAMETER;
    }

    KeAcquireSpinLock(&LoopbackBuffer->Lock, &oldIrql);

    // Check available space
    availableSpace = VMicLoopbackGetAvailableSpace(LoopbackBuffer);
    if (Length > availableSpace) {
        // Buffer overflow - advance read position to make room
        LoopbackBuffer->ReadPosition = (LoopbackBuffer->WritePosition + Length) % LoopbackBuffer->Size;
    }

    // Calculate how much to write
    bytesToEnd = LoopbackBuffer->Size - LoopbackBuffer->WritePosition;

    if (Length <= bytesToEnd) {
        // Write in one chunk
        RtlCopyMemory(
            LoopbackBuffer->Buffer + LoopbackBuffer->WritePosition,
            Data,
            Length
        );
    }
    else {
        // Write in two chunks (wrap around)
        firstChunk = bytesToEnd;
        secondChunk = Length - bytesToEnd;

        RtlCopyMemory(
            LoopbackBuffer->Buffer + LoopbackBuffer->WritePosition,
            Data,
            firstChunk
        );

        RtlCopyMemory(
            LoopbackBuffer->Buffer,
            Data + firstChunk,
            secondChunk
        );
    }

    // Advance write position
    LoopbackBuffer->WritePosition = (LoopbackBuffer->WritePosition + Length) % LoopbackBuffer->Size;

    KeReleaseSpinLock(&LoopbackBuffer->Lock, oldIrql);

    return STATUS_SUCCESS;
}

// Read data from loopback buffer
NTSTATUS VMicLoopbackRead(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer,
    _Out_ PUCHAR Data,
    _In_ ULONG Length
)
{
    KIRQL oldIrql;
    ULONG availableData;
    ULONG bytesToEnd;
    ULONG firstChunk;
    ULONG secondChunk;

    if (!LoopbackBuffer->Initialized || Data == NULL || Length == 0) {
        return STATUS_INVALID_PARAMETER;
    }

    KeAcquireSpinLock(&LoopbackBuffer->Lock, &oldIrql);

    // Check available data
    availableData = VMicLoopbackGetAvailableData(LoopbackBuffer);
    if (Length > availableData) {
        // Not enough data - fill with silence
        RtlZeroMemory(Data, Length);
        KeReleaseSpinLock(&LoopbackBuffer->Lock, oldIrql);
        return STATUS_SUCCESS;
    }

    // Calculate how much to read
    bytesToEnd = LoopbackBuffer->Size - LoopbackBuffer->ReadPosition;

    if (Length <= bytesToEnd) {
        // Read in one chunk
        RtlCopyMemory(
            Data,
            LoopbackBuffer->Buffer + LoopbackBuffer->ReadPosition,
            Length
        );
    }
    else {
        // Read in two chunks (wrap around)
        firstChunk = bytesToEnd;
        secondChunk = Length - bytesToEnd;

        RtlCopyMemory(
            Data,
            LoopbackBuffer->Buffer + LoopbackBuffer->ReadPosition,
            firstChunk
        );

        RtlCopyMemory(
            Data + firstChunk,
            LoopbackBuffer->Buffer,
            secondChunk
        );
    }

    // Advance read position
    LoopbackBuffer->ReadPosition = (LoopbackBuffer->ReadPosition + Length) % LoopbackBuffer->Size;

    KeReleaseSpinLock(&LoopbackBuffer->Lock, oldIrql);

    return STATUS_SUCCESS;
}

// Get available data in buffer
ULONG VMicLoopbackGetAvailableData(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer
)
{
    ULONG available;

    if (!LoopbackBuffer->Initialized) {
        return 0;
    }

    if (LoopbackBuffer->WritePosition >= LoopbackBuffer->ReadPosition) {
        available = LoopbackBuffer->WritePosition - LoopbackBuffer->ReadPosition;
    }
    else {
        available = LoopbackBuffer->Size - LoopbackBuffer->ReadPosition + LoopbackBuffer->WritePosition;
    }

    return available;
}

// Get available space in buffer
ULONG VMicLoopbackGetAvailableSpace(
    _In_ PVMIC_LOOPBACK_BUFFER LoopbackBuffer
)
{
    ULONG used;

    if (!LoopbackBuffer->Initialized) {
        return 0;
    }

    used = VMicLoopbackGetAvailableData(LoopbackBuffer);

    return LoopbackBuffer->Size - used - 1; // -1 to distinguish full from empty
}

