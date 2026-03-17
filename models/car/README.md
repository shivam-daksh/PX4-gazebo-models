# Realistic Car Model for YOLO Detection

## Overview
This is a realistic Toyota Prius Hybrid 3D model downloaded from Gazebo Fuel, designed to work with YOLO object detection models.

## Model Details
- **Type**: Toyota Prius Hybrid
- **Format**: Wavefront OBJ with materials
- **Textures**: High-resolution car textures included
- **Dimensions**: ~4.5m length, ~1.8m width, realistic car proportions
- **Physics**: Proper collision boxes, realistic mass (1326 kg) and inertia

## Files
- `model.sdf` - Gazebo SDF model definition
- `model.config` - Model configuration
- `meshes/Hybrid.obj` - 3D mesh (204KB)
- `meshes/Hybrid.mtl` - Material definitions
- `materials/textures/` - Car textures (body, interior, wheels)

## YOLO Detection
This model is ideal for YOLO because:
- ✅ Realistic car appearance trained in COCO/ImageNet datasets
- ✅ Proper proportions and features (windows, wheels, body)
- ✅ High-quality textures for better recognition
- ✅ Standard sedan shape recognized as "car" class

## Usage
Use with `manual_control_car.py` to spawn and control the car in Gazebo simulation.

## Credits
Model source: OpenRobotics via Gazebo Fuel
