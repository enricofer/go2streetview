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

from PyQt5 import Qt, QtCore, QtWidgets, QtGui, QtWebKit, QtWebKitWidgets, QtXml, QtNetwork, uic
from qgis import core, utils, gui

import json
import os
#import html.parser as HTMLParser
import html
import xml.sax.saxutils
import resources_rc

MAIN_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_go2streetview.ui'))

NOTES_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_snapshotNotes.ui'))

LICENSE_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_go2streetviewLicense.ui'))

DUM_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_go2streetviewDum.ui'))

INFOBOX_DIALOG_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_infoBox.ui'))


# create the view dialog
class go2streetviewDialog(QtWidgets.QDockWidget, MAIN_DIALOG_CLASS):

    focus_in = QtCore.pyqtSignal(int, name='focusIn')
    closed_ev = QtCore.pyqtSignal(int, name='closed')
    resized_ev = QtCore.pyqtSignal(int, name='resized')
    enter_ev = QtCore.pyqtSignal(int, name='enter')

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

    def closeEvent(self, event):
        print("closed")
        self.closed_ev.emit(1)

    def resizeEvent (self, event):
        print("resized")
        self.resized_ev.emit(1)

    def enterEvent (self,event):
        print("entered")
        self.enter_ev.emit(1)

# create the annotation dialog
class snapshotNotesDialog(QtWidgets.QDialog, NOTES_DIALOG_CLASS):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

# create the License dialog
class snapshotLicenseDialog(QtWidgets.QDialog, LICENSE_DIALOG_CLASS):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

# create the dummy widget
class dumWidget(QtWidgets.QDialog, DUM_DIALOG_CLASS):

    enter_ev = QtCore.pyqtSignal(int, name='enter')

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

    def enterEvent (self,event):
        self.enter_ev.emit(1)

