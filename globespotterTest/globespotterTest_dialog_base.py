# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'globespotterTest_dialog_base.ui'
#
# Created: Mon Mar 02 13:34:37 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

from PyQt4 import QtWebKit
from PyQt4.QtWebKit import QWebView,QWebPage,QWebSettings

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



class MyBrowser(QWebPage):
    ''' Settings for the browser.'''

    def userAgentForUrl(self, url):
        ''' Returns a User Agent that will be seen by the website. '''
        return "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36"

class Browser(QWebView):
    def __init__(self,widget):
        QWebSettings.globalSettings().setAttribute(QWebSettings.PluginsEnabled, True);
        QWebView.__init__(self,widget)
        self.setPage(MyBrowser())



class Ui_globespotterTestDialogBase(object):
    def setupUi(self, globespotterTestDialogBase):
        globespotterTestDialogBase.setObjectName(_fromUtf8("globespotterTestDialogBase"))
        globespotterTestDialogBase.resize(431, 439)
        self.verticalLayout = QtGui.QVBoxLayout(globespotterTestDialogBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        #self.webView = QtWebKit.QWebView(globespotterTestDialogBase)
        self.webView = Browser(globespotterTestDialogBase)
        self.webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.webView.setObjectName(_fromUtf8("webView"))
        self.verticalLayout.addWidget(self.webView)
        self.button_box = QtGui.QDialogButtonBox(globespotterTestDialogBase)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(globespotterTestDialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), globespotterTestDialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), globespotterTestDialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(globespotterTestDialogBase)

    def retranslateUi(self, globespotterTestDialogBase):
        globespotterTestDialogBase.setWindowTitle(_translate("globespotterTestDialogBase", "globespotterTest", None))

