import csv
from datetime import datetime

from PyQt5.QtChart import QChart, QPieSeries, QPieSlice
import threading
from TaskManager import TaskManager
from PyQt5 import QtWidgets, QtChart, QtCore
import pyqtgraph as pg


def init_tab_content(x_range, y_range, x_label, y_label):
    resource_plot = pg.plot()
    resource_plot.showGrid(x=True, y=True)
    resource_plot.setYRange(y_range[0], y_range[1])
    resource_plot.setXRange(x_range[0], x_range[1])
    resource_plot.setLabel('left', y_label, units='%')
    resource_plot.setLabel('bottom', x_label, units='s')

    return resource_plot


def add_cpu_stats(tab, task_manager):
    cpu_physical_cores, cpu_logical_cores = task_manager.get_cpu_count()

    physical_cores_label = QtWidgets.QLabel("Physical cores: " + str(cpu_physical_cores))
    logical_cores_label = QtWidgets.QLabel("Logical cores: " + str(cpu_logical_cores))
    tab.layout.addWidget(physical_cores_label)
    tab.layout.addWidget(logical_cores_label)

    cpu_frequency = task_manager.get_cpu_freq()

    cpu_freq_max_label = QtWidgets.QLabel("CPU max frequency: " + str(cpu_frequency[0]) + " MHz")
    cpu_freq_min_label = QtWidgets.QLabel("CPU min frequency: " + str(cpu_frequency[1]) + " MHz")
    cpu_freq_current_label = QtWidgets.QLabel("CPU current frequency: " + str(cpu_frequency[2]) + " MHz")
    tab.layout.addWidget(cpu_freq_max_label)
    tab.layout.addWidget(cpu_freq_min_label)
    tab.layout.addWidget(cpu_freq_current_label)

    cpu_core_string = ""
    for index, cpu_per_core in enumerate(task_manager.get_cpu_per_core()):
        if index % 3 == 0:
            cpu_core_string += "\n"
        cpu_core_string += "Core " + str(index) + ": " + str(cpu_per_core) + "%\t"

    cpu_core_label = QtWidgets.QLabel("CPU cores usage: " + cpu_core_string)
    tab.layout.addWidget(cpu_core_label, alignment=QtCore.Qt.AlignCenter)


def add_memory_stats(tab, task_manager):
    # get memory info in gb
    memory_stats = task_manager.get_memory_stats()
    memory_stats = [round(x / (1024 ** 3), 2) for x in memory_stats]

    memory_total_label = QtWidgets.QLabel("Total memory: " + str(memory_stats[0]) + " GB")
    memory_available_label = QtWidgets.QLabel("Available memory: " + str(memory_stats[1]) + " GB")
    memory_free_label = QtWidgets.QLabel("In use memory: " + str(memory_stats[3]) + " GB")
    memory_percent_label = QtWidgets.QLabel("Memory usage: " + str(memory_stats[4]) + "%")
    tab.layout.addWidget(memory_total_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_available_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_free_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_percent_label, alignment=QtCore.Qt.AlignCenter)


def add_partitions_stats(tab, task_manager):
    partitions_info = task_manager.get_partitions_info()

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


def add_network_stats(tab, task_manager):
    network_stats = task_manager.get_network_usage()

    network_sent_label = QtWidgets.QLabel("Sent: (YELLOW) " + str(network_stats[0]) + " MB")
    network_recv_label = QtWidgets.QLabel("Received: (GREEN) " + str(network_stats[1]) + " MB")
    tab.layout.addWidget(network_sent_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(network_recv_label, alignment=QtCore.Qt.AlignCenter)


def init_tab_layout(tab: QtWidgets.QWidget, resource_plot, tab_type, task_manager):
    tab.layout = QtWidgets.QVBoxLayout()
    tab.layout.addWidget(resource_plot)

    if tab_type == 0:  # cpu
        add_cpu_stats(tab, task_manager)
    elif tab_type == 1:  # memory
        add_memory_stats(tab, task_manager)
    elif tab_type == 2:  # disk
        add_partitions_stats(tab, task_manager)
    elif tab_type == 3:  # network
        add_network_stats(tab, task_manager)

    tab.setLayout(tab.layout)


def update_partitions_info(disk_plot, partitions_info):
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
    if len(resource_usage) > 60:
        resource_usage.pop(0)

    resource_usage.append(resource_value)
    resource_curve.setData(resource_usage)


def update_plots(cpu_tab, memory_tab, partitions_tab, network_tab, cpu_usage, memory_usage, disk_plot,
                 network_sent_usage, network_received_usage, task_manager,
                 cpu_curve,
                 memory_curve, network_sent_curve, network_received_curve, app):
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
        # current time
        current_time = datetime.now().strftime("%H:%M:%S")
        try:
            #######################################################################################
            # ------------------------------- CPU TAB ---------------------------------------------#
            # update cpu usage
            update_monitoring_info(cpu_usage, cpu_curve, task_manager.get_cpu_usage())
            # update cpu stats
            cpu_core_string = ""
            for index, cpu_per_core in enumerate(task_manager.get_cpu_per_core()):
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

            # ------------------------------- MEMORY TAB ---------------------------------------------#
            # update memory usage
            update_monitoring_info(memory_usage, memory_curve, task_manager.get_memory_usage())
            # update memory stats
            memory_stats = task_manager.get_memory_stats()
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

            # ------------------------------- DISK TAB ---------------------------------------------#
            # update partitions usage
            partitions_info = task_manager.get_partitions_info()
            disk_plot.update()
            update_partitions_info(disk_plot, partitions_info)

            # update partitions stats
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

            # ------------------------------- NETWORK TAB ---------------------------------------------#
            # update network usage
            network_info = task_manager.get_network_usage()
            update_monitoring_info(network_sent_usage, network_sent_curve, network_info[0])
            update_monitoring_info(network_received_usage, network_received_curve, network_info[1])

            # update network stats
            network_tab.layout.itemAt(1).widget().setText("Sent (YELLOW): " + str(network_info[0]) + " MB")
            network_tab.layout.itemAt(2).widget().setText("Received (GREEN) : " + str(network_info[1]) + " MB")

            # save network stats in csv file
            network_csv_writer.writerow([f"#################### NETWORK STATS {current_time} ####################"])
            network_csv_writer.writerow(["Sent", str(network_info[0]) + " MB"])
            network_csv_writer.writerow(["Received", str(network_info[1]) + " MB"])

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
    task_manager = TaskManager()

    print(task_manager.get_partitions_info())

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

    memory_plot = init_tab_content([0, 60], [0, task_manager.get_total_memory()], 'Time', 'Memory Usage')
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
    init_tab_layout(cpu_tab, cpu_plot, 0, task_manager)
    init_tab_layout(memory_tab, memory_plot, 1, task_manager)
    init_tab_layout(partitions_tab, disk_plot, 2, task_manager)
    init_tab_layout(network_tab, network_plot, 3, task_manager)

    # new thread for updating the plots
    # maybe should I start a new thread for each plot?
    thread = threading.Thread(target=update_plots,
                              args=(
                                  cpu_tab, memory_tab, partitions_tab, network_tab, cpu_usage, memory_usage, disk_plot,
                                  network_sent_usage, network_received_usage,
                                  task_manager,
                                  cpu_curve, memory_curve, network_sent_curve, network_received_curve, app))
    thread.start()

    tabs.show()

    app.exec_()


if __name__ == '__main__':
    main()
