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
    # with 2 decimal places
    memory_stats = [round(x / (1024 ** 3), 2) for x in memory_stats]
    memory_total_label = QtWidgets.QLabel("Total memory: " + str(memory_stats[0]) + " GB")
    memory_available_label = QtWidgets.QLabel("Available memory: " + str(memory_stats[1]) + " GB")
    memory_free_label = QtWidgets.QLabel("In use memory: " + str(memory_stats[3]) + " GB")
    memory_percent_label = QtWidgets.QLabel("Memory usage: " + str(memory_stats[4]) + "%")
    tab.layout.addWidget(memory_total_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_available_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_free_label, alignment=QtCore.Qt.AlignCenter)
    tab.layout.addWidget(memory_percent_label, alignment=QtCore.Qt.AlignCenter)


def init_tab_layout(tab: QtWidgets.QWidget, resource_plot, tab_type, task_manager):
    tab.layout = QtWidgets.QVBoxLayout()
    tab.layout.addWidget(resource_plot)

    if tab_type == 0:  # cpu
        add_cpu_stats(tab, task_manager)
    elif tab_type == 1:  # memory
        add_memory_stats(tab, task_manager)

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
    while True:
        try:
            ###########################################################################################
            # update cpu usage
            update_monitoring_info(cpu_usage, cpu_curve, task_manager.get_cpu_usage())
            # get cpu per core
            cpu_core_string = ""
            for index, cpu_per_core in enumerate(task_manager.get_cpu_per_core()):
                if index % 3 == 0:
                    cpu_core_string += "\n"
                cpu_core_string += "Core " + str(index) + ": " + str(cpu_per_core) + "%\t"
            # update label
            cpu_tab.layout.itemAt(6).widget().setText("CPU cores usage: " + cpu_core_string)

            ############################################################################################
            # update memory usage
            update_monitoring_info(memory_usage, memory_curve, task_manager.get_memory_usage())
            # update memory stats
            memory_stats = task_manager.get_memory_stats()
            memory_stats = [round(x / (1024 ** 3), 2) for x in memory_stats]
            memory_tab.layout.itemAt(1).widget().setText("Total memory: " + str(memory_stats[0]) + " GB")
            memory_tab.layout.itemAt(2).widget().setText("Available memory: " + str(memory_stats[1]) + " GB")
            memory_tab.layout.itemAt(3).widget().setText("In use memory: " + str(memory_stats[3]) + " GB")
            memory_tab.layout.itemAt(4).widget().setText("Memory usage: " + str(memory_stats[4]) + "%")

            ############################################################################################
            # update partitions usage
            partitions_info = task_manager.get_partitions_info()
            disk_plot.update()
            update_partitions_info(disk_plot, partitions_info)

            ############################################################################################
            # update network usage
            network_info = task_manager.get_network_usage()
            update_monitoring_info(network_sent_usage, network_sent_curve, network_info[0])
            update_monitoring_info(network_received_usage, network_received_curve, network_info[1])

            ############################################################################################
            app.processEvents()

        except Exception as e:
            print(e)
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

    # add a tab for cpu with 2 layouts
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