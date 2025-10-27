cmake_minimum_required(VERSION 3.20)
project(VirtualCamera)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_definitions(-DUNICODE -D_UNICODE)

include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/BaseClasses
)

set(SOURCES
    src/VCamFilter.cpp
    src/VCamPin.cpp
    src/SharedMemory.cpp
    src/Register.cpp
    src/DllMain.cpp
)

set(HEADERS
    include/VCamFilter.h
    include/VCamPin.h
    include/SharedMemory.h
    include/common.h
)

add_library(VirtualCamera SHARED ${SOURCES} ${HEADERS})

target_link_libraries(VirtualCamera
    strmiids
    uuid
    ole32
    oleaut32
    winmm
)

set_target_properties(VirtualCamera PROPERTIES
    OUTPUT_NAME "VirtualCamera"
    SUFFIX ".ax"
)

