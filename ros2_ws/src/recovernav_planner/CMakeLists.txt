cmake_minimum_required(VERSION 3.16)
project(recovernav_planner)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(nav2_core REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(tf2_ros REQUIRED)

add_library(recovernav_planner SHARED
  src/recovernav_planner.cpp
)
target_include_directories(recovernav_planner PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(recovernav_planner
  nav2_core nav2_costmap_2d nav_msgs geometry_msgs pluginlib rclcpp rclcpp_lifecycle tf2_ros
)

pluginlib_export_plugin_description_file(nav2_core recovernav_planner_plugin.xml)

install(TARGETS recovernav_planner
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include)
install(FILES recovernav_planner_plugin.xml DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_recoverability test/test_recoverability.cpp)
  target_include_directories(test_recoverability PRIVATE include)
  ament_target_dependencies(test_recoverability nav2_costmap_2d)
endif()

ament_package()
