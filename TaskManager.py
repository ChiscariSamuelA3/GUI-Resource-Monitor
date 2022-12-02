import psutil
import time


class TaskManager:
    def __init__(self):
        pass

    def get_cpu(self):
        return psutil.cpu_percent(interval=1)

    def get_memory(self):
        # get used memory
        return psutil.virtual_memory().used

    def get_total_memory(self):
        return psutil.virtual_memory().total

    def get_partitions_info(self):
        # partitions usage
        partitions = psutil.disk_partitions()
        partitions_info = []
        for partition in partitions:
            # partition name
            partition_name = partition.device

            # mount info in GB
            mount_info = psutil.disk_usage(partition.mountpoint)
            mount_info_total = mount_info.total / 1024 / 1024 / 1024
            mount_info_used = mount_info.used / 1024 / 1024 / 1024
            mount_info_free = mount_info.free / 1024 / 1024 / 1024
            mount_info_percent = mount_info.percent

            partitions_info.append(
                [partition_name, mount_info_total, mount_info_used, mount_info_free, mount_info_percent])

        return partitions_info

    def get_network(self):
        # converted to kb/s

        network_sent_1, network_received_1 = psutil.net_io_counters().bytes_sent / 1024, psutil.net_io_counters().bytes_recv / 1024
        time.sleep(0.2)
        network_sent_2, network_received_2 = psutil.net_io_counters().bytes_sent / 1024, psutil.net_io_counters().bytes_recv / 1024

        return network_sent_2 - network_sent_1, network_received_2 - network_received_1
