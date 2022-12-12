import pyqtgraph as pg
import pyqtgraph.exporters
from TaskManager import *


def add_new_cpu_stats(cpu_tab, cpu_csv_writer, current_time):
    cpu_core_string = ""
    for index, cpu_per_core in enumerate(get_cpu_per_core()):
        # save cpu stats in csv file
        if index % 12 == 0:
            cpu_csv_writer.writerow([f"#################### CPU STATS {current_time} ####################"])
        cpu_csv_writer.writerow(["CPU", "Core " + str(index), str(cpu_per_core) + "%"])

        # create a string to display cpu stats
        if index % 3 == 0:
            cpu_core_string += "\n"
        cpu_core_string += "Core " + str(index) + ": " + str(cpu_per_core) + "%\t"

    # update label
    cpu_tab.layout.itemAt(6).widget().setText("CPU cores usage: " + cpu_core_string)


def add_new_memory_stats(memory_tab, memory_csv_writer, current_time):
    memory_stats = get_memory_stats()
    memory_stats = [round(x / (1024 ** 3), 2) for x in memory_stats]
    memory_tab.layout.itemAt(1).widget().setText("Total memory: " + str(memory_stats[0]) + " GB")
    memory_tab.layout.itemAt(2).widget().setText("Available memory: " + str(memory_stats[1]) + " GB")
    memory_tab.layout.itemAt(3).widget().setText("In use memory: " + str(memory_stats[3]) + " GB")
    memory_tab.layout.itemAt(4).widget().setText("Memory usage: " + str(memory_stats[4]) + "%")

    # save memory stats in csv file
    memory_csv_writer.writerow([f"#################### MEMORY STATS {current_time} ####################"])
    memory_csv_writer.writerow(["Total memory", str(memory_stats[0]) + " GB"])
    memory_csv_writer.writerow(["Available memory", str(memory_stats[1]) + " GB"])
    memory_csv_writer.writerow(["In use memory", str(memory_stats[3]) + " GB"])
    memory_csv_writer.writerow(["Memory usage", str(memory_stats[4]) + "%"])


def add_new_partitions_stats(partitions_tab, disk_csv_writer, current_time, partitions_info):
    for index, partition in enumerate(partitions_info):
        partition_layout = partitions_tab.layout.itemAt(index + 1).layout()
        partition_layout.itemAt(1).widget().setText("Total size: " + str(partition[1]) + " GB")
        partition_layout.itemAt(2).widget().setText("Used size: " + str(partition[2]) + " GB")
        partition_layout.itemAt(3).widget().setText("Free size: " + str(partition[3]) + " GB")
        partition_layout.itemAt(4).widget().setText("Usage: " + str(partition[4]) + "%")

        # save disk stats in csv file
        if index % 5 == 0:
            disk_csv_writer.writerow([f"#################### DISK STATS {current_time} ####################"])
        disk_csv_writer.writerow(["Partition", partition[0]])
        disk_csv_writer.writerow(["Total size", str(partition[1]) + " GB"])
        disk_csv_writer.writerow(["Used size", str(partition[2]) + " GB"])
        disk_csv_writer.writerow(["Free size", str(partition[3]) + " GB"])
        disk_csv_writer.writerow(["Usage", str(partition[4]) + "%"])
        disk_csv_writer.writerow(["---------------"])


def add_new_network_stats(network_tab, network_csv_writer, current_time, network_info):
    network_tab.layout.itemAt(1).widget().setText("Sent (YELLOW): " + str(network_info[0]) + " MB")
    network_tab.layout.itemAt(2).widget().setText("Received (GREEN) : " + str(network_info[1]) + " MB")

    # save network stats in csv file
    network_csv_writer.writerow([f"#################### NETWORK STATS {current_time} ####################"])
    network_csv_writer.writerow(["Sent", str(network_info[0]) + " MB"])
    network_csv_writer.writerow(["Received", str(network_info[1]) + " MB"])


def export_chart(tab_type, resource_plot):
    print("Exporting chart...")

    if tab_type == 0:
        exporter = pg.exporters.ImageExporter(resource_plot.plotItem)
        exporter.export("cpu_chart.jpeg")
    elif tab_type == 1:
        exporter = pg.exporters.ImageExporter(resource_plot.plotItem)
        exporter.export("memory_chart.jpeg")
    elif tab_type == 2:
        # exporting QChartView
        resource_plot.grab().save("disk_chart.jpeg")
    elif tab_type == 3:
        exporter = pg.exporters.ImageExporter(resource_plot.plotItem)
        exporter.export("network_chart.jpeg")

    print("Chart exported!")
