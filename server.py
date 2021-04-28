import sys
import socket
import threading
import json
import checker
import os
import csv

from tabulate import tabulate
try:
    from collections.abc import MutableMapping
except ModuleNotFoundError:
    from collections import MutableMapping

CMD_LISTEN = "-listen"
CMD_LIST_ALL_CLIENTS = "-list-all-clients"
CMD_CREATE_REPORT = "-create-report"
CMD_CHANGE_CLIENT_REPORT_TIME = "-change-report-time"

HEADER = 64
PORT = 12345
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

MSG_SUCCESS = "[Successful]"

PREFIX_FAILED = "[Failed]"
MSG_ERR_WRONG_PREFIX = PREFIX_FAILED + "MsgPrefixError"
MSG_ERR_UNKNOWN_ID = PREFIX_FAILED + "UnknownIDError"
MSG_ERR_UNKNOWN_NAME = PREFIX_FAILED + "UnknownNameError"


msg_type_dict = {
    ">": "Add new report"
}

path_to_list_of_clients = os.path.join(
    ".", "database", "server", "List_of_clients.json")

with open(path_to_list_of_clients) as f:
    list_of_clients = json.load(f)


def print_usage():
    pre_cmd = "python server.py "
    print(pre_cmd + CMD_LISTEN)
    print(pre_cmd + CMD_LIST_ALL_CLIENTS)
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
            conn.send(MSG_ERR_WRONG_PREFIX.encode(FORMAT))
            conn.close()
            return

        msg_type = msg_type_dict[msg[0]]

        client_name_prefix_index = msg.index("@")
        client_id = msg[1:client_name_prefix_index]
        print(f"[{addr}] {msg_type} from id({client_id})")
        if not checker.is_id_registered(client_id, list_of_clients):
            conn.send(MSG_ERR_UNKNOWN_ID.encode(FORMAT))
            conn.close()
            return

        json_start_index = msg.index("{")
        name = msg[client_name_prefix_index + 1:json_start_index]
        if not checker.is_name_correct(name, client_id, list_of_clients):
            conn.send(MSG_ERR_UNKNOWN_NAME.encode(FORMAT))
            conn.close()
            return

        report = json.loads(msg[json_start_index:])
        errors = checker.get_report_error(report)
        if errors:
            errors = PREFIX_FAILED + errors
            conn.send(errors.encode(FORMAT))
            conn.close()
            return

        add_new_report(client_id, report)
        conn.send("[Successful]".encode(FORMAT))

    conn.close()


def create_new_client(name, ip, udp_port, register_date):
    """
    Create new client
    Save new client into List_of_clients.json
    Return True if successful, else False
    """
    pass


def print_list_of_clients():
    """
    Read List_of_clients.json
    Print all devices from that list, including device's name and ID
    """
    headers = ["ID", "NAME", "IP", "UDP PORT", "REGISTER TIME"]
    table = []
    for client in list_of_clients:
        row = [client]
        row.extend(list_of_clients[client].values())
        table.append(row)
    print(tabulate(table, headers, tablefmt="psql"))


def add_new_report(id, report):
    client_report = get_client_report(id)
    client_report.update(report)
    try:
        with open(get_client_report_path(id), "w") as file:
            json.dump(client_report, file, indent=2)
    except IOError:
        raise IOError


def get_client_report_path(id):
    file_name = id + "_report.json"
    path_to_report = os.path.join(
        ".", "database", "server", "reports", file_name)
    return path_to_report


def get_client_report(id):
    # Return client report in dict
    path_to_report = get_client_report_path(id)
    with open(path_to_report) as f:
        report = json.load(f)
    return report


def create_report_in_csv(id):
    """
    Load <id>_report.json
    Write all into <id>_report.csv
    !!! NOTE: need to discuss bout the output file extension
    """
    if not checker.is_id_registered(id, list_of_clients):
        print("ID is not registered")
        return

    dir = os.path.join(".", "csv")
    if not os.path.isdir(dir):
        os.mkdir(dir)

    report = get_client_report(id)

    # Create the fieldnames from flatten dict of the first report
    fieldnames = ["Report datetime"]
    tmp_report = flatten_dict(list(report.values())[0])
    for key in tmp_report.keys():
        fieldnames.append(key)

    csv_path = os.path.join(dir, f"{id}_report.csv")
    try:
        with open(os.path.join(csv_path), mode="w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for key, value in report.items():
                row = {fieldnames[0]: key}
                value = flatten_dict(value)
                row.update(value)
                writer.writerow(row)
            csv_file.close()

            print(f"Export Client {id} report successfully. Path to CSV file is: {csv_path}")
    except IOError:
        raise IOError


def flatten_dict(d, parent_key='', sep='_'):
    """
    Flatten dict
    E.g: {'a': 1,'c': {'a': 2, 'b': {'x': 3}}}
    ---> {'a': 1,'c_a': 2,'c_b_x': 3}
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k

        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


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
    elif argv[0] == CMD_LIST_ALL_CLIENTS:
        print_list_of_clients()
    elif argv[0] == CMD_CREATE_REPORT:
        if len(argv) < 2:
            raise Exception("Required client's ID")

        id = argv[1]
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
    else:
        print_usage()


if __name__ == "__main__":
    main(sys.argv[1:])
