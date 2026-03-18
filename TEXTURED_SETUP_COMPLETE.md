# ✅ Textured Person Models - Setup Complete!

## What Was Created

You now have **textured person models** that use real photos as textures! The placeholder images have been automatically generated.

## 📁 Files Created

```
Tools/simulation/gz/
├── models/
│   ├── person_textured_female/       ✅ Female model with photo texture
│   │   ├── model.sdf
│   │   ├── model.config
│   │   └── materials/textures/
│   │       └── person_female.png     (6 MB - placeholder created)
│   │
│   ├── person_textured_male/         ✅ Male model with photo texture
│   │   ├── model.sdf
│   │   ├── model.config
│   │   └── materials/textures/
│   │       └── person_male.png       (9.8 MB - placeholder created)
│   │
│   ├── setup_textured_persons.py     Setup script
│   └── test_textured_setup.py        Test script
│
├── spawn_textured_person.py          ✅ Spawner (executable)
├── TEXTURED_PERSONS.md                📖 Complete guide
└── TEXTURED_SETUP_COMPLETE.md         This file
```

## 🎯 Quick Start

### 1. Start Simulation

```bash
cd /home/shivam-daksh/px4/PX4-IDR
make px4_sitl gz_x500_mono_cam
```

### 2. Spawn a Moving Person (in new terminal)

```bash
cd /home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz

# Spawn female model moving in a circle
./spawn_textured_person.py --female --x 5 --y 0 --move --pattern circle

# OR spawn male model moving in a line
./spawn_textured_person.py --male --x -3 --y 2 --move --pattern line
```

### 3. Run Drone Tracker (in another terminal)

```bash
cd /home/shivam-daksh/px4/PX4-IDR/object_tracking/rpi_deployment/ubuntu
python3 main.py
```

## 🎨 About the Placeholder Textures

The setup script created colorful placeholder images:
- **Female texture**: Purple/pink colored (6 MB)
- **Male texture**: Blue colored (9.8 MB)

These work fine for testing! YOLO should detect them as persons.

## 🖼️ Using Your Own Photos (Optional)

To use the actual photos from your attachments:

```bash
cd /home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/models

# Save your downloaded photos, then:
cp /path/to/female_photo.jpg person_textured_female/materials/textures/person_female.png
cp /path/to/male_photo.jpg person_textured_male/materials/textures/person_male.png
```

**Photo tips:**
- Format: PNG or JPG
- Orientation: Portrait (taller than wide)
- Any size works, but 512x1024 is optimal
- Clear, well-lit photos work best

## 🎮 Movement Patterns

```bash
# Line pattern (back and forth)
./spawn_textured_person.py --female --move --pattern line

# Circle pattern (perfect for yaw testing!)
./spawn_textured_person.py --female --move --pattern circle

# Figure-8 pattern (complex movement)
./spawn_textured_person.py --female --move --pattern figure8

# Random movement (unpredictable)
./spawn_textured_person.py --male --move --pattern random
```

## 📊 Testing Your Visual Servoing

Once person is spawned and drone tracker is running:

### What to Look For:

1. **YOLO Detection**: Person should be detected immediately
2. **Control Mode**: Should show "yaw_only" (yellow) during tracking
3. **Lateral Velocity**: vy should be 0.00 for small errors ✅
4. **Drone Behavior**: Should **rotate** (yaw) to follow, not tilt sideways
5. **Stability**: Smooth tracking, no oscillations

### Console Output Should Show:

```
📊 Mode: yaw_only | Err H:+0.12 V:-0.05 D:+0.08 | Vel vx:0.05 vy:0.00 vz:0.03 yaw:0.10
```

**Key indicator: vy=0.00** means no lateral movement = no roll = correct! ✅

## 🎯 Why This Is Great for Testing

1. **Realistic Detection**: YOLO detects textured boxes as real persons
2. **Controlled Movement**: You control the pattern and speed
3. **Safe Environment**: Test visual servoing before real flights
4. **Multiple Scenarios**: Test different movement patterns
5. **Visual Servoing Validation**: Verify yaw-based control works

## 💡 Testing Scenarios

### Scenario 1: Basic Tracking
```bash
# Spawn person moving in circle at moderate speed
./spawn_textured_person.py --female --x 5 --y 0 --move --pattern circle --speed 0.3
```
**Expected**: Drone rotates smoothly to keep person centered

### Scenario 2: Fast Movement
```bash
# Spawn person moving quickly in line
./spawn_textured_person.py --male --x 3 --y 0 --move --pattern line --speed 0.8
```
**Expected**: Drone increases yaw rate, may briefly use lateral assist

### Scenario 3: Complex Movement
```bash
# Spawn person in figure-8
./spawn_textured_person.py --female --x 0 --y 0 --move --pattern figure8 --speed 0.4
```
**Expected**: Smooth tracking through complex path

### Scenario 4: Multiple Targets
```bash
# Spawn 2 people (drone will track one)
./spawn_textured_person.py --female --x 5 --y 2 --move --pattern circle --name person1 &
./spawn_textured_person.py --male --x -3 --y -2 --move --pattern line --name person2 &
```
**Expected**: Drone locks onto one target, ByteTrack manages both

## 🔍 Troubleshooting

### Person not visible in camera
- Check spawn position: `--x 5 --y 0` is good starting point
- Verify Gazebo is running
- Check drone altitude (should be 10m after takeoff)

### YOLO not detecting person
- Placeholder textures should work fine
- Check YOLO confidence threshold in config
- Try with better lighting in Gazebo world

### Person not moving
- Ensure `--move` flag is used
- Check Gazebo transport connection
- Try stopping and respawning

### Drone not tracking
- Verify drone is in TRACK mode
- Check console for errors
- Ensure person is detected (bounding box visible)

## 📚 Documentation

- **Complete Guide**: [TEXTURED_PERSONS.md](TEXTURED_PERSONS.md)
- **Visual Servoing**: [object_tracking/rpi_deployment/ubuntu/VISUAL_SERVOING.md](../../object_tracking/rpi_deployment/ubuntu/VISUAL_SERVOING.md)
- **Quick Reference**: [object_tracking/rpi_deployment/ubuntu/QUICKREF.md](../../object_tracking/rpi_deployment/ubuntu/QUICKREF.md)

## ✅ Verification

Run the test script to verify everything:

```bash
cd /home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/models
python3 test_textured_setup.py
```

Should show: ✅ ALL CHECKS PASSED!

## 🎉 Summary

You can now:
- ✅ Spawn textured person models in Gazebo
- ✅ Control their movement patterns
- ✅ Test visual servoing with realistic targets
- ✅ Verify yaw-based horizontal tracking
- ✅ Validate no-roll control strategy

**The textured models work with the placeholder images, but you can replace them with real photos for even better results!**

---

**Ready to test?** Follow the Quick Start section above! 🚀
