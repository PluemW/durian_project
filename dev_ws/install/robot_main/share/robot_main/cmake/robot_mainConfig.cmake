# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_robot_main_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED robot_main_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(robot_main_FOUND FALSE)
  elseif(NOT robot_main_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(robot_main_FOUND FALSE)
  endif()
  return()
endif()
set(_robot_main_CONFIG_INCLUDED TRUE)

# output package information
if(NOT robot_main_FIND_QUIETLY)
  message(STATUS "Found robot_main: 0.0.0 (${robot_main_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'robot_main' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT robot_main_DEPRECATED_QUIET)
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(robot_main_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${robot_main_DIR}/${_extra}")
endforeach()
