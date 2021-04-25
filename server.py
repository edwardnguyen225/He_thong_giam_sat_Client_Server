import sys
import os
import time
import psutil

CMD_LISTEN = "-listen"
CMD_LIST_ALL_DEVICES = "-list-all-devices"
CMD_CREATE_REPORT = "-create-report"
CMD_CHANGE_CLIENT_REPORT_TIME = "-change-report-time"


def print_usage():
    pre_cmd = "python server.py "
    print(pre_cmd + CMD_LISTEN)
    print(pre_cmd + CMD_LIST_ALL_DEVICES)
    print(pre_cmd + CMD_CREATE_REPORT + "<device's id>")
    print(pre_cmd + CMD_CHANGE_CLIENT_REPORT_TIME +
          "<device's id> + <time in seconds>")


def listen():
    """
    Listen continuously for Client msgs
    If receive register msg then:
        Check if msg is valid:
            If not then send back error
        Create new client
        Then send successful msg to client

    Else if receive report msg then:
        Check if msg is valid:
            If not then send back error
        Store report into Client_reports.json
        Then send successful msg to client
    """
    pass


def create_new_client(name, ip, udp_port, register_date):
    """
    Create new client
    Save new client into List_of_clients.json
    Return True if successful, else False
    """
    pass


def list_all_devices():
    """
    Read List_of_clients.json
    Print all devices from that list, including device's name and ID
    """
    pass


def create_report(id):
    """
    Find all report having client's id
    Write all into <id>_report.csv? 
    !!! NOTE: need to discuss bout the output file extension
    """
    if id == None:
        return None
    pass


def change_client_report_time(id, report_time):
    """
    Send UCP msg to client including TCP port, recurring time
    If id == -10 then send to all clients
    """
    pass


def main(argv):
    if len(argv) < 1:
        print_usage()
    if argv[0] == CMD_LISTEN:
        listen()
    elif argv[0] == CMD_LIST_ALL_DEVICES:
        list_all_devices()
    elif argv[0] == CMD_CREATE_REPORT:
        id = int(argv[1])
        while id == None or id != -1:
            print("Please insert client's ID.")
            print("If you want to cancel, insert -1")
            id = input("Client ID:")
        if id == -1:
            return

        create_report(id)
    elif argv[0] == CMD_CHANGE_CLIENT_REPORT_TIME:
        id = int(argv[1])
        while id == None or id != -1:
            print("Please insert client's ID.")
            print("If you want to cancel, insert -1")
            print("If you want to send all, insert -10")
            id = input("Client ID:")
        if id == -1:
            return

        report_time = argv[2]
        change_client_report_time(id, report_time)


if __name__ == "__main__":
    main(sys.argv[1:])
