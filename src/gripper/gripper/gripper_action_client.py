#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from gripper_interfaces.action import MoveGripper


HOME = [0.0] * 12
BALL = [-5,-2.3,62,69,-60,-1.6,57.5,69.2,60,-2.3,54.8,68.4]


class GripperActionClient(Node):

    def __init__(self):
        super().__init__('gripper_action_client')

        self._action_client = ActionClient(
            self,
            MoveGripper,
            'move_gripper'
        )

    def send_goal(self, target):

        goal_msg = MoveGripper.Goal()
        goal_msg.target_positions = target

        self._action_client.wait_for_server()

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info("Goal rejected")
            return

        self.get_logger().info("Goal accepted")

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"Current positions: {feedback.current_positions}")

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Result: {result.success}")
        rclpy.shutdown()


def main():
    rclpy.init()

    client = GripperActionClient()

    print("Select target:")
    print("1 → HOME")
    print("2 → BALL")

    choice = input("Enter option: ")

    if choice == "1":
        target = HOME
    elif choice == "2":
        target = BALL
    else:
        print("Invalid choice")
        return

    client.send_goal(target)

    rclpy.spin(client)

