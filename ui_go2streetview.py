# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\documenti\dev\go2streetview\go2streetview.ui'
#
# Created: Wed Mar 25 12:28:58 2015
#      by: PyQt4 UI code generator 4.11.3
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
        self.SV = QtWebKit.QWebView(Dialog)
        self.SV.setGeometry(QtCore.QRect(0, 0, 600, 360))
        self.SV.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.SV.setObjectName(_fromUtf8("SV"))
        self.horizontalLayoutWidget = QtGui.QWidget(Dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 199, 36))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSpacing(1)
        self.horizontalLayout.setMargin(1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnSwitchView = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.btnSwitchView.setMinimumSize(QtCore.QSize(32, 32))
        self.btnSwitchView.setObjectName(_fromUtf8("btnSwitchView"))
        self.horizontalLayout.addWidget(self.btnSwitchView)
        self.btnOpenInBrowser = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.btnOpenInBrowser.setMinimumSize(QtCore.QSize(32, 32))
        self.btnOpenInBrowser.setObjectName(_fromUtf8("btnOpenInBrowser"))
        self.horizontalLayout.addWidget(self.btnOpenInBrowser)
        self.btnTakeSnapshop = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.btnTakeSnapshop.setMinimumSize(QtCore.QSize(32, 32))
        self.btnTakeSnapshop.setObjectName(_fromUtf8("btnTakeSnapshop"))
        self.horizontalLayout.addWidget(self.btnTakeSnapshop)
        self.btnInfoLayer = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.btnInfoLayer.setMinimumSize(QtCore.QSize(32, 32))
        self.btnInfoLayer.setObjectName(_fromUtf8("btnInfoLayer"))
        self.horizontalLayout.addWidget(self.btnInfoLayer)
        self.btnPrint = QtGui.QToolButton(self.horizontalLayoutWidget)
        self.btnPrint.setMinimumSize(QtCore.QSize(32, 32))
        self.btnPrint.setObjectName(_fromUtf8("btnPrint"))
        self.horizontalLayout.addWidget(self.btnPrint)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.btnSwitchView.setText(_translate("Dialog", "Sw", None))
        self.btnOpenInBrowser.setText(_translate("Dialog", "Br", None))
        self.btnTakeSnapshop.setText(_translate("Dialog", "Sn", None))
        self.btnInfoLayer.setText(_translate("Dialog", "In", None))
        self.btnPrint.setText(_translate("Dialog", "Pr", None))

from PyQt4 import QtWebKit
