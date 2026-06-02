#!/usr/bin/env python3

import socket
import struct
import time
import threading


class DeltoGripper:
    def __init__(self, ip_address="169.254.186.72", port=502):
        self.ip_address = ip_address
        self.port = port
        self.socket = None

        self.current_target = None
        self.target_lock = threading.Lock()
        self.target_updated = threading.Event()
        self.stop_event = threading.Event()

        self.control_thread = None
        self.control_running = False
        self.comm_lock = threading.Lock()

        self.overrides = [None] * 12
        self.overrides_lock = threading.Lock()

    # ---------------- CONNECTION ----------------
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.ip_address, self.port))
            print("[Gripper] Connected")
            return True
        except Exception as e:
            print(f"[Gripper] Connection failed: {e}")
            return False

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            print("[Gripper] Disconnected")

    # ---------------- LOW LEVEL ----------------
    def calculate_crc16(self, data):
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if (crc & 1) else (crc >> 1)
        return crc

    def set_motor_duties(self, duties):
        if not self.socket:
            return

        packet = bytes([0x03, 0x28])
        for i, duty in enumerate(duties, 1):
            packet += bytes([i])
            packet += struct.pack(">h", max(-1000, min(1000, duty)))

        crc = self.calculate_crc16(packet)
        packet += struct.pack("<H", crc)

        with self.comm_lock:
            self.socket.send(packet)

    def read_motor_positions(self):
        if not self.socket:
            return None

        packet = bytes([0x01, 0x05, 0xEE])
        crc = self.calculate_crc16(packet)
        packet += struct.pack("<H", crc)

        with self.comm_lock:
            self.socket.send(packet)
            response = self.socket.recv(4096)

        positions = {}
        for i in range(12):
            base = 2 + i * 5
            if base + 2 >= len(response):
                break
            motor = response[base]
            pos = (response[base + 1] << 8) | response[base + 2]
            if pos > 32767:
                pos -= 65536
            positions[motor] = pos * 0.1

        return positions

    # ---------------- CONTROL LOOP ----------------
    def start_hold_loop(self, target):
        self.current_target = list(target)
        self.stop_event.clear()

        def loop():
            while not self.stop_event.is_set():
                pos = self.read_motor_positions()
                if not pos:
                    time.sleep(0.1)
                    continue

                duties = []
                for i in range(12):
                    error = self.current_target[i] - pos.get(i + 1, 0)
                    duty = int(error * 20)
                    duties.append(max(-600, min(600, duty)))

                self.set_motor_duties(duties)
                time.sleep(0.05)

        self.control_thread = threading.Thread(target=loop, daemon=True)
        self.control_thread.start()

    def update_target(self, target):
        self.current_target = list(target)

    def stop(self):
        self.stop_event.set()
        self.set_motor_duties([0] * 12)
