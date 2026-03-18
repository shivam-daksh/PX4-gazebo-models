#!/usr/bin/env python3
"""
setup_textured_persons.py - Setup textured person models with real photos

This script saves the person images to the appropriate texture directories
and creates a spawner for moving textured person models.

Usage:
    python3 setup_textured_persons.py
"""

import os
import sys
from pathlib import Path

# Base paths
MODELS_DIR = Path("/home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/models")
FEMALE_TEXTURE = MODELS_DIR / "person_textured_female/materials/textures/person_female.png"
MALE_TEXTURE = MODELS_DIR / "person_textured_male/materials/textures/person_male.png"

def save_placeholder_images():
    """
    Create placeholder images for textures.

    Note: Replace these with actual person photos by placing:
    - Female photo at: person_textured_female/materials/textures/person_female.png
    - Male photo at: person_textured_male/materials/textures/person_male.png
    """
    try:
        from PIL import Image, ImageDraw, ImageFont

        def create_placeholder(path, label, color):
            # Create a simple colored image with text
            img = Image.new('RGB', (512, 1024), color=color)
            draw = ImageDraw.Draw(img)

            # Add text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            except:
                font = ImageFont.load_default()

            text = f"{label}\nPERSON\nMODEL"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (512 - text_width) // 2
            y = (1024 - text_height) // 2

            draw.text((x, y), text, fill='white', font=font)

            # Save
            img.save(path)
            print(f"✅ Created placeholder: {path}")

        create_placeholder(FEMALE_TEXTURE, "FEMALE", (180, 100, 150))  # Purple
        create_placeholder(MALE_TEXTURE, "MALE", (100, 150, 180))  # Blue

        print("\n📸 Placeholder images created!")
        print("\n🎯 To use real photos:")
        print(f"   1. Save female photo as: {FEMALE_TEXTURE}")
        print(f"   2. Save male photo as: {MALE_TEXTURE}")
        print("   3. Photos should be portrait orientation (taller than wide)")

    except ImportError:
        print("⚠️  PIL not available. Creating empty files.")
        print("   Please manually place person photos at:")
        print(f"   - {FEMALE_TEXTURE}")
        print(f"   - {MALE_TEXTURE}")

        # Create empty files as placeholders
        FEMALE_TEXTURE.touch()
        MALE_TEXTURE.touch()

def create_spawner_script():
    """Create a script to spawn and control textured persons"""

    spawner_script = '''#!/usr/bin/env python3
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
from gz.transport13 import Node
from gz.msgs10.pose_pb2 import Pose
from gz.msgs10.entity_factory_pb2 import EntityFactory

def spawn_person(model_type="female", x=0, y=0, z=0, name=None):
    """Spawn a textured person model"""

    if name is None:
        name = f"person_{model_type}_{int(time.time())}"

    model_name = f"person_textured_{model_type}"

    # Create entity factory message
    req = EntityFactory()
    req.sdf_filename = f"model://{model_name}"
    req.name = name

    # Set pose
    pose = Pose()
    pose.position.x = x
    pose.position.y = y
    pose.position.z = z

    req.pose.CopyFrom(pose)

    # Spawn via Gazebo transport
    node = Node()
    success = node.request("/world/default/create",
                          req.SerializeToString(),
                          EntityFactory,
                          timeout=5000)

    if success:
        print(f"✅ Spawned {model_type} person at ({x}, {y}, {z})")
        return name
    else:
        print(f"❌ Failed to spawn {model_type} person")
        return None

def move_person(name, pattern="line", speed=0.5, duration=60):
    """Move person in a pattern"""

    node = Node()
    pose_pub = node.advertise(f"/model/{name}/cmd_pos", Pose)

    print(f"🚶 Moving {name} in {pattern} pattern...")

    start_time = time.time()
    t = 0

    try:
        while time.time() - start_time < duration:
            pose = Pose()

            if pattern == "line":
                # Move back and forth in X
                pose.position.x = 5 * math.sin(t * speed)
                pose.position.y = 0

            elif pattern == "circle":
                # Move in circle
                radius = 5
                pose.position.x = radius * math.cos(t * speed)
                pose.position.y = radius * math.sin(t * speed)

            elif pattern == "figure8":
                # Move in figure-8
                pose.position.x = 5 * math.sin(t * speed)
                pose.position.y = 3 * math.sin(2 * t * speed)

            elif pattern == "random":
                # Random walk
                import random
                pose.position.x = random.uniform(-10, 10)
                pose.position.y = random.uniform(-10, 10)
                time.sleep(2)

            pose.position.z = 0

            # Orient towards movement direction
            if pattern != "random":
                yaw = math.atan2(pose.position.y, pose.position.x)
                pose.orientation.z = math.sin(yaw / 2)
                pose.orientation.w = math.cos(yaw / 2)

            pose_pub.publish(pose)

            time.sleep(0.1)
            t += 0.1

    except KeyboardInterrupt:
        print("\\n⏹️  Stopped movement")

def main():
    parser = argparse.ArgumentParser(description="Spawn and control textured person models")
    parser.add_argument("--female", action="store_true", help="Spawn female model")
    parser.add_argument("--male", action="store_true", help="Spawn male model")
    parser.add_argument("--x", type=float, default=5, help="X position")
    parser.add_argument("--y", type=float, default=0, help="Y position")
    parser.add_argument("--z", type=float, default=0, help="Z position")
    parser.add_argument("--name", type=str, help="Model name")
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
    name = spawn_person(model_type, args.x, args.y, args.z, args.name)

    if name and args.move:
        time.sleep(2)  # Wait for model to stabilize
        move_person(name, args.pattern, args.speed, args.duration)

if __name__ == "__main__":
    main()
'''

    spawner_path = MODELS_DIR / "../../spawn_textured_person.py"
    spawner_path = spawner_path.resolve()

    with open(spawner_path, 'w') as f:
        f.write(spawner_script)

    os.chmod(spawner_path, 0o755)
    print(f"✅ Created spawner: {spawner_path}")

def main():
    print("=" * 60)
    print("TEXTURED PERSON MODEL SETUP")
    print("=" * 60)

    # Create placeholder textures
    print("\n1️⃣  Setting up textures...")
    save_placeholder_images()

    # Create spawner
    print("\n2️⃣  Creating spawner script...")
    create_spawner_script()

    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)

    print("\n📋 Next Steps:")
    print("\n1. Replace placeholder images with real photos:")
    print(f"   cp your_female_photo.png {FEMALE_TEXTURE}")
    print(f"   cp your_male_photo.png {MALE_TEXTURE}")

    print("\n2. Start PX4 SITL with Gazebo")

    print("\n3. Spawn textured persons:")
    print("   cd /home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz")
    print("   ./spawn_textured_person.py --female --x 5 --y 0 --move --pattern circle")
    print("   ./spawn_textured_person.py --male --x -3 --y 2 --move --pattern line")

    print("\n4. Start your drone tracker:")
    print("   cd /home/shivam-daksh/px4/PX4-IDR/object_tracking/rpi_deployment/ubuntu")
    print("   python3 main.py")

    print("\n💡 Tips:")
    print("   - Use portrait photos (taller than wide)")
    print("   - PNG format recommended")
    print("   - Resolution: 512x1024 or similar")
    print("   - YOLO will detect these as real persons!")

if __name__ == "__main__":
    main()
