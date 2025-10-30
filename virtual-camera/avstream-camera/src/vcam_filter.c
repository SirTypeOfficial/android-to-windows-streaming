#include "../inc/vcam_common.h"

// Pin descriptor
static const KSPIN_DESCRIPTOR_EX VCamPinDescriptor = {
    NULL,                                   // Dispatch
    NULL,                                   // AutomationTable
    {
        0,                                  // InterfacesCount
        NULL,                               // Interfaces
        0,                                  // MediumsCount
        NULL,                               // Mediums
        ARRAYSIZE(VCamPinDataRanges),       // DataRangesCount
        (PKSDATARANGE*)VCamPinDataRanges,   // DataRanges
        KSPIN_DATAFLOW_OUT,                 // DataFlow
        KSPIN_COMMUNICATION_BOTH,           // Communication
        NULL,                               // Category
        NULL,                               // Name
        0                                   // Reserved
    },
    KSPIN_FLAG_GENERATE_MAPPINGS |
    KSPIN_FLAG_PROCESS_IN_RUN_STATE_ONLY |
    KSPIN_FLAG_ASYNCHRONOUS_PROCESSING,     // Flags
    1,                                      // InstancesPossible
    1,                                      // InstancesNecessary
    NULL,                                   // AllocatorFraming
    VCamPinIntersectHandler                 // IntersectHandler
};

// Filter pins
static const KSPIN_DESCRIPTOR_EX* const VCamFilterPins[] = {
    &VCamPinDescriptor
};

// Filter dispatch table
static const KSFILTER_DISPATCH VCamFilterDispatch = {
    NULL,                   // Create
    NULL,                   // Close
    NULL,                   // Process
    NULL                    // Reset
};

// Filter descriptor
const KSFILTER_DESCRIPTOR VCamFilterDescriptor = {
    &VCamFilterDispatch,                    // Dispatch
    NULL,                                   // AutomationTable
    KSFILTER_DESCRIPTOR_VERSION,            // Version
    0,                                      // Flags
    NULL,                                   // ReferenceGuid
    ARRAYSIZE(VCamFilterPins),              // PinDescriptorsCount
    sizeof(KSPIN_DESCRIPTOR_EX),            // PinDescriptorSize
    VCamFilterPins,                         // PinDescriptors
    0,                                      // CategoriesCount
    NULL,                                   // Categories
    0,                                      // NodeDescriptorsCount
    0,                                      // NodeDescriptorSize
    NULL,                                   // NodeDescriptors
    0,                                      // ConnectionsCount
    NULL,                                   // Connections
    NULL                                    // ComponentId
};

