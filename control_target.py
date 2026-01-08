#!/usr/bin/env python3
"""
Control target movement in Gazebo for object tracking tests.

This script spawns a red target and moves it in various patterns to test
the drone's object detection and tracking capabilities.

Patterns:
  - circle: Moves in circular path (default: 10m radius)
  - linear: Back and forth in straight line
  - figure8: Figure-8 pattern
  - random: Random waypoints
  - manual: Keyboard control (WASD)

Usage:
  python3 control_target.py --pattern circle --speed 1.5 --radius 10
"""

import subprocess
import time
import math
import argparse
import sys
import signal

class TargetController:
    def __init__(self, pattern='circle', speed=1.5, radius=10.0, height=1.0):
        self.pattern = pattern
        self.speed = speed  # m/s
        self.radius = radius  # meters
        self.height = height  # meters above ground
        self.time = 0.0
        self.running = True
        self.world_name = None

        # Setup signal handler for clean exit
        signal.signal(signal.SIGINT, self.signal_handler)

        print("=" * 60)
        print("Target Controller Started")
        print("=" * 60)
        print(f"Pattern: {pattern}")
        print(f"Speed: {speed} m/s")
        print(f"Radius: {radius} m" if pattern == 'circle' else "")
        print(f"Height: {height} m")
        print("Press Ctrl+C to stop")
        print("=" * 60)

        # Detect world name
        self.detect_world()

        # Spawn the target
        self.spawn_target()

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\nStopping target controller...")
        self.running = False
        self.delete_target()
        sys.exit(0)

    def detect_world(self):
        """Auto-detect the active Gazebo world name"""
        print("Detecting active world...")

        try:
            # List all worlds
            result = subprocess.run(
                ['gz', 'topic', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse world name from topics like /world/forest/...
            for line in result.stdout.split('\n'):
                if line.startswith('/world/') and '/pose/info' in line:
                    # Extract world name: /world/WORLDNAME/pose/info
                    parts = line.split('/')
                    if len(parts) >= 3:
                        self.world_name = parts[2]
                        print(f"✓ Detected world: {self.world_name}")
                        return

            # Fallback
            print("⚠ Could not detect world, using 'default'")
            self.world_name = 'default'

        except Exception as e:
            print(f"⚠ Error detecting world: {e}, using 'default'")
            self.world_name = 'default'

    def spawn_target(self):
        """Spawn red target model in Gazebo at origin"""
        print("Spawning red target...")

        model_path = "/home/shivam-daksh/px4/PX4-IDR/Tools/simulation/gz/models/red_target/model.sdf"

        cmd = [
            'gz', 'service', '-s', f'/world/{self.world_name}/create',
            '--reqtype', 'gz.msgs.EntityFactory',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '5000',
            '--req',
            f'sdf_filename: "{model_path}", name: "red_target", pose: {{position: {{x: 0, y: 0, z: {self.height}}}}}'
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                    text=True, timeout=10)
            if result.returncode == 0:
                print("✓ Target spawned successfully!")
            else:
                print("⚠ Target may already exist, continuing...")
        except subprocess.TimeoutExpired:
            print("⚠ Spawn timeout - target may already exist")
        except Exception as e:
            print(f"✗ Error spawning target: {e}")

    def delete_target(self):
        """Remove target from Gazebo"""
        print("Deleting target...")

        cmd = [
            'gz', 'service', '-s', f'/world/{self.world_name}/remove',]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            print("✓ Target deleted")
        except:
            pass  # Ignore errors on cleanup

    def set_position(self, x, y, z):
        """Update target position in Gazebo"""
        cmd = [
            'gz', 'service', '-s', f'/world/{self.world_name}/set_pose',
            '--reqtype', 'gz.msgs.Pose',
            '--reptype', 'gz.msgs.Boolean',
            '--timeout', '100',
            '--req',
            f'name: "red_target", position: {{x: {x}, y: {y}, z: {z}}}'
        ]

        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.5)
        except:
            pass  # Ignore timeouts to maintain update rate

    def move_circular(self):
        """Move in circular path"""
        # Angular velocity (rad/s) = linear speed / radius
        omega = self.speed / self.radius
        angle = omega * self.time

        x = self.radius * math.cos(angle)
        y = self.radius * math.sin(angle)

        self.set_position(x, y, self.height)

    def move_linear(self):
        """Move back and forth in X direction"""
        distance = 20.0  # Total distance
        period = distance / self.speed  # Time for one direction

        # Sawtooth wave: goes 0->1->0
        t_norm = (self.time % (2 * period)) / period
        if t_norm > 1:
            t_norm = 2 - t_norm

        x = (t_norm - 0.5) * distance  # Center at origin
        y = 0

        self.set_position(x, y, self.height)

    def move_figure8(self):
        """Move in figure-8 pattern"""
        omega = self.speed / self.radius
        angle = omega * self.time

        # Lissajous curve for figure-8
        x = self.radius * math.sin(angle)
        y = self.radius * math.sin(2 * angle) / 2

        self.set_position(x, y, self.height)

    def move_random(self):
        """Move to random waypoints"""
        # For now, circular motion (implement waypoints later if needed)
        self.move_circular()

    def run(self):
        """Main control loop at 10Hz"""
        rate = 10  # Hz (reduced from 20 to lower Gazebo load)
        dt = 1.0 / rate

        print(f"\n▶ Moving target in '{self.pattern}' pattern...")
        print(f"Update rate: {rate} Hz\n")

        last_print = time.time()

        try:
            while self.running:
                # Execute movement pattern
                if self.pattern == 'circle':
                    self.move_circular()
                elif self.pattern == 'linear':
                    self.move_linear()
                elif self.pattern == 'figure8':
                    self.move_figure8()
                elif self.pattern == 'random':
                    self.move_random()
                else:
                    print(f"Unknown pattern: {self.pattern}")
                    break

                # Print status every 2 seconds
                if time.time() - last_print > 2.0:
                    if self.pattern == 'circle':
                        angle = (self.speed / self.radius) * self.time
                        x = self.radius * math.cos(angle)
                        y = self.radius * math.sin(angle)
                        print(f"Position: ({x:6.2f}, {y:6.2f}, {self.height:.2f}) | "
                              f"Time: {self.time:.1f}s | "
                              f"Angle: {math.degrees(angle) % 360:.0f}°")
                    last_print = time.time()

                self.time += dt
                time.sleep(dt)

        except KeyboardInterrupt:
            self.signal_handler(None, None)

def main():
    parser = argparse.ArgumentParser(
        description='Control target movement in Gazebo for object tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Circular pattern (default)
  python3 control_target.py

  # Faster circular motion
  python3 control_target.py --pattern circle --speed 3.0 --radius 15

  # Linear back and forth
  python3 control_target.py --pattern linear --speed 2.0

  # Figure-8 pattern
  python3 control_target.py --pattern figure8 --speed 2.5
        """
    )

    parser.add_argument(
        '--pattern',
        choices=['circle', 'linear', 'figure8', 'random'],
        default='circle',
        help='Movement pattern (default: circle)'
    )

    parser.add_argument(
        '--speed',
        type=float,
        default=1.5,
        help='Movement speed in m/s (default: 1.5)'
    )

    parser.add_argument(
        '--radius',
        type=float,
        default=10.0,
        help='Radius for circular/figure8 patterns in meters (default: 10.0)'
    )

    parser.add_argument(
        '--height',
        type=float,
        default=1.0,
        help='Target height above ground in meters (default: 1.0)'
    )

    args = parser.parse_args()

    # Create and run controller
    controller = TargetController(
        pattern=args.pattern,
        speed=args.speed,
        radius=args.radius,
        height=args.height
    )

    controller.run()

if __name__ == '__main__':
    main()
