#
# Filtering UI for the simple path through the storage code.
#
# Copyright (C) 2009  Red Hat, Inc.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import gtk, gobject
import gtk.glade
import gui

import gettext
_ = lambda x: gettext.ldgettext("anaconda", x)

# The column that holds a python object containing information about the
# device in each row.  This value really shouldn't be overridden.
OBJECT_COL = 0

# These columns can be overridden with the active= and visible= parameters to
# __init__.  active indicates which column tracks whether the row is checked
# by default, and visible indicates which column tracks whether the row is
# seen or not.
VISIBLE_COL = 1
ACTIVE_COL = 2

class DeviceDisplayer(object):
    def _column_toggled(self, menuItem, col):
        # This is called when a selection is made in the column visibility drop
        # down menu, and obviously makes a column visible (or not).
        col.set_visible(not col.get_visible())

    def __init__(self, store, model, view, active=ACTIVE_COL, visible=VISIBLE_COL):
        self.store = store
        self.model = model
        self.view = view

        self.menu = None

        self.active = active
        self.visible = visible

    def addColumn(self, title, num, displayed=True):
        cell = gtk.CellRendererText()
        cell.set_property("yalign", 0)

        col = gtk.TreeViewColumn(title, cell, text=num, active=self.active)
        col.set_visible(displayed)
        col.set_expand(True)
        col.set_resizable(True)
        self.view.append_column(col)

        # This needs to be set on all columns or it will be impossible to sort
        # by that column.
        col.set_sort_column_id(num)

        if self.menu:
            # Add a new entry to the drop-down menu.
            item = gtk.CheckMenuItem(title)
            item.set_active(displayed)
            item.connect("toggled", self._column_toggled, col)
            item.show()
            self.menu.append(item)

    def createMenu(self):
        self.menu = gtk.Menu()

        # Add a blank column at the (current) end of the view.  This column
        # exists only so we can have a header to click on and display the
        # drop down allowing column configuration.
        menuCol = gtk.TreeViewColumn("")
        menuCol.set_clickable(True)
        menuCol.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        menuCol.set_fixed_width(30)
        menuCol.connect("clicked", lambda col, menu: menu.popup(None, None, None, 0, 0),
                        self.menu)

        image = gui.readImageFromFile("filter-menu.png")
        image.show_all()
        menuCol.set_widget(image)

        # Make sure the menu column gets added after all other columns so it
        # will be on the far right edge.
        self.view.connect("show", lambda x: self.view.append_column(menuCol))

    def getSelected(self):
        """Return a list of all the items currently checked in the UI, or
           an empty list if nothing is selected.
        """
        retval = []
        iter = self.store.get_iter_first()

        while iter:
            if self.store.get_value(iter, self.active):
                retval.append(self.store[iter])

            iter = self.store.iter_next(iter)

        return retval

    def getNVisible(self):
        visible = 0

        for row in self.store:
            if row[self.visible]:
                visible += 1

        return visible

class DeviceSelector(DeviceDisplayer):
    def createSelectionCol(self, title="", radioButton=False, toggledCB=None):
        # Add a column full of checkboxes/radiobuttons in the first column of the view.
        crt = gtk.CellRendererToggle()
        crt.set_property("activatable", True)
        crt.set_property("yalign", 0)
        crt.set_radio(radioButton)

        crt.connect("toggled", self._device_toggled, toggledCB, radioButton)

        col = gtk.TreeViewColumn(title, crt, active=self.active)
        col.set_alignment(0.75)

        if not radioButton:
            self.allButton = gtk.ToggleButton()
            col.connect("clicked", lambda *args: self.allButton.set_active(self.allButton.get_active() != True))

            col.set_widget(self.allButton)
            self.allButton.show_all()

            self.allButton.connect("toggled", self._all_clicked, toggledCB)

        self.view.append_column(col)
        self.view.set_headers_clickable(True)

    def _all_clicked(self, button, cb=None):
        # This is called when the Add/Remove all button is checked and does
        # the obvious.
        def _toggle_all(model, path, iter, set):
            # Don't check the boxes of rows that aren't visible.
            visible = model.get_value(iter, self.visible)
            if not visible:
                return

            # Don't try to set a row to active if it's already been checked.
            # This prevents devices that have been checked before the all
            # button was checked from getting double counted.
            if model.get_value(iter, self.active) == set:
                return

            model.set_value(iter, self.active, set)

            if cb:
                cb(set, model.get_value(iter, OBJECT_COL))

        set = button.get_active()
        self.store.foreach(_toggle_all, set)

    def _device_toggled(self, button, row, cb, isRadio):
        # This is called when the checkbox for a device is clicked or unclicked.
        model = self.model
        iter = model.get_iter(row)

        if not iter:
            return

        while not self.store.iter_is_valid(iter):
            iter = model.convert_iter_to_child_iter(iter)
            model = model.get_model()

        if isRadio:
            # This is lame, but there's no other way to do it.  First we have
            # to uncheck everything in the store, then we check the one that
            # was clicked on.
            for r in self.store:
                r[self.active] = False

            self.store[iter][self.active] = True
        else:
            is_checked = self.store.get_value(iter, self.active)
            self.store.set_value(iter, self.active, not is_checked)

        if cb:
            cb(not is_checked, self.store.get_value(iter, OBJECT_COL))