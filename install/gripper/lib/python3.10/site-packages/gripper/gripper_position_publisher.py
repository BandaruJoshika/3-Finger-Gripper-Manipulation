#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

from gripper.gripper_driver import DeltoGripper


class GripperPositionPublisher(Node):

    def __init__(self):
        super().__init__('gripper_position_publisher')

        self.gripper = DeltoGripper()
        self.gripper.connect()

        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/gripper/positions',
            10
        )

        self.timer = self.create_timer(0.1, self.publish_positions)

        self.get_logger().info("Publishing motor positions")

    def publish_positions(self):

        positions = self.gripper.read_motor_positions()

        if not positions:
            return

        msg = Float64MultiArray()
        msg.data = [positions.get(i + 1, 0.0) for i in range(12)]

        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = GripperPositionPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

