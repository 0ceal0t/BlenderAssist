cmake_minimum_required(VERSION 3.10)
project(bintoxml)

include_directories("${CMAKE_SOURCE_DIR}/3rd_party/HavokLib/source")
include_directories("${CMAKE_SOURCE_DIR}/3rd_party/HavokLib/include")
include_directories("${CMAKE_SOURCE_DIR}/3rd_party/HavokLib/3rd_party/Precore")
include_directories("${CMAKE_SOURCE_DIR}/3rd_party/HavokLib/3rd_party/PugiXml/src")
add_subdirectory("${CMAKE_SOURCE_DIR}/3rd_party/HavokLib")
include(${CMAKE_SOURCE_DIR}/3rd_party/HavokLib/3rd_party/Precore/cmake/3dsmax.cmake)

set(CMAKE_CXX_STANDARD 14)

add_definitions(-DUNICODE -D_UNICODE)
add_executable(bintoxml main.cpp)
target_link_libraries(bintoxml PRIVATE havok-objects)
set_precore_sources(bintoxml directory_scanner)