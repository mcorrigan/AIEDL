cmake_minimum_required(VERSION 3.10)
project(AIEDL)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Source files
set(SOURCES
    aiedl.cpp
)

# Header files
set(HEADERS
    aiedl.h
)

# Create library
add_library(aiedl STATIC ${SOURCES} ${HEADERS})

# Include directories
target_include_directories(aiedl PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# Example executable
add_executable(aiedl_example example.cpp)
target_link_libraries(aiedl_example aiedl)

# Install
install(TARGETS aiedl DESTINATION lib)
install(FILES ${HEADERS} DESTINATION include/aiedl)

