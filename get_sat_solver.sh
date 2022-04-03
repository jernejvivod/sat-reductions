#!/bin/bash
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit
fi
git clone https://github.com/msoos/cryptominisat.git
apt-get install build-essential cmake
apt-get install zlib1g-dev libboost-program-options-dev libm4ri-dev libsqlite3-dev help2man
cd cryptominisat
mkdir build && cd build
cmake ..
make
make install
ldconfig
