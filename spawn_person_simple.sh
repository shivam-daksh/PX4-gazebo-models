#!/bin/bash
# Simple spawner using gz command-line tool

MODEL_TYPE=$1
X=${2:-5}
Y=${3:-0}
Z=${4:-0}
NAME=${5:-"person_$RANDOM"}

# Auto-detect world name
WORLD="default"
if gz topic -l 2>/dev/null | grep -q "forest"; then
    WORLD="forest"
fi

echo "🌍 Using world: $WORLD"

if [ "$MODEL_TYPE" != "female" ] && [ "$MODEL_TYPE" != "male" ]; then
    echo "Usage: $0 <female|male> [x] [y] [z] [name]"
    echo "Example: $0 female 5 0 0"
    exit 1
fi

MODEL_NAME="person_textured_$MODEL_TYPE"

echo "🚀 Spawning $MODEL_TYPE person at ($X, $Y, $Z)..."

gz service \
    -s /world/$WORLD/create \
    --reqtype gz.msgs.EntityFactory \
    --reptype gz.msgs.Boolean \
    --timeout 5000 \
    --req "sdf_filename: \"model://$MODEL_NAME\" name: \"$NAME\" pose: {position: {x: $X y: $Y z: $Z}}"

if [ $? -eq 0 ]; then
    echo "✅ Spawned $MODEL_TYPE person '$NAME' successfully!"
else
    echo "❌ Failed to spawn person. Is Gazebo running?"
    exit 1
fi
