#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
This script connects to a Petoi robot via serial communication, sends a series
of commands to the robot, and provides an interface for the user to quit the script.
"""

# Standard Library
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


class PetoiController:
    INITIAL_SLEEP_TIME = 3
    SEND_DELAY = 1

    def __init__(self):
        self._exit_flag = False
        self.connected_ports = {}
        self.initialize_connection()

    @property
    def exit_flag(self):
        return self._exit_flag

    def initialize_connection(self):
        ard.connectPort(self.connected_ports)

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
        self.send_command(['I', [12, 90, 13, 90, 14, -40, 15, -40], 1])

    def check_user_input(self):
        while not self.exit_flag:
            user_command = input("Press Enter to continue or 'q' + Enter to quit: ")
            if user_command == 'q':
                self._exit_flag = True
                logger.info("Received 'q' command. Exiting soon...")

    def send_robot_commands(self):
        while not self.exit_flag:
            for i in range(1, 20):
                if self.exit_flag:
                    break
                command = ['I', [8, i-50, 9, i-50], 0.5]
                logger.info(command)
                self.send_command(command)

            for i in range(18, -1, -1):
                if self.exit_flag:
                    break
                command = ['I', [8, i-50, 9, i-50], 0.5]
                logger.info(command)
                self.send_command(command)

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