#create the infobox dialog
class infobox (QtWidgets.QDialog, INFOBOX_DIALOG_CLASS):

    defined = QtCore.pyqtSignal()

    def __init__(self,parentModule):
        QtWidgets.QDialog.__init__(self)
        # Set up the user interface from Designer.
        #self.ui = Ui_Dialog()
        self.parentModule = parentModule
        self.iface = parentModule.iface
        self.setupUi(self)
        self.editInfoBoxHtml.clicked.connect(self.editInfoBoxHtmlAction)
        self.editIconPath.clicked.connect(self.editIconPathAction)
        self.editInfoField.clicked.connect(self.editInfoFieldAction)
        self.enableInfoBoxCheckbox.stateChanged.connect(self.enableInfoBoxAction)
        self.enableInfoLayerCheckbox.stateChanged.connect(self.enableInfoLayerAction)
        self.applyButton.clicked.connect(self.acceptInfoBoxState)
        self.cancelButton.clicked.connect(self.rejectInfoBoxState)
        self.progressBar.hide()
        self.iconPath.setText(self.tr("Icon Path"))
        self.layersCombo.clear()
        self.distanceBuffer.setText("")
        self.distanceBuffer.setValidator(QtGui.QIntValidator(1,1000,self))
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
            self.parentModule.disableControlShape()


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
        txt = self.layersCombo.currentText()
        if txt and txt != "" and txt != self.tr("Select Info Layer"):
            self.infoBoxIni["infoLayer"] = txt
            #set dialog to default
            units = self.layerSet[txt].crs().mapUnits()
            if units == core.QgsUnitTypes.DistanceMeters:
                dValue = '100'
                uStr = self.tr("(Meters)")
            elif units == core.QgsUnitTypes.DistanceFeet:
                dValue = '300'
                uStr = self.tr("(Feet)")
            elif units == core.QgsUnitTypes.DistanceDegrees:
                dValue = '0.000899838928832'
                uStr = self.tr("(Degrees)")
            elif units == core.QgsUnitTypes.DistanceUnknownUnit:
                dValue = ''
                uStr = self.tr("(Unknown unit)")
            elif units == core.QgsUnitTypes.DistanceNauticalMiles:
                dValue = ''
                uStr = self.tr("(Nautical Miles)")
            self.distanceBuffer.setText(dValue)
            self.labelDistanceBuffer.setText(self.tr("Distance buffer ") + uStr)
            self.infoField.clear()
            self.infoboxHtml.clear()
            self.iconPath.clear()
            self.enableInfoBoxCheckbox.setCheckState(QtCore.Qt.Unchecked)
            #self.infoBoxIni = {'infoLayerEnabled': None,'infoBoxTemplate': u'','infoField': '','infoBoxEnabled': None,'iconPath': '','infoLayer': '','distanceBuffer':'100'}
            self.saveIni()


    def loadPointLayers(self,default = None):
        self.layerSet = {}
        for layer_name, layer in core.QgsProject.instance().mapLayers().items():
            
            if layer.type() == core.QgsMapLayer.VectorLayer and (layer.geometryType() in (core.QgsWkbTypes.PointGeometry, core.QgsWkbTypes.LineGeometry, core.QgsWkbTypes.PolygonGeometry)):
                self.layerSet[layer.name()] = layer
        if default:
            if default in self.layerSet.keys():
                defaultLayer = default
            else:
                defaultLayer = None
        else:
            defaultLayer = None
        self.populateComboBox(self.layersCombo,self.layerSet.keys(),predef=defaultLayer,sort = True,msg=self.tr("Select Info Layer"))
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
            self.populateComboBox(self.fieldsCombo,fieldNames,predef=defaultField,msg=self.tr("Select Info Field"))
            #self.fieldsCombo.activated.connect(self.fieldsComboAction)


    def editInfoBoxHtmlAction(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            self.QEX = gui.QgsExpressionBuilderDialog(self.layerSet[self.infoBoxIni["infoLayer"]],"Insert expression",None)
            self.QEX.setExpressionText(self.infoboxHtml.textCursor().selectedText().strip('[%').strip('%]').strip())
            if self.QEX.exec_():
                self.infoboxHtml.insertPlainText('[% {} %]'.format(self.QEX.expressionText()))

    def editInfoFieldAction(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            self.QEX = gui.QgsExpressionBuilderDialog(self.layerSet[self.infoBoxIni["infoLayer"]],"Insert expression",None)
            self.QEX.setExpressionText(self.infoField.text().strip('[%').strip('%]').strip())
            if self.QEX.exec_():
                self.infoField.setText('[% {} %]'.format(self.QEX.expressionText()))

    def editIconPathAction(self):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys():
            self.QEX = gui.QgsExpressionBuilderDialog(self.layerSet[self.infoBoxIni["infoLayer"]],"Insert expression",None)
            self.QEX.setExpressionText(self.iconPath.text().strip('[%').strip('%]').strip())
            if self.QEX.exec_():
                self.iconPath.setText('[% {} %]'.format(self.QEX.expressionText()))

    def populateComboBox(self,combo,list,predef = None,sort = None,msg = ""):
        #procedure to fill specified combobox with provided list
        combo.clear()
        model=QtGui.QStandardItemModel(combo)
        for elem in list:
            try:
                item = QtGui.QStandardItem(elem)
            except TypeError:
                item = QtGui.QStandardItem(str(elem))
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

    def get_featureContext(self,feat):
        infoboxContext = core.QgsExpressionContext()
        infoboxContext.appendScopes(core.QgsExpressionContextUtils.globalProjectLayerScopes(self.getInfolayer()))
        infoboxContext.setFeature(feat)
        infoboxContext.setFields(self.getInfolayer().fields())
        return infoboxContext

    def getHtml(self,feat):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys() and self.enableInfoBoxCheckbox.isChecked():
            htmlExp = core.QgsExpression()
            html = htmlExp.replaceExpressionText(self.infoboxHtml.toPlainText().replace("\n",""), self.get_featureContext(feat))
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
            infoFieldExp = core.QgsExpression()
            content = infoFieldExp.replaceExpressionText(self.infoField.text(), self.get_featureContext(feat))
            if content:
                content = content.replace("\n","")
                content = content.replace('"',"")
                content = content.replace("'","")
            return content
        return ""

    def getFeatId(self,feat):
        if self.mapCommandsCheck.isChecked():
            return feat.id()
        else:
            return 0

    def getIconPath(self,feat):
        if self.infoBoxIni["infoLayer"] in self.layerSet.keys() and self.iconPath.text() != "":
            iconPathExp = core.QgsExpression()
            content = iconPathExp.replaceExpressionText(self.iconPath.text().replace("\n",""), self.get_featureContext(feat))
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
        #prjFileInfo = QtCore.QFileInfo(core.QgsProject.instance().fileName())
        #iniFileInfo = QtCore.QFileInfo(os.path.join(prjFileInfo.path(),prjFileInfo.baseName()+".gsv"))
        stored_settings = core.QgsExpressionContextUtils.projectScope(core.QgsProject.instance()).variable('go2sv_infolayer_settings')
        if stored_settings:
            self.infoBoxIni = json.loads(stored_settings)
            self.loadPointLayers(default = self.infoBoxIni["infoLayer"])
            self.infoField.setText(self.infoBoxIni["infoField"])
        else:
            self.infoBoxIni = {'infoLayerEnabled': None,'infoBoxTemplate': u'','infoField': '','infoBoxEnabled': None,'iconPath': '','infoLayer': '','distanceBuffer':'100',"mapCommandsEnabled":None}
            self.loadPointLayers()
        if self.infoBoxIni["infoLayerEnabled"]:
            self.enableInfoLayerCheckbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.enableInfoLayerCheckbox.setCheckState(QtCore.Qt.Unchecked)
        self.iconPath.setText(self.infoBoxIni["iconPath"])
        self.distanceBuffer.setText(self.infoBoxIni["distanceBuffer"])
        if self.infoBoxIni["infoBoxEnabled"]:
            self.enableInfoBoxCheckbox.setCheckState(QtCore.Qt.Checked)
        else:
            self.enableInfoBoxCheckbox.setCheckState(QtCore.Qt.Unchecked)
        if self.infoBoxIni["mapCommandsEnabled"]:
            self.mapCommandsCheck.setCheckState(QtCore.Qt.Checked)
        else:
            self.enableInfoBoxCheckbox.setCheckState(QtCore.Qt.Unchecked)
        self.infoboxHtml.setPlainText(html.unescape(self.infoBoxIni["infoBoxTemplate"]))
        self.enableInfoLayerAction(True)
        if self.infoIndex and self.enableInfoLayerCheckbox.isChecked():
            self.updateSpatialIndex()
        self.defined.emit()


    def saveIni(self):
        self.infoBoxIni["infoLayerEnabled"] = self.enableInfoLayerCheckbox.isChecked()
        if self.layersCombo.currentText() != self.tr("Select Info Layer"):
            self.infoBoxIni["infoLayer"] = self.layersCombo.currentText()
        else:
            self.infoBoxIni["infoLayer"] = ""
        self.infoBoxIni["infoField"] = self.infoField.text()
        if self.iconPath.text() != self.tr("Icon Path"):
            self.infoBoxIni["iconPath"] = self.iconPath.text()
        else:
            self.infoBoxIni["iconPath"] = ""
        self.infoBoxIni["distanceBuffer"] = self.distanceBuffer.text()
        self.infoBoxIni["infoBoxEnabled"] = self.enableInfoBoxCheckbox.isChecked()
        self.infoBoxIni["mapCommandsEnabled"] = self.mapCommandsCheck.isChecked()
        self.infoBoxIni["infoBoxTemplate"] = xml.sax.saxutils.escape(self.infoboxHtml.toPlainText())
        core.QgsExpressionContextUtils.setProjectVariable(core.QgsProject.instance(), 'go2sv_infolayer_settings', json.dumps(self.infoBoxIni))

    def showEvent(self,event):
        self.raise_()
        self.restoreIni()

    def getContextFeatures(self,point):
        dist = self.getDistanceBuffer()
        context = core.QgsRectangle(point.x()-dist,point.y()-dist,point.x()+dist,point.y()+dist)
        try:
            return self.infoIndex.intersects(context)
        except:
            return []


    def updateSpatialIndex(self):
        if self.enableInfoLayerCheckbox.isChecked():
            self.infoIndex = core.QgsSpatialIndex ()
            self.progressBar.show()
            self.progressBar.setRange(0,self.getInfolayer().featureCount ())
            infoFeats = self.getInfolayer().getFeatures()
            processed = 0
            for feat in infoFeats:
                self.infoIndex.insertFeature(feat)
                self.progressBar.setValue(processed)
                processed += 1
            self.progressBar.hide()
            self.progressBar.reset()
        else:
            self.infoIndex = None

    def acceptInfoBoxState(self):
        self.saveIni()
        try:
            self.layersCombo.activated.disconnect(self.layersComboAction)
        except:
            pass
        self.updateSpatialIndex()
        self.hide()
        self.defined.emit()

    def rejectInfoBoxState(self):
        self.hide()

