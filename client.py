import sys
import os
import time
import psutil

CMD_REGISTER = "-register"
CMD_MONITOR_SYSTEM = "-monitor-system"


def print_usage():
    pre_cmd = "python client.py "
    print(pre_cmd + CMD_REGISTER)
    print(pre_cmd + CMD_MONITOR_SYSTEM)


def register():
    """
    Register this computer (Client) to the Server
    Send TCP message to Server, including: Name, IP, UDP port, Current date time
    Then listen for the response
        If responded msg is successful then:
            Retrieve from response: id, server_tcp_port, recurring_time
            Write those data into client.json
            Start monitor system
        Else responded msg is failed, display error message
    """
    pass


def monitor_system():
    """
    Check if (current time - init time) % recurring_time = 0
    If True then send data msg to Server
    """
    pass


def main(argv):
    if len(argv) < 1:
        print_usage()
    if argv[0] == CMD_REGISTER:
        register()
    elif argv[0] == CMD_MONITOR_SYSTEM:
        monitor_system()


if __name__ == "__main__":
    main(sys.argv[1:])
