#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import socket
import threading

HOST = "192.168.23.202"
PORT = 5000

class TCPPosePublisher(Node):

    def __init__(self):
        super().__init__('tcp_pose_publisher')
        self.publisher_ = self.create_publisher(String, 'pose_points', 10)

        thread = threading.Thread(target=self.start_server)
        thread.daemon = True
        thread.start()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(5)
        self.get_logger().info("TCP Server Started...")

        while True:
            conn, addr = server.accept()
            self.get_logger().info(f"Connected: {addr}")

            data = conn.recv(4096).decode()
            conn.close()

            msg = String()
            msg.data = data
            self.publisher_.publish(msg)
            self.get_logger().info("Published pose data")

def main(args=None):
    rclpy.init(args=args)
    node = TCPPosePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

