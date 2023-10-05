#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
This script connects to a Petoi robot via serial communication, sends a series
of commands to the robot, and provides an interface for the user to quit the script.
"""

# Standard Library
from enum import Enum
import logging
import os
import sys
import time
import threading

# Local Modules
# Adding the parent directory to the system path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import ardSerial as ard

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class JointID(Enum):
    HEAD_PAN = 0
    HEAD_TILT = 1
    LEFT_FRONT_HIP = 8
    RIGHT_FRONT_HIP = 9
    FRONT_LEFT_KNEE_PITCH = 12
    FRONT_RIGHT_KNEE_PITCH = 13
    REAR_RIGHT_KNEE_PITCH = 14
    REAR_LEFT_KNEE_PITCH = 15

class PetoiController:
    INITIAL_SLEEP_TIME = 3
    SEND_DELAY = 1
    DEFAULT_SERVO_DELAY = 0.5

    def __init__(self):
        self._exit_flag = False
        self.connected_ports = {}
        self.initialize_connection()

    @property
    def exit_flag(self):
        return self._exit_flag

    def initialize_connection(self):
        ard.connectPort(self.connected_ports)

        # Only use one port for communication
        if len(self.connected_ports) > 1:
            first_key = next(iter(self.connected_ports))
            self.connected_ports = {first_key: self.connected_ports[first_key]}

        if self.connected_ports:
            time.sleep(self.INITIAL_SLEEP_TIME)
            self.send_initial_commands()

    def send_command(self, command, delay=SEND_DELAY):
        ard.send(self.connected_ports, command)
        time.sleep(delay)

    def send_initial_commands(self):
        self.send_command(['g', 1])
        self.send_command(['ksit', 1])
        self.send_command(['I', [JointID.FRONT_LEFT_KNEE_PITCH.value, 90, 
                        JointID.FRONT_RIGHT_KNEE_PITCH.value, 90, 
                        JointID.REAR_RIGHT_KNEE_PITCH.value, -40, 
                        JointID.REAR_LEFT_KNEE_PITCH.value, -40], 1])

    def check_user_input(self):
        while not self.exit_flag:
            user_command = input("Press Enter to continue or 'q' + Enter to quit: ")
            if user_command == 'q':
                self._exit_flag = True
                logger.info("Received 'q' command. Exiting soon...")

    def send_robot_commands(self):
        while not self._exit_flag:
            for i in range(1, 20):
                if self._exit_flag:
                    break

                left_front_hip_angle = i - 50
                right_front_hip_angle = i - 50

                command = [
                    'I', 
                    [JointID.LEFT_FRONT_HIP.value, left_front_hip_angle, 
                     JointID.RIGHT_FRONT_HIP.value, right_front_hip_angle], 
                    self.DEFAULT_SERVO_DELAY
                ]
                print(command)
                ard.send(self.connected_ports, command)
                time.sleep(self.SEND_DELAY)

            for i in range(18, -1, -1):
                if self._exit_flag:
                    break
                
                left_front_hip_angle = i - 50
                right_front_hip_angle = i - 50

                command = [
                    'I', 
                    [JointID.LEFT_FRONT_HIP.value, left_front_hip_angle, 
                     JointID.RIGHT_FRONT_HIP.value, right_front_hip_angle], 
                    self.DEFAULT_SERVO_DELAY
                ]
                print(command)
                ard.send(self.connected_ports, command)
                time.sleep(self.SEND_DELAY)

    def close_all(self):
        ard.closeAllSerial(self.connected_ports)
        logger.info("Finished!")

    def run(self):
        try:
            # Ensure there's a connection before proceeding
            if not self.connected_ports:
                logger.error("No ports connected. Exiting.")
                return

            input_thread = threading.Thread(target=self.check_user_input)
            input_thread.start()

            self.send_robot_commands()
            self.close_all()

        except Exception as e:
            logger.error(f"Exception: {e}")
            self.close_all()
            raise e


if __name__ == '__main__':

    controller = PetoiController()
    controller.run()
