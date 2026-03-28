cmake_minimum_required(VERSION 3.8)
project(manufacturing_os_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Bu komut urdf ve meshes klasörlerini build sonrası çalıştırılabilir alana taşır
install(DIRECTORY 
  meshes 
  urdf
  config
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
