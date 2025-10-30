#include "../inc/vcam_common.h"

// Helper macro for frame interval calculation (100-nanosecond units)
#define FPS_TO_FRAME_INTERVAL(fps) (10000000 / (fps))

// RGB24 format ranges
static const KS_DATARANGE_VIDEO VCamFormatRGB24_640x480_30fps = {
    {
        sizeof(KS_DATARANGE_VIDEO),
        0,
        640 * 480 * 3,
        0,
        { STATIC_KSDATAFORMAT_TYPE_VIDEO },
        { STATIC_KSDATAFORMAT_SUBTYPE_RGB24 },
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO }
    },
    TRUE,
    TRUE,
    KS_VIDEOSTREAM_CAPTURE,
    0,
    {
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO },
        KS_AnalogVideo_None,
        640, 480,
        640, 480,
        640, 480,
        640, 480,
        640 * 480 * 3,
        {
            FPS_TO_FRAME_INTERVAL(30), FPS_TO_FRAME_INTERVAL(30),
            0, 0,
            30,
            { 640, 480 }
        },
        {
            sizeof(KS_BITMAPINFOHEADER),
            640,
            480,
            1,
            24,
            KS_BI_RGB,
            640 * 480 * 3,
            0,
            0,
            0,
            0
        }
    }
};

static const KS_DATARANGE_VIDEO VCamFormatRGB24_1280x720_30fps = {
    {
        sizeof(KS_DATARANGE_VIDEO),
        0,
        1280 * 720 * 3,
        0,
        { STATIC_KSDATAFORMAT_TYPE_VIDEO },
        { STATIC_KSDATAFORMAT_SUBTYPE_RGB24 },
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO }
    },
    TRUE,
    TRUE,
    KS_VIDEOSTREAM_CAPTURE,
    0,
    {
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO },
        KS_AnalogVideo_None,
        1280, 720,
        1280, 720,
        1280, 720,
        1280, 720,
        1280 * 720 * 3,
        {
            FPS_TO_FRAME_INTERVAL(30), FPS_TO_FRAME_INTERVAL(30),
            0, 0,
            30,
            { 1280, 720 }
        },
        {
            sizeof(KS_BITMAPINFOHEADER),
            1280,
            720,
            1,
            24,
            KS_BI_RGB,
            1280 * 720 * 3,
            0,
            0,
            0,
            0
        }
    }
};

static const KS_DATARANGE_VIDEO VCamFormatRGB24_1920x1080_30fps = {
    {
        sizeof(KS_DATARANGE_VIDEO),
        0,
        1920 * 1080 * 3,
        0,
        { STATIC_KSDATAFORMAT_TYPE_VIDEO },
        { STATIC_KSDATAFORMAT_SUBTYPE_RGB24 },
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO }
    },
    TRUE,
    TRUE,
    KS_VIDEOSTREAM_CAPTURE,
    0,
    {
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO },
        KS_AnalogVideo_None,
        1920, 1080,
        1920, 1080,
        1920, 1080,
        1920, 1080,
        1920 * 1080 * 3,
        {
            FPS_TO_FRAME_INTERVAL(30), FPS_TO_FRAME_INTERVAL(30),
            0, 0,
            30,
            { 1920, 1080 }
        },
        {
            sizeof(KS_BITMAPINFOHEADER),
            1920,
            1080,
            1,
            24,
            KS_BI_RGB,
            1920 * 1080 * 3,
            0,
            0,
            0,
            0
        }
    }
};

// NV12 format ranges (1920x1080 example)
static const KS_DATARANGE_VIDEO VCamFormatNV12_1920x1080_30fps = {
    {
        sizeof(KS_DATARANGE_VIDEO),
        0,
        1920 * 1080 * 3 / 2,
        0,
        { STATIC_KSDATAFORMAT_TYPE_VIDEO },
        { STATIC_KSDATAFORMAT_SUBTYPE_NV12 },
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO }
    },
    TRUE,
    TRUE,
    KS_VIDEOSTREAM_CAPTURE,
    0,
    {
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO },
        KS_AnalogVideo_None,
        1920, 1080,
        1920, 1080,
        1920, 1080,
        1920, 1080,
        1920 * 1080 * 3 / 2,
        {
            FPS_TO_FRAME_INTERVAL(30), FPS_TO_FRAME_INTERVAL(30),
            0, 0,
            30,
            { 1920, 1080 }
        },
        {
            sizeof(KS_BITMAPINFOHEADER),
            1920,
            1080,
            1,
            12,
            MAKEFOURCC('N','V','1','2'),
            1920 * 1080 * 3 / 2,
            0,
            0,
            0,
            0
        }
    }
};

