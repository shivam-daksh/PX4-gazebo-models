// car_cmd_pub.cc
// Minimal C++ bridge: reads "speed yawRate\n" lines from stdin,
// publishes gz.msgs.Twist to /model/car/cmd_vel.
// Python opens this as a subprocess and writes to its stdin.

#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>

#include <iostream>
#include <sstream>
#include <string>

int main()
{
  gz::transport::Node node;
  auto pub = node.Advertise<gz::msgs::Twist>("/model/car/cmd_vel");

  if (!pub)
  {
    std::cerr << "[car_cmd_pub] Failed to advertise topic\n";
    return 1;
  }

  // Give transport a moment to discover subscribers
  std::this_thread::sleep_for(std::chrono::milliseconds(200));

  std::string line;
  while (std::getline(std::cin, line))
  {
    if (line.empty()) continue;

    double speed = 0.0, yawRate = 0.0;
    std::istringstream iss(line);
    iss >> speed >> yawRate;

    gz::msgs::Twist msg;
    msg.mutable_linear()->set_x(speed);
    msg.mutable_angular()->set_z(yawRate);
    pub.Publish(msg);
  }

  return 0;
}
