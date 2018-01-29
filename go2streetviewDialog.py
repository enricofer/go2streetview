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

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.utils import *
from qgis.gui import *

from ui_go2streetview import Ui_Dialog
from ui_snapshotNotes import Ui_snapshotNotesDialog
from ui_go2streetviewDum import Ui_go2streetviewDum
from ui_infoBox import Ui_infoBoxDialog

import json
import HTMLParser
import xml.sax.saxutils
import os
import resources_rc

#MAIN_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui_go2streetview.ui'))

#NOTES_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui_snapshotNotes.ui'))

LICENSE_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_go2streetviewLicense.ui'))

#DUM_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui_go2streetviewDum.ui'))

#INFOBOX_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui_infoBox.ui'))


# create the view dialog
class go2streetviewDialog(QDockWidget, Ui_Dialog):

    focus_in = QtCore.pyqtSignal(int, name='focusIn')
    closed_ev = QtCore.pyqtSignal(int, name='closed')
    resized_ev = QtCore.pyqtSignal(int, name='resized')
    enter_ev = QtCore.pyqtSignal(int, name='enter')

    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)

    def closeEvent(self, event):
        #print "closed"
        self.closed_ev.emit(1)
        #QtGui.QWidget.closeEvent(self, event)

    def resizeEvent (self, event):
        #print "resized"
        self.resized_ev.emit(1)

    def enterEvent (self,event):
        self.enter_ev.emit(1)

# create the annotation dialog
class snapshotNotesDialog(QDialog, Ui_snapshotNotesDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)

# create the License dialog
class snapshotLicenseDialog(QDialog, LICENSE_DIALOG_CLASS):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)

# create the dummy widget
class dumWidget(QDialog, Ui_go2streetviewDum):

    enter_ev = QtCore.pyqtSignal(int, name='enter')

    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.setupUi(self)

    def enterEvent (self,event):
        self.enter_ev.emit(1)

