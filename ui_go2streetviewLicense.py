# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\documenti\dev\go2streetview\ui_go2streetviewLicense.ui'
#
# Created: Mon Oct 27 14:43:17 2014
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_go2streetviewLicense(object):
    def setupUi(self, go2streetviewLicense):
        go2streetviewLicense.setObjectName(_fromUtf8("go2streetviewLicense"))
        go2streetviewLicense.resize(441, 344)
        self.verticalLayout = QtGui.QVBoxLayout(go2streetviewLicense)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.textBrowser = QtGui.QTextBrowser(go2streetviewLicense)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.verticalLayout.addWidget(self.textBrowser)
        self.checkGoogle = QtGui.QCheckBox(go2streetviewLicense)
        self.checkGoogle.setObjectName(_fromUtf8("checkGoogle"))
        self.verticalLayout.addWidget(self.checkGoogle)
        self.checkBing = QtGui.QCheckBox(go2streetviewLicense)
        self.checkBing.setObjectName(_fromUtf8("checkBing"))
        self.verticalLayout.addWidget(self.checkBing)

        self.retranslateUi(go2streetviewLicense)
        QtCore.QMetaObject.connectSlotsByName(go2streetviewLicense)

    def retranslateUi(self, go2streetviewLicense):
        go2streetviewLicense.setWindowTitle(QtGui.QApplication.translate("go2streetviewLicense", "Licence and Terms of services", None, QtGui.QApplication.UnicodeUTF8))
        self.textBrowser.setHtml(QtGui.QApplication.translate("go2streetviewLicense", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600;\">License</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">go2streetview plugin is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-style:italic;\">Copyright (c) 2014 Enrico Ferreguti</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">The plugin gives access to services Google Maps and Microsoft Bing Maps that have specific terms of service you must accept to use the plugin:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://developers.google.com/maps/terms\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">Google Maps</span></a><span style=\" font-size:8pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.microsoft.com/maps/product/terms.html\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; text-decoration: underline; color:#0057ae;\">Microsoft® Bing™ Maps</span></a></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.checkGoogle.setText(QtGui.QApplication.translate("go2streetviewLicense", "I have Read and I agree With Google Maps Terms of Service", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBing.setText(QtGui.QApplication.translate("go2streetviewLicense", "I have Read and I agree With Microsoft(R) Bing Maps Terms of Service", None, QtGui.QApplication.UnicodeUTF8))

