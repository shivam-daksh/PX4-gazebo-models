// car_teleport.cc
// Standalone binary: reads "speed yawRate\n" lines from stdin,
// integrates a bicycle-model pose, and calls the Gazebo set_pose service
// at 30 Hz. This bypasses physics entirely — reliable for SITL.
//
// Usage: car_teleport <world_name> [model_name]
//   world_name  – e.g. iris_runway, default
//   model_name  – default: car

#include <gz/transport/Node.hh>
#include <gz/msgs/pose.pb.h>
#include <gz/msgs/boolean.pb.h>
#include <gz/math/Pose3.hh>
#include <gz/math/Quaternion.hh>

#include <atomic>
#include <chrono>
#include <cmath>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>

static std::atomic<double> g_speed{0.0};
static std::atomic<double> g_yawRate{0.0};

// ── stdin reader thread ────────────────────────────────────────────────────
void stdinReader()
{
  std::string line;
  while (std::getline(std::cin, line))
  {
    if (line.empty()) continue;
    double s = 0.0, yr = 0.0;
    std::istringstream ss(line);
    ss >> s >> yr;
    g_speed.store(s);
    g_yawRate.store(yr);
  }
  // stdin closed → stop the car
  g_speed.store(0.0);
  g_yawRate.store(0.0);
}

// ── main ──────────────────────────────────────────────────────────────────
int main(int argc, char **argv)
{
  const std::string worldName = (argc > 1) ? argv[1] : "default";
  const std::string modelName = (argc > 2) ? argv[2] : "car";

  const std::string service =
      "/world/" + worldName + "/set_pose";

  gz::transport::Node node;

  // Verify service exists
  std::vector<std::string> services;
  node.ServiceList(services);
  bool found = false;
  for (const auto &s : services)
    if (s == service) { found = true; break; }

  if (!found)
  {
    std::cerr << "[car_teleport] Service not found: " << service
              << "\n  Available worlds:\n";
    for (const auto &s : services)
      if (s.find("/set_pose") != std::string::npos)
        std::cerr << "    " << s << "\n";
    return 1;
  }

  std::cerr << "[car_teleport] Ready on " << service
            << "  model=" << modelName << "\n";

  // Start stdin reader
  std::thread reader(stdinReader);
  reader.detach();

  // Give Gazebo a moment
  std::this_thread::sleep_for(std::chrono::milliseconds(200));

  // Pose state
  double x   = 5.0;
  double y   = 0.0;
  double z   = 0.03; // Prius chassis height
  double yaw = 0.0;

  const double dt    = 1.0 / 30.0;   // 30 Hz
  const auto   period = std::chrono::duration<double>(dt);

  while (true)
  {
    auto t0 = std::chrono::steady_clock::now();

    const double speed   = g_speed.load();
    const double yawRate = g_yawRate.load();

    // Bicycle model integration
    yaw += yawRate * dt;
    yaw  = std::atan2(std::sin(yaw), std::cos(yaw));  // normalise
    x   += speed * std::sin(yaw) * dt;
    y   += speed * -std::cos(yaw) * dt;

    // Build Pose message
    gz::msgs::Pose req;
    req.set_name(modelName);
    req.mutable_position()->set_x(x);
    req.mutable_position()->set_y(y);
    req.mutable_position()->set_z(z);

    // Yaw → quaternion (roll=0, pitch=0)
    const double halfYaw = yaw * 0.5;
    req.mutable_orientation()->set_x(0.0);
    req.mutable_orientation()->set_y(0.0);
    req.mutable_orientation()->set_z(std::sin(halfYaw));
    req.mutable_orientation()->set_w(std::cos(halfYaw));

    // Non-blocking service call (fire and forget)
    gz::msgs::Boolean rep;
    bool result = false;
    node.Request(service, req, 100, rep, result);

    // Sleep for remainder of 30 Hz period
    auto elapsed = std::chrono::steady_clock::now() - t0;
    auto remaining = period - elapsed;
    if (remaining > std::chrono::duration<double>(0))
      std::this_thread::sleep_for(remaining);
  }

  return 0;
}
