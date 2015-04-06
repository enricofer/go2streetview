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
from PyQt4 import uic
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from PyQt4.QtNetwork import *
from string import digits
from go2streetviewDialog import go2streetviewDialog, dumWidget,snapshotLicenseDialog, infobox
from snapshot import snapShot
from transformgeom import transformGeometry

import resources
import webbrowser
import urllib2
import string 
import os
import math
import json

class go2streetview(QgsMapTool):

    def __init__(self, iface):
       
       # Save reference to the QGIS interface
        self.iface = iface
        # reference to the canvas
        self.canvas = self.iface.mapCanvas()
        self.version = 'v6.1'
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
        QObject.connect(self.StreetviewAction, SIGNAL("triggered()"), self.StreetviewRun)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.StreetviewAction)
        self.iface.addPluginToWebMenu("&go2streetview", self.StreetviewAction)
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        #self.view = uic.loadUi( os.path.join( self.path, "go2streetview.ui" ) )
        self.actualPOV = {}
        self.view = go2streetviewDialog()
        self.dumView = dumWidget()
        self.dumView.enter.connect(self.clickOn)
        self.dumView.iconRif.setPixmap(QPixmap(":/plugins/go2streetview/res/icoStreetview.png"))
        self.apdockwidget=QDockWidget("go2streetview" , self.iface.mainWindow() )
        self.apdockwidget.setObjectName("go2streetview")
        self.apdockwidget.setWidget(self.dumView)
        #self.apdockwidget.setTitleBarWidget(self.view)
        #self.apdockwidget.resize(150,225)
        self.iface.addDockWidget( Qt.LeftDockWidgetArea, self.apdockwidget)
        self.resizeWidget()
        self.viewHeight=self.dumView.size().height()
        self.viewWidth=self.dumView.size().width()
        self.snapshotOutput = snapShot(self.iface,self.view.SV)
        self.view.SV.page().statusBarMessage.connect(self.catchJSevents)
        self.view.enter.connect(self.clickOn)
        self.view.closed.connect(self.closeDialog)
        self.setButtonBarSignals()
        self.infoBoxManager = infobox(self.iface)
        self.infoBoxManager.defined.connect(self.infoLayerDefinedAction)
        self.apdockwidget.visibilityChanged.connect(self.apdockChangeVisibility)
        self.pressed=None
        self.CTRLPressed=None
        self.position=QgsRubberBand(iface.mapCanvas(),QGis.Point )
        self.position.setWidth( 5 ) 
        self.position.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position.setIconSize(6)
        self.position.setColor(Qt.red)
        self.aperture=QgsRubberBand(iface.mapCanvas(),QGis.Line )
        self.rotateTool = transformGeometry()
        self.dumLayer = QgsVectorLayer("Point?crs=EPSG:4326", "temporary_points", "memory")
        self.actualPOV = {"lat":0.0,"lon":0.0,"heading":0.0}
        # procedure to set proxy if needed
        s = QSettings() #getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled", "")
        proxyType = s.value("proxy/proxyType", "" )
        proxyHost = s.value("proxy/proxyHost", "" )
        proxyPort = s.value("proxy/proxyPort", "" )
        proxyUser = s.value("proxy/proxyUser", "" )
        proxyPassword = s.value("proxy/proxyPassword", "" )
        #print proxyEnabled+"; "+proxyType+"; "+proxyHost+"; " + proxyPort+"; " + proxyUser+"; " +"*********; "
        
        if proxyEnabled == "true": # test if there are proxy settings
           proxy = QNetworkProxy()
           if proxyType == "DefaultProxy":
               proxy.setType(QNetworkProxy.DefaultProxy)
           elif proxyType == "Socks5Proxy":
               proxy.setType(QNetworkProxy.Socks5Proxy)
           elif proxyType == "HttpProxy":
               proxy.setType(QNetworkProxy.HttpProxy)
           elif proxyType == "HttpCachingProxy":
               proxy.setType(QNetworkProxy.HttpCachingProxy)
           elif proxyType == "FtpCachingProxy":
               proxy.setType(QNetworkProxy.FtpCachingProxy)
           proxy.setHostName(proxyHost)
           proxy.setPort(int(proxyPort))
           proxy.setUser(proxyUser)
           proxy.setPassword(proxyPassword)
           QNetworkProxy.setApplicationProxy(proxy)

    def setButtonBarSignals(self):
        self.view.btnInfoLayer.clicked.connect(self.infoLayerAction)
        self.view.btnSwitchView.clicked.connect(self.switchViewAction)
        self.view.btnOpenInBrowser.clicked.connect(self.openInBrowserAction)
        self.view.btnTakeSnapshop.clicked.connect(self.takeSnapshopAction)
        #self.view.btnPrint.clicked.connect(self.printAction)
        self.view.btnPrint.hide()

    def infoLayerAction(self):
        self.infoBoxManager.show()

    def infoLayerDefinedAction(self):
        if self.infoBoxManager.isEnabled():
            actualPoint = QgsPoint(float(self.actualPOV['lon']),float(self.actualPOV['lat']))
            self.writeInfoBuffer(self.transformToCurrentSRS(actualPoint))
        else:
            js = "this.clearMarkers();"
            self.view.SV.page().mainFrame().evaluateJavaScript(js)
            js = "for (var i = 0; i < this.pins.length; i++) {this.map.DeleteShape(this.pins[i])}"
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

    def printAction(self):
        pass

    def unload(self):
        # Hide License 
        try:
            self.license.hide()
        except:
            pass
        try:
            # Remove the plugin menu item and icon and dock Widget
            self.iface.removePluginMenu("&go2streetview",self.StreetviewAction)
            self.iface.removeToolBarIcon(self.StreetviewAction)
            self.iface.removeDockWidget(self.apdockwidget)
        except:
            pass

    def catchJSevents(self,status):
        try:
            tmpPOV = json.JSONDecoder().decode(status)
        except:
            tmpPOV = None
        if tmpPOV:
            if self.actualPOV["lat"] != tmpPOV["lat"] or self.actualPOV["lon"] != tmpPOV["lon"]:
                self.actualPOV = tmpPOV
                actualPoint = QgsPoint(float(self.actualPOV['lon']),float(self.actualPOV['lat']))
                if self.infoBoxManager.isEnabled():
                    self.writeInfoBuffer(self.transformToCurrentSRS(actualPoint))
            else:
                self.actualPOV = tmpPOV
            #print status
            self.setPosition()

    def setPosition(self,forcePosition = None):
        try:
            actualWGS84 = QgsPoint (float(self.actualPOV['lon']),float(self.actualPOV['lat']))
        except:
            return
        actualSRS = self.transformToCurrentSRS(actualWGS84)
        self.position.reset()
        self.position=QgsRubberBand(iface.mapCanvas(),QGis.Point )
        self.position.setWidth( 4 )
        self.position.setIcon(QgsRubberBand.ICON_CIRCLE)
        self.position.setIconSize(4)
        self.position.setColor(Qt.blue)
        self.position.addPoint(actualSRS)
        CS = self.canvas.mapUnitsPerPixel()*25
        #print "zoom",self.actualPOV['zoom']
        #fov = (90/max(1,float(self.actualPOV['zoom'])))*math.pi/360
        zoom = float(self.actualPOV['zoom'])
        fov = (3.9018*pow(zoom,2) - 42.432*zoom + 123)/100;
        #print "fov",fov
        A1x = actualSRS.x()-CS*math.cos(math.pi/2-fov)
        A2x = actualSRS.x()+CS*math.cos(math.pi/2-fov)
        A1y = actualSRS.y()+CS*math.sin(math.pi/2-fov)
        A2y = A1y
        #print A1x,A1y,actualSRS.x(),actualSRS.y()
        self.aperture.reset()
        self.aperture=QgsRubberBand(iface.mapCanvas(),QGis.Line )
        self.aperture.setWidth( 3 )
        self.aperture.setColor(Qt.blue)
        self.aperture.addPoint(QgsPoint(A1x,A1y))
        self.aperture.addPoint(actualSRS)
        self.aperture.addPoint(QgsPoint(A2x,A2y))
        tmpGeom = self.aperture.asGeometry()
        angle = float(self.actualPOV['heading'])*math.pi/-180
        self.aperture.setToGeometry(self.rotateTool.rotate(tmpGeom,actualSRS,angle),self.dumLayer)
        self.gswBrowserUrl ="https://maps.google.com/maps?q=&layer=c&cbll="+str(self.actualPOV['lat'])+","+str(self.actualPOV['lon'])+"&cbp=12,"+str(self.actualPOV['heading'])+",0,0,0&z=18"
        #Sync Bing Map
        js = "this.map.SetCenter(new VELatLong(%s, %s));" % (str(self.actualPOV['lat']),str(self.actualPOV['lon']))
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = "this.map.DeleteShape (this.SVpov);"
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = "this.map.SetScaleBarDistanceUnit(VEDistanceUnit.Kilometers);"
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = "var SVpov = this.map.AddPushpin(new VELatLong(%s, %s));" % (str(self.actualPOV['lat']),str(self.actualPOV['lon']))
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        js = """this.SVpov.SetCustomIcon("<img src='http://icons.iconarchive.com/icons/webalys/kameleon.pics/32/Street-View-icon.png' />");"""
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        

    def checkLicenseAction(self):
        if self.license.checkGoogle.isChecked() and self.license.checkBing.isChecked():
            self.license.hide()
            self.licenseAgree = True
            self.S.setValue("go2sv/license",self.version)
            #self.initGui()

    def closeDialog(self):
        #print "CLOSEDDIALOG"
        self.position.reset()
        self.aperture.reset()

    def apdockChangeVisibility(self,vis):
        #print "WIDGET OPEN: ",vis
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
        if self.actualPOV['lat'] != 0.0:
            self.gswDialogUrl = "qrc:///plugins/go2streetview/res/g2sv.html?lat="+str(self.actualPOV['lat'])+"&long="+str(self.actualPOV['lon'])+"&width="+str(self.viewWidth)+"&height="+str(self.viewHeight)+"&heading="+str(self.actualPOV['heading'])
            self.view.SV.load(QUrl(self.gswDialogUrl))


    def clickOn(self):
        self.explore()

    def resizeWidget(self):
        self.viewHeight=self.view.size().height()
        self.viewWidth=self.view.size().width()
        #print "RESIZEWIDGET",self.viewWidth,self.viewHeight
        self.view.SV.resize(self.viewWidth,self.viewHeight)
        self.view.BE.resize(self.viewWidth,self.viewHeight)
        self.view.buttonBar.move(self.viewWidth-252,0)

    def switch2BE(self):
        # Procedure to operate switch to bing dialog set
        self.view.BE.show()
        self.view.SV.hide()
        self.view.btnSwitchView.setIcon(QIcon(":/plugins/go2streetview/res/icoStreetview.png"))
        self.view.btnPrint.setDisabled(True)
        self.view.btnTakeSnapshop.setDisabled(True)
        self.view.setWindowTitle("Bing Bird's Eye")

    def switch2SV(self):
        # Procedure to operate switch to streetview dialog set
        self.view.BE.hide()
        self.view.SV.show()
        self.view.btnSwitchView.setIcon(QIcon(":/plugins/go2streetview/res/icoBing.png"))
        self.view.btnPrint.setDisabled(False)
        self.view.btnTakeSnapshop.setDisabled(False)
        self.view.setWindowTitle("Google Street View")

    def openInBrowserBE(self):
        # open an external browser with the bing url for location/heading
        webbrowser.open_new(self.bbeUrl)
        
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
        crcMappaCorrente = iface.mapCanvas().mapRenderer().destinationCrs() # get current crs
        crsSrc = crcMappaCorrente
        crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84
        xform = QgsCoordinateTransform(crsSrc, crsDest)
        return xform.transform(pPoint) # forward transformation: src -> dest

    def transformToCurrentSRS(self, pPoint):
        # transformation from the current SRS to WGS84
        crcMappaCorrente = iface.mapCanvas().mapRenderer().destinationCrs() # get current crs
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
        self.highlight=QgsRubberBand(iface.mapCanvas(),QGis.Line )
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
            self.license = snapshotLicenseDialog()
            self.license.checkGoogle.stateChanged.connect(self.checkLicenseAction)
            self.license.checkBing.stateChanged.connect(self.checkLicenseAction)
            self.license.setWindowFlags(self.license.windowFlags() | Qt.WindowStaysOnTopHint)
            self.license.show()
            self.license.raise_()
            self.license.activateWindow()
            return
        self.releasedx = event.pos().x()
        self.releasedy = event.pos().y()
        #print "x:",self.releasedx," y:",self.releasedy
        if (self.releasedx==self.pressx)&(self.releasedy==self.pressy):
            self.heading=0
            result=0
        else:
            result = math.atan2((self.releasedx - self.pressx),(self.releasedy - self.pressy))
            result = math.degrees(result)
            if result > 0:
                self.heading =  180 - result
            else:
                self.heading = 360 - (180 + result)
        if CTRLPressed:
            self.openInBrowserOnCTRLClick()
        else:
            self.openSVDialog()
        
    def openSVDialog(self):
        # procedure for compiling streetview and bing url with the given location and heading
        self.heading = math.trunc(self.heading)
        self.gswDialogUrl = "qrc:///plugins/go2streetview/res/g2sv.html?lat="+str(self.pointWgs84.y())+"&long="+str(self.pointWgs84.x())+"&width="+str(self.viewWidth)+"&height="+str(self.viewHeight)+"&heading="+str(self.heading)
        self.headingBing = math.trunc(round (self.heading/90)*90)
        self.bbeUrl = "http://dev.virtualearth.net/embeddedMap/v1/ajax/Birdseye?zoomLevel=17&center="+str(self.pointWgs84.y())+"_"+str(self.pointWgs84.x())+"&heading="+str(self.headingBing)
        gswTitle = "Google Street View"
        print QUrl(self.gswDialogUrl).toString()
        #print self.gswBrowserUrl
        print self.bbeUrl
        self.view.setWindowTitle("Google Street View")
        self.apdockwidget.setWidget(self.view)
        self.view.show()
        self.apdockwidget.raise_()
        self.view.activateWindow()
        self.view.BE.hide()
        self.view.SV.hide()
        self.view.SV.load(QUrl(self.gswDialogUrl))
        self.view.BE.load(QUrl(self.bbeUrl))
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
        iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.dumLayer.setCrs(iface.mapCanvas().mapRenderer().destinationCrs())
        self.canvas.setMapTool(self)

    def writeInfoBuffer(self,p):
        dBuffer = self.infoBoxManager.getDistanceBuffer()
        infoLayer = self.infoBoxManager.getInfolayer()
        toInfoLayerProjection = QgsCoordinateTransform(iface.mapCanvas().mapRenderer().destinationCrs(),infoLayer.crs())#DEPRECATED
        toWGS84 = QgsCoordinateTransform(infoLayer.crs(),QgsCoordinateReferenceSystem(4326))
        # create layer and replicate fields
        bufferLayer = QgsVectorLayer("Point?crs="+infoLayer.crs().toWkt(), "temporary_points", "memory")
        #bufferLayer.setCrs(infoLayer.crs()) #This generates alert message
        bufferLayer.startEditing()
        bufferLayer.addAttribute(QgsField("id",QVariant.String))
        bufferLayer.addAttribute(QgsField("html",QVariant.String))
        bufferLayer.addAttribute(QgsField("icon",QVariant.String))
        bufferGeom = QgsGeometry.fromPoint(toInfoLayerProjection.transform(p)).buffer(dBuffer,10)
        fetched = 0
        for feat in infoLayer.getFeatures():
            if fetched < 200:
                if feat.geometry().within(bufferGeom):
                    if feat.geometry().isMultipart():
                        multipoint = feat.geometry().asMultiPoint()
                        point = multipoint[0]
                    else:
                        point = feat.geometry().asPoint()
                    fetched += 1
                    newGeom = QgsGeometry.fromPoint(point)
                    newFeat = QgsFeature()
                    newFeat.setGeometry(newGeom)
                    newFeat.setAttributes([self.infoBoxManager.getInfoField(feat),self.infoBoxManager.getHtml(feat),self.infoBoxManager.getIconPath(feat)])
                    bufferLayer.addFeature(newFeat)
            else:
                print "fetched too much features..... 200 max"
                break
        bufferLayer.commitChanges()
        #StreetView markers
        QgsVectorFileWriter.writeAsVectorFormat (bufferLayer,os.path.join(self.path,"tmp.geojson"),"UTF8",toWGS84,"GeoJSON")
        with open(os.path.join(self.path,"tmp.geojson")) as f:
            geojson = f.read().replace('\n','')
        js = geojson.replace("'",'')
        js = js.replace("\n",'\n')
        js = "this.markersJson = '%s'" % unicode(js,"utf8")
        #print js
        self.view.SV.page().mainFrame().evaluateJavaScript(js)
        self.view.SV.page().mainFrame().evaluateJavaScript("""this.readJson() """)
        #Bing Pushpins
        pushpins = json.loads(geojson)
        js = "var pins = [];"
        self.view.BE.page().mainFrame().evaluateJavaScript(js)
        for feat in pushpins["features"]:
            point = feat["geometry"]["coordinates"]
            js = "var loc = new VELatLong(%s, %s);" % (point[1],point[0])
            self.view.BE.page().mainFrame().evaluateJavaScript(js)
            js = "var pin = this.map.AddPushpin(this.loc);"
            self.view.BE.page().mainFrame().evaluateJavaScript(js)
            js = "this.pins.push(this.pin);"
            self.view.BE.page().mainFrame().evaluateJavaScript(js)

            if feat["properties"]["id"] != "":
                js = 'this.pin.SetTitle("%s");' % feat["properties"]["id"]
                self.view.BE.page().mainFrame().evaluateJavaScript(js)
            if feat["properties"]["html"] != "":
                js = 'this.pin.SetDescription("%s");' % feat["properties"]["html"]
                self.view.BE.page().mainFrame().evaluateJavaScript(js)
            if feat["properties"]["icon"] != "":
                js = """this.pin.SetCustomIcon("<img src='%s' />");""" % feat["properties"]["icon"]
                self.view.BE.page().mainFrame().evaluateJavaScript(js)

            
            