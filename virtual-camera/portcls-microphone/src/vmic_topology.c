#include "../inc/vmic_common.h"

// Pin data ranges for Render (Input)
static const KSDATARANGE_AUDIO VMicPinDataRangeRender[] = {
    {
        {
            sizeof(KSDATARANGE_AUDIO),
            0,
            0,
            0,
            { STATIC_KSDATAFORMAT_TYPE_AUDIO },
            { STATIC_KSDATAFORMAT_SUBTYPE_PCM },
            { STATIC_KSDATAFORMAT_SPECIFIER_WAVEFORMATEX }
        },
        VMIC_DEFAULT_CHANNELS,      // MaximumChannels
        16,                          // MinimumBitsPerSample
        24,                          // MaximumBitsPerSample
        44100,                       // MinimumSampleFrequency
        48000                        // MaximumSampleFrequency
    }
};

// Pin data ranges for Capture (Output)
static const KSDATARANGE_AUDIO VMicPinDataRangeCapture[] = {
    {
        {
            sizeof(KSDATARANGE_AUDIO),
            0,
            0,
            0,
            { STATIC_KSDATAFORMAT_TYPE_AUDIO },
            { STATIC_KSDATAFORMAT_SUBTYPE_PCM },
            { STATIC_KSDATAFORMAT_SPECIFIER_WAVEFORMATEX }
        },
        VMIC_DEFAULT_CHANNELS,      // MaximumChannels
        16,                          // MinimumBitsPerSample
        24,                          // MaximumBitsPerSample
        44100,                       // MinimumSampleFrequency
        48000                        // MaximumSampleFrequency
    }
};

// Data range pointers
static const PKSDATARANGE VMicPinDataRangesRender[] = {
    (PKSDATARANGE)&VMicPinDataRangeRender[0]
};

static const PKSDATARANGE VMicPinDataRangesCapture[] = {
    (PKSDATARANGE)&VMicPinDataRangeCapture[0]
};

// Pin descriptors
static const PCPIN_DESCRIPTOR VMicPinDescriptors[] = {
    // VMIC_PIN_RENDER_SINK (Input from user-mode)
    {
        0, 0, 0,
        NULL,
        {
            0,
            NULL,
            0,
            NULL,
            ARRAYSIZE(VMicPinDataRangesRender),
            (PKSDATARANGE*)VMicPinDataRangesRender,
            KSPIN_DATAFLOW_IN,
            KSPIN_COMMUNICATION_SINK,
            (GUID*)&KSCATEGORY_AUDIO,
            NULL,
            0
        }
    },

    // VMIC_PIN_CAPTURE_SOURCE (Output to applications)
    {
        0, 0, 0,
        NULL,
        {
            0,
            NULL,
            0,
            NULL,
            ARRAYSIZE(VMicPinDataRangesCapture),
            (PKSDATARANGE*)VMicPinDataRangesCapture,
            KSPIN_DATAFLOW_OUT,
            KSPIN_COMMUNICATION_BOTH,
            (GUID*)&KSCATEGORY_AUDIO,
            NULL,
            0
        }
    }
};

// Node descriptors
static const PCNODE_DESCRIPTOR VMicNodeDescriptors[] = {
    // VMIC_NODE_LOOPBACK
    {
        0,
        NULL,
        (GUID*)&KSNODETYPE_SUM,
        NULL
    }
};

// Connections (Render -> Loopback -> Capture)
static const PCCONNECTION_DESCRIPTOR VMicConnections[] = {
    // Connect Render Pin to Loopback Node
    {
        PCFILTER_NODE,
        VMIC_PIN_RENDER_SINK,
        PCFILTER_NODE,
        VMIC_NODE_LOOPBACK
    },
    // Connect Loopback Node to Capture Pin
    {
        PCFILTER_NODE,
        VMIC_NODE_LOOPBACK,
        PCFILTER_NODE,
        VMIC_PIN_CAPTURE_SOURCE
    }
};

// Filter descriptor
const PCFILTER_DESCRIPTOR VMicFilterDescriptor = {
    0,                                          // Version
    NULL,                                       // AutomationTable
    sizeof(PCPIN_DESCRIPTOR),                   // PinSize
    ARRAYSIZE(VMicPinDescriptors),              // PinCount
    (PCPIN_DESCRIPTOR*)VMicPinDescriptors,      // Pins
    sizeof(PCNODE_DESCRIPTOR),                  // NodeSize
    ARRAYSIZE(VMicNodeDescriptors),             // NodeCount
    (PCNODE_DESCRIPTOR*)VMicNodeDescriptors,    // Nodes
    ARRAYSIZE(VMicConnections),                 // ConnectionCount
    (PCCONNECTION_DESCRIPTOR*)VMicConnections,  // Connections
    0,                                          // CategoryCount
    NULL                                        // Categories
};

