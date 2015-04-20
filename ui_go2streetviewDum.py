# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/enrico/Documenti/plugins/go2streetview/ui_go2streetviewDum.ui'
#
# Created: Mon Apr 20 19:06:05 2015
#      by: PyQt4 UI code generator 4.10.4
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
        go2streetviewDum.resize(326, 281)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(go2streetviewDum.sizePolicy().hasHeightForWidth())
        go2streetviewDum.setSizePolicy(sizePolicy)
        self.verticalLayout = QtGui.QVBoxLayout(go2streetviewDum)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.iconRif = QtGui.QLabel(go2streetviewDum)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.iconRif.sizePolicy().hasHeightForWidth())
        self.iconRif.setSizePolicy(sizePolicy)
        self.iconRif.setMinimumSize(QtCore.QSize(0, 100))
        self.iconRif.setText(_fromUtf8(""))
        self.iconRif.setPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/go2streetview/res/icoStreetview.png")))
        self.iconRif.setScaledContents(False)
        self.iconRif.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.iconRif.setObjectName(_fromUtf8("iconRif"))
        self.verticalLayout.addWidget(self.iconRif)
        self.labelBottom = QtGui.QLabel(go2streetviewDum)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelBottom.sizePolicy().hasHeightForWidth())
        self.labelBottom.setSizePolicy(sizePolicy)
        self.labelBottom.setMinimumSize(QtCore.QSize(0, 20))
        self.labelBottom.setMaximumSize(QtCore.QSize(16777215, 20))
        self.labelBottom.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.labelBottom.setObjectName(_fromUtf8("labelBottom"))
        self.verticalLayout.addWidget(self.labelBottom)
        self.labelTop = QtGui.QLabel(go2streetviewDum)
        self.labelTop.setMinimumSize(QtCore.QSize(0, 100))
        self.labelTop.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.labelTop.setObjectName(_fromUtf8("labelTop"))
        self.verticalLayout.addWidget(self.labelTop)

        self.retranslateUi(go2streetviewDum)
        QtCore.QMetaObject.connectSlotsByName(go2streetviewDum)

    def retranslateUi(self, go2streetviewDum):
        go2streetviewDum.setWindowTitle(_translate("go2streetviewDum", "go2streetview", None))
        self.labelBottom.setText(_translate("go2streetviewDum", "click and drag cursor on map", None))
        self.labelTop.setText(_translate("go2streetviewDum", "to open Google Streetview", None))

import resources
