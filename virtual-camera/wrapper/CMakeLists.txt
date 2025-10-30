cmake_minimum_required(VERSION 3.15)

project(VirtuCore VERSION 1.0.0 LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Windows specific settings
if(WIN32)
    add_definitions(-DUNICODE -D_UNICODE)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

# DLL Export/Import
add_definitions(-DVIRTUCORE_EXPORTS)

# Source files
set(SOURCES
    DllMain.cpp
    VirtuCoreCamera.cpp
    VirtuCoreMicrophone.cpp
    VirtuCoreError.cpp
)

# Header files
set(HEADERS
    VirtuCoreAPI.h
)

# Create DLL
add_library(VirtuCore SHARED
    ${SOURCES}
    ${HEADERS}
)

# Include directories
target_include_directories(VirtuCore 
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
)

# Link libraries
target_link_libraries(VirtuCore
    PRIVATE
        # Windows libraries
        kernel32
        user32
        ole32
        oleaut32
        uuid
)

# Output directories
set_target_properties(VirtuCore PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
    ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib
)

# Install rules
install(TARGETS VirtuCore
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
)

install(FILES ${HEADERS}
    DESTINATION include
)

# Version info
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/version.rc.in"
    "${CMAKE_CURRENT_BINARY_DIR}/version.rc"
    @ONLY
)

# Optional: Build example
option(BUILD_EXAMPLES "Build example programs" OFF)
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Optional: Build tests
option(BUILD_TESTS "Build test programs" OFF)
if(BUILD_TESTS)
    add_subdirectory(tests)
endif()

message(STATUS "VirtuCore DLL configuration complete")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")

