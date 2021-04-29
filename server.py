import sys
import socket
import threading
import json
import time
import checker
import os
import csv
import monitor

from datetime import datetime
from tabulate import tabulate
try:
    from collections.abc import MutableMapping
except ModuleNotFoundError:
    from collections import MutableMapping

CMD_LISTEN = "-listen"
CMD_LIST_ALL_CLIENTS = "-list-all-clients"
CMD_EXPORT_REPORT = "-export-report"
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

MSG_TYPE_REGISTER = "Register"
MSG_TYPE_REPORT = "Add new report"
msg_type_dict = {
    "#": MSG_TYPE_REGISTER,
    ">": MSG_TYPE_REPORT
}

path_to_list_of_clients = os.path.join(
    ".", "database", "server", "List_of_clients.json")

with open(path_to_list_of_clients) as f:
    list_of_clients = json.load(f)


def print_usage():
    pre_cmd = "python server.py "
    print(pre_cmd + CMD_LISTEN)
    print(pre_cmd + CMD_LIST_ALL_CLIENTS)
    print(pre_cmd + CMD_EXPORT_REPORT + "<client's id>")
    print(pre_cmd + CMD_CHANGE_CLIENT_REPORT_TIME +
          "<client's id> + <time in seconds>")


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
        thread = threading.Thread(
            target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
        # print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


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
        print("\n" + msg + "\n")
        if msg_type == MSG_TYPE_REPORT:
            handle_client_report(conn, addr, msg)
        elif msg_type == MSG_TYPE_REGISTER:
            handle_client_register(conn, addr, msg)

    conn.close()


def handle_client_report(conn, addr, msg):
    """
    prefix = ">"
    valid msg = prefix + "<id>@<client name><report in json>"
    """
    client_name_prefix_index = msg.index("@")
    client_id = msg[1:client_name_prefix_index]
    print(f"[{addr}] {MSG_TYPE_REPORT} from id({client_id})")
    if not checker.is_id_registered(client_id, list_of_clients):
        conn.send(MSG_ERR_UNKNOWN_ID.encode(FORMAT))
        return

    json_start_index = msg.index("{")
    name = msg[client_name_prefix_index + 1:json_start_index]
    if not checker.is_name_correct(name, client_id, list_of_clients):
        conn.send(MSG_ERR_UNKNOWN_NAME.encode(FORMAT))
        return

    report = json.loads(msg[json_start_index:])
    errors = checker.get_report_error(report)
    if errors:
        errors = PREFIX_FAILED + errors
        conn.send(errors.encode(FORMAT))
        return

    add_new_report(client_id, report)
    conn.send("[Successful]".encode(FORMAT))


def handle_client_register(conn, addr, msg):
    """
    prefix = "#"
    valid msg = prefix + "<name>,<ip>,<udp_port>"
    Return: "[RegisterSuccess]<id>,<server_ip>,<server_tcp_port>,<recurring_time>" if successful
            else "[RegisterFailed]"
    """
    msg_success = "[RegisterSuccess]"
    msg_failed = "[RegisterFailed]"
    print(f"[NEW REGISTRATION] Got new registration from {addr}")

    try:
        name, udp_port = msg[1:].split(",")

        udp_port = int(udp_port)
    except Exception:
        msg_failed += "Failed before validations"
        conn.send(msg_failed.encode(FORMAT))
        print(Exception("Registration Failed"))

    id = get_new_client_id()
    create_new_client(id, name, addr, udp_port)
    msg_success += create_regis_postfix(id)
    conn.send(msg_success.encode(FORMAT))


def create_new_client(id, name, ip, udp_port):
    """
    Create new client
    Save new client into List_of_clients.json
    Return True if successful, else False
    """
    client = {
        "name": name,
        "ip": ip,
        "client_udp_port": udp_port,
        "register_time": str(datetime.now())
    }
    list_of_clients[id] = client
    monitor.write_JSON(list_of_clients,path_to_list_of_clients)


def create_regis_postfix(id, recurring_time=3):
    # <id>,<server_tcp_port>,<recurring_time>
    postfix = f"{id},{PORT},{recurring_time}"
    return postfix


def get_new_client_id():
    last_id = list(list_of_clients.keys())[-1]
    tmp_id = int(last_id) + 1
    id = str(tmp_id)
    return id


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


def export_report_to_csv(id):
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

            print(
                f"Export Client {id} report successfully. Path to CSV file is: {csv_path}")
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


def get_client_ip_and_udp(id):
    # Return tuple of (client_ip, client_udp_port)
    client = list_of_clients[id]
    return (client["ip"], client["client_udp_port"])


def change_client_report_time(id, new_recurring_time):
    """
    Send new report time to the client having the id passed
    """
    if not checker.is_id_registered(id, list_of_clients):
        raise Exception("ID is not registered")

    client_ip, client_udp_port = get_client_report(id)

    # TODO: Setup new connection to the client, and send new_recurring_time

    pass


def change_all_report_time(new_recurring_time):
    """
    Send new report time to the client having the id passed
    """
    for id in list_of_clients:
        client_ip, client_udp_port = get_client_report(id)
        thread = threading.Thread(
            target=change_client_report_time, args=(client_ip, client_udp_port), daemon=True)
        thread.start()


# def change_client_report_time(id, report_time):

#     if id==-10:
#     # Set a timeout so the socket does not block
#     # indefinitely when trying to receive data.
#         serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#         serverUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
#         serverUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#         serverUDP.settimeout(0.2)
#         message = (id,report_time)
#         while True:
#             serverUDP.sendto(message, ('<broadcast>', PORT))
#             print("message sent!")
#             time.sleep(1)
#     elif id!=-1:
#         #send UDP message to a client
#         serverUDP=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#         serverUDP.bind(ADDR)
#         serverUDP.sendto(message,id)
#     pass


def main(argv):
    if len(argv) < 1:
        print_usage()
    elif argv[0] == CMD_LISTEN:
        listen()
    elif argv[0] == CMD_LIST_ALL_CLIENTS:
        print_list_of_clients()
    elif argv[0] == CMD_EXPORT_REPORT:
        if len(argv) < 2:
            raise Exception("Required client's ID")

        id = argv[1]
        export_report_to_csv(id)
    elif argv[0] == CMD_CHANGE_CLIENT_REPORT_TIME:
        if len(argv) < 1:
            raise Exception(
                "Required client's ID or -all (to send all Clients)")
        elif len(argv) < 2:
            raise Exception("Required new recurring time")

        id = argv[1]
        report_time = argv[2]
        if id == "-all":
            change_all_report_time(report_time)
        else:
            change_client_report_time(id, report_time)
    else:
        print_usage()


if __name__ == "__main__":
    main(sys.argv[1:])
