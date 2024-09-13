cmake_minimum_required(VERSION 3.0.2)
project(bash_action)

## Compile as C++11, supported in ROS Kinetic and newer
# add_compile_options(-std=c++11)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
# Trouver les dépendances nécessaires
find_package(catkin REQUIRED COMPONENTS
  actionlib_msgs
  actionlib
  rospy
  std_msgs
)

## Génération de messages et d'actions
add_action_files(
  FILES
  Bash.action
)

## Générer les messages après les avoir définis
generate_messages(
  DEPENDENCIES
  actionlib_msgs
  std_msgs
)

## Définition du package catkin
catkin_package(
  CATKIN_DEPENDS actionlib_msgs rospy std_msgs
)

## Installer les scripts Python
catkin_install_python(PROGRAMS
  scripts/bash_action_server.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

## Installer le fichier YAML
install(FILES
  config/actions.yaml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/config
)

###########
## Build ##
###########

## Specify additional locations of header files
## Your package locations should be listed before other locations
include_directories(
# include
  ${catkin_INCLUDE_DIRS}
)
