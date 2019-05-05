"""Customize maya gui
"""
import yaml
import os
import pymel.core as pm
from maya import OpenMaya, cmds
from maya_utils._core import qt_utils as _qt_utils
from maya_utils._core.Qt import QtWidgets


def find_menu(name):
    """Find the maya menu with name.This was written maya
    currently does not allow to query for a menu path.

    Args:
        name (str):

    Returns:

    """
    _main_window = _qt_utils.get_maya_window()
    for menu_widget in _main_window.findChildren(QtWidgets.QMenu):
        if name == menu_widget.title():
            return _qt_utils.qt_to_maya(menu_widget)
    return None


def create_sub_menus(parent_menu, menu_items):
    """[summary]

    Arguments:
        parent_menu {[type]} -- [description]
        menu_items {[type]} -- [description]
    """
    for label,item in menu_items.iteritems():
        if isinstance(item, dict):
            new_menu = pm.menuItem(subMenu=True, label=label, parent=parent_menu)
            create_sub_menus(new_menu, item)
        else:
            pm.menuItem(label=label, command=item, parent=parent_menu)


def add_menu_to_maya(menu_name, menu_items, append=False):
    """Add a menuitem to the maya main menu

    Args:
        menu_name:
        menu_items:
    """
    _main_window= pm.language.melGlobals['gMainWindow']
    custom_menu = None
    if append:
        custom_menu = find_menu(menu_name)

    if not custom_menu:
        if pm.menu(menu_name, exists=True):
            pm.deleteUI(menu_name, menu=True)
        custom_menu = pm.menu(menu_name, parent=_main_window)
    create_sub_menus(custom_menu,menu_items)


def create_menu_from_yaml(file_path):
    data_map = None
    with open(file_path) as f:
        data_map = yaml.safe_load(f)
    add_menu_to_maya("maya_utils",data_map)

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)

create_menu_from_yaml(
    os.path.join(parent_dir, "configs", "startup_menu.yaml")
)
