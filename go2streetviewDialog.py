"""
/***************************************************************************
go2streetview
                                 A QGIS plugin

                             -------------------
        begin                : 
        copyright            : 
        email                : 
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

from PyQt4 import QtCore, QtGui
from ui_go2streetview import Ui_Dialog
from ui_snapshotNotes import Ui_snapshotNotesDialog
# create the view dialog
class go2streetviewDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)
# create the annotation dialog
class snapshotNotesDialog(QtGui.QDialog, Ui_snapshotNotesDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)