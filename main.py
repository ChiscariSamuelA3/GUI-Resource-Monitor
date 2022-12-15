import csv
from datetime import datetime
from PyQt5.QtChart import QChart, QPieSeries, QPieSlice
import threading
from PyQt5 import QtWidgets, QtChart, QtCore

from Resources import *


def init_tab_content(x_range, y_range, x_label, y_label):
    """
    Initialize tab content with chart and curve for resource usage monitoring (CPU, memory, network)
    :param x_range: x range
    :param y_range: y range
    :param x_label: x label
    :param y_label: y label
    :return: chart, curve
    """
    resource_plot = pg.plot()
    resource_plot.showGrid(x=True, y=True)
    resource_plot.setYRange(y_range[0], y_range[1])
    resource_plot.setXRange(x_range[0], x_range[1])
    resource_plot.setLabel('left', y_label, units='%')
    resource_plot.setLabel('bottom', x_label, units='s')

    return resource_plot


def create_cpu_stats(tab):
    """
    Create CPU stats tab content (chart, curve, labels) and start monitoring. CPU usage is updated every 1 second with
    percentages per core, physical and logical core, cpu max, min and current frequency
    :param tab: tab widget to add
    cpu stats to
    :return:
    """
    cpu_physical_cores, cpu_logical_cores = get_cpu_count()

    physical_cores_label = QtWidgets.QLabel("Physical cores: " + str(cpu_physical_cores))
    logical_cores_label = QtWidgets.QLabel("Logical cores: " + str(cpu_logical_cores))
    tab.layout.addWidget(physical_cores_label)
    tab.layout.addWidget(logical_cores_label)

    cpu_frequency = get_cpu_freq()

    cpu_freq_max_label = QtWidgets.QLabel("CPU max frequency: " + str(cpu_frequency[0]) + " MHz")
    cpu_freq_min_label = QtWidgets.QLabel("CPU min frequency: " + str(cpu_frequency[1]) + " MHz")
    cpu_freq_current_label = QtWidgets.QLabel("CPU current frequency: " + str(cpu_frequency[2]) + " MHz")
    tab.layout.addWidget(cpu_freq_max_label)
    tab.layout.addWidget(cpu_freq_min_label)
    tab.layout.addWidget(cpu_freq_current_label)

    cpu_core_string = ""
    for index, cpu_per_core in enumerate(get_cpu_per_core()):
        if index % 3 == 0:
            cpu_core_string += "\n"
        cpu_core_string += "Core " + str(index) + ": " + str(cpu_per_core) + "%\t"

    cpu_core_label = QtWidgets.QLabel("CPU cores usage: " + cpu_core_string)
    tab.layout.addWidget(cpu_core_label, alignment=QtCore.Qt.AlignCenter)


def create_memory_stats(tab):
    """
    Create memory stats tab content (chart, curve, labels) and start monitoring. Memory usage is updated every 1 second
    with memory usage in percent (total, available, used, free)
    :param tab: tab widget to add memory stats to
    :return:
    """
    # get memory info in gb
    memory_stats = get_memory_stats()
    memory_stats = [round(x / (1024 ** 3), 2) for x in memory_stats]

    memory_total_label = QtWidgets.QLabel("Total memory: " + str(memory_stats[0]) + " GB")
    memory_available_label = QtWidgets.QLabel("Available memory: " + str(memory_stats[1]) + " GB")
    memory_free_label = QtWidgets.QLabel("In use memory: " + str(memory_stats[3]) + " GB")
    memory_percent_label = QtWidgets.QLabel("Memory usage: " + str(memory_stats[4]) + "%")
    tab.layout.addWidget(memory_total_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_available_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_free_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_percent_label, alignment=QtCore.Qt.AlignCenter)


def create_partitions_stats(tab):
    """
    Create partitions stats tab content (chart, curve, labels) and start monitoring
    Partitions usage is updated every 1 second with partitions usage in percent for each partition
    :param tab: tab widget to add partitions stats to
    :return:
    """
    partitions_info = get_partitions_info()

    for partition in partitions_info:
        partition_layout = QtWidgets.QGridLayout()
        partition_layout.setSpacing(50)

        # partition name
        partition_name_label = QtWidgets.QLabel("Partition name: " + partition[0])
        partition_layout.addWidget(partition_name_label, 0, 0)

        # partition total size
        partition_total_size_label = QtWidgets.QLabel("Total size: " + str(partition[1]) + " GB")
        partition_layout.addWidget(partition_total_size_label, 0, 1)

        # partition used size
        partition_used_size_label = QtWidgets.QLabel("Used size: " + str(partition[2]) + " GB")
        partition_layout.addWidget(partition_used_size_label, 0, 2)

        # partition free size
        partition_free_size_label = QtWidgets.QLabel("Free size: " + str(partition[3]) + " GB")
        partition_layout.addWidget(partition_free_size_label, 0, 3)

        # partition usage
        partition_usage_label = QtWidgets.QLabel("Usage: " + str(partition[4]) + "%")
        partition_layout.addWidget(partition_usage_label, 0, 4)

        tab.layout.addLayout(partition_layout)


