#include "../inc/vcam_common.h"

// Dispatch IOCTL handler
NTSTATUS VCamDispatchIoControl(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    PIO_STACK_LOCATION irpStack;
    ULONG ioControlCode;
    PVOID inputBuffer;
    PVOID outputBuffer;
    ULONG inputBufferLength;
    ULONG outputBufferLength;
    NTSTATUS status;
    ULONG_PTR information;

    KdPrint(("VCam: DispatchIoControl called\n"));

    irpStack = IoGetCurrentIrpStackLocation(Irp);
    ioControlCode = irpStack->Parameters.DeviceIoControl.IoControlCode;
    inputBuffer = Irp->AssociatedIrp.SystemBuffer;
    outputBuffer = Irp->AssociatedIrp.SystemBuffer;
    inputBufferLength = irpStack->Parameters.DeviceIoControl.InputBufferLength;
    outputBufferLength = irpStack->Parameters.DeviceIoControl.OutputBufferLength;

    status = STATUS_SUCCESS;
    information = 0;

    switch (ioControlCode) {
        case IOCTL_VCAM_SEND_FRAME:
            status = VCamHandleSendFrame(DeviceObject, inputBuffer, inputBufferLength);
            break;

        case IOCTL_VCAM_GET_STATUS:
            status = VCamHandleGetStatus(DeviceObject, outputBuffer, outputBufferLength, &information);
            break;

        case IOCTL_VCAM_SET_FORMAT:
            status = VCamHandleSetFormat(DeviceObject, inputBuffer, inputBufferLength);
            break;

        default:
            KdPrint(("VCam: Unknown IOCTL code: 0x%08X\n", ioControlCode));
            status = STATUS_INVALID_DEVICE_REQUEST;
            break;
    }

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = information;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}

