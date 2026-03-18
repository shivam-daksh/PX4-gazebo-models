#!/bin/bash
# Build and install the Gazebo car control plugin + publisher bridge

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$SCRIPT_DIR/build"

echo "Building CarControlPlugin + car_cmd_pub..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
make install

echo ""
echo "✓ Installed:"
echo "  ~/.gz/sim/8/plugins/libCarControlPlugin.so  (Gazebo plugin)"
echo "  ~/.gz/sim/8/plugins/car_cmd_pub             (Python bridge binary)"
echo "  ~/.gz/sim/8/plugins/car_teleport            (set_pose 30Hz binary)"
