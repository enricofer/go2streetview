"""
/***************************************************************************
 go2streetview
                                 A QGIS plugin
 Click to open Google Street View
                              -------------------
        begin                : 2014-03-29
        copyright            : (C) 2014 enrico ferreguti
        email                : enricofer@gmail.com
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
# Import the PyQt and QGIS libraries

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtXml import *
from PyQt4 import uic
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from PyQt4.QtNetwork import *
from string import digits
from go2streetviewDialog import go2streetviewDialog, dumWidget,snapshotLicenseDialog, infobox
from snapshot import snapShot
from transformgeom import transformGeometry

import resources_rc
import webbrowser
import urllib2
import string
import os
import math
import time
import json

class go2streetview(QgsMapTool):

    def __init__(self, iface):

       # Save reference to the QGIS interface
        self.iface = iface
        # reference to the canvas
        self.canvas = self.iface.mapCanvas()
        self.version = 'v7.5'
        QgsMapTool.__init__(self, self.canvas)
        self.S = QSettings()
        terms = self.S.value("go2sv/license", defaultValue =  "undef")
        if terms == self.version:
            self.licenseAgree = True
        else:
            self.licenseAgree = None

    def initGui(self):
        # Create actions that will start plugin configuration
        self.StreetviewAction = QAction(QIcon(":/plugins/go2streetview/res/icoStreetview.png"), \
            "Click to open Google Street View", self.iface.mainWindow())
        self.StreetviewAction.triggered.connect(self.StreetviewRun)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.StreetviewAction)
        self.iface.addPluginToWebMenu("&go2streetview", self.StreetviewAction)
        self.dirPath = os.path.dirname( os.path.abspath( __file__ ) )
        self.actualPOV = {}
        self.view = go2streetviewDialog()
        self.dumView = dumWidget()
        self.dumView.enter.connect(self.clickOn)
        self.dumView.iconRif.setPixmap(QPixmap(":/plugins/go2streetview/res/icoStreetview.png"))
        self.apdockwidget=QDockWidget("go2streetview" , self.iface.mainWindow() )
        self.apdockwidget.setObjectName("go2streetview")
        self.apdockwidget.setWidget(self.dumView)
        self.iface.addDockWidget( Qt.LeftDockWidgetArea, self.apdockwidget)
        self.apdockwidget.update()
        self.viewHeight=self.apdockwidget.size().height()
        self.viewWidth=self.apdockwidget.size().width()
        self.snapshotOutput = snapShot(self)
        self.view.SV.settings().globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True);
        self.view.SV.page().statusBarMessage.connect(self.catchJSevents)
        self.view.BE.page().statusBarMessage.connect(self.catchJSevents)
        #self.view.SV.page().networkAccessManager().finished.connect(self.noSVConnectionsPending)
        #self.view.BE.page().networkAccessManager().finished.connect(self.noBingConnectionsPending)
        #self.view.SV.page().loadFinished.connect(self.loadFinishedAction)
        self.view.enter.connect(self.clickOn)
        self.view.closed.connect(self.closeDialog)
        self.setButtonBarSignals()
        self.infoBoxManager = infobox(self.iface)
        self.infoBoxManager.defined.connect(self.infoLayerDefinedAction)
        self.apdockwidget.visibilityChanged.connect(self.apdockChangeVisibility)
        self.iface.projectRead.connect(self.projectReadAction)
        self.pressed=None
        self.CTRLPressed=None
        self.position=QgsRubberBand(self.iface.mapCanvas(),QGis.Point )
        self.position.setWidth( 5 )
        self.position.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position.setIconSize(6)
        self.position.setColor(Qt.red)
        self.aperture=QgsRubberBand(self.iface.mapCanvas(),QGis.Line )
        self.rotateTool = transformGeometry()
        self.canvas.rotationChanged.connect(self.mapRotationChanged)
        self.canvas.scaleChanged.connect(self.setPosition)
        self.dumLayer = QgsVectorLayer("Point?crs=EPSG:4326", "temporary_points", "memory")
        self.actualPOV = {"lat":0.0,"lon":0.0,"heading":0.0,"zoom":1}
        self.mkDirs()
        self.licenceDlg = snapshotLicenseDialog()
        self.S = QSettings()
        terms = self.S.value("go2sv/license", defaultValue =  "undef")
        self.APIkey = self.S.value("go2sv/APIkey", defaultValue =  "")
        self.licenceDlg.APIkey.setText(self.APIkey)
        if terms == self.version:
            self.licenseAgree = True
            self.licenceDlg.checkGoogle.setCheckState(Qt.Checked)
            self.licenceDlg.checkGoogle.setEnabled(False)
        else:
            self.licenseAgree = None
        self.licenceDlg.OKbutton.clicked.connect(self.checkLicenseAction)
        self.licenceDlg.textBrowser.anchorClicked.connect(self.openExternalUrl)

        self.view.SV.page().setNetworkAccessManager(QgsNetworkAccessManager.instance())
        self.view.BE.page().setNetworkAccessManager(QgsNetworkAccessManager.instance())

        #setting a webinspector dialog
        self.webInspectorDialog = QDialog()
        self.webInspector = QWebInspector(self.webInspectorDialog)
        self.webInspector.setPage(self.view.BE.page())
        self.webInspectorDialog.setLayout(QVBoxLayout())
        self.webInspectorDialog.setWindowTitle("Web Inspector")
        self.webInspectorDialog.resize(800, 480)
        self.webInspectorDialog.layout().addWidget(self.webInspector)
        self.webInspectorDialog.setModal(False)
        self.webInspectorDialog.hide()


    def mkDirs(self):
        newDir = QDir()
        newDir.mkpath(os.path.join(self.dirPath,"tmp"))
        newDir.mkpath(os.path.join(self.dirPath,"snapshots"))

    def setButtonBarSignals(self):
        #Switch button
        self.view.btnSwitchView.clicked.connect(self.switchViewAction)
        #contextMenu
        contextMenu = QMenu()
        self.openInBrowserItem = contextMenu.addAction(QIcon(os.path.join(self.dirPath,"res","browser.png")),"Open in external browser")
        self.openInBrowserItem.triggered.connect(self.openInBrowserAction)
        self.takeSnapshopItem = contextMenu.addAction(QIcon(os.path.join(self.dirPath,"res","images.png")),"Take a panorama snaphot")
        self.takeSnapshopItem.triggered.connect(self.takeSnapshopAction)
        self.infoLayerItem = contextMenu.addAction(QIcon(os.path.join(self.dirPath,"res","markers.png")),"Add info layer")
        self.infoLayerItem.triggered.connect(self.infoLayerAction)
        self.printItem = contextMenu.addAction(QIcon(os.path.join(self.dirPath,"res","print.png")),"Print keymap leaflet")
        self.printItem.triggered.connect(self.printAction)
        contextMenu.addSeparator()
        optionsMenu = contextMenu.addMenu("Options")
        self.showCoverage = optionsMenu.addAction("Show streetview coverage")
        self.showCoverage.setCheckable(True)
        self.showCoverage.setChecked(False)
        optionsMenu.addSeparator()
        self.checkFollow = optionsMenu.addAction("Map follows Streetview")
        self.checkFollow.setCheckable(True)
        self.checkFollow.setChecked(False)
        optionsMenu.addSeparator()
        self.viewLinks = optionsMenu.addAction("View Streetview links")
        self.viewLinks.setCheckable(True)
        self.viewLinks.setChecked(True)
        self.viewAddress = optionsMenu.addAction("View Streetview address")
        self.viewAddress.setCheckable(True)
        self.viewAddress.setChecked(False)
        self.imageDateControl = optionsMenu.addAction("View Streetview image date")
        self.imageDateControl.setCheckable(True)
        self.imageDateControl.setChecked(False)
        self.viewZoomControl = optionsMenu.addAction("View Streetview zoom control")
        self.viewZoomControl.setCheckable(True)
        self.viewZoomControl.setChecked(False)
        self.viewPanControl = optionsMenu.addAction("View Streetview pan control")
        self.viewPanControl.setCheckable(True)
        self.viewPanControl.setChecked(False)
        self.clickToGoControl = optionsMenu.addAction("Streetview click to go")
        self.clickToGoControl.setCheckable(True)
        self.clickToGoControl.setChecked(True)
        self.checkFollow.toggled.connect(self.updateRotate)
        self.viewLinks.toggled.connect(self.updateSVOptions)
        self.viewAddress.toggled.connect(self.updateSVOptions)
        self.imageDateControl.toggled.connect(self.updateSVOptions)
        self.viewZoomControl.toggled.connect(self.updateSVOptions)
        self.viewPanControl.toggled.connect(self.updateSVOptions)
        self.clickToGoControl.toggled.connect(self.updateSVOptions)
        self.showCoverage.toggled.connect(self.showCoverageLayer)
        contextMenu.addSeparator()
        self.showWebInspector = contextMenu.addAction("Show web inspector for debugging")
        self.showWebInspector.triggered.connect(self.showWebInspectorAction)
        self.aboutItem = contextMenu.addAction("About plugin")
        self.aboutItem.triggered.connect(self.aboutAction)

        self.view.btnMenu.setMenu(contextMenu)
        self.view.btnMenu.setPopupMode(QToolButton.InstantPopup)

    def updateSVOptions(self):
        if self.viewLinks.isChecked():
            linksOpt = "true"
        else:
            linksOpt = "false"
        if self.viewAddress.isChecked():
            addressOpt = "true"
        else:
            addressOpt = "false"
        if self.imageDateControl.isChecked():
            imgDateCtrl = "true"
        else:
            imgDateCtrl = "false"
        if self.viewZoomControl.isChecked():
            zoomCtrlOpt = "true"
        else:
            zoomCtrlOpt = "false"
        if self.viewPanControl.isChecked():
            panCtrlOpt = "true"
        else:
            panCtrlOpt = "false"
        if self.clickToGoControl.isChecked():
            clickToGoOpt = "true"
        else:
            clickToGoOpt = "false"
        js = "this.panoClient.setOptions({linksControl:%s,addressControl:%s,imageDateControl:%s,zoomControl:%s,panControl:%s,clickToGo:%s});" %(linksOpt,addressOpt,imgDateCtrl,zoomCtrlOpt,panCtrlOpt,clickToGoOpt)
        self.view.SV.page().mainFrame().evaluateJavaScript(js)


    def showWebInspectorAction(self):
        self.webInspectorDialog.show()
        self.webInspectorDialog.raise_()
        self.webInspectorDialog.activateWindow()


    def showCoverageLayer(self): #r = QgsRasterLayer('type=xyz&url=http://c.tile.openstreetmap.org/${z}/${x}/${y}.png', 'osm', 'wms')
        if self.showCoverage.isChecked():
            service_url = "https://mts2.google.com/mapslt?lyrs=svv&x={x}&y={y}&z={z}&w=256&h=256&hl=en&style=40,18"
            service_uri = "type=xyz&zmin=0&zmax=21&url="+service_url.replace("=", "%3D").replace("&", "%26")
            layer = QgsRasterLayer(service_uri, "Streetview coverage", "wms")
            self.coverageLayerId = layer.id()
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            toc_root = QgsProject.instance().layerTreeRoot()
            toc_root.insertLayer(0, layer)
        else:
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(self.coverageLayerId)
            except:
                pass

    def scanForCoverageLayer(self):
        #used for catching coverage layer if saved along with projectS
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.PluginLayer and layer.id()[:19] == "Streetview_coverage":
                self.showCoverage.blockSignals ( True )
                self.showCoverage.setChecked(True)
                self.showCoverage.blockSignals ( False )
                self.coverageLayerId = layer.id()

    def updateRotate(self):
        QgsMessageLog.logMessage(self.actualPOV,360-float(self.actualPOV['heading']), tag="go2streetview", level=QgsMessageLog.INFO)
        if self.checkFollow.isChecked():
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(self.coverageLayerId)
            except:
                pass
            self.setPosition()

    def mapRotationChanged(self,r):
        if r <> 0:
            try:
                QgsMapLayerRegistry.instance().removeMapLayer(self.coverageLayerId)
            except:
                pass

    def printAction(self):
        #export tmp imgs of qwebviews
        for imgFile,webview in {"tmpSV.png":self.view.SV,"tmpBE.png":self.view.BE}.iteritems():
            painter = QPainter()
            img = QImage(webview.size().width(), webview.size().height(), QImage.Format_ARGB32)
            painter.begin(img)
            webview.page().mainFrame().render(painter)
            painter.end()
            img.save(os.path.join(self.dirPath,"tmp",imgFile))
        # portion of code from: http://gis.stackexchange.com/questions/77848/programmatically-load-composer-from-template-and-generate-atlas-using-pyqgis

        # Load template
        myComposition = QgsComposition(self.iface.mapCanvas().mapSettings())
        myFile = os.path.join(os.path.dirname(__file__), 'res','go2SV_A4.qpt')
        myTemplateFile = file(myFile, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()
        myDocument = QDomDocument()
        myDocument.setContent(myTemplateContent)
        myComposition.loadFromTemplate(myDocument)

        #MAP
        mapFrame = myComposition.getComposerItemById("MAP")
        mapFrameAspectRatio = mapFrame.extent().width()/mapFrame.extent().height()
        newMapFrameExtent = QgsRectangle()
        actualPosition = self.transformToCurrentSRS(QgsPoint (float(self.actualPOV['lon']),float(self.actualPOV['lat'])))
        centerX = actualPosition.x()
        centerY = actualPosition.y()
        if float(self.actualPOV['heading']) > 360:
            head = float(self.actualPOV['heading'])-360
        else:
            head = float(self.actualPOV['heading'])
        newMapFrameExtent.set(centerX - self.iface.mapCanvas().extent().height()*mapFrameAspectRatio/2,centerY - self.iface.mapCanvas().extent().height()/2,centerX + self.iface.mapCanvas().extent().height()*mapFrameAspectRatio/2,centerY + self.iface.mapCanvas().extent().height()/2)
        mapFrame.setNewExtent(newMapFrameExtent)
        mapFrame.setRotation(self.canvas.rotation())
        mapFrame.updateItem()

        #CURSOR
        mapFrameCursor = myComposition.getComposerItemById("CAMERA")
        mapFrameCursor.setPictureFile(os.path.join(os.path.dirname(__file__),'res', 'camera.svg'))
        mapFrameCursor.setItemRotation(head+self.canvas.rotation(), adjustPosition = True)

        #NORTH
        mapFrameNorth = myComposition.getComposerItemById("NORTH")
        mapFrameNorth.setPictureFile(os.path.join(os.path.dirname(__file__),'res', 'NorthArrow_01.svg'))
        mapFrameNorth.setItemRotation(self.canvas.rotation(), adjustPosition = True)

        #STREETVIEW AND BING PICS
        if self.view.SV.isHidden():
            LargePic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpBE.png')
            SmallPic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpSV.png')
        else:
            LargePic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpSV.png')
            SmallPic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpBE.png')

        SVFrame = myComposition.getComposerItemById("LARGE")
        SVFrame.setPictureFile(LargePic)
        BEFrame = myComposition.getComposerItemById("SMALL")
        BEFrame.setPictureFile(SmallPic)

        #DESCRIPTION
        DescFrame = myComposition.getComposerItemById("DESC")
        info = self.snapshotOutput.getGeolocationInfo()
        #print "INFO", info
        DescFrame.setText("LAT: %s\nLON: %s\nHEAD: %s\nADDRESS:\n%s" % (info['lat'], info['lon'], head, info['address']))
        workDir = QgsProject.instance().readPath("./")
        fileName = QFileDialog().getSaveFileName(None,"Save pdf", workDir, "*.pdf");
        if fileName:
            if QFileInfo(fileName).suffix() != "pdf":
                fileName += ".pdf"
            myComposition.exportAsPDF(fileName)

        # Save image
        #myImagePath = os.path.join(os.path.dirname(__file__),'tmp', 'go2SV_A4.png')
        #myImage = myComposition.printPageAsRaster(0)
        #myImage.save(myImagePath)

    def aboutAction(self):
        self.licenceDlg.show()

    def infoLayerAction(self):
        self.infoBoxManager.show()

    def infoLayerDefinedAction(self):
        if self.infoBoxManager.isEnabled():
            actualPoint = QgsPoint(float(self.actualPOV['lon']),float(self.actualPOV['lat']))
            self.writeInfoBuffer(self.transformToCurrentSRS(actualPoint))
            time.sleep(1)
            js = "this.overlay.draw();"
            self.view.SV.page().mainFrame().evaluateJavaScript(js)
        else:
            js = "this.clearMarkers();"
            self.view.SV.page().mainFrame().evaluateJavaScript(js)
            self.view.BE.page().mainFrame().evaluateJavaScript(js)

    def switchViewAction(self):
        if self.view.SV.isVisible():
            self.switch2BE()
        else:
            self.switch2SV()

    def openInBrowserAction(self):
        if self.view.SV.isVisible():
            self.openInBrowserSV()
        else:
            self.openInBrowserBE()

    def takeSnapshopAction(self):
        self.takeSnapshotSV()

    def unload(self):
        try:
            QgsMapLayerRegistry.instance().removeMapLayer(self.coverageLayerId)
        except:
            pass
        # Hide License
        try:
            self.license.hide()
        except:
            pass
        # Remove the plugin menu item and icon and dock Widget
        try:
            self.iface.projectRead.disconnect(self.projectReadAction)
        except:
            pass
        try:
            self.canvas.rotationChanged.disconnect(self.mapRotationChanged)
        except:
            pass
        try:
            self.canvas.scaleChanged.disconnect(self.setPosition)
        except:
            pass
        try:
            self.controlShape.reset()
        except:
            pass
        try:
            self.controlPoints.reset()
        except:
            pass
        try:
            self.position.reset()
        except:
            pass
        self.iface.removePluginMenu("&go2streetview",self.StreetviewAction)
        self.iface.removeToolBarIcon(self.StreetviewAction)
        self.iface.removeDockWidget(self.apdockwidget)

    def catchJSevents(self,status):
        try:
            tmpPOV = json.JSONDecoder().decode(status)
        except:
            tmpPOV = None
        if tmpPOV:
            if tmpPOV["transport"] == "drag":
                self.refreshWidget(tmpPOV['lon'], tmpPOV['lat'])
            elif tmpPOV["transport"] == "view":
                self.httpConnecting = True
                if self.actualPOV["lat"] != tmpPOV["lat"] or self.actualPOV["lon"] != tmpPOV["lon"]:
                    self.actualPOV = tmpPOV
                    actualPoint = QgsPoint(float(self.actualPOV['lon']),float(self.actualPOV['lat']))
                    if self.infoBoxManager.isEnabled():
                        #self.view.SV.settings().clearMemoryCaches()
                        #self.view.BE.settings().clearMemoryCaches()
                        self.writeInfoBuffer(self.transformToCurrentSRS(actualPoint))
                else:
                    self.actualPOV = tmpPOV
                #print status
                self.setPosition()
            elif tmpPOV["transport"] == "mapCommand":
                #print tmpPOV
                feat = self.infoBoxManager.getInfolayer().getFeatures(QgsFeatureRequest(tmpPOV["fid"])).next()
                #print feat.id()
                if tmpPOV["type"] == "edit":
                    self.iface.openFeatureForm(self.infoBoxManager.getInfolayer(),feat,True)
                if tmpPOV["type"] == "select":
                    self.infoBoxManager.getInfolayer().select(feat.id())

    def setPosition(self,forcePosition = None):
        if self.apdockwidget.widget() == self.dumView or not self.apdockwidget.isVisible():
          return
        try:
            actualWGS84 = QgsPoint (float(self.actualPOV['lon']),float(self.actualPOV['lat']))
        except:
            return
        actualSRS = self.transformToCurrentSRS(actualWGS84)
        if self.checkFollow.isChecked():
            if float(self.actualPOV['heading'])>180:
                rotAngle = 360-float(self.actualPOV['heading'])
            else:
                rotAngle = -float(self.actualPOV['heading'])
            self.canvas.setRotation(rotAngle)
            self.canvas.setCenter(actualSRS)
            self.canvas.refresh()
        #print self.viewWidth,self.viewHeight
        self.position.reset()
        self.position=QgsRubberBand(self.iface.mapCanvas(),QGis.Point )
        self.position.setWidth( 4 )
        self.position.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position.setIconSize(4)
        self.position.setColor(Qt.blue)
        self.position.addPoint(actualSRS)
        CS = self.canvas.mapUnitsPerPixel()*25
        #print "zoom",self.actualPOV['zoom']
        #fov = (90/max(1,float(self.actualPOV['zoom'])))*math.pi/360
        zoom = float(self.actualPOV['zoom'])
        fov = (3.9018*pow(zoom,2) - 42.432*zoom + 123)/100
        A1x = actualSRS.x()-CS*math.cos(math.pi/2-fov)
        A2x = actualSRS.x()+CS*math.cos(math.pi/2-fov)
        A1y = actualSRS.y()+CS*math.sin(math.pi/2-fov)
        A2y = A1y
        #print A1x,A1y,actualSRS.x(),actualSRS.y()
        self.aperture.reset()
        self.aperture=QgsRubberBand(self.iface.mapCanvas(),QGis.Line )
        self.aperture.setWidth( 3 )
        self.aperture.setColor(Qt.blue)
        self.aperture.addPoint(QgsPoint(A1x,A1y))
        self.aperture.addPoint(actualSRS)
        self.aperture.addPoint(QgsPoint(A2x,A2y))
        tmpGeom = self.aperture.asGeometry()
        angle = float(self.actualPOV['heading'])*math.pi/-180
        self.aperture.setToGeometry(self.rotateTool.rotate(tmpGeom,actualSRS,angle),self.dumLayer)
        self.updateSVOptions()


        self.gswBrowserUrl ="https://maps.google.com/maps?q=&layer=c&cbll="+str(self.actualPOV['lat'])+","+str(self.actualPOV['lon'])+"&cbp=12,"+str(self.actualPOV['heading'])+",0,0,0&z=18"
        #Sync Google map
        js = "this.map.setCenter(new google.maps.LatLng(%s, %s));" % (str(self.actualPOV['lat']),str(self.actualPOV['lon']))
        self.view.BE.page().mainFrame().evaluateJavaScript(js)


    def checkLicenseAction(self):
        if self.licenceDlg.checkGoogle.isChecked() and self.licenceDlg.APIkey.text() != '':
            self.licenceDlg.hide()
            self.APIkey = self.licenceDlg.APIkey.text().strip()
            self.S.setValue("go2sv/license",self.version)
            self.S.setValue("go2sv/APIkey",self.APIkey)
            self.licenseAgree = True

    def closeDialog(self):
        self.position.reset()
        self.aperture.reset()

    def apdockChangeVisibility(self,vis):
        if not vis:
            self.position.reset()
            self.aperture.reset()
            try:
                self.StreetviewAction.setIcon(QIcon(":/plugins/go2streetview/res/icoStreetview_gray.png"))
                #self.StreetviewAction.setDisabled(True)
            except:
                pass

        else:
            self.StreetviewAction.setEnabled(True)
            self.StreetviewAction.setIcon(QIcon(":/plugins/go2streetview/res/icoStreetview.png"))

    def resizeStreetview(self):
        #self.resizing = True
        self.resizeWidget()
        try:
            self.view.SV.loadFinished.connect(self.endRefreshWidget)
            self.refreshWidget()
        except:
            pass

    def refreshWidget(self, new_lon, new_lat):
        if self.actualPOV['lat'] != 0.0:
            self.gswDialogUrl = os.path.join(self.dirPath,'res','g2sv.html?lat=' + str(new_lat) + "&long=" + str(new_lon) + "&width=" + str(self.viewWidth) + "&height=" + str(self.viewHeight) + "&heading=" + str(self.heading) + "&APIkey=" + self.APIkey)
            self.view.SV.load(QUrl('file:///' + QDir.fromNativeSeparators(self.gswDialogUrl)))

    def endRefreshWidget(self):
        self.view.SV.loadFinished.disconnect()
        self.refreshWidget(self.pointWgs84.x(), self.pointWgs84.y())

    def clickOn(self):
        self.explore()

    def resizeWidget(self):
        self.viewHeight=self.view.size().height()
        self.viewWidth=self.view.size().width()
        self.view.SV.resize(self.viewWidth,self.viewHeight)
        self.view.BE.resize(self.viewWidth,self.viewHeight)
        self.view.buttonBar.move(self.viewWidth-252,0)

    def switch2BE(self):
        # Procedure to operate switch to bing dialog set
        self.view.BE.show()
        self.view.SV.hide()
        self.view.btnSwitchView.setIcon(QIcon(":/plugins/go2streetview/res/icoStreetview.png"))
        #self.view.btnPrint.setDisabled(True)
        self.takeSnapshopItem.setDisabled(True)
        self.view.setWindowTitle("Google maps oblique")

    def switch2SV(self):
        # Procedure to operate switch to streetview dialog set
        self.view.BE.hide()
        self.view.SV.show()
        self.view.btnSwitchView.setIcon(QIcon(":/plugins/go2streetview/res/icoGMaps.png"))
        #self.view.btnPrint.setDisabled(False)
        self.takeSnapshopItem.setDisabled(False)
        self.view.setWindowTitle("Google Street View")

    def openInBrowserBE(self):
        # open an external browser with the google maps url for location/heading
        p = self.snapshotOutput.setCurrentPOV()
        webbrowser.open_new("https://www.google.com/maps/@%s,%s,150m/data=!3m1!1e3" % (str(p['lat']), str(p['lon'])))

    def openExternalUrl(self,url):
        QgsMessageLog.logMessage(url.toString(), tag="go2streetview", level=QgsMessageLog.INFO)
        webbrowser.open_new(url.toString())

    def openInBrowserSV(self):
        # open an external browser with the streetview url for current location/heading
        p = self.snapshotOutput.setCurrentPOV()
        pitch = str(-1*int(p['pitch']))
        webbrowser.open_new_tab("https://maps.google.com/maps?q=&layer=c&cbll="+p['lat']+","+p['lon']+"&cbp=12,"+p['heading']+",0,0,"+str(-1*int(p['pitch']))+"&z=18")

    def openInBrowserOnCTRLClick(self):
        webbrowser.open("https://maps.google.com/maps?q=&layer=c&cbll="+str(self.pointWgs84.y())+","+str(self.pointWgs84.x())+"&cbp=12,"+str(self.heading)+",0,0,0&z=18", new=0, autoraise=True)

    def takeSnapshotSV(self,):
        self.snapshotOutput.saveSnapShot()

    def transformToWGS84(self, pPoint):
        # transformation from the current SRS to WGS84
        crcMappaCorrente = self.iface.mapCanvas().mapSettings().destinationCrs() # get current crs
        crsSrc = crcMappaCorrente
        crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = QgsCoordinateTransform(crsSrc, crsDest)
        return xform.transform(pPoint) # forward transformation: src -> dest

    def transformToCurrentSRS(self, pPoint):
        # transformation from the current SRS to WGS84
        crcMappaCorrente = self.iface.mapCanvas().mapSettings().destinationCrs() # get current crs
        crsDest = crcMappaCorrente
        crsSrc = QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = QgsCoordinateTransform(crsSrc, crsDest)
        return xform.transform(pPoint) # forward transformation: src -> dest

    def canvasPressEvent(self, event):
        # Press event handler inherited from QgsMapTool used to store the given location in WGS84 long/lat
        self.pressed=True
        self.pressx = event.pos().x()
        self.pressy = event.pos().y()
        self.movex = event.pos().x()
        self.movey = event.pos().y()
        self.highlight=QgsRubberBand(self.iface.mapCanvas(),QGis.Line )
        self.highlight.setColor(Qt.yellow)
        self.highlight.setWidth(5)
        #print "x:",self.pressx," y:",self.pressy
        self.PressedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(self.pressx, self.pressy)
        #print self.PressedPoint.x(),self.PressedPoint.y()
        self.pointWgs84 = self.transformToWGS84(self.PressedPoint)
        # start infobox
        self.infoBoxManager.restoreIni()

    def canvasMoveEvent(self, event):
        # Moved event handler inherited from QgsMapTool needed to highlight the direction that is giving by the user
        if self.pressed:
            #print "canvasMoveEvent"
            x = event.pos().x()
            y = event.pos().y()
            movedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.highlight.reset()
            self.highlight.addPoint(self.PressedPoint)
            self.highlight.addPoint(movedPoint)


    def canvasReleaseEvent(self, event):
        # Release event handler inherited from QgsMapTool needed to calculate heading
        event.modifiers()
        if (event.modifiers() & Qt.ControlModifier):
            CTRLPressed = True
        else:
            CTRLPressed = None
        self.pressed=None
        self.highlight.reset()
        if not self.licenseAgree:
            self.licenceDlg.checkGoogle.stateChanged.connect(self.checkLicenseAction)
            self.licenceDlg.setWindowFlags(self.licenceDlg.windowFlags() | Qt.WindowStaysOnTopHint)
            self.licenceDlg.show()
            self.licenceDlg.raise_()
            self.licenceDlg.activateWindow()
            return
        self.releasedx = event.pos().x()
        self.releasedy = event.pos().y()
        if (self.releasedx==self.pressx)&(self.releasedy==self.pressy):
            self.heading=0
            result=0
        else:
            result = math.atan2((self.releasedx - self.pressx),(self.releasedy - self.pressy))
            result = math.degrees(result)+self.canvas.rotation()
            if result > 0:
                self.heading =  180 - result
            else:
                self.heading = 360 - (180 + result)
        if CTRLPressed:
            self.openInBrowserOnCTRLClick()
        else:
            self.openSVDialog()

    def openSVDialog(self):
        # procedure for compiling streetview and gmaps url with the given location and heading
        self.heading = math.trunc(self.heading)
        self.view.setWindowTitle("Google Street View")
        self.apdockwidget.setWidget(self.view)
        self.view.show()
        self.apdockwidget.raise_()
        self.view.activateWindow()
        self.view.BE.hide()
        self.view.SV.hide()
        self.viewHeight=self.view.size().height()
        self.viewWidth=self.view.size().width()

        self.gswDialogUrl = os.path.join(self.dirPath,'res','g2sv.html?lat=' + str(
            self.pointWgs84.y()) + "&long=" + str(self.pointWgs84.x()) + "&width=" + str(
            self.viewWidth) + "&height=" + str(self.viewHeight) + "&heading=" + str(
            self.heading) + "&APIkey=" + self.APIkey)

        self.headingGM = math.trunc(round (self.heading / 90) * 90)
        self.bbeUrl = os.path.join(self.dirPath, "res","g2gm.html?lat=" + str(self.pointWgs84.y()) + "&long=" + str(
            self.pointWgs84.x()) + "&width=" + str(self.viewWidth) + "&height=" + str(
            self.viewHeight) + "&zoom=19&heading=" + str(self.headingGM) + "&APIkey=" + self.APIkey)

        gswTitle = "Google Street View"
        QgsMessageLog.logMessage(QUrl(self.gswDialogUrl).toString(), tag="go2streetview", level=QgsMessageLog.INFO)
        #print (QDir.fromNativeSeparators(self.gswDialogUrl))
        #print(QDir.fromNativeSeparators(self.bbeUrl))
        QgsMessageLog.logMessage(self.bbeUrl, tag="go2streetview", level=QgsMessageLog.INFO)
        self.view.SV.load(QUrl('file:///'+QDir.fromNativeSeparators(self.gswDialogUrl)))
        self.view.BE.load(QUrl('file:///'+QDir.fromNativeSeparators(self.bbeUrl)))
        self.switch2SV()

    def StreetviewRun(self):
        # called by click on toolbar icon
        if self.apdockwidget.isVisible():
            self.apdockwidget.hide()
        else:
            self.apdockwidget.show()
            self.explore()

    def explore(self):
        self.view.resized.connect(self.resizeStreetview)
        gsvMessage="Click on map and drag the cursor to the desired direction to display Google Street View"
        self.iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.dumLayer.setCrs(self.iface.mapCanvas().mapSettings().destinationCrs())
        self.canvas.setMapTool(self)

    def writeInfoBuffer(self,p):
        cyclePause = 0
        while self.httpConnecting:
            time.sleep(1)
            cyclePause += 1
            #print "ciclePause",cyclePause
            if cyclePause > 1:
                break
        try:
            self.controlShape.reset()
            self.controlPoints.reset()
        except:
            pass
        self.controlShape = QgsRubberBand(self.iface.mapCanvas(),QGis.Line )
        self.controlShape.setWidth( 1 )
        self.controlPoints = QgsRubberBand(self.iface.mapCanvas(),QGis.Point )
        self.controlPoints.setWidth( 8 )
        self.controlPoints.setColor( Qt.red )
        if self.infoBoxManager.getInfolayer().geometryType() == QGis.Point:
            self.pointBuffer(p)
        elif self.infoBoxManager.getInfolayer().geometryType() == QGis.Line:
            self.lineBuffer(p)
        elif self.infoBoxManager.getInfolayer().geometryType() == QGis.Polygon :
            self.pointBuffer(p)
            self.lineBuffer(p,polygons = True)

    def pointBuffer(self,p):
        dBuffer = self.infoBoxManager.getDistanceBuffer()
        infoLayer = self.infoBoxManager.getInfolayer()
        toInfoLayerProjection = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),infoLayer.crs())
        toWGS84 = QgsCoordinateTransform(infoLayer.crs(),QgsCoordinateReferenceSystem(4326))
        # create layer and replicate fields
        bufferLayer = QgsVectorLayer("Point?crs="+infoLayer.crs().toWkt(), "temporary_points", "memory")
        #bufferLayer.setCrs(infoLayer.crs()) #This generates alert message
        bufferLayer.startEditing()
        bufferLayer.addAttribute(QgsField("id",QVariant.String))
        bufferLayer.addAttribute(QgsField("html",QVariant.String))
        bufferLayer.addAttribute(QgsField("icon",QVariant.String))
        bufferLayer.addAttribute(QgsField("fid",QVariant.Int))
        fetched = 0
        self.featsId = self.infoBoxManager.getContextFeatures(toInfoLayerProjection.transform(p))
        #print featsId
        #print toInfoLayerProjection.transform(p).x(),toInfoLayerProjection.transform(p).y()
        for featId in self.featsId:
            feat = infoLayer.getFeatures(QgsFeatureRequest(featId)).next()
            #print fetched
            if fetched < 100:
                if infoLayer.geometryType() == QGis.Polygon:
                    fGeom = feat.geometry().pointOnSurface()
                elif infoLayer.geometryType() == QGis.Point:
                    fGeom = feat.geometry()
                if fGeom.isMultipart():
                    multipoint = fGeom.asMultiPoint()
                    point = multipoint[0]
                else:
                    point = fGeom.asPoint()
                fetched += 1
                newGeom = QgsGeometry.fromPoint(point)
                newFeat = QgsFeature()
                newFeat.setGeometry(newGeom)
                newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat),self.infoBoxManager.getFeatId(feat)])
                bufferLayer.addFeature(newFeat)
            else:
                QgsMessageLog.logMessage("fetched too much features..... 100 max", tag="go2streetview", level=QgsMessageLog.WARNING)
                break
        bufferLayer.commitChanges()
        QgsMessageLog.logMessage("markers context rebuilt", tag="go2streetview", level=QgsMessageLog.INFO)
        #StreetView markers
        tmpfile = os.path.join(self.dirPath,"tmp","tmp_markers.geojson")
        QgsVectorFileWriter.writeAsVectorFormat (bufferLayer, tmpfile,"UTF8",toWGS84,"GeoJSON")
        with open(tmpfile) as f:
            geojson = f.read().replace('\n','')
        #js = geojson.replace("'",'')
        #js = js.replace("\n",'\n')
        js = """this.markersJson = %s""" % json.dumps(geojson)
        #print js
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        js = """this.readJson() """
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        QgsMessageLog.logMessage("webview markers refreshed", tag="go2streetview", level=QgsMessageLog.INFO)



    def lineBuffer(self,p,polygons = None):
        dBuffer = self.infoBoxManager.getDistanceBuffer()
        infoLayer = self.infoBoxManager.getInfolayer()
        toInfoLayerProjection = QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),infoLayer.crs())
        toWGS84 = QgsCoordinateTransform(infoLayer.crs(),QgsCoordinateReferenceSystem(4326))
        # create layer and replicate fields
        bufferLayer = QgsVectorLayer("LineString?crs="+infoLayer.crs().toWkt(), "temporary_lines", "memory")
        bufferLayer.startEditing()
        bufferLayer.addAttribute(QgsField("id",QVariant.String))
        bufferLayer.addAttribute(QgsField("html",QVariant.String))
        bufferLayer.addAttribute(QgsField("icon",QVariant.String))
        bufferLayer.addAttribute(QgsField("fid",QVariant.Int))
        fetched = 0
        viewBuffer = QgsGeometry.fromPoint(toInfoLayerProjection.transform(p)).buffer(dBuffer,10)
        cutBuffer = QgsGeometry.fromPoint(toInfoLayerProjection.transform(p)).buffer(dBuffer*2,10)
        self.controlShape.setToGeometry(viewBuffer,infoLayer)
        if not polygons:
            self.featsId = self.infoBoxManager.getContextFeatures(toInfoLayerProjection.transform(p))
        for featId in self.featsId:
            feat = infoLayer.getFeatures(QgsFeatureRequest(featId)).next()
            if fetched < 500:
                if infoLayer.geometryType() == QGis.Polygon:
                    fGeom = feat.geometry().convertToType(QGis.Line)
                elif infoLayer.geometryType() == QGis.Line:
                    fGeom = feat.geometry()
                if fGeom:
                    #break on closest point on segment to pov to improve visibility
                    closestResult = fGeom.closestSegmentWithContext(toInfoLayerProjection.transform(p));
                    fGeom.insertVertex(closestResult[1][0],closestResult[1][1],closestResult[2])
                    cGeom = fGeom.intersection(cutBuffer)
                    if cGeom.isMultipart():
                        multigeom = cGeom.asMultiPolyline()
                        for geom in multigeom:
                            newGeom = QgsGeometry.fromPolyline(geom)
                            newFeat = QgsFeature()
                            newFeat.setGeometry(newGeom)
                            newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat),self.infoBoxManager.getFeatId(feat)])
                            bufferLayer.addFeature(newFeat)

                    else:
                        geom = cGeom.asPolyline()
                        newGeom = QgsGeometry.fromPolyline(geom)
                        newFeat = QgsFeature()
                        newFeat.setGeometry(newGeom)
                        newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat),self.infoBoxManager.getFeatId(feat)])
                        bufferLayer.addFeature(newFeat)
                    fetched = fetched + len(newGeom.asPolyline())
                else:
                    QgsMessageLog.logMessage("Null geometry!", tag="go2streetview", level=QgsMessageLog.WARNING)
            else:
                QgsMessageLog.logMessage("fetched too much features..... max 500", tag="go2streetview", level=QgsMessageLog.WARNING)
                break
        bufferLayer.commitChanges()
        QgsMessageLog.logMessage("line context rebuilt: %s features" % bufferLayer.featureCount(), tag="go2streetview", level=QgsMessageLog.INFO)
        #StreetView lines
        tmpfile = os.path.join(self.dirPath, "tmp", "tmp_lines.geojson")
        QgsVectorFileWriter.writeAsVectorFormat(bufferLayer, tmpfile,"UTF8", toWGS84, "GeoJSON")
        with open(tmpfile) as f:
            geojson = f.read().replace('\n', '')
        js = """this.linesJson = %s""" % json.dumps(geojson)
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        js = """this.readLinesJson() """
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        QgsMessageLog.logMessage("webview lines refreshed", tag="go2streetview", level=QgsMessageLog.INFO)

    def noSVConnectionsPending(self,reply):
        self.httpConnecting = None
        if reply.error() == QNetworkReply.NoError:
            pass
        elif reply.error() == QNetworkReply.ContentNotFoundError:
            failedUrl = reply.request.url()
            httpStatus = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toInt()
            httpStatusMessage = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute).toByteArray()
            QgsMessageLog.logMessage("STREETVIEW FAILED REQUEST: {} {} {}".format(failedUrl,httpStatus,httpStatusMessage), tag="go2streetview", level=QgsMessageLog.CRITICAL)
        else:
            QgsMessageLog.logMessage("STREETVIEW OTHER CONNECTION ERROR: {}".format(reply.error()), tag="go2streetview", level=QgsMessageLog.CRITICAL)

    def noBingConnectionsPending(self,reply):
        if reply.error() == QNetworkReply.NoError:
            pass
        elif reply.error() == QNetworkReply.ContentNotFoundError:
            failedUrl = reply.request.url()
            httpStatus = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute).toInt()
            httpStatusMessage = reply.attribute(QNetworkRequest.HttpReasonPhraseAttribute).toByteArray()
            QgsMessageLog.logMessage("BING FAILED REQUEST: {} {} {}".format(failedUrl,httpStatus,httpStatusMessage), tag="go2streetview", level=QgsMessageLog.CRITICAL)
        else:
            QgsMessageLog.logMessage("BING OTHER CONNECTION ERROR: {}".format(reply.error()), tag="go2streetview", level=QgsMessageLog.CRITICAL)

    def projectReadAction(self):
        #remove current sketches
        self.infoBoxManager.restoreIni()
        self.scanForCoverageLayer()

    def loadFinishedAction(self,ok):
        if ok:
            QgsMessageLog.logMessage("Finished loading", tag="go2streetview", level=QgsMessageLog.INFO)
            pass
        else:
            QgsMessageLog.logMessage("Failed loading", tag="go2streetview", level=QgsMessageLog.CRITICAL)
            pass

    def setupInspector(self):
        self.page = self.view.SV.page()
        page.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.webInspector = QWebInspector(self)
        self.webInspector.setPage(page)
