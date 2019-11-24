import sys,os
parent = os.path.dirname(__file__)
sys.path.append(os.path.dirname(parent))

from multitask.Qt import QtCore, QtWidgets, QtGui
from multitask import manager
from itertools import cycle
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class ListModel(QtCore.QAbstractListModel):

    def __init__(self, data, parent=None):
        super(ListModel, self).__init__(parent)
        self.__data = data
        
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return 'Horizontal Header'
            else:
                return 'V {}'.format(section)

    def rowCount(self, parent):
        return len(self.__data)

    def data(self, index, role):
        row = index.row()
        value = self.__data[row]

        if role == QtCore.Qt.DisplayRole:
            return value['name']

        if role == QtCore.Qt.DecorationRole:
            status = value['status']
            
            default = QtWidgets.QStyle.SP_DialogNoButton
            if status == "BUSY":
                default = QtWidgets.QStyle.SP_DialogNoButton
            if status == "ACTIVE":
                default = QtWidgets.QStyle.SP_DialogYesButton
            icon = QtWidgets.QWidget().style().standardIcon(
                default
            )
            return icon

        if role == QtCore.Qt.ToolTipRole:
            return 'Pid:{pid}, Task: {task}, Metadata:{metadata}'.format(**value)

        if role == QtCore.Qt.UserRole:
            return value

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | \
               QtCore.Qt.ItemIsEditable | \
               QtCore.Qt.ItemIsEnabled

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        if role ==QtCore.Qt.EditRole:
            #check if item is correct
            self.__data[row] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
                            #index, first, last
        self.beginInsertRows(QtCore.QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            self.__data.insert(position, 'NewRow')
        self.endInsertRows()
        return True

    def removetRows(self, position, rows, parent=QtCore.QModelIndex()):
        self.beginRemoveRows()
        for i in xrange(rows):
            value = self.__data[position]
            self.__data.remove(value)
        self.insertRows()
        return True


class ListView(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent=parent)
        # self.setEditTriggers(
        #     QtWidgets.QAbstractItemView.AnyKeyPressed |
        #     QtWidgets.QAbstractItemView.DoubleClicked
        # )
        
        self.setFlow(QtWidgets.QListView.TopToBottom)
        self.setViewMode(QtWidgets.QListView.IconMode)


class ProcessInfoWidget(QtWidgets.QWidget):
    """
    Label        Button
    Process Name:PID Status
    Label
    Current task:  Memory:
    """
    def __init__(self, data=None, parent=None):
        """Constructor for ListItem"""
        super(ProcessInfoWidget, self).__init__(parent)
        self.process_name = QtWidgets.QLabel('Process Name')
        self.process_pid = QtWidgets.QLabel('PID')
        self.process_status = QtWidgets.QPushButton('UNDEF')
        self.process_task = QtWidgets.QLabel('Task')
        self.process_metadata = QtWidgets.QLabel('Memory')

        self.layout = QtWidgets.QVBoxLayout()
        self.toplayout = QtWidgets.QHBoxLayout()
        self.btmlayout = QtWidgets.QHBoxLayout()

        self.layout.addLayout(self.toplayout)
        self.layout.addLayout(self.btmlayout)

        self.toplayout.addWidget(self.process_name)
        self.toplayout.addWidget(self.process_pid)
        self.toplayout.addWidget(self.process_status)

        self.btmlayout.addWidget(self.process_task)
        self.btmlayout.addWidget(self.process_metadata)
        self.setLayout(self.layout)

        if data:
            self.set_data(data)

    def set_data(self, info):
        self.process_name.setText(info['name'])
        self.process_pid.setText(str(info['pid']))
        self.process_status.setText(info['status'])
        self.process_task.setText(info['task'])
        self.process_metadata.setText(info['metadata'])


class ListDelegate(QtWidgets.QStyledItemDelegate):
    # def createEditor(self, parent, option, index):
    #     value = index.data(QtCore.Qt.UserRole)

    #     if isinstance(value, dict):
    #         return ProcessInfoWidget(data=value, parent=parent)

    #     return super(ListDelegate, self).createEditor(parent, option, index)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(
            option.rect.x(),
            option.rect.y() + option.rect.height(), 
            200, 200
        )

    def paint(self, painter, option, index):
        value = index.data(QtCore.Qt.UserRole)
        
        painter.setPen(QtCore.Qt.black)
        painter.setFont(QtGui.QFont("Arial", 10))
        painter.drawText(option.rect, value["status"])
        # painter.drawRect(option.rect)
        super(ListDelegate, self).paint(
            painter, option, index
        )


