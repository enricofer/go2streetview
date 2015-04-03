# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/enrico/Documenti/plugins/go2streetview/ui_infoBox.ui'
#
# Created: Fri Apr  3 00:32:30 2015
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

class Ui_infoBoxDialog(object):
    def setupUi(self, infoBoxDialog):
        infoBoxDialog.setObjectName(_fromUtf8("infoBoxDialog"))
        infoBoxDialog.resize(270, 452)
        self.verticalLayout_2 = QtGui.QVBoxLayout(infoBoxDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.enableInfoLayerCheckbox = QtGui.QCheckBox(infoBoxDialog)
        self.enableInfoLayerCheckbox.setObjectName(_fromUtf8("enableInfoLayerCheckbox"))
        self.verticalLayout_2.addWidget(self.enableInfoLayerCheckbox)
        self.labelInfoLayer = QtGui.QLabel(infoBoxDialog)
        self.labelInfoLayer.setObjectName(_fromUtf8("labelInfoLayer"))
        self.verticalLayout_2.addWidget(self.labelInfoLayer)
        self.layersCombo = QtGui.QComboBox(infoBoxDialog)
        self.layersCombo.setObjectName(_fromUtf8("layersCombo"))
        self.verticalLayout_2.addWidget(self.layersCombo)
        self.labelDistanceBuffer = QtGui.QLabel(infoBoxDialog)
        self.labelDistanceBuffer.setObjectName(_fromUtf8("labelDistanceBuffer"))
        self.verticalLayout_2.addWidget(self.labelDistanceBuffer)
        self.distanceBuffer = QtGui.QLineEdit(infoBoxDialog)
        self.distanceBuffer.setObjectName(_fromUtf8("distanceBuffer"))
        self.verticalLayout_2.addWidget(self.distanceBuffer)
        self.labelInfoField = QtGui.QLabel(infoBoxDialog)
        self.labelInfoField.setObjectName(_fromUtf8("labelInfoField"))
        self.verticalLayout_2.addWidget(self.labelInfoField)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.infoField = QtGui.QLineEdit(infoBoxDialog)
        self.infoField.setObjectName(_fromUtf8("infoField"))
        self.horizontalLayout.addWidget(self.infoField)
        self.editInfoField = QtGui.QToolButton(infoBoxDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editInfoField.sizePolicy().hasHeightForWidth())
        self.editInfoField.setSizePolicy(sizePolicy)
        self.editInfoField.setMinimumSize(QtCore.QSize(22, 22))
        self.editInfoField.setMaximumSize(QtCore.QSize(24, 24))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/go2streetview/res/expression.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editInfoField.setIcon(icon)
        self.editInfoField.setIconSize(QtCore.QSize(30, 30))
        self.editInfoField.setObjectName(_fromUtf8("editInfoField"))
        self.horizontalLayout.addWidget(self.editInfoField)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.labelIconPath = QtGui.QLabel(infoBoxDialog)
        self.labelIconPath.setObjectName(_fromUtf8("labelIconPath"))
        self.verticalLayout_2.addWidget(self.labelIconPath)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.iconPath = QtGui.QLineEdit(infoBoxDialog)
        self.iconPath.setMaximumSize(QtCore.QSize(16777215, 23))
        self.iconPath.setText(_fromUtf8(""))
        self.iconPath.setObjectName(_fromUtf8("iconPath"))
        self.horizontalLayout_2.addWidget(self.iconPath)
        self.editIconPath = QtGui.QToolButton(infoBoxDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editIconPath.sizePolicy().hasHeightForWidth())
        self.editIconPath.setSizePolicy(sizePolicy)
        self.editIconPath.setMinimumSize(QtCore.QSize(22, 22))
        self.editIconPath.setMaximumSize(QtCore.QSize(24, 24))
        self.editIconPath.setIcon(icon)
        self.editIconPath.setIconSize(QtCore.QSize(30, 30))
        self.editIconPath.setObjectName(_fromUtf8("editIconPath"))
        self.horizontalLayout_2.addWidget(self.editIconPath)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.enableInfoBoxCheckbox = QtGui.QCheckBox(infoBoxDialog)
        self.enableInfoBoxCheckbox.setObjectName(_fromUtf8("enableInfoBoxCheckbox"))
        self.verticalLayout_2.addWidget(self.enableInfoBoxCheckbox)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(4)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.infoboxHtml = QtGui.QPlainTextEdit(infoBoxDialog)
        self.infoboxHtml.setObjectName(_fromUtf8("infoboxHtml"))
        self.horizontalLayout_3.addWidget(self.infoboxHtml)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.editInfoBoxHtml = QtGui.QToolButton(infoBoxDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editInfoBoxHtml.sizePolicy().hasHeightForWidth())
        self.editInfoBoxHtml.setSizePolicy(sizePolicy)
        self.editInfoBoxHtml.setMinimumSize(QtCore.QSize(22, 22))
        self.editInfoBoxHtml.setMaximumSize(QtCore.QSize(24, 24))
        self.editInfoBoxHtml.setIcon(icon)
        self.editInfoBoxHtml.setIconSize(QtCore.QSize(30, 30))
        self.editInfoBoxHtml.setObjectName(_fromUtf8("editInfoBoxHtml"))
        self.verticalLayout.addWidget(self.editInfoBoxHtml)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.buttonBox = QtGui.QDialogButtonBox(infoBoxDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(infoBoxDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), infoBoxDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), infoBoxDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(infoBoxDialog)

    def retranslateUi(self, infoBoxDialog):
        infoBoxDialog.setWindowTitle(_translate("infoBoxDialog", "Dialog", None))
        self.enableInfoLayerCheckbox.setText(_translate("infoBoxDialog", "Enable Info Layer", None))
        self.labelInfoLayer.setText(_translate("infoBoxDialog", "Info Layer", None))
        self.labelDistanceBuffer.setText(_translate("infoBoxDialog", "Distance buffer", None))
        self.labelInfoField.setText(_translate("infoBoxDialog", "Info Field", None))
        self.editInfoField.setText(_translate("infoBoxDialog", "...", None))
        self.labelIconPath.setText(_translate("infoBoxDialog", "Icon Path", None))
        self.editIconPath.setText(_translate("infoBoxDialog", "...", None))
        self.enableInfoBoxCheckbox.setText(_translate("infoBoxDialog", "Enable Html Infobox ", None))
        self.editInfoBoxHtml.setText(_translate("infoBoxDialog", "...", None))

import resources
