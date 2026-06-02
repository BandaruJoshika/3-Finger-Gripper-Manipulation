#!/usr/bin/env python3

import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer

from gripper_interfaces.action import MoveGripper
from gripper.gripper_driver import DeltoGripper


class GripperActionServer(Node):

    def __init__(self):
        super().__init__('gripper_action_server')

        self.gripper = DeltoGripper()
        self.gripper.connect()

        self._action_server = ActionServer(
            self,
            MoveGripper,
            'move_gripper',
            self.execute_callback
        )

        self.get_logger().info("Gripper Action Server Ready")

    async def execute_callback(self, goal_handle):

        self.get_logger().info("Goal received")

        target = goal_handle.request.target_positions
        self.gripper.update_target(target)
        self.gripper.start_hold_loop(target)

        feedback_msg = MoveGripper.Feedback()
        result = MoveGripper.Result()

        while rclpy.ok():

            positions = self.gripper.read_motor_positions()
            if not positions:
                continue

            current = [positions.get(i + 1, 0.0) for i in range(12)]

            feedback_msg.current_positions = current
            goal_handle.publish_feedback(feedback_msg)

            errors = [abs(current[i] - target[i]) for i in range(12)]

            if max(errors) < 1.0:
                break

            time.sleep(0.1)

        goal_handle.succeed()
        result.success = True

        self.get_logger().info("Goal completed")

        return result


def main():
    rclpy.init()
    node = GripperActionServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

