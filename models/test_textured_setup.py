#!/usr/bin/env python3
"""
Quick test to verify textured person models
"""
import os
from pathlib import Path

print("🔍 Checking Textured Person Models Setup\n")

base = Path("/home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/models")

models = {
    "Female": base / "person_textured_female",
    "Male": base / "person_textured_male"
}

all_good = True

for name, path in models.items():
    print(f"📦 {name} Model:")

    # Check model files
    sdf = path / "model.sdf"
    config = path / "model.config"
    texture = path / "materials/textures" / f"person_{name.lower()}.png"

    if sdf.exists():
        print(f"   ✅ SDF file: {sdf.name}")
    else:
        print(f"   ❌ Missing: {sdf.name}")
        all_good = False

    if config.exists():
        print(f"   ✅ Config file: {config.name}")
    else:
        print(f"   ❌ Missing: {config.name}")
        all_good = False

    if texture.exists():
        size = texture.stat().st_size
        print(f"   ✅ Texture: {texture.name} ({size:,} bytes)")
    else:
        print(f"   ❌ Missing: {texture.name}")
        all_good = False

    print()

# Check spawner
spawner = Path("/home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/spawn_textured_person.py")
if spawner.exists() and os.access(spawner, os.X_OK):
    print(f"✅ Spawner script: {spawner.name} (executable)")
else:
    print(f"⚠️  Spawner: {spawner.name} (check permissions)")
    all_good = False

print("\n" + "="*50)
if all_good:
    print("✅ ALL CHECKS PASSED!")
    print("\n🚀 Ready to use! See TEXTURED_PERSONS.md for usage.")
else:
    print("⚠️  Some issues found. Run setup_textured_persons.py again.")

print("="*50)
