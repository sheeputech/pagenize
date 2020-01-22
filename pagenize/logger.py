from termcolor import colored
import sys


class Logger:
    """
    Logger provides functions for logging
    """

    @classmethod
    def info(cls, message):
        print(message, flush=True)

    @classmethod
    def primary(cls, essage):
        __print_color_message(message, 'green')

    @classmethod
    def warn(cls, message):
        __print_color_message(message, 'yellow')

    @classmethod
    def fatal(cls, message):
        __print_color_message(message, 'red')
        sys.exit()

    @classmethod
    def color_str(cls, message, color: str = 'white') -> str:
        return colored(message, color)

    @classmethod
    def __print_color_message(cls, self, message: str, color: str):
        print(colored(message, color), flush=True)
