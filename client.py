import sys
import os
import time
import json
import socket
import threading

import monitor as monitor

CMD_REGISTER = "-register"
CMD_START = "-start"
CMD_MONITOR_SYSTEM = "-monitor-system"


def print_usage():
    pre_cmd = "python client.py "
    print(pre_cmd + CMD_REGISTER)
    print(pre_cmd + CMD_START)
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


class Client:
    def __init__(self):
        # Check if client is registered
        path_to_client_json = os.path.join(
            ".", "database", "client", "client_info.json")
        if not os.path.isfile(path_to_client_json):
            raise Exception("This client is not registered")
        self.load_client_info(path_to_client_json)

        self.name = monitor.get_system_name()
        self.UDP_PORT = 5050
        self.HEADER = 64
        self.FORMAT = 'utf-8'

    def load_client_info(self, path_to_client_json):
        with open(path_to_client_json) as f:
            client_info = json.load(f)

        self.ID = client_info["id"]
        self.SERVER = client_info["server_ip"]
        self.SERVER = "172.18.240.1"
        self.PORT = client_info["server_tcp_port"]
        self.recurring_time = int(client_info["recurring_time"])
        self.ADDR = (self.SERVER, self.PORT)

    def start(self):
        try:
            self.is_quitting = False
            monitor = threading.Thread(target=self.monitor_system)
            monitor.start()

            listen_for_UDP = threading.Thread(
                target=self.listen_for_UDP)
            listen_for_UDP.setDaemon(True)
            listen_for_UDP.start()

            # Need time.sleep to allow KeyboardInterrupt
            while True:
                time.sleep(100)
        except KeyboardInterrupt:
            print('\n! Received keyboard interrupt, quitting threads.\n')
            self.is_quitting = True
            monitor.join()
            listen_for_UDP.join()
            sys.exit()

    def monitor_system(self):
        """
        Check if (current time - init time) % recurring_time = 0
        If True then send data msg to Server
        """
        print("="*16 + "Start Monitoring System" + "="*16)
        report_count = 0
        while not self.is_quitting:
            print(f"[REPORTING] Report number: {report_count}")
            msg = ">"  # For reporting purpose
            msg += str(self.ID) + "@" + self.name

            report = self.get_report_str()
            msg += report
            self.send_TCP(msg)
            print("Report sent")

            report_count += 1
            #  Wait for the next reporting time
            time.sleep(self.recurring_time)

    def send_TCP(self, msg):
        _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _client.connect(self.ADDR)
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        _client.send(send_length)
        _client.send(message)
        response = _client.recv(2048).decode(self.FORMAT)
        if response != "[Successful]":
            raise Exception(response)
        print("[Server Response] Report succeed")

    def get_report_str(self):
        report = str(monitor.Report())
        return report

    def listen_for_UDP(self):
        while not self.is_quitting:
            print("[Listening]")
            time.sleep(1)

    def handle_server_UDP_msg():
        pass

    # def get_message_UDP(id):
    #     if id == -10:
    #         clientUDP = socket.socket(
    #             socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    #         clientUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #         clientUDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    #         clientUDP.bind(("", PORT))
    #         while True:
    #             data, addr = clientUDP.recvfrom(1024)
    #     else:
    #         data, addr = clientUDP.recvfrom(1024)


def main(argv):
    if len(argv) < 1:
        print_usage()
        return

    if argv[0] == CMD_REGISTER:
        register()
        return

    client = Client()
    if argv[0] == CMD_START:
        client.start()
    elif argv[0] == CMD_MONITOR_SYSTEM:
        client = Client()
        client.monitor_system()


if __name__ == "__main__":
    main(sys.argv[1:])
