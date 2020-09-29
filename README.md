Myanmar License Plate Recogition
===

_Project base is ./anpr_mm && rest are tests._


### Setups ###
 - [For Linux](#workplace-setup-for-linux)
 - [For Windows](#workplace-setup-for-windows)
 - I don't have MAC -`)

---

## Workplace setup for LINUX

1. [Install CUDA](#cuda-installation)

2. [Install CUDNN](#cudnn-installation)

3. [Install nvidia driver](#nvidia-driver-installation)

4. [Build OPENCV with CUDA then Install](#opencv-installation-with-cuda)

5. [Compile Darknet v4](https://github.com/AlexeyAB/darknet/#how-to-compile-on-linuxmacos-using-cmake)
   

## CUDA Installation
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
    sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
    sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
    sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
    sudo apt update
    sudo apt install cuda


## cuDNN installation 
* Note - cuda v11.0 need cudnn v8.0.3.33
    sudo mv cuda/include/cudnn*.h /usr/local/cuda/include/




## Nvidia Driver Installation


## OPENCV Installation with CUDA
`git clone opencv`

`git clone opencv_contrib`

`mkdir build && cd build`

`cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local \
-D WITH_CUDA=ON -D ENABLE_FAST_MATH=1 -D CUDA_FAST_MATH=1 -D WITH_CUBLAS=1 \
-D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -D BUILD_EXAMPLES=ON .. `




