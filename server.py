import sys
import socket
import threading
import json
import checker

CMD_LISTEN = "-listen"
CMD_LIST_ALL_DEVICES = "-list-all-devices"
CMD_CREATE_REPORT = "-create-report"
CMD_CHANGE_CLIENT_REPORT_TIME = "-change-report-time"

HEADER = 64
PORT = 12345
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

MESSAGE_WRONG_PREFIX = "Wrong prefix"

msg_type_dict = {
    ">": "Add new report"
}


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

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    print("[STARTING] server is starting...")

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()

        # Create new thread for each connection
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    msg_length = conn.recv(HEADER).decode(FORMAT)

    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
        if msg[0] not in msg_type_dict:
            conn.send(MESSAGE_WRONG_PREFIX.encode(FORMAT))
            conn.close()
            return

        msg_type = msg_type_dict[msg[0]]
        report = json.loads(msg[1:])
        checker.validate_report(report)
        print(f"[{addr}] {msg_type}")
        conn.send("Successful".encode(FORMAT))

    conn.close()


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


def create_report_in_csv(id):
    """
    Load <id>_report.json
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
    elif argv[0] == CMD_LISTEN:
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

        create_report_in_csv(id)
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
