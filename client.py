from json.decoder import JSONDecodeError
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
    # print(pre_cmd + CMD_MONITOR_SYSTEM)


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


def is_IP(str):
    try:
        socket.inet_aton(str)
    except socket.error:
        return False
    return True


class Client:
    def __init__(self, server=None):
        # Check if client is registered
        self.path_to_client_json = os.path.join(
            ".", "database", "client", "client_info.json")
        if not os.path.isfile(self.path_to_client_json):
            raise Exception("This client is not registered")
        self.load_client_info()

        self.name = monitor.get_system_name()
        self.UDP_PORT = 5050
        self.HEADER = 64
        self.FORMAT = 'utf-8'

        if server != None and server != self.SERVER:
            self.update_server_ip(server)

    def load_client_info(self):
        try:
            with open(self.path_to_client_json) as f:
                client_info = json.load(f)
            self.ID = client_info["id"]
            self.SERVER = client_info["server_ip"]
            self.PORT = client_info["server_tcp_port"]
            self.recurring_time = int(client_info["recurring_time"])
            self.ADDR = (self.SERVER, self.PORT)
        except JSONDecodeError:
            raise JSONDecodeError
        except IOError:
            raise IOError

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
            while not self.is_quitting:
                time.sleep(100)
        except KeyboardInterrupt:
            print('\n! Received keyboard interrupt, quitting threads.')
            print("  Please wait until program exit completely...")
            self.is_quitting = True
            monitor.join()
            listen_for_UDP.join()
            sys.exit()
        except Exception:
            print(f'\n! {Exception}, quitting threads.')
            print("  Please wait until program exit completely...")
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
        try:
            _client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _client.settimeout(1)
            _client.connect(self.ADDR)
            message = msg.encode(self.FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            _client.send(send_length)
            _client.send(message)
            response = _client.recv(2048).decode(self.FORMAT)
            if response != "[Successful]":
                self.is_quitting = True
                raise Exception(response)
            print("[Server Response] Report succeed")
        except socket.timeout:
            self.is_quitting = True
            raise socket.timeout
        except ConnectionRefusedError:
            self.is_quitting = True
            raise ConnectionRefusedError

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

    def update_client_json(self, key, value):
        with open(self.path_to_client_json) as f:
            client_info = json.load(f)
            client_info[key] = value

        monitor.write_JSON(client_info, self.path_to_client_json)

    def update_server_ip(self, server):
        self.update_client_json("server_ip", server)
        self.SERVER = server
        pass


def main(argv):
    if len(argv) < 1:
        print_usage()
        return

    if argv[0] == CMD_REGISTER:
        register()
        return

    elif argv[0] == CMD_START:
        server = None
        if len(argv) > 1:
            server = argv[1]

        client = Client(server)
        client.start()

    else:
        print_usage()


if __name__ == "__main__":
    main(sys.argv[1:])
