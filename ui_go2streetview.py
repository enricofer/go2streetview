# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'go2streetview.ui'
#
# Created: Fri Oct 10 11:13:39 2014
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(600, 360)
        self.BE = QtWebKit.QWebView(Dialog)
        self.BE.setGeometry(QtCore.QRect(0, 0, 600, 360))
        self.BE.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.BE.setObjectName(_fromUtf8("BE"))
        self.openInBrowserBE = QtGui.QPushButton(Dialog)
        self.openInBrowserBE.setGeometry(QtCore.QRect(448, 28, 150, 25))
        self.openInBrowserBE.setObjectName(_fromUtf8("openInBrowserBE"))
        self.SV = QtWebKit.QWebView(Dialog)
        self.SV.setGeometry(QtCore.QRect(0, 0, 600, 360))
        self.SV.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.SV.setObjectName(_fromUtf8("SV"))
        self.openInBrowserSV = QtGui.QPushButton(Dialog)
        self.openInBrowserSV.setGeometry(QtCore.QRect(448, 28, 150, 25))
        self.openInBrowserSV.setObjectName(_fromUtf8("openInBrowserSV"))
        self.takeSnapshotSV = QtGui.QPushButton(Dialog)
        self.takeSnapshotSV.setGeometry(QtCore.QRect(448, 54, 150, 25))
        self.takeSnapshotSV.setObjectName(_fromUtf8("takeSnapshotSV"))
        self.switch2BE = QtGui.QPushButton(Dialog)
        self.switch2BE.setGeometry(QtCore.QRect(448, 2, 150, 25))
        self.switch2BE.setObjectName(_fromUtf8("switch2BE"))
        self.switch2SV = QtGui.QPushButton(Dialog)
        self.switch2SV.setGeometry(QtCore.QRect(448, 2, 150, 25))
        self.switch2SV.setObjectName(_fromUtf8("switch2SV"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.openInBrowserBE.setText(_translate("Dialog", "open view in browser", None))
        self.openInBrowserSV.setText(_translate("Dialog", "open view in browser", None))
        self.takeSnapshotSV.setText(_translate("Dialog", "take a snapshot", None))
        self.switch2BE.setText(_translate("Dialog", "Switch to Bing Bird\'s Eye", None))
        self.switch2SV.setText(_translate("Dialog", "Switch to Google Streetview", None))

from PyQt4 import QtWebKit
