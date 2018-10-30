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

from PyQt5 import Qt, QtCore, QtWidgets, QtGui, QtWebKit, QtWebKitWidgets, QtXml, QtNetwork, uic
from qgis import core, utils, gui
from qgis.utils import iface, qgsfunction, plugins
from string import digits
from .go2streetviewDialog import go2streetviewDialog, dumWidget,snapshotLicenseDialog, infobox
from .snapshot import snapShot
from .transformgeom import transformGeometry
#from py_tiled_layer.tilelayer import TileLayer, TileLayerType
#from py_tiled_layer.tiles import TileServiceInfo

import resources_rc

import webbrowser
import tempfile
import os
import math
import time
import json
import configparser
import sip
import pathlib
import datetime


@qgsfunction(args=0, group='go2streetview', usesgeometry=True)
def get_streetview_pov(value1, feature, parent):
    sv = plugins['go2streetview']
    toP = feature.geometry().centroid().asPoint()
    toP_wgs84 = sv.transformToWGS84(toP)
    #try:
    fromP_wgs84 = sv.getNearestSVLocation(toP_wgs84.x(),toP_wgs84.y())
    fromP = sv.transformToCurrentSRS(fromP_wgs84)
    head = heading(fromP,toP)
    location = 'LINESTRING(%f %f %f,%f %f %f)' % (toP.x(),toP.y(),head,fromP.x(),fromP.y(),head)
    return location
    #except Exception as e:
        #return "no imagery for location: "+ str(e)

@qgsfunction(args='auto', group='go2streetview', usesgeometry=True)
def get_streetview_url(value1, feature, parent):
    sv = plugins['go2streetview']
    toP = sv.transformToWGS84(feature.geometry().centroid().asPoint())
    h = 640.0
    w = 640.0
    if value1 > 1:
        h = w / value1
    elif value1 < 1:
        w = h * value1
    size = str(int(w)) + 'x' + str(int(h))

    #try:
    fromP = sv.getNearestSVLocation(toP.x(),toP.y())
    location = '%f,%f' % (fromP.y(),fromP.x())
    head = heading(fromP,toP)
    key = sv.APIkey
    url = 'https://maps.googleapis.com/maps/api/streetview'
    url += "?location=%s&size=%s&key=%s&heading=%f" % (location,size,key,head)
    return url
    #except Exception as e:
        #return "no imagery for location: " + str(e)

def heading(fromP, toP):
    result = math.atan2((toP.x() - fromP.x()),(toP.y() - fromP.y()))
    result = math.degrees(result)
    return (result + 360) % 360