def create_network_stats(tab):
    """
    Create network stats tab content (chart, curve, labels) and start monitoring. Network usage is updated every 1
    second with network sent and received bytes
    :param tab: tab widget to add network stats to
    :return:
    """
    network_stats = get_network_usage()

    network_sent_label = QtWidgets.QLabel("Sent: (YELLOW) " + str(network_stats[0]) + " MB")
    network_recv_label = QtWidgets.QLabel("Received: (GREEN) " + str(network_stats[1]) + " MB")
    tab.layout.addWidget(network_sent_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(network_recv_label, alignment=QtCore.Qt.AlignCenter)


def clear_history(tab_type):
    """
    Clear history csv file for tab type
    :param tab_type: tab type to clear history for
    :return:
    """
    current_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")
    if tab_type == 0:  # cpu
        # clear cpu_stats.csv
        with open('cpu_stats.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["deleted cpu stats", current_time])
    elif tab_type == 1:  # memory
        # clear memory_stats.csv
        with open('memory_stats.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["deleted memory stats", current_time])
    elif tab_type == 2:  # disk
        # clear disk_stats.csv
        with open('disk_stats.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["deleted disk stats", current_time])
    elif tab_type == 3:  # network
        # clear network_stats.csv
        with open('network_stats.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["deleted network stats", current_time])


def init_tab_layout(tab: QtWidgets.QWidget, resource_plot, tab_type):
    """
    Initialize tab layout with chart, curve, labels and start monitoring
    :param tab: tab widget to initialize
    :param resource_plot: chart to add to tab layout
    :param tab_type: tab type to initialize (cpu, memory, disk, network)
    :return:
    """
    tab.layout = QtWidgets.QVBoxLayout()
    tab.layout.addWidget(resource_plot)

    if tab_type == 0:  # cpu
        create_cpu_stats(tab)
    elif tab_type == 1:  # memory
        create_memory_stats(tab)
    elif tab_type == 2:  # disk
        create_partitions_stats(tab)
    elif tab_type == 3:  # network
        create_network_stats(tab)

    export_button = QtWidgets.QPushButton("Export chart")
    # noinspection PyUnresolvedReferences
    export_button.clicked.connect(lambda: export_chart(tab_type, resource_plot))
    tab.layout.addWidget(export_button, alignment=QtCore.Qt.AlignCenter)

    clear_button = QtWidgets.QPushButton("Clear history")
    # noinspection PyUnresolvedReferences
    clear_button.clicked.connect(lambda: clear_history(tab_type))
    tab.layout.addWidget(clear_button, alignment=QtCore.Qt.AlignCenter)

    tab.setLayout(tab.layout)


def update_partitions_info(disk_plot, partitions_info):
    """
    Update partitions info (chart, curve, labels)
    :param disk_plot: chart to update
    :param partitions_info: partitions info to update chart with
    :return:
    """
    total_disk_space = 0
    for partition in partitions_info:
        total_disk_space += partition[1]

    disk_plot.chart().setTitle("Total disk space: " + str(total_disk_space) + " GB ")
    series = QPieSeries()

    for partition in partitions_info:
        partition_slice_used = QPieSlice()
        partition_slice_free = QPieSlice()

        partition_slice_used.setLabel(partition[0] + " used " + str(partition[2]) + " GB")
        partition_slice_free.setLabel(partition[0] + " free " + str(partition[3]) + " GB")
        partition_slice_used.setLabelVisible()
        partition_slice_free.setLabelVisible()

        partition_slice_used.setValue(partition[2])
        partition_slice_free.setValue(partition[3])

        series.append(partition_slice_used)
        series.append(partition_slice_free)

    old_slices = disk_plot.chart().series()
    for old_slice in old_slices:
        old_slice.setVisible(False)

    # disk_plot.chart().removeAllSeries()

    # update the chart with the new series
    disk_plot.chart().addSeries(series)


def update_monitoring_info(resource_usage, resource_curve, resource_value):
    """
    Update monitoring info (chart, curve, labels) for cpu, memory, network
    :param resource_usage: resource usage to update chart with
    :param resource_curve: chart curve to update
    :param resource_value: label to update with resource usage value
    :return:
    """
    if len(resource_usage) > 60:
        resource_usage.pop(0)

    resource_usage.append(resource_value)
    resource_curve.setData(resource_usage)


def update_plots(cpu_tab, memory_tab, partitions_tab, network_tab, cpu_usage, memory_usage, disk_plot,
                 network_sent_usage, network_received_usage, cpu_curve,
                 memory_curve, network_sent_curve, network_received_curve, app):
    """
    Update charts, curves, labels and start monitoring
    :param cpu_tab: cpu tab widget to update
    :param memory_tab: memory tab widget to update
    :param partitions_tab: disk tab widget to update
    :param network_tab: network tab widget to update
    :param cpu_usage: cpu usage to update chart with
    :param memory_usage: memory usage to update chart with
    :param disk_plot: disk chart to update
    :param network_sent_usage: network sent usage to update chart with
    :param network_received_usage: network received usage to update chart with
    :param cpu_curve: cpu chart curve to update
    :param memory_curve: memory chart curve to update
    :param network_sent_curve: network sent chart curve to update
    :param network_received_curve: network received chart curve to update
    :param app: application to process events
    :return:
    """
    # csv files for saving resource usage
    cpu_csv_file = open("cpu_stats.csv", "a")
    cpu_csv_writer = csv.writer(cpu_csv_file)

    memory_csv_file = open("memory_stats.csv", "a")
    memory_csv_writer = csv.writer(memory_csv_file)

    disk_csv_file = open("disk_stats.csv", "a")
    disk_csv_writer = csv.writer(disk_csv_file)

    network_csv_file = open("network_stats.csv", "a")
    network_csv_writer = csv.writer(network_csv_file)

    while True:
        # current date and time formatted
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            #######################################################################################
            # ------------------------------- CPU TAB ---------------------------------------------#
            # update cpu usage
            update_monitoring_info(cpu_usage, cpu_curve, get_cpu_usage())

            # update and save cpu stats
            add_new_cpu_stats(cpu_tab, cpu_csv_writer, current_time)

            # ------------------------------- MEMORY TAB ---------------------------------------------#
            # update memory usage
            update_monitoring_info(memory_usage, memory_curve, get_memory_usage())

            # update and save memory stats
            add_new_memory_stats(memory_tab, memory_csv_writer, current_time)

            # ------------------------------- DISK TAB ---------------------------------------------#
            # update partitions usage
            partitions_info = get_partitions_info()
            disk_plot.update()
            update_partitions_info(disk_plot, partitions_info)

            # update and save partitions stats
            add_new_partitions_stats(partitions_tab, disk_csv_writer, current_time, partitions_info)

            # ------------------------------- NETWORK TAB ---------------------------------------------#
            # update network usage
            network_info = get_network_usage()
            update_monitoring_info(network_sent_usage, network_sent_curve, network_info[0])
            update_monitoring_info(network_received_usage, network_received_curve, network_info[1])

            # update and save network stats
            add_new_network_stats(network_tab, network_csv_writer, current_time, network_info)

            ############################################################################################
            app.processEvents()

        except Exception as e:
            print(e)

            cpu_csv_file.close()
            memory_csv_file.close()
            disk_csv_file.close()
            network_csv_file.close()

            break


def main():
    """
    Main function to run the application
    :return:
    """
    cpu_usage = []
    memory_usage = []
    network_sent_usage = []
    network_received_usage = []

    app = QtWidgets.QApplication([])

    # add tabs for each resource
    tabs = QtWidgets.QTabWidget()

    cpu_tab = QtWidgets.QWidget()
    tabs.addTab(cpu_tab, "CPU")

    memory_tab = QtWidgets.QWidget()
    tabs.addTab(memory_tab, "Memory")

    partitions_tab = QtWidgets.QWidget()
    tabs.addTab(partitions_tab, "Partitions")

    network_tab = QtWidgets.QWidget()
    tabs.addTab(network_tab, "Network")

    # init tabs content
    cpu_plot = init_tab_content([0, 60], [0, 100], 'Time', 'CPU Usage')
    cpu_curve = cpu_plot.plot(pen='r')

    memory_plot = init_tab_content([0, 60], [0, get_total_memory()], 'Time', 'Memory Usage')
    memory_curve = memory_plot.plot(pen='b')

    network_plot = init_tab_content([60, 0], [0, 1000], 'Time', 'Network')
    network_received_curve = network_plot.plot(pen='g', name='Received')
    network_sent_curve = network_plot.plot(pen='y', name='Sent')

    partitions_chart = QChart()
    partitions_chart.legend().setVisible(False)

    # create the chart view as a QWidget
    disk_plot = QtChart.QChartView(partitions_chart)
    # disk_plot.setRenderHint(QtGui.QPainter.Antialiasing)

    # init tabs layout
    init_tab_layout(cpu_tab, cpu_plot, 0)
    init_tab_layout(memory_tab, memory_plot, 1)
    init_tab_layout(partitions_tab, disk_plot, 2)
    init_tab_layout(network_tab, network_plot, 3)

    # new thread for updating the plots
    thread = threading.Thread(target=update_plots,
                              args=(
                                  cpu_tab, memory_tab, partitions_tab, network_tab, cpu_usage, memory_usage, disk_plot,
                                  network_sent_usage, network_received_usage,
                                  cpu_curve, memory_curve, network_sent_curve, network_received_curve, app))
    thread.start()

    tabs.show()

    app.exec_()


if __name__ == '__main__':
    main()