#create the infobox dialog
class infobox (QDialog, Ui_infoBoxDialog):

    def __init__(self,iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.iface = iface
        self.setupUi(self)
        self.editInfoBoxHtml.clicked.connect(self.editInfoBoxHtmlAction)
        self.editIconPath.clicked.connect(self.editIconPathAction)
        self.editInfoField.clicked.connect(self.editInfoFieldAction)
        self.enableInfoBoxCheckbox.stateChanged.connect(self.enableInfoBoxAction)
        self.enableInfoLayerCheckbox.stateChanged.connect(self.enableInfoLayerAction)
        self.applyButton.clicked.connect(self.acceptInfoBoxState)
        self.cancelButton.clicked.connect(self.rejectInfoBoxState)
        self.progressBar.hide()
        self.iconPath.setText("Icon Path")
        self.layersCombo.clear()
        self.distanceBuffer.setText("")
        self.distanceBuffer.setValidator(QIntValidator(1,1000,self))
        self.infoBoxIni = {'infoLayerEnabled': None,'infoBoxTemplate': u'','infoField': '','infoBoxEnabled': None,'iconPath': '','infoLayer': '','distanceBuffer':'100',"mapCommandsEnabled":None}
        self.layerSet = {}
        self.infoIndex = None

    def enableInfoLayerAction(self,state):
        if self.enableInfoLayerCheckbox.isChecked():
            self.layersCombo.setEnabled(True)
            self.infoField.setEnabled(True)
            self.iconPath.setEnabled(True)
            self.enableInfoBoxCheckbox.setEnabled(True)
            self.mapCommandsCheck.setEnabled(True)
            self.enableInfoBoxAction(None)
            self.distanceBuffer.setEnabled(True)
            self.editInfoField.setEnabled(True)
            self.editIconPath.setEnabled(True)
        else:
            self.layersCombo.setEnabled(False)
            self.infoField.setEnabled(False)
            self.iconPath.setEnabled(False)
            self.enableInfoBoxCheckbox.setEnabled(False)
            self.mapCommandsCheck.setEnabled(False)
            self.infoboxHtml.setEnabled(False)
            self.editInfoBoxHtml.setEnabled(False)
            self.distanceBuffer.setEnabled(False)
            self.editInfoField.setEnabled(False)
            self.editIconPath.setEnabled(False)


    def enableInfoBoxAction(self,state):
        if self.enableInfoBoxCheckbox.isChecked():
            self.infoboxHtml.setEnabled(True)
            self.editInfoBoxHtml.setEnabled(True)
            self.mapCommandsCheck.setEnabled(True)
        else:
            self.infoboxHtml.setEnabled(False)
            self.editInfoBoxHtml.setEnabled(False)
            self.mapCommandsCheck.setEnabled(False)


    def layersComboAction(self,idx):
        #print idx
        txt = self.layersCombo.currentText()
        if txt and txt != "" and txt != "Select Info Layer":
            self.infoBoxIni["infoLayer"] = txt
            #set dialog to default
            units = self.layerSet[txt].crs().mapUnits()
            if units == QGis.Meters:
                dValue = '100'
                uStr = "(Meters)"
            elif units == QGis.Feet:
                dValue = '300'
                uStr = "(Feet)"
            elif units == QGis.Degrees:
                dValue = '0.000899838928832'
                uStr = "(Degrees)"
            elif units == QGis.UnknownUnit:
                dValue = ''
                uStr = "(Unknown unit)"
            elif units == QGis.DecimalDegrees:
                dValue = ''
                uStr = "(Decimal Degrees)"
            elif units == QGis.DegreesMinutesSeconds:
                dValue = ''
                uStr = "(Degrees Minutes Seconds)"
            elif units == QGis.DegreesDecimalMinutes:
                dValue = ''
                uStr = "(Degrees Decimal Minutes)"
            elif units == QGis.NauticalMiles:
                dValue = ''
                uStr = "(Nautical Miles)"
            self.distanceBuffer.setText(dValue)
            self.labelDistanceBuffer.setText("Distance buffer " + uStr)
            self.infoField.clear()
            self.infoboxHtml.clear()
            self.iconPath.clear()
            self.enableInfoBoxCheckbox.setCheckState(Qt.Unchecked)
            #self.infoBoxIni = {'infoLayerEnabled': None,'infoBoxTemplate': u'','infoField': '','infoBoxEnabled': None,'iconPath': '','infoLayer': '','distanceBuffer':'100'}
            self.saveIni()


    def loadPointLayers(self,default = None):
        self.layerSet = {}
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer and (layer.geometryType() == QGis.Point or layer.geometryType() == QGis.Line or layer.geometryType() == QGis.Polygon):
                self.layerSet[layer.name()] = layer
        if default:
            if default in self.layerSet.keys():
                defaultLayer = default
            else:
                defaultLayer = None
        else:
            defaultLayer = None
        #print self.layerSet
        self.populateComboBox(self.layersCombo,self.layerSet.keys(),predef=defaultLayer,sort = True,msg="Select Info Layer")
        self.layersCombo.activated.connect(self.layersComboAction)


    def loadFields(self,layer,default = None):
        if layer and layer != "":
            fieldNames = [field.name() for field in layer.pendingFields() ]
            if default:
                if default in fieldNames:
                    defaultField = default
                else:
                    defaultField = None
            else:
                defaultField = None
            self.populateComboBox(self.fieldsCombo,fieldNames,predef=defaultField,msg="Select Info Field")
            #self.fieldsCombo.activated.connect(self.fieldsComboAction)

    #def fieldsComboAction(self):
    #    self.saveIni()

    def editInfoBoxHtmlAction(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            self.QEX = QgsExpressionBuilderDialog(self.layerSet[self.infoBoxIni["infoLayer"]],"Insert expression",None)
            self.QEX.setExpressionText(self.infoboxHtml.textCursor().selectedText().strip('[%').strip('%]').strip())
            if self.QEX.exec_():
                self.infoboxHtml.insertPlainText('[% {} %]'.format(self.QEX.expressionText()))

    def editInfoFieldAction(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            self.QEX = QgsExpressionBuilderDialog(self.layerSet[self.infoBoxIni["infoLayer"]],"Insert expression",None)
            self.QEX.setExpressionText(self.infoField.text().strip('[%').strip('%]').strip())
            if self.QEX.exec_():
                self.infoField.setText('[% {} %]'.format(self.QEX.expressionText()))

    def editIconPathAction(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            self.QEX = QgsExpressionBuilderDialog(self.layerSet[self.infoBoxIni["infoLayer"]],"Insert expression",None)
            self.QEX.setExpressionText(self.iconPath.text().strip('[%').strip('%]').strip())
            if self.QEX.exec_():
                self.iconPath.setText('[% {} %]'.format(self.QEX.expressionText()))

    def populateComboBox(self,combo,list,predef = None,sort = None,msg = ""):
        #procedure to fill specified combobox with provided list
        combo.clear()
        model=QStandardItemModel(combo)
        for elem in list:
            try:
                item = QStandardItem(unicode(elem))
            except TypeError:
                item = QStandardItem(str(elem))
            model.appendRow(item)
        if sort:
            model.sort(0)
        combo.setModel(model)
        idx = combo.findText(predef)
        if idx != -1:
            combo.setCurrentIndex(idx)
        else:
            combo.insertItem(0,msg)
            combo.setCurrentIndex(0)

    def copyToTextBox(self,valid):
        if valid:
            self.infoboxHtml.setPlainText (self.QEX.expressionText())

    def getHtml(self,feat):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys() and self.enableInfoBoxCheckbox.isChecked():
            infoLayerId = self.layerSet[self.infoBoxIni["infoLayer"]]
            html = QgsExpression.replaceExpressionText(self.infoboxHtml.toPlainText().replace("\n",""),feat,infoLayerId)
            if html:
                html = html.replace("\n","")
                html = html.replace('"',"")
                html = html.replace("'","")
                return html
            else:
                return ""
        else:
            return ""

    def getInfoField(self,feat):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys() and self.infoField.text() != "":
            infoLayerId = self.layerSet[self.infoBoxIni["infoLayer"]]
            content = QgsExpression.replaceExpressionText(self.infoField.text(),feat,infoLayerId)
            content = content.replace("\n","")
            content = content.replace('"',"")
            content = content.replace("'","")
            #print content
            return content
        return ""

    def getFeatId(self,feat):
        if self.mapCommandsCheck.isChecked():
            return feat.id()
        else:
            return 0

    def getIconPath(self,feat):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys() and self.iconPath.text() != "":
            infoLayerId = self.layerSet[self.infoBoxIni["infoLayer"]]
            content = QgsExpression.replaceExpressionText(self.iconPath.text().replace("\n",""),feat,infoLayerId)
            return content
        return ""

    def getFieldContent(self,feat):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            idx = self.layerSet[self.infoBoxIni["infoLayer"]].fieldNameIndex(self.infoBoxIni["infoField"])
            return feat.attributes()[idx]

    def getInfolayer(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            return self.layerSet[self.infoBoxIni["infoLayer"]]
        else:
            return None

    def isEnabled(self):
        return self.infoBoxIni["infoLayerEnabled"]

    def infoBoxEnabled(self):
        return self.infoBoxIni["infoLayerEnabled"]

    def getDistanceBuffer(self):
        return float(self.infoBoxIni["distanceBuffer"])

    def restoreIni(self):
        prjFileInfo = QFileInfo(QgsProject.instance().fileName())
        iniFileInfo = QFileInfo(os.path.join(prjFileInfo.path(),prjFileInfo.baseName()+".gsv"))
        if iniFileInfo.exists():
            with open(iniFileInfo.filePath(), 'r') as data_file:
                self.infoBoxIni = json.load(data_file)
            self.loadPointLayers(default = self.infoBoxIni["infoLayer"])
            self.infoField.setText(self.infoBoxIni["infoField"])
        else:
            self.infoBoxIni = {'infoLayerEnabled': None,'infoBoxTemplate': u'','infoField': '','infoBoxEnabled': None,'iconPath': '','infoLayer': '','distanceBuffer':'100',"mapCommandsEnabled":None}
            self.loadPointLayers()
        #print self.infoBoxIni
        if self.infoBoxIni["infoLayerEnabled"]:
            self.enableInfoLayerCheckbox.setCheckState(Qt.Checked)
        else:
            self.enableInfoLayerCheckbox.setCheckState(Qt.Unchecked)
        self.iconPath.setText(self.infoBoxIni["iconPath"])
        self.distanceBuffer.setText(self.infoBoxIni["distanceBuffer"])
        if self.infoBoxIni["infoBoxEnabled"]:
            self.enableInfoBoxCheckbox.setCheckState(Qt.Checked)
        else:
            self.enableInfoBoxCheckbox.setCheckState(Qt.Unchecked)
        if self.infoBoxIni["mapCommandsEnabled"]:
            self.mapCommandsCheck.setCheckState(Qt.Checked)
        else:
            self.enableInfoBoxCheckbox.setCheckState(Qt.Unchecked)
        html_parser = HTMLParser.HTMLParser()
        self.infoboxHtml.setPlainText(html_parser.unescape(self.infoBoxIni["infoBoxTemplate"]))
        self.enableInfoLayerAction(True)
        try:
            self.infoIndex
        except:
            if self.enableInfoLayerCheckbox.isChecked():
                self.updateSpatialIndex()

    def saveIni(self):
        self.infoBoxIni["infoLayerEnabled"] = self.enableInfoLayerCheckbox.isChecked()
        if self.layersCombo.currentText() != "Select Info Layer":
            self.infoBoxIni["infoLayer"] = self.layersCombo.currentText()
        else:
            self.infoBoxIni["infoLayer"] = ""
        self.infoBoxIni["infoField"] = self.infoField.text()
        if self.iconPath.text() != "Icon Path":
            self.infoBoxIni["iconPath"] = self.iconPath.text()
        else:
            self.infoBoxIni["iconPath"] = ""
        self.infoBoxIni["distanceBuffer"] = self.distanceBuffer.text()
        self.infoBoxIni["infoBoxEnabled"] = self.enableInfoBoxCheckbox.isChecked()
        self.infoBoxIni["mapCommandsEnabled"] = self.mapCommandsCheck.isChecked()
        self.infoBoxIni["infoBoxTemplate"] = xml.sax.saxutils.escape(self.infoboxHtml.toPlainText())
        prjFileInfo = QFileInfo(QgsProject.instance().fileName())
        iniFileInfo = QFileInfo(os.path.join(prjFileInfo.path(),prjFileInfo.baseName()+".gsv"))
        with open(iniFileInfo.filePath(), 'w') as data_file:
            json.dump(self.infoBoxIni, data_file, indent=3)

    def showEvent(self,event):
        self.raise_()
        self.restoreIni()

    def getContextFeatures(self,point):
        dist = self.getDistanceBuffer()
        context = QgsRectangle(point.x()-dist,point.y()-dist,point.x()+dist,point.y()+dist)
        try:
            return self.infoIndex.intersects(context)
        except:
            return []


    def updateSpatialIndex(self):
        if self.enableInfoLayerCheckbox.isChecked():
            self.infoIndex = QgsSpatialIndex ()
            self.progressBar.show()
            self.progressBar.setRange(0,self.getInfolayer().featureCount ())
            infoFeats = self.getInfolayer().getFeatures()
            processed = 0
            #print self.getInfolayer().featureCount ()
            for feat in infoFeats:
                self.infoIndex.insertFeature(feat)
                self.progressBar.setValue(processed)
                processed += 1
            #print "indexed:",processed
            self.progressBar.hide()
            self.progressBar.reset()
        else:
            self.infoIndex = None

    def acceptInfoBoxState(self):
        self.saveIni()
        self.layersCombo.activated.disconnect(self.layersComboAction)
        self.updateSpatialIndex()
        self.hide()
        self.defined.emit()

    def rejectInfoBoxState(self):
        self.hide()

    defined = pyqtSignal()
