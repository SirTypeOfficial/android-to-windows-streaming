#include "../inc/vcam_common.h"

// Pin create callback
NTSTATUS VCamPinCreate(
    _In_ PKSPIN Pin,
    _In_ PIRP Irp
)
{
    PVCAM_PIN_CONTEXT pinContext;
    NTSTATUS status;

    UNREFERENCED_PARAMETER(Irp);

    KdPrint(("VCam: PinCreate called\n"));

    // Allocate pin context
    pinContext = (PVCAM_PIN_CONTEXT)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(VCAM_PIN_CONTEXT),
        VCAM_POOL_TAG
    );

    if (pinContext == NULL) {
        KdPrint(("VCam: Failed to allocate pin context\n"));
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(pinContext, sizeof(VCAM_PIN_CONTEXT));

    // Initialize pin context with default values
    pinContext->Pin = Pin;
    pinContext->Width = VCAM_DEFAULT_WIDTH;
    pinContext->Height = VCAM_DEFAULT_HEIGHT;
    pinContext->FrameRate = VCAM_DEFAULT_FPS;
    pinContext->FrameNumber = 0;
    KeQuerySystemTime(&pinContext->StartTime);
    pinContext->PreviousState = KSSTATE_STOP;

    // Set pin context
    Pin->Context = pinContext;

    KdPrint(("VCam: Pin created successfully\n"));
    return STATUS_SUCCESS;
}

// Pin close callback
NTSTATUS VCamPinClose(
    _In_ PKSPIN Pin,
    _In_ PIRP Irp
)
{
    PVCAM_PIN_CONTEXT pinContext;

    UNREFERENCED_PARAMETER(Irp);

    KdPrint(("VCam: PinClose called\n"));

    pinContext = (PVCAM_PIN_CONTEXT)Pin->Context;
    if (pinContext != NULL) {
        ExFreePoolWithTag(pinContext, VCAM_POOL_TAG);
        Pin->Context = NULL;
    }

    KdPrint(("VCam: Pin closed\n"));
    return STATUS_SUCCESS;
}

