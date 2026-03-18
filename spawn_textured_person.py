#!/usr/bin/env python3
"""
spawn_textured_person.py - Spawn and move textured person models

Usage:
    # Spawn female model
    python3 spawn_textured_person.py --female --x 5 --y 3

    # Spawn male model
    python3 spawn_textured_person.py --male --x -2 --y 4

    # Move in pattern
    python3 spawn_textured_person.py --female --move --pattern circle
"""

import argparse
import time
import math
import subprocess
import sys

def spawn_person(model_type="female", x=0, y=0, z=0, name=None, world="default"):
    """Spawn a textured person model using gz command"""

    if name is None:
        name = f"person_{model_type}_{int(time.time())}"

    model_name = f"person_textured_{model_type}"

    # Auto-detect world if default doesn't work
    if world == "default":
        # Try to detect actual world name
        try:
            result = subprocess.run(["gz", "topic", "-l"], capture_output=True, text=True, timeout=2)
            if "forest" in result.stdout:
                world = "forest"
        except:
            pass

    print(f"🌍 Using world: {world}")

    # Use gz service to spawn model
    cmd = [
        "gz", "service",
        "-s", f"/world/{world}/create",
        "--reqtype", "gz.msgs.EntityFactory",
        "--reptype", "gz.msgs.Boolean",
        "--timeout", "5000",
        "--req",
        f'sdf_filename: "model://{model_name}" '
        f'name: "{name}" '
        f'pose: {{position: {{x: {x} y: {y} z: {z}}}}}'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0 and "data: true" in result.stdout:
            print(f"✅ Spawned {model_type} person '{name}' at ({x}, {y}, {z})")
            return name
        else:
            print(f"❌ Failed to spawn {model_type} person")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print(f"❌ Timeout spawning {model_type} person")
        return None
    except FileNotFoundError:
        print(f"❌ 'gz' command not found. Make sure Gazebo is installed and in PATH.")
        return None
    except Exception as e:
        print(f"❌ Error spawning {model_type} person: {e}")
        return None

def move_person(name, pattern="line", speed=0.5, duration=60, world="default"):
    """Move person in a pattern using gz topic"""

    # Auto-detect world if default doesn't work
    if world == "default":
        try:
            result = subprocess.run(["gz", "topic", "-l"], capture_output=True, text=True, timeout=2)
            if "forest" in result.stdout:
                world = "forest"
        except:
            pass

    print(f"🚶 Moving {name} in {pattern} pattern for {duration}s...")
    print(f"   (Press Ctrl+C to stop)")

    start_time = time.time()
    t = 0

    try:
        while time.time() - start_time < duration:

            # Calculate position based on pattern
            if pattern == "line":
                # Move back and forth in X
                x = 5 * math.sin(t * speed)
                y = 0

            elif pattern == "circle":
                # Move in circle
                radius = 5
                x = radius * math.cos(t * speed)
                y = radius * math.sin(t * speed)

            elif pattern == "figure8":
                # Move in figure-8
                x = 5 * math.sin(t * speed)
                y = 3 * math.sin(2 * t * speed)

            elif pattern == "random":
                # Random walk
                import random
                x = random.uniform(-10, 10)
                y = random.uniform(-10, 10)
                time.sleep(2)
            else:
                x, y = 0, 0

            z = 0

            # Calculate yaw orientation towards movement direction
            if pattern != "random" and t > 0:
                yaw = math.atan2(y, x)
            else:
                yaw = 0

            # Construct pose message and send via gz topic
            pose_msg = f'position: {{x: {x} y: {y} z: {z}}} orientation: {{x: 0 y: 0 z: {math.sin(yaw/2)} w: {math.cos(yaw/2)}}}'

            cmd = [
                "gz", "topic",
                "-t", f"/model/{name}/pose",
                "-m", "gz.msgs.Pose",
                "-p", pose_msg
            ]

            # Send command (non-blocking)
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            time.sleep(0.1)
            t += 0.1

    except KeyboardInterrupt:
        print("\n⏹️  Stopped movement")

    print(f"✅ Movement completed for {name}")

def main():
    parser = argparse.ArgumentParser(description="Spawn and control textured person models")
    parser.add_argument("--female", action="store_true", help="Spawn female model")
    parser.add_argument("--male", action="store_true", help="Spawn male model")
    parser.add_argument("--x", type=float, default=5, help="X position")
    parser.add_argument("--y", type=float, default=0, help="Y position")
    parser.add_argument("--z", type=float, default=0, help="Z position")
    parser.add_argument("--name", type=str, help="Model name")
    parser.add_argument("--world", type=str, default="default", help="World name (default: auto-detect)")
    parser.add_argument("--move", action="store_true", help="Move after spawning")
    parser.add_argument("--pattern", choices=["line", "circle", "figure8", "random"],
                       default="line", help="Movement pattern")
    parser.add_argument("--speed", type=float, default=0.3, help="Movement speed")
    parser.add_argument("--duration", type=float, default=120, help="Movement duration (seconds)")

    args = parser.parse_args()

    # Determine model type
    if args.male:
        model_type = "male"
    elif args.female:
        model_type = "female"
    else:
        print("❌ Please specify --female or --male")
        return

    # Spawn
    name = spawn_person(model_type, args.x, args.y, args.z, args.name, args.world)

    if name and args.move:
        time.sleep(2)  # Wait for model to stabilize
        move_person(name, args.pattern, args.speed, args.duration, args.world)

if __name__ == "__main__":
    main()
