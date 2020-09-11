Myanmar License Plate Recogition
===

project base is at ./anpr_mm

rest are tests.

## Table of Contents for <b>LINUX</b>

1. [How to compile Darknet v4](https://github.com/AlexeyAB/darknet/#how-to-compile-on-linuxmacos-using-cmake)

2. [How to install nvidia driver](#nvidia-driver-installation)

3. [How to install CUDA](#cuda-installation)

4. [How to build OPENCV with CUDA and install](#opencv-installation-with-cuda)


## Nvidia Driver Installation
    sample

## CUDA Installation
    sample

## OPENCV Installation with CUDA
`git clone opencv`

`git clone opencv_contrib`

`mkdir build && cd build`

`cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local \
-D WITH_CUDA=ON -D ENABLE_FAST_MATH=1 -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 \
-D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D BUILD_EXAMPLES=ON .. `




