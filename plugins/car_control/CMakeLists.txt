cmake_minimum_required(VERSION 3.14)
project(CarControl)

# Gazebo Harmonic packages
find_package(gz-cmake3  REQUIRED)
find_package(gz-sim8    REQUIRED)
find_package(gz-transport13 REQUIRED)
find_package(gz-msgs10  REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS loader register)

# ── Kinematic car control plugin ────────────────────────────────────────────
add_library(CarControlPlugin SHARED CarControlPlugin.cc)

target_include_directories(CarControlPlugin PRIVATE
  ${gz-sim8_INCLUDE_DIRS}
  ${gz-transport13_INCLUDE_DIRS}
  ${gz-msgs10_INCLUDE_DIRS}
  ${gz-plugin2_INCLUDE_DIRS})

target_link_libraries(CarControlPlugin
  gz-sim8::gz-sim8
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10
  gz-plugin2::register)

set_target_properties(CarControlPlugin PROPERTIES
  POSITION_INDEPENDENT_CODE ON)

# ── Stdin → gz-transport bridge (used by Python script) ─────────────────────
add_executable(car_cmd_pub car_cmd_pub.cc)

target_include_directories(car_cmd_pub PRIVATE
  ${gz-transport13_INCLUDE_DIRS}
  ${gz-msgs10_INCLUDE_DIRS})

target_link_libraries(car_cmd_pub
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10)

# ── Teleport-based car mover (30Hz set_pose service calls) ──────────────────
add_executable(car_teleport car_teleport.cc)

target_include_directories(car_teleport PRIVATE
  ${gz-transport13_INCLUDE_DIRS}
  ${gz-msgs10_INCLUDE_DIRS})

target_link_libraries(car_teleport
  gz-transport13::gz-transport13
  gz-msgs10::gz-msgs10)

# ── Install ──────────────────────────────────────────────────────────────────
# Plugin goes to ~/.gz/sim/8/plugins/ (always searched by Gazebo Harmonic)
install(TARGETS CarControlPlugin
  LIBRARY DESTINATION "$ENV{HOME}/.gz/sim/8/plugins/")

install(TARGETS car_cmd_pub car_teleport
  RUNTIME DESTINATION "$ENV{HOME}/.gz/sim/8/plugins/")