class go2streetview(gui.QgsMapTool):

    def __init__(self, iface):

       # Save reference to the QGIS interface
        self.iface = iface
        # reference to the canvas
        self.canvas = self.iface.mapCanvas()
        pluginMetadata = configparser.ConfigParser()
        pluginMetadata.read(os.path.join(os.path.dirname(__file__), 'metadata.txt'))
        self.version = pluginMetadata.get('general', 'version')
        gui.QgsMapTool.__init__(self, self.canvas)
        self.S = QtCore.QSettings()
        terms = self.S.value("go2sv/license", defaultValue =  "undef")
        if terms == self.version:
            self.licenseAgree = True
        else:
            self.licenseAgree = None

    def initGui(self):
        # Create actions that will start plugin configuration
        self.StreetviewAction = QtWidgets.QAction(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'res', 'icoStreetview.png')), \
            "Click to open Google Street View", self.iface.mainWindow())
        #self.StreetviewAction = QtWidgets.QAction(QtGui.QIcon(":/plugins/go2streetview/res/icoStreetview.png"), \
        #    "Click to open Google Street View", self.iface.mainWindow())
        self.StreetviewAction.triggered.connect(self.StreetviewRun)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.StreetviewAction)
        self.iface.addPluginToWebMenu("&go2streetview", self.StreetviewAction)
        self.dirPath = os.path.dirname( os.path.abspath( __file__ ) )
        self.actualPOV = {}
        self.view = go2streetviewDialog()
        self.dumView = dumWidget()
        self.dumView.enter.connect(self.clickOn)
        self.dumView.iconRif.setPixmap(QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'res', 'icoStreetview.png')))
        #self.dumView.iconRif.setPixmap(QtGui.QPixmap(":/plugins/go2streetview/res/icoStreetview.png"))
        self.apdockwidget=QtWidgets.QDockWidget("go2streetview" , self.iface.mainWindow() )
        self.apdockwidget.setObjectName("go2streetview")
        self.apdockwidget.setWidget(self.dumView)
        self.iface.addDockWidget( QtCore.Qt.LeftDockWidgetArea, self.apdockwidget)
        self.apdockwidget.update()

        self.viewHeight=self.apdockwidget.size().height()
        self.viewWidth=self.apdockwidget.size().width()
        self.snapshotOutput = snapShot(self)
        self.view.SV.settings().globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True);
        self.view.SV.settings().globalSettings().setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True);
        self.view.SV.page().networkAccessManager().finished.connect(self.noSVConnectionsPending)
        self.view.SV.page().statusBarMessage.connect(self.catchJSevents)
        self.view.BE.page().statusBarMessage.connect(self.catchJSevents)
        self.view.btnSwitchView.setIcon(QtGui.QIcon(os.path.join(self.dirPath,"res","icoGMaps.png")))

        self.view.enter.connect(self.clickOn)
        self.view.closed.connect(self.closeDialog)
        self.setButtonBarSignals()
        self.infoBoxManager = infobox(self)
        self.infoBoxManager.defined.connect(self.infoLayerDefinedAction)
        self.apdockwidget.visibilityChanged.connect(self.apdockChangeVisibility)
        self.iface.projectRead.connect(self.projectReadAction)
        self.pressed=None
        self.CTRLPressed=None

        self.controlShape = gui.QgsRubberBand(self.iface.mapCanvas(),core.QgsWkbTypes.LineGeometry )
        self.controlShape.setWidth( 1 )
        self.position=gui.QgsRubberBand(self.iface.mapCanvas(),core.QgsWkbTypes.PointGeometry )
        self.position.setWidth( 5 )
        self.position.setIcon(gui.QgsRubberBand.ICON_CIRCLE)
        self.position.setIconSize(6)
        self.position.setColor(QtCore.Qt.red)
        self.aperture=gui.QgsRubberBand(self.iface.mapCanvas(),core.QgsWkbTypes.LineGeometry )
        self.rotateTool = transformGeometry()
        self.canvas.rotationChanged.connect(self.mapRotationChanged)
        self.canvas.scaleChanged.connect(self.setPosition)
        self.dumLayer = core.QgsVectorLayer("Point?crs=EPSG:4326", "temporary_points", "memory")
        self.actualPOV = {"lat":0.0,"lon":0.0,"heading":0.0,"zoom":1}
        self.pointWgs84 = None
        self.mkDirs()
        self.licenceDlg = snapshotLicenseDialog()
        self.httpConnecting = None

        self.S = QtCore.QSettings()
        terms = self.S.value("go2sv/license", defaultValue =  "undef")
        self.APIkey = self.S.value("go2sv/APIkey", defaultValue =  "")
        self.licenceDlg.APIkey.setText(self.APIkey)
        if terms == self.version:
            self.licenseAgree = True
            self.licenceDlg.checkGoogle.setCheckState(QtCore.Qt.Checked)
            self.licenceDlg.checkGoogle.setEnabled(False)
        else:
            self.licenseAgree = None
        self.licenceDlg.OKbutton.clicked.connect(self.checkLicenseAction)
        self.licenceDlg.textBrowser.anchorClicked.connect(self.openExternalUrl)

        # Register plugin layer type
        #self.tileLayerType = TileLayerType(self)
        #QgsPluginLayerRegistry.instance().addPluginLayerType(self.tileLayerType)

        self.view.SV.page().setNetworkAccessManager(core.QgsNetworkAccessManager.instance())
        self.view.BE.page().setNetworkAccessManager(core.QgsNetworkAccessManager.instance())

        #setting a webinspector dialog
        self.webInspectorDialog = QtWidgets.QDialog()
        self.webInspector = QtWebKitWidgets.QWebInspector(self.webInspectorDialog)
        self.webInspector.setPage(self.view.BE.page())
        self.webInspectorDialog.setLayout(QtWidgets.QVBoxLayout())
        self.webInspectorDialog.setWindowTitle("Web Inspector")
        self.webInspectorDialog.resize(960, 480)
        self.webInspectorDialog.layout().addWidget(self.webInspector)
        self.webInspectorDialog.setModal(False)
        self.webInspectorDialog.hide()
        core.QgsExpression.registerFunction(get_streetview_url)
        core.QgsExpression.registerFunction(get_streetview_pov)


    def mkDirs(self):
        newDir = QtCore.QDir()
        newDir.mkpath(os.path.join(self.dirPath,"tmp"))
        newDir.mkpath(os.path.join(self.dirPath,"snapshots"))

    def setButtonBarSignals(self):
        #Switch button
        self.view.btnSwitchView.clicked.connect(self.switchViewAction)
        #contextMenu
        contextMenu = QtWidgets.QMenu()
        self.openInBrowserItem = contextMenu.addAction(QtGui.QIcon(os.path.join(self.dirPath,"res","browser.png")),"Open in external browser")
        self.openInBrowserItem.triggered.connect(self.openInBrowserAction)
        self.takeSnapshopItem = contextMenu.addAction(QtGui.QIcon(os.path.join(self.dirPath,"res","images.png")),"Take a panorama snaphot")
        self.takeSnapshopItem.triggered.connect(self.takeSnapshopAction)
        self.infoLayerItem = contextMenu.addAction(QtGui.QIcon(os.path.join(self.dirPath,"res","markers.png")),"Add info layer")
        self.infoLayerItem.triggered.connect(self.infoLayerAction)
        self.printItem = contextMenu.addAction(QtGui.QIcon(os.path.join(self.dirPath,"res","print.png")),"Print keymap leaflet")
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
        self.view.btnMenu.setPopupMode(QtWidgets.QToolButton.InstantPopup)

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
        if self.view.SV.isVisible():
            self.webInspector.setPage(self.view.SV.page())
        else:
            self.webInspector.setPage(self.view.BE.page())
        self.webInspectorDialog.show()
        self.webInspectorDialog.raise_()
        self.webInspectorDialog.activateWindow()


    def showCoverageLayer(self): #r = QgsRasterLayer('type=xyz&url=http://c.tile.openstreetmap.org/${z}/${x}/${y}.png', 'osm', 'wms')
        if self.showCoverage.isChecked():
            service_url = "https://mts2.google.com/mapslt?lyrs=svv&x={x}&y={y}&z={z}&w=256&h=256&hl=en&style=40,18"
            service_uri = "type=xyz&zmin=0&zmax=21&url="+service_url.replace("=", "%3D").replace("&", "%26")
            layer = core.QgsRasterLayer(service_uri, "Streetview coverage", "wms")
            self.coverageLayerId = layer.id()
            core.QgsProject.instance().addMapLayer(layer, False)
            toc_root = core.QgsProject.instance().layerTreeRoot()
            toc_root.insertLayer(0, layer)
        else:
            try:
                core.QgsProject.instance().removeMapLayer(self.coverageLayerId)
            except:
                pass

    def scanForCoverageLayer(self):
        return
        #used for catching coverage layer if saved along with projectS
        for layer_id,layer in core.QgsProject.instance().mapLayers().items():
            if layer.type() == core.QgsMapLayer.PluginLayer and layer.id()[:19] == "Streetview_coverage":
                self.showCoverage.blockSignals ( True )
                self.showCoverage.setChecked(True)
                self.showCoverage.blockSignals ( False )
                self.coverageLayerId = layer.id()

    def updateRotate(self):
        if self.checkFollow.isChecked():
            try:
                pass
                #core.QgsProject.instance().removeMapLayer(self.coverageLayerId)
            except:
                pass
            self.setPosition()

    def mapRotationChanged(self,r):
        #unused landing method for rotationChanged signal.
        return

    def getNearestSVLocation(self,lon,lat):
        js = "this.getNearestSVLocation(%f,%f)" %(lon,lat)
        if not self.pointWgs84:
            self.pointWgs84 = core.QgsPointXY(lon,lat)
            self.heading = 0
            self.StreetviewRun()
            self.openSVDialog()
            time.sleep(1)
            self.StreetviewRun()
            delay = 10
        else:
            delay = 4

        self.SVLocationResponse = None
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        start = datetime.datetime.now()
        timeout = False
        while not (self.SVLocationResponse or timeout):
            time.sleep(0.2)
            tdiff = datetime.datetime.now()-start
            core.QgsMessageLog.logMessage("getNearestSVLocation %f" % tdiff, tag="go2streetview", level=core.Qgis.Info)
            print ("getNearestSVLocation", self.SVLocationResponse, tdiff, timeout)
            if tdiff.seconds > delay:
                timeout = True
        return self.SVLocationResponse

    def printAction(self):
        #export tmp imgs of qwebviews
        for imgFile,webview in {"tmpSV.png":self.view.SV,"tmpBE.png":self.view.BE}.items():
            painter = QtGui.QPainter()
            img = QtGui.QImage(webview.size().width(), webview.size().height(), QtGui.QImage.Format_ARGB32)
            painter.begin(img)
            webview.page().mainFrame().render(painter)
            painter.end()
            img.save(os.path.join(self.dirPath,"tmp",imgFile))
        # portion of code from: http://gis.stackexchange.com/questions/77848/programmatically-load-composer-from-template-and-generate-atlas-using-pyqgis

        # Load template
        myLayout = core.QgsLayout(core.QgsProject.instance())
        myFile = os.path.join(os.path.dirname(__file__), 'res','go2SV_A4.qpt')
        myTemplateFile = open(myFile, 'rt')
        myTemplateContent = myTemplateFile.read()
        myTemplateFile.close()
        myDocument = QtXml.QDomDocument()
        myDocument.setContent(myTemplateContent)
        myLayout.loadFromTemplate(myDocument,core.QgsReadWriteContext())

        #MAP
        mapFrame = sip.cast(myLayout.itemById('MAP'),core.QgsLayoutItemMap)
        mapFrameAspectRatio = mapFrame.extent().width()/mapFrame.extent().height()
        newMapFrameExtent = core.QgsRectangle()
        actualPosition = self.transformToCurrentSRS(core.QgsPointXY (float(self.actualPOV['lon']),float(self.actualPOV['lat'])))
        centerX = actualPosition.x()
        centerY = actualPosition.y()
        if float(self.actualPOV['heading']) > 360:
            head = float(self.actualPOV['heading'])-360
        else:
            head = float(self.actualPOV['heading'])
        newMapFrameExtent.set(centerX - self.iface.mapCanvas().extent().height()*mapFrameAspectRatio/2,centerY - self.iface.mapCanvas().extent().height()/2,centerX + self.iface.mapCanvas().extent().height()*mapFrameAspectRatio/2,centerY + self.iface.mapCanvas().extent().height()/2)
        mapFrame.setExtent(newMapFrameExtent)
        mapFrame.setMapRotation(self.canvas.rotation())
        mapFrame.redraw()

        #CURSOR
        mapFrameCursor = sip.cast(myLayout.itemById('CAMERA'),core.QgsLayoutItemPicture)
        mapFrameCursor.setPicturePath(os.path.join(os.path.dirname(__file__),'res', 'camera.svg'))
        mapFrameCursor.setItemRotation(head+self.canvas.rotation(), adjustPosition=True)

        #NORTH
        mapFrameNorth = sip.cast(myLayout.itemById('NORTH'),core.QgsLayoutItemPicture)
        mapFrameNorth.setPicturePath(os.path.join(os.path.dirname(__file__),'res', 'NorthArrow_01.svg'))
        mapFrameNorth.setPictureRotation(self.canvas.rotation())

        #STREETVIEW AND GM PICS
        if self.view.SV.isHidden():
            LargePic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpBE.png')
            SmallPic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpSV.png')
        else:
            LargePic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpSV.png')
            SmallPic = os.path.join(os.path.dirname(__file__),'tmp', 'tmpBE.png')

        SVFrame = sip.cast(myLayout.itemById('LARGE'),core.QgsLayoutItemPicture)
        SVFrame.setPicturePath(LargePic)
        BEFrame = sip.cast(myLayout.itemById('SMALL'),core.QgsLayoutItemPicture)
        BEFrame.setPicturePath(SmallPic)

        #DESCRIPTION
        DescFrame = sip.cast(myLayout.itemById('DESC'),core.QgsLayoutItemLabel)
        info = self.snapshotOutput.getGeolocationInfo()
        DescFrame.setText("LAT: %s\nLON: %s\nHEAD: %s\nADDRESS:\n%s" % (info['lat'], info['lon'], head, info['address']))
        workDir = core.QgsProject.instance().readPath("./")
        fileName, filter = QtWidgets.QFileDialog().getSaveFileName(None,"Save pdf", workDir, "*.pdf");
        if fileName:
            if QtCore.QFileInfo(fileName).suffix() != "pdf":
                fileName += ".pdf"
            exporter = core.QgsLayoutExporter(myLayout)
            exporter.exportToPdf(fileName,core.QgsLayoutExporter.PdfExportSettings())


    def aboutAction(self):
        self.licenceDlg.show()

    def infoLayerAction(self):
        self.infoBoxManager.show()
        self.infoBoxManager.raise_()

    def infoLayerDefinedAction(self):
        if self.infoBoxManager.isEnabled():
            actualPoint = core.QgsPointXY(float(self.actualPOV['lon']),float(self.actualPOV['lat']))
            self.writeInfoBuffer(self.transformToCurrentSRS(actualPoint))
            time.sleep(1)
            js = "this.overlay.draw()"
            self.view.SV.page().mainFrame().evaluateJavaScript(js)
            #self.view.BE.page().mainFrame().evaluateJavaScript(js)
        else:
            js = "this.clearMarkers();this.clearLines();"
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
        self.disableControlShape()
        try:
            core.QgsProject.instance().removeMapLayer(self.coverageLayerId)
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
            self.position.reset()
        except:
            pass
        self.iface.removePluginMenu("&go2streetview",self.StreetviewAction)
        self.iface.removeToolBarIcon(self.StreetviewAction)
        self.iface.removeDockWidget(self.apdockwidget)

        core.QgsExpression.unregisterFunction('get_streetview_pov')
        core.QgsExpression.unregisterFunction('get_streetview_url')

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
                    actualPoint = core.QgsPointXY(float(self.actualPOV['lon']),float(self.actualPOV['lat']))
                    if self.infoBoxManager.isEnabled():
                        #self.view.SV.settings().clearMemoryCaches()
                        #self.view.BE.settings().clearMemoryCaches()
                        self.writeInfoBuffer(self.transformToCurrentSRS(actualPoint))
                else:
                    self.actualPOV = tmpPOV
                self.setPosition()
            elif tmpPOV["transport"] == "mapCommand":
                feat = self.infoBoxManager.getInfolayer().getFeatures(core.QgsFeatureRequest(tmpPOV["fid"])).__next__()
                if tmpPOV["type"] == "edit":
                    self.iface.openFeatureForm(self.infoBoxManager.getInfolayer(),feat,True)
                if tmpPOV["type"] == "select":
                    self.infoBoxManager.getInfolayer().select(feat.id())
            elif tmpPOV["transport"] == "SVLocation":
                if tmpPOV["status"] == 'OK':
                    self.SVLocationResponse = core.QgsPointXY(tmpPOV["lon"],tmpPOV["lat"])
                else:
                    self.SVLocationResponse = "cucu" #core.QgsPointXY()


    def setPosition(self,forcePosition = None):
        #if self.apdockwidget.widget().__dict__ == self.dumView.__dict__ or not self.apdockwidget.isVisible():
        if not self.apdockwidget.isVisible():
          return
        try:
            actualWGS84 = core.QgsPointXY (float(self.actualPOV['lon']),float(self.actualPOV['lat']))
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
        self.position.reset()
        self.position=gui.QgsRubberBand(self.iface.mapCanvas(),core.QgsWkbTypes.PointGeometry )
        self.position.setWidth( 4 )
        self.position.setIcon(gui.QgsRubberBand.ICON_CIRCLE)
        self.position.setIconSize(4)
        self.position.setColor(QtCore.Qt.blue)
        self.position.addPoint(actualSRS)
        CS = self.canvas.mapUnitsPerPixel()*25
        zoom = float(self.actualPOV['zoom'])
        fov = (3.9018*pow(zoom,2) - 42.432*zoom + 123)/100;
        A1x = actualSRS.x()-CS*math.cos(math.pi/2-fov)
        A2x = actualSRS.x()+CS*math.cos(math.pi/2-fov)
        A1y = actualSRS.y()+CS*math.sin(math.pi/2-fov)
        A2y = A1y
        self.aperture.reset()
        self.aperture=gui.QgsRubberBand(self.iface.mapCanvas(),core.QgsWkbTypes.LineGeometry )
        self.aperture.setWidth( 3 )
        self.aperture.setColor(QtCore.Qt.blue)
        self.aperture.addPoint(core.QgsPointXY(A1x,A1y))
        self.aperture.addPoint(actualSRS)
        self.aperture.addPoint(core.QgsPointXY(A2x,A2y))
        tmpGeom = self.aperture.asGeometry()
        angle = float(self.actualPOV['heading'])*math.pi/-180
        self.aperture.setToGeometry(self.rotateTool.rotate(tmpGeom,actualSRS,angle),self.dumLayer)
        self.updateSVOptions()


        self.gswBrowserUrl ="https://maps.google.com/maps?q=&layer=c&cbll="+str(self.actualPOV['lat'])+","+str(self.actualPOV['lon'])+"&cbp=12,"+str(self.actualPOV['heading'])+",0,0,0&z=18"
        #Sync Google map
        js = "this.map.setCenter(new google.maps.LatLng(%s, %s));" % (str(self.actualPOV['lat']),str(self.actualPOV['lon']))
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = "this.SVpov.setPosition(new google.maps.LatLng(%s, %s));" % (str(self.actualPOV['lat']),str(self.actualPOV['lon']))
        self.view.BE.page().mainFrame().evaluateJavaScript(js)


    def checkLicenseAction(self):
        if self.licenceDlg.checkGoogle.isChecked()  and self.licenceDlg.APIkey.text() != '':
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
            self.disableControlShape()
            try:
                self.StreetviewAction.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'res', 'icoStreetview_gray.png')))
                #self.StreetviewAction.setIcon(QtGui.QIcon(":/plugins/go2streetview/res/icoStreetview_gray.png"))
                #self.StreetviewAction.setDisabled(True)
            except:
                pass

        else:
            self.StreetviewAction.setEnabled(True)
            self.StreetviewAction.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'res', 'icoStreetview.png')))
            self.setPosition()
            if self.infoBoxManager.isEnabled() and self.apdockwidget.widget() != self.dumView:
                infoLayer = self.infoBoxManager.getInfolayer()
                toInfoLayerProjection = core.QgsCoordinateTransform(core.QgsCoordinateReferenceSystem(4326),infoLayer.crs(), core.QgsProject.instance())
                self.enableControlShape(toInfoLayerProjection.transform(core.QgsPointXY(self.pointWgs84)))

    def resizeStreetview(self):
        #self.resizing = True
        self.resizeWidget()
        try:
            self.view.SV.loadFinished.connect(self.endRefreshWidget)
            self.refreshWidget(self.pointWgs84.x(), self.pointWgs84.y())
        except:
            pass

    def refreshWidget(self, new_lon, new_lat):
        if self.actualPOV['lat'] != 0.0:
            self.gswDialogUrl = os.path.join(self.dirPath,'res','g2sv.html?lat=' + str(new_lat) + "&long=" + str(new_lon) + "&width=" + str(self.viewWidth) + "&height=" + str(self.viewHeight) + "&heading=" + str(self.heading) + "&APIkey=" + self.APIkey)
            self.view.SV.load(QtCore.QUrl(pathlib.Path(QtCore.QDir.fromNativeSeparators(self.gswDialogUrl)).as_uri()))

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
        # Procedure to operate switch to google maps dialog set
        self.view.BE.show()
        self.view.SV.hide()
        self.view.btnSwitchView.setIcon(QtGui.QIcon(os.path.join(self.dirPath, "res", "icoStreetview.png")))
        #self.view.btnPrint.setDisabled(True)
        self.takeSnapshopItem.setDisabled(True)
        self.view.setWindowTitle("Google maps oblique")

    def switch2SV(self):
        # Procedure to operate switch to streetview dialog set
        self.view.BE.hide()
        self.view.SV.show()
        self.view.btnSwitchView.setIcon(QtGui.QIcon(os.path.join(self.dirPath, "res", "icoGMaps.png")))
        #self.view.btnPrint.setDisabled(False)
        self.takeSnapshopItem.setDisabled(False)
        self.view.setWindowTitle("Google Street View")

    def openInBrowserBE(self):
        # open an external browser with the google maps url for location/heading
        p = self.snapshotOutput.setCurrentPOV()
        webbrowser.open_new("https://www.google.com/maps/@%s,%s,150m/data=!3m1!1e3" % (str(p['lat']), str(p['lon'])))

    def openExternalUrl(self,url):
        core.QgsMessageLog.logMessage(url.toString(), tag="go2streetview", level=core.Qgis.Info)
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
        crsDest = core.QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = core.QgsCoordinateTransform(crsSrc, crsDest, core.QgsProject.instance())
        return xform.transform(pPoint) # forward transformation: src -> dest

    def transformToCurrentSRS(self, pPoint):
        # transformation from the current SRS to WGS84
        crcMappaCorrente = self.iface.mapCanvas().mapSettings().destinationCrs() # get current crs
        crsDest = crcMappaCorrente
        crsSrc = core.QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = core.QgsCoordinateTransform(crsSrc, crsDest, core.QgsProject.instance())
        return xform.transform(pPoint) # forward transformation: src -> dest

    def canvasPressEvent(self, event):
        # Press event handler inherited from QgsMapTool used to store the given location in WGS84 long/lat
        self.pressed=True
        self.pressx = event.pos().x()
        self.pressy = event.pos().y()
        self.movex = event.pos().x()
        self.movey = event.pos().y()
        self.highlight=gui.QgsRubberBand(self.iface.mapCanvas(),core.QgsWkbTypes.LineGeometry )
        self.highlight.setColor(QtCore.Qt.yellow)
        self.highlight.setWidth(5)
        self.PressedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(self.pressx, self.pressy)
        self.pointWgs84 = self.transformToWGS84(self.PressedPoint)
        # start infobox
        self.infoBoxManager.restoreIni()

    def canvasMoveEvent(self, event):
        # Moved event handler inherited from QgsMapTool needed to highlight the direction that is giving by the user
        if self.pressed:
            x = event.pos().x()
            y = event.pos().y()
            movedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            self.highlight.reset()
            self.highlight.addPoint(self.PressedPoint)
            self.highlight.addPoint(movedPoint)


    def canvasReleaseEvent(self, event):
        # Release event handler inherited from QgsMapTool needed to calculate heading
        event.modifiers()
        if (event.modifiers() & QtCore.Qt.ControlModifier):
            CTRLPressed = True
        else:
            CTRLPressed = None
        self.pressed=None
        self.highlight.reset()
        if not self.licenseAgree:
            self.licenceDlg.checkGoogle.stateChanged.connect(self.checkLicenseAction)
            self.licenceDlg.setWindowFlags(self.licenceDlg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
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

    def openSVDialog(self, show=True):
        # procedure for compiling streetview and gmaps url with the given location and heading
        self.heading = math.trunc(self.heading)
        if show:
            self.view.setWindowTitle("Google Street View")
            self.apdockwidget.setWidget(self.view)
            self.view.show()
            self.apdockwidget.raise_()
            self.view.activateWindow()
            self.view.BE.hide()
            self.view.SV.hide()
        self.viewHeight=self.view.size().height()
        self.viewWidth=self.view.size().width()

        self.gswDialogUrl = os.path.join(pathlib.Path(self.dirPath).as_uri(),'res','g2sv.html?lat=' + str(
            self.pointWgs84.y()) + "&long=" + str(self.pointWgs84.x()) + "&width=" + str(
            self.viewWidth) + "&height=" + str(self.viewHeight) + "&heading=" + str(
            self.heading) + "&APIkey=" + self.APIkey)

        self.headingGM = math.trunc(round (self.heading / 90) * 90)
        self.bbeUrl = os.path.join(pathlib.Path(self.dirPath).as_uri(), "res","g2gm.html?lat=" + str(self.pointWgs84.y()) + "&long=" + str(
            self.pointWgs84.x()) + "&width=" + str(self.viewWidth) + "&height=" + str(
            self.viewHeight) + "&zoom=19&heading=" + str(self.headingGM) + "&APIkey=" + self.APIkey)

        gswTitle = "Google Street View"
        core.QgsMessageLog.logMessage(QtCore.QUrl(self.gswDialogUrl).toString(), tag="go2streetview", level=core.Qgis.Info)
        core.QgsMessageLog.logMessage(self.bbeUrl, tag="go2streetview", level=core.Qgis.Info)
        self.httpConnecting = True
        self.view.SV.load(QtCore.QUrl(QtCore.QDir.fromNativeSeparators(self.gswDialogUrl)))
        self.view.BE.load(QtCore.QUrl(QtCore.QDir.fromNativeSeparators(self.bbeUrl)))
        self.view.SV.show()

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
            if cyclePause > 1:
                break
        #self.disableControlShape()
        if self.infoBoxManager.getInfolayer().geometryType() == core.QgsWkbTypes.PointGeometry:
            self.pointBuffer(p)
        elif self.infoBoxManager.getInfolayer().geometryType() == core.QgsWkbTypes.LineGeometry:
            self.lineBuffer(p)
        elif self.infoBoxManager.getInfolayer().geometryType() == core.QgsWkbTypes.PolygonGeometry :
            self.pointBuffer(p)
            self.lineBuffer(p,polygons = True)
        else:
            print ("Geometry error", self.infoBoxManager.getInfolayer().geometryType())

    def enableControlShape(self,XYPoint):
        pointgeom = core.QgsGeometry.fromPointXY(XYPoint)
        viewBuffer = pointgeom.buffer(self.infoBoxManager.getDistanceBuffer(),10)
        self.controlShape.setToGeometry(viewBuffer,self.infoBoxManager.getInfolayer())

    def disableControlShape(self):
        try:
            self.controlShape.reset()
        except:
            pass

    def pointBuffer(self,p):
        infoLayer = self.infoBoxManager.getInfolayer()
        toInfoLayerProjection = core.QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),infoLayer.crs(), core.QgsProject.instance())
        toWGS84 = core.QgsCoordinateTransform(infoLayer.crs(),core.QgsCoordinateReferenceSystem(4326), core.QgsProject.instance())
        # create layer and replicate fields
        bufferLayer = core.QgsVectorLayer("Point?crs="+infoLayer.crs().toWkt(), "temporary_points", "memory")
        #bufferLayer.setCrs(infoLayer.crs()) #This generates alert message
        bufferLayer.startEditing()
        bufferLayer.addAttribute(core.QgsField("id",QtCore.QVariant.String))
        bufferLayer.addAttribute(core.QgsField("html",QtCore.QVariant.String))
        bufferLayer.addAttribute(core.QgsField("icon",QtCore.QVariant.String))
        bufferLayer.addAttribute(core.QgsField("fid",QtCore.QVariant.Int))
        self.enableControlShape(toInfoLayerProjection.transform(core.QgsPointXY(p)))
        fetched = 0
        self.featsId = self.infoBoxManager.getContextFeatures(toInfoLayerProjection.transform(p))
        for featId in self.featsId:
            feat = infoLayer.getFeatures(core.QgsFeatureRequest(featId)).__next__()
            if fetched < 200:
                if infoLayer.geometryType() == core.QgsWkbTypes.PolygonGeometry:
                    fGeom = feat.geometry().pointOnSurface()
                elif infoLayer.geometryType() == core.QgsWkbTypes.PointGeometry:
                    fGeom = feat.geometry()
                if fGeom.isMultipart():
                    multipoint = fGeom.asMultiPoint()
                    point = multipoint[0]
                else:
                    point = fGeom.asPoint()
                fetched += 1
                newGeom = core.QgsGeometry.fromPointXY(core.QgsPointXY(point))
                newFeat = core.QgsFeature()
                newFeat.setGeometry(newGeom)
                newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat),self.infoBoxManager.getFeatId(feat)])
                bufferLayer.addFeature(newFeat)
            else:
                core.QgsMessageLog.logMessage("fetched too much features..... 200 max", tag="go2streetview", level=core.Qgis.Warning)
                break
        bufferLayer.commitChanges()
        core.QgsMessageLog.logMessage("markers context rebuilt", tag="go2streetview", level=core.Qgis.Info)
        #StreetView markers
        tmpfile = os.path.join(self.dirPath,"tmp","tmp_markers.geojson")
        core.QgsVectorFileWriter.writeAsVectorFormat (bufferLayer, tmpfile,"UTF8",toWGS84,"GeoJSON")
        with open(tmpfile) as f:
            geojson = f.read().replace('\n','')
        os.remove(tmpfile)
        #js = geojson.replace("'",'')
        #js = js.replace("\n",'\n')
        js = """this.markersJson = %s""" % json.dumps(geojson)
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = """this.readJson() """
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        core.QgsMessageLog.logMessage("webview markers refreshed", tag="go2streetview", level=core.Qgis.Info)



    def lineBuffer(self,p,polygons = None):
        dBuffer = self.infoBoxManager.getDistanceBuffer()
        infoLayer = self.infoBoxManager.getInfolayer()
        toInfoLayerProjection = core.QgsCoordinateTransform(self.iface.mapCanvas().mapSettings().destinationCrs(),infoLayer.crs(), core.QgsProject.instance())
        toWGS84 = core.QgsCoordinateTransform(infoLayer.crs(),core.QgsCoordinateReferenceSystem(4326), core.QgsProject.instance())
        # create layer and replicate fields
        bufferLayer = core.QgsVectorLayer("LineString?crs="+infoLayer.crs().toWkt(), "temporary_lines", "memory")
        #bufferLayer.setCrs(infoLayer.crs()) #This generates alert message
        bufferLayer.startEditing()
        bufferLayer.addAttribute(core.QgsField("id",QtCore.QVariant.String))
        bufferLayer.addAttribute(core.QgsField("html",QtCore.QVariant.String))
        bufferLayer.addAttribute(core.QgsField("icon",QtCore.QVariant.String))
        bufferLayer.addAttribute(core.QgsField("fid",QtCore.QVariant.Int))
        fetched = 0
        cutBuffer = core.QgsGeometry.fromPointXY(toInfoLayerProjection.transform(core.QgsPointXY(p))).buffer(dBuffer*2,10)
        self.enableControlShape(toInfoLayerProjection.transform(core.QgsPointXY(p)))
        if not polygons:
            self.featsId = self.infoBoxManager.getContextFeatures(toInfoLayerProjection.transform(p))
        for featId in self.featsId:
            feat = infoLayer.getFeatures(core.QgsFeatureRequest(featId)).__next__()
            if fetched < 1500:
                if infoLayer.geometryType() == core.QgsWkbTypes.PolygonGeometry:
                    fGeom = feat.geometry().convertToType(core.QgsWkbTypes.LineGeometry)
                elif infoLayer.geometryType() == core.QgsWkbTypes.LineGeometry:
                    fGeom = feat.geometry()
                if fGeom:
                    #break on closest point on segment to pov to improve visibility
                    closestResult = fGeom.closestSegmentWithContext(toInfoLayerProjection.transform(p));
                    fGeom.insertVertex(closestResult[1][0],closestResult[1][1],closestResult[2])
                    cGeom = fGeom.intersection(cutBuffer)
                    if cGeom.isMultipart():
                        multigeom = cGeom.asMultiPolyline()
                        for geom in multigeom:
                            newGeom = core.QgsGeometry.fromPolylineXY(geom)
                            newFeat = core.QgsFeature()
                            newFeat.setGeometry(newGeom)
                            newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat),self.infoBoxManager.getFeatId(feat)])
                            bufferLayer.addFeature(newFeat)

                    else:
                        geom = cGeom.asPolyline()
                        newGeom = core.QgsGeometry.fromPolylineXY(geom)
                        newFeat = core.QgsFeature()
                        newFeat.setGeometry(newGeom)
                        newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat),self.infoBoxManager.getFeatId(feat)])
                        bufferLayer.addFeature(newFeat)
                    fetched = fetched + len(newGeom.asPolyline())
                else:
                    core.QgsMessageLog.logMessage("Null geometry!", tag="go2streetview", level=core.Qgis.Warning)
            else:
                core.QgsMessageLog.logMessage("fetched too much features..... 200 max", tag="go2streetview", level=core.Qgis.Warning)
                break
        bufferLayer.commitChanges()
        core.QgsMessageLog.logMessage("line context rebuilt: %s features" % bufferLayer.featureCount(), tag="go2streetview", level=core.Qgis.Info)
        #StreetView lines
        tmpfile = os.path.join(self.dirPath, "tmp", "tmp_lines.geojson")
        core.QgsVectorFileWriter.writeAsVectorFormat(bufferLayer, tmpfile,"UTF8", toWGS84, "GeoJSON")
        with open(tmpfile) as f:
            geojson = f.read().replace('\n', '')
        os.remove(tmpfile)
        js = """this.linesJson = %s""" % json.dumps(geojson)
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = """this.readLinesJson() """
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        core.QgsMessageLog.logMessage("webview lines refreshed", tag="go2streetview", level=core.Qgis.Info)

    def noSVConnectionsPending(self,reply):
        print ("finished loading SV")
        self.httpConnecting = None
        if reply.error() == QtNetwork.QNetworkReply.NoError:
            pass
        elif reply.error() == QtNetwork.QNetworkReply.ContentNotFoundError:
            failedUrl = reply.request.url()
            httpStatus = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute).toInt()
            httpStatusMessage = reply.attribute(QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute).toByteArray()
            core.QgsMessageLog.logMessage("STREETVIEW FAILED REQUEST: {} {} {}".format(failedUrl,httpStatus,httpStatusMessage), tag="go2streetview", level=core.Qgis.Critical)
        else:
            core.QgsMessageLog.logMessage("STREETVIEW OTHER CONNECTION ERROR: {}".format(reply.error()), tag="go2streetview", level=core.Qgis.Critical)

    def noGMConnectionsPending(self, reply):
        if reply.error() == QtNetwork.QNetworkReply.NoError:
            pass
        elif reply.error() == QtNetwork.QNetworkReply.ContentNotFoundError:
            failedUrl = reply.request.url()
            httpStatus = reply.attribute(QtNetwork.QNetworkRequest.HttpStatusCodeAttribute).toInt()
            httpStatusMessage = reply.attribute(QtNetwork.QNetworkRequest.HttpReasonPhraseAttribute).toByteArray()
            core.QgsMessageLog.logMessage("GM FAILED REQUEST: {} {} {}".format(failedUrl,httpStatus,httpStatusMessage), tag="go2streetview", level=core.Qgis.Critical)
        else:
            core.QgsMessageLog.logMessage("GM OTHER CONNECTION ERROR: {}".format(reply.error()), tag="go2streetview", level=core.Qgis.Critical)

    def projectReadAction(self):
        #remove current sketches
        self.infoBoxManager.restoreIni()
        self.scanForCoverageLayer()
        if self.infoBoxManager.isEnabled() and self.apdockwidget.widget() != self.dumView:
            infoLayer = self.infoBoxManager.getInfolayer()
            toInfoLayerProjection = core.QgsCoordinateTransform(core.QgsCoordinateReferenceSystem(4326),
                                                                infoLayer.crs(), core.QgsProject.instance())
            self.enableControlShape(toInfoLayerProjection.transform(core.QgsPointXY(self.pointWgs84)))
            self.infoBoxManager.show()
            self.infoBoxManager.raise_()
            QtGui.QGuiApplication.processEvents()
            self.infoBoxManager.acceptInfoBoxState()
            QtGui.QGuiApplication.processEvents()

    def loadFinishedAction(self,ok):
        if ok:
            core.QgsMessageLog.logMessage("Finished loading", tag="go2streetview", level=core.Qgis.Info)
            pass
        else:
            core.QgsMessageLog.logMessage("Failed loading", tag="go2streetview", level=core.Qgis.Critical)
            pass

    def setupInspector(self):
        self.page = self.view.SV.page()
        self.page.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        self.webInspector = QtWebKitWidgets.QWebInspector(self)
        self.webInspector.setPage(self.page)
