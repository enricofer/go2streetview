# -*- coding: utf-8 -*-
"""
/***************************************************************************
 globespotterTestDialog
                                 A QGIS plugin
 desc
                             -------------------
        begin                : 2015-01-30
        git sha              : $Format:%H$
        copyright            : (C) 2015 by ef
        email                : enricofer@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtCore, QtGui, uic
from globespotterTest_dialog_base import Ui_globespotterTestDialogBase


class globespotterTestDialog(QtGui.QDialog, Ui_globespotterTestDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        QtGui.QDialog.__init__(self)
        #super(globespotterTestDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
