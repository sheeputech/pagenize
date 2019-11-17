from termcolor import colored
import sys


class Logger:
    """
    Logger provides functions for logging
    """

    def __print_color_message(self, message: str, color: str):
        print(colored(message, color), flush=True)

    @classmethod
    def info(self, message):
        print(message, flush=True)

    @classmethod
    def primary(self, message):
        self.__print_color_message(message, "green")

    @classmethod
    def warn(self, message):
        self.__print_color_message(message, "yellow")

    @classmethod
    def fatal(self, message):
        self.__print_color_message(message, "red")
        sys.exit()
