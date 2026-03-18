// CarControlPlugin.cc
// Gazebo Harmonic (gz-sim8) kinematic car control plugin.
// Subscribes to /model/car/cmd_vel (gz.msgs.Twist) and teleports the car
// each simulation step using a bicycle steering model.

#include <gz/plugin/Register.hh>
#include <gz/sim/Model.hh>
#include <gz/sim/System.hh>
#include <gz/sim/Util.hh>
#include <gz/sim/components/Pose.hh>
#include <gz/sim/components/PoseCmd.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <gz/math/Pose3.hh>
#include <gz/math/Quaternion.hh>

#include <chrono>
#include <cmath>
#include <mutex>
#include <string>

using namespace gz;
using namespace sim;

class CarControlPlugin
    : public System,
      public ISystemConfigure,
      public ISystemPreUpdate
{
public:
  void Configure(const Entity &entity,
                 const std::shared_ptr<const sdf::Element> &sdfElem,
                 EntityComponentManager &ecm,
                 EventManager &) override
  {
    this->model = Model(entity);

    // Ensure WorldPose component is created so PreUpdate can read it
    if (!ecm.Component<components::WorldPose>(entity))
      ecm.CreateComponent(entity, components::WorldPose());

    // Topic can be overridden in SDF: <topic>/custom/cmd</topic>
    std::string topic = "/model/car/cmd_vel";
    if (sdfElem && sdfElem->HasElement("topic"))
      topic = sdfElem->Get<std::string>("topic");

    if (!this->node.Subscribe(topic, &CarControlPlugin::OnCmdVel, this))
      gzerr << "[CarControlPlugin] Failed to subscribe to " << topic << "\n";
    else
      gzmsg << "[CarControlPlugin] Subscribed to " << topic << "\n";
  }

  void PreUpdate(const UpdateInfo &info,
                 EntityComponentManager &ecm) override
  {
    if (info.paused) return;

    const double dt =
        std::chrono::duration<double>(info.dt).count();

    std::lock_guard<std::mutex> lock(this->mtx);

    // Read current world pose via WorldPose component
    const auto *worldPoseComp =
        ecm.Component<components::WorldPose>(this->model.Entity());
    if (!worldPoseComp) return;

    const auto &worldPose = worldPoseComp->Data();
    const double yaw    = worldPose.Rot().Yaw();
    const double newYaw = yaw + this->yawRate * dt;

    // Bicycle model: forward speed projected along current yaw
    const double dx = this->speed * std::cos(yaw) * dt;
    const double dy = this->speed * std::sin(yaw) * dt;

    math::Pose3d next(
      worldPose.Pos().X() + dx,
      worldPose.Pos().Y() + dy,
      worldPose.Pos().Z(),
      0.0, 0.0, newYaw);

    this->model.SetWorldPoseCmd(ecm, next);
  }

private:
  void OnCmdVel(const msgs::Twist &msg)
  {
    std::lock_guard<std::mutex> lock(this->mtx);
    this->speed   = msg.linear().x();   // m/s forward
    this->yawRate = msg.angular().z();  // rad/s
  }

  Model            model;
  transport::Node  node;
  std::mutex       mtx;
  double speed{0.0};
  double yawRate{0.0};
};

GZ_ADD_PLUGIN(CarControlPlugin, System,
              CarControlPlugin::ISystemConfigure,
              CarControlPlugin::ISystemPreUpdate)
GZ_ADD_PLUGIN_ALIAS(CarControlPlugin, "CarControlPlugin")
