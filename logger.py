from termcolor import colored


class Logger:
    """
    Logger provides functions for logging
    """

    def print_color_message(self, message: str, color: str):
        print(colored(message, color), flush=True)

    def info(self, message):
        print(message, flush=True)

    def primary(self, message):
        self.print_color_message(message, "green")

    def warn(self, message):
        self.print_color_message(message, "yellow")

    def fatal(self, message):
        self.print_color_message(message, "red")
        sys.exit()
