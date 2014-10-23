# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\DEMO\Documents\dev\go2streetview\ui-go2streetviewDum.ui'
#
# Created: Fri Oct 10 15:56:30 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_go2streetviewDum(object):
    def setupUi(self, go2streetviewDum):
        go2streetviewDum.setObjectName(_fromUtf8("go2streetviewDum"))
        go2streetviewDum.resize(300, 300)
        self.label = QtGui.QLabel(go2streetviewDum)
        self.label.setGeometry(QtCore.QRect(5, 0, 291, 301))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))

        self.retranslateUi(go2streetviewDum)
        QtCore.QMetaObject.connectSlotsByName(go2streetviewDum)

    def retranslateUi(self, go2streetviewDum):
        go2streetviewDum.setWindowTitle(_translate("go2streetviewDum", "go2streetview", None))
        self.label.setText(_translate("go2streetviewDum", "click to open Google Streetview", None))