// Handle IOCTL_VCAM_SEND_FRAME
NTSTATUS VCamHandleSendFrame(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PVOID InputBuffer,
    _In_ ULONG InputBufferLength
)
{
    PVCAM_DEVICE_EXTENSION deviceExtension;
    PVCAM_FRAME_HEADER header;
    PUCHAR frameData;
    ULONG expectedFrameSize;
    NTSTATUS status;

    KdPrint(("VCam: HandleSendFrame called\n"));

    // Get device extension
    deviceExtension = (PVCAM_DEVICE_EXTENSION)DeviceObject->DeviceExtension;
    if (deviceExtension == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    // Validate input buffer size
    if (InputBufferLength < sizeof(VCAM_FRAME_HEADER)) {
        KdPrint(("VCam: Input buffer too small for header\n"));
        return STATUS_BUFFER_TOO_SMALL;
    }

    header = (PVCAM_FRAME_HEADER)InputBuffer;

    // Calculate expected frame size
    switch (header->Format) {
        case 0: // RGB24
            expectedFrameSize = header->Width * header->Height * 3;
            break;
        case 1: // NV12
            expectedFrameSize = header->Width * header->Height * 3 / 2;
            break;
        case 2: // YUY2
            expectedFrameSize = header->Width * header->Height * 2;
            break;
        default:
            KdPrint(("VCam: Unknown format: %d\n", header->Format));
            return STATUS_INVALID_PARAMETER;
    }

    // Validate buffer size matches expected
    if (InputBufferLength < sizeof(VCAM_FRAME_HEADER) + expectedFrameSize) {
        KdPrint(("VCam: Input buffer too small for frame data\n"));
        return STATUS_BUFFER_TOO_SMALL;
    }

    // Get frame data (after header)
    frameData = (PUCHAR)((PUCHAR)InputBuffer + sizeof(VCAM_FRAME_HEADER));

    // Store frame in circular buffer
    status = VCamStoreFrame(deviceExtension, header, frameData);
    if (!NT_SUCCESS(status)) {
        KdPrint(("VCam: Failed to store frame: 0x%08X\n", status));
        return status;
    }

    KdPrint(("VCam: Frame stored successfully\n"));
    return STATUS_SUCCESS;
}

// Handle IOCTL_VCAM_GET_STATUS
NTSTATUS VCamHandleGetStatus(
    _In_ PDEVICE_OBJECT DeviceObject,
    _Out_ PVOID OutputBuffer,
    _In_ ULONG OutputBufferLength,
    _Out_ PULONG_PTR Information
)
{
    PVCAM_DEVICE_EXTENSION deviceExtension;
    PVCAM_STATUS status;

    KdPrint(("VCam: HandleGetStatus called\n"));

    // Validate output buffer
    if (OutputBufferLength < sizeof(VCAM_STATUS)) {
        return STATUS_BUFFER_TOO_SMALL;
    }

    // Get device extension
    deviceExtension = (PVCAM_DEVICE_EXTENSION)DeviceObject->DeviceExtension;
    if (deviceExtension == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    status = (PVCAM_STATUS)OutputBuffer;
    RtlZeroMemory(status, sizeof(VCAM_STATUS));

    // Fill status information
    status->IsStreaming = TRUE; // Simplified - should check actual state
    status->CurrentWidth = VCAM_DEFAULT_WIDTH;
    status->CurrentHeight = VCAM_DEFAULT_HEIGHT;
    status->CurrentFormat = 0; // RGB24
    status->FramesDelivered = deviceExtension->TotalFramesReceived;

    *Information = sizeof(VCAM_STATUS);

    KdPrint(("VCam: Status retrieved successfully\n"));
    return STATUS_SUCCESS;
}

// Handle IOCTL_VCAM_SET_FORMAT
NTSTATUS VCamHandleSetFormat(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PVOID InputBuffer,
    _In_ ULONG InputBufferLength
)
{
    UNREFERENCED_PARAMETER(DeviceObject);
    UNREFERENCED_PARAMETER(InputBuffer);
    UNREFERENCED_PARAMETER(InputBufferLength);

    KdPrint(("VCam: HandleSetFormat called\n"));

    // TODO: Implement format setting logic
    // For now, just return success

    return STATUS_SUCCESS;
}

// Buffer management functions
NTSTATUS VCamAllocateFrameBuffers(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension
)
{
    ULONG i;
    ULONG bufferSize;

    KdPrint(("VCam: AllocateFrameBuffers called\n"));

    // Calculate buffer size for maximum resolution (1920x1080 RGB24)
    bufferSize = 1920 * 1080 * 3;

    for (i = 0; i < VCAM_FRAME_BUFFER_COUNT; i++) {
        DeviceExtension->FrameBuffers[i].Data = (PUCHAR)ExAllocatePoolWithTag(
            NonPagedPool,
            bufferSize,
            VCAM_POOL_TAG
        );

        if (DeviceExtension->FrameBuffers[i].Data == NULL) {
            // Free previously allocated buffers
            while (i > 0) {
                i--;
                ExFreePoolWithTag(DeviceExtension->FrameBuffers[i].Data, VCAM_POOL_TAG);
                DeviceExtension->FrameBuffers[i].Data = NULL;
            }
            KdPrint(("VCam: Failed to allocate frame buffer\n"));
            return STATUS_INSUFFICIENT_RESOURCES;
        }

        DeviceExtension->FrameBuffers[i].Size = bufferSize;
        DeviceExtension->FrameBuffers[i].Valid = FALSE;
        RtlZeroMemory(DeviceExtension->FrameBuffers[i].Data, bufferSize);
    }

    KdPrint(("VCam: Frame buffers allocated successfully\n"));
    return STATUS_SUCCESS;
}

VOID VCamFreeFrameBuffers(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension
)
{
    ULONG i;

    KdPrint(("VCam: FreeFrameBuffers called\n"));

    for (i = 0; i < VCAM_FRAME_BUFFER_COUNT; i++) {
        if (DeviceExtension->FrameBuffers[i].Data != NULL) {
            ExFreePoolWithTag(DeviceExtension->FrameBuffers[i].Data, VCAM_POOL_TAG);
            DeviceExtension->FrameBuffers[i].Data = NULL;
            DeviceExtension->FrameBuffers[i].Valid = FALSE;
        }
    }
}

NTSTATUS VCamStoreFrame(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension,
    _In_ PVCAM_FRAME_HEADER Header,
    _In_ PUCHAR FrameData
)
{
    KIRQL oldIrql;
    PVCAM_FRAME_BUFFER buffer;
    ULONG frameSize;

    // Calculate frame size
    frameSize = Header->BufferSize;

    // Acquire spin lock
    KeAcquireSpinLock(&DeviceExtension->BufferLock, &oldIrql);

    // Get current write buffer
    buffer = &DeviceExtension->FrameBuffers[DeviceExtension->CurrentWriteIndex];

    // Check if buffer is large enough
    if (frameSize > buffer->Size) {
        KeReleaseSpinLock(&DeviceExtension->BufferLock, oldIrql);
        KdPrint(("VCam: Frame too large for buffer\n"));
        return STATUS_BUFFER_TOO_SMALL;
    }

    // Copy frame data
    RtlCopyMemory(buffer->Data, FrameData, frameSize);
    buffer->Size = frameSize;
    buffer->Timestamp = Header->Timestamp;
    buffer->Valid = TRUE;

    // Advance write index
    DeviceExtension->CurrentWriteIndex = (DeviceExtension->CurrentWriteIndex + 1) % VCAM_FRAME_BUFFER_COUNT;
    DeviceExtension->TotalFramesReceived++;

    // Release spin lock
    KeReleaseSpinLock(&DeviceExtension->BufferLock, oldIrql);

    return STATUS_SUCCESS;
}

NTSTATUS VCamGetFrame(
    _In_ PVCAM_DEVICE_EXTENSION DeviceExtension,
    _Out_ PVCAM_FRAME_BUFFER* FrameBuffer
)
{
    KIRQL oldIrql;
    ULONG readIndex;

    // Acquire spin lock
    KeAcquireSpinLock(&DeviceExtension->BufferLock, &oldIrql);

    // Calculate read index (one behind write index for most recent frame)
    if (DeviceExtension->CurrentWriteIndex == 0) {
        readIndex = VCAM_FRAME_BUFFER_COUNT - 1;
    }
    else {
        readIndex = DeviceExtension->CurrentWriteIndex - 1;
    }

    // Get frame buffer
    *FrameBuffer = &DeviceExtension->FrameBuffers[readIndex];

    // Release spin lock
    KeReleaseSpinLock(&DeviceExtension->BufferLock, oldIrql);

    return STATUS_SUCCESS;
}

