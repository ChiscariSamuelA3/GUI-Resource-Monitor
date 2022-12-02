from PyQt5.QtChart import QChart, QPieSeries, QPieSlice
import threading
from TaskManager import TaskManager
from PyQt5 import QtWidgets, QtChart
import pyqtgraph as pg


def init_tab_content(x_range, y_range, x_label, y_label):
    resource_plot = pg.plot()
    resource_plot.showGrid(x=True, y=True)
    resource_plot.setYRange(y_range[0], y_range[1])
    resource_plot.setXRange(x_range[0], x_range[1])
    resource_plot.setLabel('left', y_label, units='%')
    resource_plot.setLabel('bottom', x_label, units='s')

    return resource_plot


def init_tab_layout(tab: QtWidgets.QWidget, resource_plot):
    tab.layout = QtWidgets.QVBoxLayout()
    tab.layout.addWidget(resource_plot)
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


def update_plots(cpu_usage, memory_usage, disk_plot, network_sent_usage, network_received_usage, task_manager,
                 cpu_curve,
                 memory_curve, network_sent_curve, network_received_curve, app):
    while True:
        try:
            # update cpu usage
            update_monitoring_info(cpu_usage, cpu_curve, task_manager.get_cpu())

            # update memory usage
            update_monitoring_info(memory_usage, memory_curve, task_manager.get_memory())

            # update partitions usage
            partitions_info = task_manager.get_partitions_info()
            disk_plot.update()
            update_partitions_info(disk_plot, partitions_info)

            # update network usage
            network_info = task_manager.get_network()
            update_monitoring_info(network_sent_usage, network_sent_curve, network_info[0])
            update_monitoring_info(network_received_usage, network_received_curve, network_info[1])

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
    init_tab_layout(cpu_tab, cpu_plot)
    init_tab_layout(memory_tab, memory_plot)
    init_tab_layout(partitions_tab, disk_plot)
    init_tab_layout(network_tab, network_plot)

    # new thread for updating the plots
    thread = threading.Thread(target=update_plots,
                              args=(cpu_usage, memory_usage, disk_plot, network_sent_usage, network_received_usage,
                                    task_manager,
                                    cpu_curve, memory_curve, network_sent_curve, network_received_curve, app))
    thread.start()

    tabs.show()

    app.exec_()


if __name__ == '__main__':
    main()
