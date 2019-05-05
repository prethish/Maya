""" Utils related to Qt and maya windows"""
from maya import mel, cmds, OpenMayaUI
from maya_utils._core.Qt import QtWidgets
try:
    import shiboken
except:
    import shiboken2 as shiboken


def get_maya_window():
    """
        Find Maya's main Window
    """
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken.wrapInstance(long(window), QtWidgets.QMainWindow)
    return window


def get_maya_menu():
    """
        Find Maya's main MenuBar.
    """
    menuBar = [m for m in get_maya_window().children() if type(m) == QtWidgets.QMenuBar] or [None]
    return menuBar[0]


def get_m3view_widget():
    model_editor = cmds.playblast(activeEditor=True)
    main_m3dView= omUI.M3dView.getM3dViewFromModelEditor(model_editor)
    return shiboken.wrapInstance(long(main_m3dView.widget()), QtWidgets.QWidget)

def maya_to_qt(name):
    """
        Maya name -> QWidget
    """
    ptr = OpenMayaUI.MQtUtil.findControl(name)
    if ptr is None: ptr = OpenMayaUI.MQtUtil.findLayout(name)
    if ptr is None: ptr = OpenMayaUI.MQtUtil.findMenuItem(name)
    if ptr is not None:
        return shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)


def qt_to_maya(widget):
    """ QWidget -> Maya name

        Args:
            widget (QtWidgets.QWidget):

        Returns:

    """
    return OpenMayaUI.MQtUtil.fullName(long(shiboken.getCppPointer(widget)[0]))


def get_maya_statusLine():
    """ Get the QtWidget for maya status line"""
    gStatusLine = mel.eval("global string $gStatusLine;$gStatusLine= $gStatusLine;")
    return maya_to_qt(gStatusLine)