// YUY2 format ranges (1920x1080 example)
static const KS_DATARANGE_VIDEO VCamFormatYUY2_1920x1080_30fps = {
    {
        sizeof(KS_DATARANGE_VIDEO),
        0,
        1920 * 1080 * 2,
        0,
        { STATIC_KSDATAFORMAT_TYPE_VIDEO },
        { STATIC_KSDATAFORMAT_SUBTYPE_YUY2 },
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO }
    },
    TRUE,
    TRUE,
    KS_VIDEOSTREAM_CAPTURE,
    0,
    {
        { STATIC_KSDATAFORMAT_SPECIFIER_VIDEOINFO },
        KS_AnalogVideo_None,
        1920, 1080,
        1920, 1080,
        1920, 1080,
        1920, 1080,
        1920 * 1080 * 2,
        {
            FPS_TO_FRAME_INTERVAL(30), FPS_TO_FRAME_INTERVAL(30),
            0, 0,
            30,
            { 1920, 1080 }
        },
        {
            sizeof(KS_BITMAPINFOHEADER),
            1920,
            1080,
            1,
            16,
            MAKEFOURCC('Y','U','Y','2'),
            1920 * 1080 * 2,
            0,
            0,
            0,
            0
        }
    }
};

// Array of all supported data ranges
const PKSDATARANGE VCamPinDataRanges[] = {
    (PKSDATARANGE)&VCamFormatRGB24_640x480_30fps,
    (PKSDATARANGE)&VCamFormatRGB24_1280x720_30fps,
    (PKSDATARANGE)&VCamFormatRGB24_1920x1080_30fps,
    (PKSDATARANGE)&VCamFormatNV12_1920x1080_30fps,
    (PKSDATARANGE)&VCamFormatYUY2_1920x1080_30fps
};

const ULONG VCamPinDataRangesCount = ARRAYSIZE(VCamPinDataRanges);

// Format validation
NTSTATUS VCamValidateFormat(
    _In_ const KS_DATAFORMAT_VIDEOINFOHEADER* Format
)
{
    ULONG i;
    BOOLEAN found = FALSE;

    if (Format == NULL) {
        return STATUS_INVALID_PARAMETER;
    }

    // Check if width and height are supported
    for (i = 0; i < VCAM_NUM_RESOLUTIONS; i++) {
        if (Format->VideoInfoHeader.bmiHeader.biWidth == (LONG)g_SupportedResolutions[i].Width &&
            abs(Format->VideoInfoHeader.bmiHeader.biHeight) == (LONG)g_SupportedResolutions[i].Height) {
            found = TRUE;
            break;
        }
    }

    if (!found) {
        KdPrint(("VCam: Unsupported resolution: %dx%d\n",
            Format->VideoInfoHeader.bmiHeader.biWidth,
            Format->VideoInfoHeader.bmiHeader.biHeight));
        return STATUS_NOT_SUPPORTED;
    }

    // Check format type
    if (Format->VideoInfoHeader.bmiHeader.biCompression != KS_BI_RGB &&
        Format->VideoInfoHeader.bmiHeader.biCompression != MAKEFOURCC('N','V','1','2') &&
        Format->VideoInfoHeader.bmiHeader.biCompression != MAKEFOURCC('Y','U','Y','2')) {
        KdPrint(("VCam: Unsupported format compression: 0x%08X\n",
            Format->VideoInfoHeader.bmiHeader.biCompression));
        return STATUS_NOT_SUPPORTED;
    }

    return STATUS_SUCCESS;
}

