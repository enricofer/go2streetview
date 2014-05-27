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

    focus_in = QtCore.pyqtSignal(int, name='focusIn')
    closed_ev = QtCore.pyqtSignal(int, name='closed')
    resized_ev = QtCore.pyqtSignal(int, name='resized')

    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)
        
    def focusInEvent(self, event):
        print "FOCUS IN"
        self.focus_in.emit()
        #QtGui.QWidget.focusInEvent(self, event)
        
    def focusOutEvent(self, event):
        print "FOCUS OUT"
        
    def closeEvent(self, event):
        print "closed"
        self.closed_ev.emit(1)
        #QtGui.QWidget.closeEvent(self, event)
        
    def resizeEvent (self, event):
        print "resized"
        self.resized_ev.emit(1)

# create the annotation dialog
class snapshotNotesDialog(QtGui.QDialog, Ui_snapshotNotesDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)