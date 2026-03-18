# Textured Person Models - Quick Guide

## What This Does

Creates person models with **real photo textures** that YOLO will detect as actual people. Perfect for testing your visual servoing drone tracker!

## 📁 Files Created

```
Tools/simulation/gz/models/
├── person_textured_female/
│   ├── model.sdf
│   ├── model.config
│   └── materials/textures/
│       └── person_female.png  ← Replace with real photo
│
├── person_textured_male/
│   ├── model.sdf
│   ├── model.config
│   └── materials/textures/
│       └── person_male.png    ← Replace with real photo
│
└── setup_textured_persons.py

Tools/simulation/gz/
└── spawn_textured_person.py   ← Spawner script
```

## 🎯 How to Use

### Step 1: Add Real Photos (Optional but Recommended)

The setup created placeholder images. To use the real photos from your attachments:

```bash
# Navigate to textures directory
cd /home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/models

# Save your photos (you'll need to download them first)
# Then copy them:
cp /path/to/female_photo.png person_textured_female/materials/textures/person_female.png
cp /path/to/male_photo.png person_textured_male/materials/textures/person_male.png
```

**Photo requirements:**
- Format: PNG or JPG
- Orientation: Portrait (taller than wide)
- Recommended size: 512x1024 pixels
- Background: Any (will be mapped to box)

### Step 2: Start Simulation

```bash
cd /home/shivam-daksh/px4/PX4-IDR
make px4_sitl gz_x500_mono_cam
```

### Step 3: Spawn Textured Persons

In a new terminal:

```bash
cd /home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz

# Spawn female model (moving in circle)
./spawn_textured_person.py --female --x 5 --y 0 --move --pattern circle

# Or spawn male model (moving in line)
./spawn_textured_person.py --male --x -3 --y 2 --move --pattern line
```

### Step 4: Run Drone Tracker

In another terminal:

```bash
cd /home/shivam-daksh/px4/PX4-IDR/object_tracking/rpi_deployment/ubuntu
python3 main.py
```

## 🎮 Spawner Options

```bash
# Basic spawn at position
./spawn_textured_person.py --female --x 10 --y 5

# Spawn with custom name
./spawn_textured_person.py --male --x 3 --y -2 --name "target_person"

# Spawn and move in different patterns
./spawn_textured_person.py --female --x 0 --y 0 --move --pattern circle
./spawn_textured_person.py --male --x 5 --y 5 --move --pattern figure8
./spawn_textured_person.py --female --x -5 --y 3 --move --pattern random

# Control movement speed and duration
./spawn_textured_person.py --female --move --pattern line --speed 0.5 --duration 120
```

## 📐 Movement Patterns

| Pattern | Description | Good For |
|---------|-------------|----------|
| **line** | Back and forth in X-axis | Testing horizontal tracking |
| **circle** | Circular path | Testing yaw-based control |
| **figure8** | Figure-8 pattern | Testing complex movements |
| **random** | Random positions | Testing search & reacquisition |

## 🎯 Testing Visual Servoing

Once you spawn a textured person and start the tracker:

1. **Observe Control Mode**: Should show "yaw_only" (yellow) during tracking
2. **Check vy velocity**: Should be 0.00 for small errors (no roll!)
3. **Watch the drone**: Should rotate (yaw) to follow, not tilt sideways
4. **Monitor stability**: Tracking should be smooth, no oscillations

## 💡 Why This Works

- **YOLO Detection**: The photo texture makes YOLO detect these as real people
- **Realistic Testing**: Tests visual servoing with actual person appearance
- **Controlled Movement**: You control the movement patterns for systematic testing
- **Safe Environment**: Test in simulation before real-world deployment

## 🔍 Troubleshooting

### Person not detected by YOLO
- Make sure photo has good contrast
- Verify person is within camera view
- Check YOLO confidence threshold in config

### Model not spawning
- Ensure Gazebo is running
- Check model paths are correct
- Verify SDF syntax with: `gz sdf -k model.sdf`

### Person not moving
- Check Gazebo transport connection
- Verify movement plugin is loaded
- Try simpler pattern first (line)

### Visual Servoing Issues
- Refer to [VISUAL_SERVOING.md](../../object_tracking/rpi_deployment/ubuntu/VISUAL_SERVOING.md)
- Check control mode indicator
- Verify vy ≈ 0.00 for small errors

## 🚀 Advanced Usage

### Multiple Persons

```bash
# Spawn multiple people for multi-target testing
./spawn_textured_person.py --female --x 5 --y 0 --name person1 --move --pattern circle &
./spawn_textured_person.py --male --x -3 --y 5 --name person2 --move --pattern line &
./spawn_textured_person.py --female --x 0 --y -5 --name person3 --move --pattern figure8 &
```

### Custom Trajectories

Edit `spawn_textured_person.py` and add your own movement patterns in the `move_person()` function.

### Different Textures

You can add more variants:
1. Copy model directories
2. Rename to `person_textured_child`, `person_textured_elder`, etc.
3. Update texture paths in SDF
4. Add different photos

## 📊 Testing Checklist

- [ ] Photos are in correct directories
- [ ] PX4 SITL running
- [ ] Gazebo world loaded
- [ ] Textured person spawned
- [ ] Person visible in camera feed
- [ ] YOLO detects person
- [ ] Drone tracks smoothly
- [ ] Control mode shows "yaw_only"
- [ ] No lateral velocity for small errors
- [ ] Stable tracking, no oscillations

## 🎓 Next Steps

1. Test with placeholder images first
2. Replace with real photos for better detection
3. Test different movement patterns
4. Tune visual servoing parameters if needed
5. Test multiple persons for complex scenarios

---

**For visual servoing details, see:**
- [VISUAL_SERVOING.md](../../object_tracking/rpi_deployment/ubuntu/VISUAL_SERVOING.md)
- [QUICKREF.md](../../object_tracking/rpi_deployment/ubuntu/QUICKREF.md)
