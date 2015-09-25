# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\dev\go2streetview\ui_go2streetviewLicense.ui'
#
# Created: Fri Sep 25 12:37:29 2015
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

class Ui_go2streetviewLicense(object):
    def setupUi(self, go2streetviewLicense):
        go2streetviewLicense.setObjectName(_fromUtf8("go2streetviewLicense"))
        go2streetviewLicense.resize(441, 310)
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
        go2streetviewLicense.setWindowTitle(_translate("go2streetviewLicense", "Licence and Terms of services", None))
        self.textBrowser.setHtml(_translate("go2streetviewLicense", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:10pt; font-weight:600;\">License</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">go2streetview plugin is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic;\">Copyright (C) 2014 Enrico Ferreguti</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic;\">Tiledlayer class: Copyright (C) 2013 by Minoru Akagi</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic;\">ReverseGeocoder class: Copyright (C) 2011 Rupert de Guzman</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt;\">The plugin gives access to services Google Maps and Microsoft Bing Maps that have specific terms of service you are accepting in order to use the plugin:</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Ubuntu\'; font-size:9pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://developers.google.com/maps/terms\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic; text-decoration: underline; color:#0057ae;\">Google Maps</span></a><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"http://www.microsoft.com/maps/product/terms.html\"><span style=\" font-family:\'Ubuntu\'; font-size:9pt; font-style:italic; text-decoration: underline; color:#0057ae;\">Microsoft® Bing™ Maps</span></a></p></body></html>", None))
        self.checkGoogle.setText(_translate("go2streetviewLicense", "I have Read and I agree to the Google Maps Terms of Service", None))
        self.checkBing.setText(_translate("go2streetviewLicense", "I have Read and I agree to the Microsoft(R) Bing Maps Terms of Service", None))

