# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\documenti\dev\go2streetview\ui_go2streetviewDum.ui'
#
# Created: Mon Oct 27 12:32:24 2014
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_go2streetviewDum(object):
    def setupUi(self, go2streetviewDum):
        go2streetviewDum.setObjectName(_fromUtf8("go2streetviewDum"))
        go2streetviewDum.resize(326, 234)
        self.verticalLayout = QtGui.QVBoxLayout(go2streetviewDum)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelBottom = QtGui.QLabel(go2streetviewDum)
        self.labelBottom.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.labelBottom.setObjectName(_fromUtf8("labelBottom"))
        self.verticalLayout.addWidget(self.labelBottom)
        self.iconRif = QtGui.QLabel(go2streetviewDum)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.iconRif.sizePolicy().hasHeightForWidth())
        self.iconRif.setSizePolicy(sizePolicy)
        self.iconRif.setText(_fromUtf8(""))
        self.iconRif.setPixmap(QtGui.QPixmap(_fromUtf8("icoStreetview.png")))
        self.iconRif.setScaledContents(False)
        self.iconRif.setAlignment(QtCore.Qt.AlignCenter)
        self.iconRif.setObjectName(_fromUtf8("iconRif"))
        self.verticalLayout.addWidget(self.iconRif)
        self.labelTop = QtGui.QLabel(go2streetviewDum)
        self.labelTop.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.labelTop.setObjectName(_fromUtf8("labelTop"))
        self.verticalLayout.addWidget(self.labelTop)

        self.retranslateUi(go2streetviewDum)
        QtCore.QMetaObject.connectSlotsByName(go2streetviewDum)

    def retranslateUi(self, go2streetviewDum):
        go2streetviewDum.setWindowTitle(QtGui.QApplication.translate("go2streetviewDum", "go2streetview", None, QtGui.QApplication.UnicodeUTF8))
        self.labelBottom.setText(QtGui.QApplication.translate("go2streetviewDum", "click icon", None, QtGui.QApplication.UnicodeUTF8))
        self.labelTop.setText(QtGui.QApplication.translate("go2streetviewDum", "to open Google Streetview", None, QtGui.QApplication.UnicodeUTF8))

