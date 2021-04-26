import json
import psutil
import platform
from datetime import datetime


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f'{bytes:.2f}{unit}{suffix}'
        bytes /= factor


def get_system_info():
    uname = platform.uname()
    system_info = {
        "System": uname.system,
        "Node Name": uname.node,
        "Release": uname.release,
        "Version": uname.version,
        "Machine": uname.machine,
        "Processor": uname.processor
    }
    return system_info


def print_system_info():
    print("="*40, "System Information", "="*40)
    system_info = get_system_info()
    for e in system_info:
        print(f'{e}: {system_info[e]}')


def get_boot_time():
    boot_time_timestamp = psutil.boot_time()
    boot_time = datetime.fromtimestamp(boot_time_timestamp)
    return boot_time


def print_boot_time():
    print("="*40, "Boot Time", "="*40)
    bt = get_boot_time()
    print(
        f'Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}')


def get_cpu_info():
    cpu_freq = psutil.cpu_freq()
    cpu_info = {
        "Physical cores": psutil.cpu_count(logical=False),
        "Total cores": psutil.cpu_count(logical=True),
        "Max Frequency": f'{cpu_freq.max:.2f}Mhz',
        "Min Frequency": f'{cpu_freq.min:.2f}Mhz',
        "Current Frequency": f'{cpu_freq.current:.2f}Mhz'
    }
    return cpu_info


def print_cpu_info():
    # let's print CPU information
    print("="*40, "CPU Info", "="*40)
    cpu_info = get_cpu_info()
    for e in cpu_info:
        print(f'{e}: {cpu_info[e]}')


def get_memory_usage():
    svmem = psutil.virtual_memory()
    mem_usage = {
        "Total": get_size(svmem.total),
        "Available": get_size(svmem.available),
        "Used": get_size(svmem.used),
        "Percentage": svmem.percent
    }
    return mem_usage


def print_memory_usage():
    # Memory Information
    print("="*40, "Memory Information", "="*40)
    mem_usage = get_memory_usage()
    for e in mem_usage:
        print(f'{e}: {mem_usage[e]}')


def get_disk_usage():
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    disk_usage = {
        "Total read": get_size(disk_io.read_bytes),
        "Total write": get_size(disk_io.write_bytes),
        "Partition list": {}
    }

    partitions = psutil.disk_partitions()
    for partition in partitions:
        current_partition = {
            "Mountpoint": partition.mountpoint,
            "File system type": partition.fstype
        }

        # Check if disk is ready or not, if not then skip
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        current_partition["Total Size"] = get_size(partition_usage.total),
        current_partition["Used"] = get_size(partition_usage.used),
        current_partition["Free"] = get_size(partition_usage.free),
        current_partition["Percentage"] = partition_usage.percent

        # Add current_partition dict to disk_usage dict
        disk_usage["Partition list"][partition.device] = current_partition

    return disk_usage


def print_disk_usage():
    # Disk Information
    print("="*40, "Disk Information", "="*40)
    disk_usage = get_disk_usage()
    print(f'"Total read": {disk_usage["Total read"]}')
    print(f'"Total write": {disk_usage["Total write"]}')
    print("Partitions and Usage:")
    for partition, partition_info in disk_usage["Partition list"].items():

        print(f'======= Device: {partition} =======')
        for key in partition_info:
            print(f'\t{key}: {partition_info[key]}')


class Report:
    def __init__(self):
        self.init_time = datetime.now()
        self.boot_time = get_boot_time()
        self.mem_usage = get_memory_usage()
        self.disk_usage = get_disk_usage()

    def to_dict(self):
        dict = {}
        dict[str(self.init_time)] = {
            "Boot time": str(self.boot_time),
            "Memory usage": self.mem_usage,
            "Disk usage": self.disk_usage
        }
        return dict

    def write_JSON(self, path):
        try:
            dict = self.to_dict()
            with open(path, "w") as file:
                json.dump(dict, file, indent=3)
        except IOError:
            raise IOError