// Pin set device state callback
NTSTATUS VCamPinSetDeviceState(
    _In_ PKSPIN Pin,
    _In_ KSSTATE ToState,
    _In_ KSSTATE FromState
)
{
    PVCAM_PIN_CONTEXT pinContext;

    KdPrint(("VCam: PinSetDeviceState from %d to %d\n", FromState, ToState));

    pinContext = (PVCAM_PIN_CONTEXT)Pin->Context;
    if (pinContext == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    // Handle state transitions
    if (ToState == KSSTATE_RUN && FromState != KSSTATE_RUN) {
        // Starting streaming
        KdPrint(("VCam: Starting streaming\n"));
        pinContext->FrameNumber = 0;
        KeQuerySystemTime(&pinContext->StartTime);
    }
    else if (FromState == KSSTATE_RUN && ToState != KSSTATE_RUN) {
        // Stopping streaming
        KdPrint(("VCam: Stopping streaming\n"));
    }

    pinContext->PreviousState = FromState;

    return STATUS_SUCCESS;
}

// Helper function to calculate frame size based on format
static ULONG VCamGetFrameSize(
    _In_ ULONG Width,
    _In_ ULONG Height,
    _In_ const GUID* Format
)
{
    if (IsEqualGUID(Format, &KSDATAFORMAT_SUBTYPE_RGB24)) {
        return Width * Height * 3;
    }
    else if (IsEqualGUID(Format, &KSDATAFORMAT_SUBTYPE_NV12)) {
        return Width * Height * 3 / 2;
    }
    else if (IsEqualGUID(Format, &KSDATAFORMAT_SUBTYPE_YUY2)) {
        return Width * Height * 2;
    }

    return Width * Height * 3; // Default to RGB24
}

// Pin process callback
NTSTATUS VCamPinProcess(
    _In_ PKSPIN Pin
)
{
    PVCAM_PIN_CONTEXT pinContext;
    PVCAM_DEVICE_EXTENSION deviceExtension;
    PKSSTREAM_POINTER streamPointer;
    PUCHAR frameBuffer;
    ULONG frameSize;
    PVCAM_FRAME_BUFFER sourceFrame;
    NTSTATUS status;

    pinContext = (PVCAM_PIN_CONTEXT)Pin->Context;
    if (pinContext == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    deviceExtension = (PVCAM_DEVICE_EXTENSION)Pin->Context;
    if (deviceExtension == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    // Get leading stream pointer
    streamPointer = KsPinGetLeadingEdgeStreamPointer(Pin, KSSTREAM_POINTER_STATE_LOCKED);
    if (streamPointer == NULL) {
        return STATUS_DEVICE_NOT_READY;
    }

    // Get frame buffer
    frameBuffer = (PUCHAR)streamPointer->StreamHeader->Data;
    frameSize = VCamGetFrameSize(pinContext->Width, pinContext->Height, &pinContext->Format);

    // Get frame from circular buffer
    status = VCamGetFrame(deviceExtension, &sourceFrame);
    if (NT_SUCCESS(status) && sourceFrame != NULL && sourceFrame->Valid) {
        // Copy frame data
        if (sourceFrame->Size <= frameSize) {
            RtlCopyMemory(frameBuffer, sourceFrame->Data, sourceFrame->Size);
        }
        else {
            // Source frame is larger, copy what fits
            RtlCopyMemory(frameBuffer, sourceFrame->Data, frameSize);
        }
    }
    else {
        // No valid frame available, generate black frame
        RtlZeroMemory(frameBuffer, frameSize);
    }

    // Set stream header information
    streamPointer->StreamHeader->DataUsed = frameSize;
    streamPointer->StreamHeader->Size = frameSize;
    streamPointer->StreamHeader->PresentationTime.Time = pinContext->FrameNumber * 10000000 / pinContext->FrameRate;
    streamPointer->StreamHeader->PresentationTime.Numerator = 1;
    streamPointer->StreamHeader->PresentationTime.Denominator = 1;
    streamPointer->StreamHeader->Duration = 10000000 / pinContext->FrameRate;

    // Advance frame number
    pinContext->FrameNumber++;

    // Delete and unlock stream pointer
    KsStreamPointerDelete(streamPointer);

    return STATUS_SUCCESS;
}

// Pin intersect handler
NTSTATUS VCamPinIntersectHandler(
    _In_ PVOID Context,
    _In_ PIRP Irp,
    _In_ PKSP_PIN Pin,
    _In_ PKSDATARANGE CallerDataRange,
    _In_ PKSDATARANGE DescriptorDataRange,
    _In_ ULONG BufferSize,
    _Out_opt_ PVOID Data,
    _Out_ PULONG DataSize
)
{
    const KS_DATARANGE_VIDEO* callerVideoRange;
    const KS_DATARANGE_VIDEO* descriptorVideoRange;
    PKS_DATAFORMAT_VIDEOINFOHEADER resultFormat;
    ULONG requiredSize;

    UNREFERENCED_PARAMETER(Context);
    UNREFERENCED_PARAMETER(Irp);
    UNREFERENCED_PARAMETER(Pin);

    KdPrint(("VCam: PinIntersectHandler called\n"));

    // Validate parameters
    if (CallerDataRange == NULL || DescriptorDataRange == NULL || DataSize == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    // Cast to video ranges
    callerVideoRange = (const KS_DATARANGE_VIDEO*)CallerDataRange;
    descriptorVideoRange = (const KS_DATARANGE_VIDEO*)DescriptorDataRange;

    // Calculate required size
    requiredSize = sizeof(KS_DATAFORMAT_VIDEOINFOHEADER);
    *DataSize = requiredSize;

    // If no buffer provided, just return required size
    if (Data == NULL) {
        return STATUS_SUCCESS;
    }

    // Check buffer size
    if (BufferSize < requiredSize) {
        return STATUS_BUFFER_TOO_SMALL;
    }

    // Fill result format
    resultFormat = (PKS_DATAFORMAT_VIDEOINFOHEADER)Data;
    RtlZeroMemory(resultFormat, requiredSize);

    // Copy format information from descriptor
    resultFormat->DataFormat.FormatSize = requiredSize;
    resultFormat->DataFormat.Flags = 0;
    resultFormat->DataFormat.Reserved = 0;
    resultFormat->DataFormat.MajorFormat = descriptorVideoRange->DataRange.MajorFormat;
    resultFormat->DataFormat.SubFormat = descriptorVideoRange->DataRange.SubFormat;
    resultFormat->DataFormat.Specifier = descriptorVideoRange->DataRange.Specifier;
    resultFormat->DataFormat.SampleSize = descriptorVideoRange->DataRange.SampleSize;

    // Copy video info header
    RtlCopyMemory(
        &resultFormat->VideoInfoHeader,
        &descriptorVideoRange->VideoInfoHeader,
        sizeof(KS_VIDEOINFOHEADER)
    );

    KdPrint(("VCam: Format intersection successful\n"));
    return STATUS_SUCCESS;
}