class ProcessControlWidget(QtWidgets.QWidget):
    """
    Label: Input - Range
    N procs (cpu procs): 
    Button Button
    Start/Stop Kill
    """
    def __init__(self,parent=None):

        super(ProcessControlWidget, self).__init__(parent=parent)
        self.proc_label = QtWidgets.QLabel("Num of Processors")
        self.proc_number = QtWidgets.QLineEdit('6')
        self.start_stop = QtWidgets.QPushButton('Start')
        self._start_state = "start"
        self._proc_manager = None
        self.start_stop.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        )
        self.refresh = QtWidgets.QPushButton()
        self.refresh.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_BrowserReload)
        )
        self.kill =  QtWidgets.QPushButton('Kill')
        self.kill.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.SP_BrowserStop)
        )
        self.layout = QtWidgets.QVBoxLayout()
        self.toplayout = QtWidgets.QHBoxLayout()
        self.btmlayout = QtWidgets.QHBoxLayout()

        self.toplayout.addWidget(self.proc_label)
        self.toplayout.addWidget(self.proc_number)
        
        self.btmlayout.addWidget(self.start_stop)
        self.btmlayout.addWidget(self.refresh)
        self.btmlayout.addWidget(self.kill)
        self.process_view = ListView()
        self.process_delegate = ListDelegate()
        self.process_view.setItemDelegate(self.process_delegate)
        self.layout.addLayout(self.toplayout)
        self.layout.addLayout(self.btmlayout)
        self.layout.addWidget(self.process_view)
        self.setLayout(self.layout)
        self.connect_slots()

    def connect_slots(self):
        self.start_stop.clicked.connect(self.start_action)
        self.refresh.clicked.connect(self._update_info)

    def toggle_start_btn(self):
        icon = QtWidgets.QStyle.SP_MediaStop if self._start_state == "start" \
                else QtWidgets.QStyle.SP_MediaPlay
        self.start_stop.setIcon(
            self.style().standardIcon(icon)
        )
        self._start_state = "stop" if self._start_state == "start" else 'start'
        self.start_stop.setText(self._start_state.title())

    def _update_info(self):
        if self._proc_manager:
            self.model = ListModel(self._proc_manager.get_update())
            self.process_view.setModel(self.model)

    def start_action(self):
        n_procs = int(self.proc_number.text())
        if not self._proc_manager:
            self._proc_manager = manager.MultiProcessManager(n_procs)
        
        current_state = self._start_state
        
        if current_state == "stop":
            self._proc_manager.stop()

        self._update_info()
        self.toggle_start_btn()

        

def get_processes_info():

    return [
        {
            "name": "test",
            "pid": 1234,
            "task": "func",
            "status": "running", 
            "metadata": "mem"
        },
        {
            "name": "test2",
            "pid": 1234,
            "task": "func",
            "status": "running", 
            "metadata": "mem"
        },
    ]

if __name__ == '__main__':
    print(logger.getEffectiveLevel())
    logger.info("Starting app..")
    logger.debug("DStarting app..")
    logger.warning("WStarting app..")
    application = QtWidgets.QApplication([])
    widget = ProcessControlWidget()
    widget.show()
    application.exec_()

