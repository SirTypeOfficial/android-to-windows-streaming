#include "../inc/vmic_common.h"

// Driver entry point
NTSTATUS DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS status;

    KdPrint(("VMic: DriverEntry called\n"));

    // Initialize driver object
    DriverObject->DriverExtension->AddDevice = VMicAddDevice;
    DriverObject->DriverUnload = VMicUnload;
    DriverObject->MajorFunction[IRP_MJ_PNP] = VMicDispatchPnp;
    DriverObject->MajorFunction[IRP_MJ_POWER] = VMicDispatchPower;

    // Initialize PortCls
    status = PcInitializeAdapterDriver(
        DriverObject,
        RegistryPath,
        NULL
    );

    if (!NT_SUCCESS(status)) {
        KdPrint(("VMic: PcInitializeAdapterDriver failed: 0x%08X\n", status));
        return status;
    }

    KdPrint(("VMic: Driver loaded successfully\n"));
    return STATUS_SUCCESS;
}

// Add device callback
NTSTATUS VMicAddDevice(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PDEVICE_OBJECT PhysicalDeviceObject
)
{
    NTSTATUS status;

    KdPrint(("VMic: AddDevice called\n"));

    // Add device
    status = PcAddAdapterDevice(
        DriverObject,
        PhysicalDeviceObject,
        (PCPFNSTARTDEVICE)NULL,
        MAX_MINIPORT,
        0
    );

    if (!NT_SUCCESS(status)) {
        KdPrint(("VMic: PcAddAdapterDevice failed: 0x%08X\n", status));
        return status;
    }

    KdPrint(("VMic: Device added successfully\n"));
    return STATUS_SUCCESS;
}

// Unload driver
VOID VMicUnload(
    _In_ PDRIVER_OBJECT DriverObject
)
{
    UNREFERENCED_PARAMETER(DriverObject);

    KdPrint(("VMic: Driver unloaded\n"));
}

// PnP dispatch
NTSTATUS VMicDispatchPnp(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    NTSTATUS status;

    KdPrint(("VMic: DispatchPnp called\n"));

    status = PcDispatchIrp(DeviceObject, Irp);

    return status;
}

// Power dispatch
NTSTATUS VMicDispatchPower(
    _In_ PDEVICE_OBJECT DeviceObject,
    _In_ PIRP Irp
)
{
    NTSTATUS status;

    KdPrint(("VMic: DispatchPower called\n"));

    PoStartNextPowerIrp(Irp);
    status = PcDispatchIrp(DeviceObject, Irp);

    return status;
}

