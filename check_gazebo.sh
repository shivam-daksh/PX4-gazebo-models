#!/bin/bash
# Check Gazebo status and available services

echo "🔍 Checking Gazebo Status..."
echo ""

# Check if gz process is running
if pgrep -f "gz sim" > /dev/null; then
    echo "✅ Gazebo process is running"
else
    echo "❌ Gazebo process NOT running"
    echo "   Start with: cd ~/px4/PX4-IDR && make px4_sitl gz_x500_mono_cam"
    exit 1
fi

echo ""
echo "🌍 Available worlds:"
gz topic -l | grep -E "/world/.*/stats" | sed 's|/stats||' | sed 's|/world/||' || echo "   No worlds found"

echo ""
echo "🔌 Checking /world/default/create service:"
if gz service -l | grep -q "/world/default/create"; then
    echo "✅ Service available"
else
    echo "❌ Service not available"
    echo ""
    echo "Available services:"
    gz service -l | grep "/world/" | head -10
fi

echo ""
echo "📋 World stats:"
gz topic -e -t /world/default/stats -n 1 2>/dev/null || echo "   Could not get world stats"

echo ""
echo "✅ If everything looks good, try spawning again!"
echo "   If world is not 'default', update spawn script with correct world name"
