import psutil
import time


# ---------------------------CPU------------------------------ #
def get_cpu_count():
    # get total number of physical cores
    # get total number of logical cores
    return psutil.cpu_count(logical=False), psutil.cpu_count(logical=True)


def get_cpu_freq():
    # get cpu frequency
    return psutil.cpu_freq()


def get_cpu_per_core():
    # get cpu usage per physical core
    return psutil.cpu_percent(interval=0.5, percpu=True)


def get_cpu_usage():
    # get cpu usage per physical core
    return psutil.cpu_percent(interval=0.5)


# ---------------------------Memory------------------------------ #

def get_memory_usage():
    # get used memory
    return psutil.virtual_memory().used


def get_total_memory():
    # get total memory
    return psutil.virtual_memory().total


def get_memory_stats():
    # get memory stats
    return psutil.virtual_memory()


# ---------------------------DISK-------------------------------- #

def get_partitions_info():
    # partitions usage
    partitions = psutil.disk_partitions()
    partitions_info = []
    for partition in partitions:
        # partition name
        partition_name = partition.device

        # mount info in GB
        mount_info = psutil.disk_usage(partition.mountpoint)
        mount_info_total = round(mount_info.total / (1024 ** 3), 4)
        mount_info_used = round(mount_info.used / (1024 ** 3), 4)
        mount_info_free = round(mount_info.free / (1024 ** 3), 4)
        mount_info_percent = mount_info.percent

        partitions_info.append(
            [partition_name, mount_info_total, mount_info_used, mount_info_free, mount_info_percent])

    return partitions_info


# ---------------------------NETWORK------------------------------ #

def get_network_usage():
    # get network usage
    # converted to kb/s

    network_sent_1 = psutil.net_io_counters().bytes_sent / 1024
    network_received_1 = psutil.net_io_counters().bytes_recv / 1024
    time.sleep(0.2)
    network_sent_2 = psutil.net_io_counters().bytes_sent / 1024
    network_received_2 = psutil.net_io_counters().bytes_recv / 1024

    return network_sent_2 - network_sent_1, network_received_2 - network_received_1
