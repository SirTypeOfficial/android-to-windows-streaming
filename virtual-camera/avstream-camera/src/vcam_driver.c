#include "../inc/vcam_common.h"

// Device descriptor
const KSDEVICE_DESCRIPTOR VCamDeviceDescriptor = {
    NULL,                           // Dispatch
    0,                              // FilterDescriptorsCount (will be set at runtime)
    NULL,                           // FilterDescriptors (will be set at runtime)
    0,                              // Version
    NULL,                           // Flags
    VCamDeviceAdd,                  // Add
    NULL,                           // Start
    NULL,                           // PostStart
    NULL,                           // QueryStop
    NULL,                           // CancelStop
    NULL,                           // Stop
    NULL,                           // QueryRemove
    NULL,                           // CancelRemove
    NULL,                           // Remove
    NULL,                           // QueryCapabilities
    NULL,                           // SurpriseRemoval
    NULL,                           // QueryPower
    NULL                            // SetPower
};

// Driver entry point
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS status;

    KdPrint(("VCam: DriverEntry called\n"));

    // Initialize KS driver
    status = KsInitializeDriver(
        DriverObject,
        RegistryPath,
        &VCamDeviceDescriptor
    );

    if (!NT_SUCCESS(status)) {
        KdPrint(("VCam: KsInitializeDriver failed with status 0x%08X\n", status));
        return status;
    }

    KdPrint(("VCam: Driver loaded successfully\n"));
    return STATUS_SUCCESS;
}

// Device add callback
NTSTATUS VCamDeviceAdd(
    _In_ PKSDEVICE Device
)
{
    NTSTATUS status;
    PVCAM_DEVICE_EXTENSION deviceExtension;

    KdPrint(("VCam: DeviceAdd called\n"));

    // Allocate device extension
    deviceExtension = (PVCAM_DEVICE_EXTENSION)ExAllocatePoolWithTag(
        NonPagedPool,
        sizeof(VCAM_DEVICE_EXTENSION),
        VCAM_POOL_TAG
    );

    if (deviceExtension == NULL) {
        KdPrint(("VCam: Failed to allocate device extension\n"));
        return STATUS_INSUFFICIENT_RESOURCES;
    }

    RtlZeroMemory(deviceExtension, sizeof(VCAM_DEVICE_EXTENSION));

    // Initialize device extension
    deviceExtension->KsDevice = Device;
    KeInitializeSpinLock(&deviceExtension->BufferLock);
    deviceExtension->CurrentWriteIndex = 0;
    deviceExtension->CurrentReadIndex = 0;
    deviceExtension->TotalFramesReceived = 0;
    // Initialize streaming state
    deviceExtension->IsStreaming = FALSE;
    deviceExtension->CurrentWidth = VCAM_DEFAULT_WIDTH;
    deviceExtension->CurrentHeight = VCAM_DEFAULT_HEIGHT;
    deviceExtension->CurrentFormat = 0; // RGB24
    deviceExtension->FramesDelivered = 0;

    // Allocate frame buffers
    status = VCamAllocateFrameBuffers(deviceExtension);
    if (!NT_SUCCESS(status)) {
        KdPrint(("VCam: Failed to allocate frame buffers\n"));
        ExFreePoolWithTag(deviceExtension, VCAM_POOL_TAG);
        return status;
    }

    // Set device context
    Device->Context = deviceExtension;

    KdPrint(("VCam: Device added successfully\n"));
    return STATUS_SUCCESS;
}

// Device start callback
NTSTATUS VCamDeviceStart(
    _In_ PKSDEVICE Device,
    _In_ PIRP Irp,
    _In_opt_ PCM_RESOURCE_LIST TranslatedResourceList,
    _In_opt_ PCM_RESOURCE_LIST UntranslatedResourceList
)
{
    UNREFERENCED_PARAMETER(Irp);
    UNREFERENCED_PARAMETER(TranslatedResourceList);
    UNREFERENCED_PARAMETER(UntranslatedResourceList);

    KdPrint(("VCam: DeviceStart called\n"));

    if (Device == NULL || Device->Context == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    KdPrint(("VCam: Device started successfully\n"));
    return STATUS_SUCCESS;
}

// Device stop callback
VOID VCamDeviceStop(
    _In_ PKSDEVICE Device,
    _In_ PIRP Irp
)
{
    PVCAM_DEVICE_EXTENSION deviceExtension;

    UNREFERENCED_PARAMETER(Irp);

    KdPrint(("VCam: DeviceStop called\n"));

    deviceExtension = (PVCAM_DEVICE_EXTENSION)Device->Context;
    if (deviceExtension != NULL) {
        // Free frame buffers
        VCamFreeFrameBuffers(deviceExtension);

        // Free device extension
        ExFreePoolWithTag(deviceExtension, VCAM_POOL_TAG);
        Device->Context = NULL;
    }

    KdPrint(("VCam: Device stopped\n"));
}

// Dispatch create
NTSTATUS VCamDispatchCreate(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    UNREFERENCED_PARAMETER(DeviceObject);

    KdPrint(("VCam: DispatchCreate called\n"));

    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 0;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return STATUS_SUCCESS;
}

// Dispatch close
NTSTATUS VCamDispatchClose(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    UNREFERENCED_PARAMETER(DeviceObject);

    KdPrint(("VCam: DispatchClose called\n"));

    Irp->IoStatus.Status = STATUS_SUCCESS;
    Irp->IoStatus.Information = 0;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return STATUS_SUCCESS;
}

