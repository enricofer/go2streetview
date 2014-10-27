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
from go2streetviewDialog import go2streetviewDialog, dumWidget,snapshotLicenseDialog
from snapshot import snapShot
from transformgeom import transformGeometry

import resources
import webbrowser
import urllib2
import string 
import os
import math

class go2streetview(QgsMapTool):

    def __init__(self, iface):
       
       # Save reference to the QGIS interface
        self.iface = iface
        # reference to the canvas
        self.canvas = self.iface.mapCanvas()
        QgsMapTool.__init__(self, self.canvas)
        self.licenseAgree = None

    def initGui(self):
        if not self.licenseAgree:
            print "NOT CHECKED LICENSE"
            self.license = snapshotLicenseDialog()
            self.license.checkGoogle.stateChanged.connect(self.checkLicenseAction)
            self.license.checkBing.stateChanged.connect(self.checkLicenseAction)
            self.license.setWindowFlags(self.license.windowFlags() | Qt.WindowStaysOnTopHint)
            self.license.show()
            self.license.raise_()
            self.license.activateWindow()
            return
        else:
            print "CHECKED LICENSE"
        # Create actions that will start plugin configuration
        self.StreetviewAction = QAction(QIcon(":/plugins/go2streetview/icoStreetview.png"), \
            "Click to open Google Street View", self.iface.mainWindow())
        QObject.connect(self.StreetviewAction, SIGNAL("triggered()"), self.StreetviewRun)
        #timer object instance for polling position to javascript 
        self.cron = QTimer()
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.StreetviewAction)
        self.iface.addPluginToWebMenu("&go2streetview", self.StreetviewAction)
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        #self.view = uic.loadUi( os.path.join( self.path, "go2streetview.ui" ) )
        self.actualPOV = {}
        self.view = go2streetviewDialog()
        self.dumView = dumWidget()
        self.dumView.show()
        #self.view.setObjectName("go2streetview")
        self.apdockwidget=QDockWidget("go2streetview" , self.iface.mainWindow() )
        self.apdockwidget.setObjectName("go2streetview")
        self.apdockwidget.setWidget(self.dumView)
        self.dumView.iconRif.setPixmap(QPixmap(":/plugins/go2streetview/icoStreetview.png"))
        #self.apdockwidget.setTitleBarWidget(self.view)
        #self.apdockwidget.resize(150,225)
        self.iface.addDockWidget( Qt.LeftDockWidgetArea, self.apdockwidget)
        #self.view.resize(self.viewWidth,self.viewHeight)
        self.resizeWidget()
        self.snapshotOutput = snapShot(self.iface,self.view.SV)
        self.view.switch2BE.clicked.connect(self.switch2BE)
        self.view.switch2SV.clicked.connect(self.switch2SV)
        self.view.openInBrowserBE.clicked.connect(self.openInBrowserBE)      
        self.view.takeSnapshotSV.clicked.connect(self.takeSnapshotSV)
        self.view.openInBrowserSV.clicked.connect(self.openInBrowserSV)
        self.view.SV.loadFinished.connect(self.startTimer)
        self.view.closed.connect(self.closeDialog)
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
        
    def unload(self):
        # Remove the plugin menu item and icon 
        self.license.hide()
        try:
            self.iface.removePluginMenu("&go2streetview",self.StreetviewAction)
            self.iface.removeToolBarIcon(self.StreetviewAction)
        except:
            pass

    def checkLicenseAction(self):
        if self.license.checkGoogle.isChecked() and self.license.checkBing.isChecked():
            self.license.hide()
            self.licenseAgree = True
            self.initGui()

    def startTimer(self):
        self.actualPOV = self.snapshotOutput.setCurrentPOV()
        self.cron.timeout.connect(self.pollPosition)
        self.cron.start(1000)

    def pollPosition(self,forcePosition = None):
        if self.actualPOV != {} and self.snapshotOutput:
            tmpPOV = self.snapshotOutput.setCurrentPOV()
            if not(tmpPOV['lon'] == self.actualPOV['lon'] and tmpPOV['lat'] == self.actualPOV['lat'] and tmpPOV['heading'] == self.actualPOV['heading']) or forcePosition:
                #print self.actualPOV
                self.actualPOV = tmpPOV
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
        self.actualPOV = tmpPOV

    def closeDialog(self):
        #print "CLOSEDDIALOG"
        self.position.reset()
        self.aperture.reset()
        self.cron.timeout.disconnect(self.pollPosition)

    def apdockChangeVisibility(self,vis):
        #print "WIDGET OPEN: ",vis
        if not vis:
            self.position.reset()
            self.aperture.reset()
            try:
                self.cron.timeout.disconnect(self.pollPosition)
            except:
                pass
            self.StreetviewAction.setIcon(QIcon(":/plugins/go2streetview/icoStreetview_gray.png"))
            self.StreetviewAction.setDisabled(True)
        else:
            self.StreetviewAction.setEnabled(True)
            self.StreetviewAction.setIcon(QIcon(":/plugins/go2streetview/icoStreetview.png"))
            self.pollPosition(True)
            self.cron.timeout.connect(self.pollPosition)

    def resizeStreetview(self):
        #self.resizing = True
        self.resizeWidget()
        if self.actualPOV != {}:
            if self.actualPOV['heading'] != "" or self.actualPOV['lat'] != "" or self.actualPOV['lon'] != "":
                try:
                    self.gswDialogUrl = "qrc:///plugins/go2streetview/g2sv.html?lat="+self.actualPOV['lat']+"&long="+self.actualPOV['lon']+"&width="+str(self.viewWidth)+"&height="+str(self.viewHeight)+"&heading="+self.actualPOV['heading'] 
                    self.gswBrowserUrl ="https://maps.google.com/maps?q=&layer=c&cbll="+str(self.pointWgs84.y())+","+str(self.pointWgs84.x())+"&cbp=12,"+str(self.heading)+",0,0,0&z=18"
                    self.headingBing = math.trunc(round (float(self.actualPOV['heading'])/90)*90)
                    self.bbeUrl = "http://dev.virtualearth.net/embeddedMap/v1/ajax/Birdseye?zoomLevel=17&center="+self.actualPOV['lat']+"_"+self.actualPOV['lon']+"&heading="+str(self.headingBing)
                    self.view.SV.load(QUrl(self.gswDialogUrl))
                    self.view.BE.load(QUrl(self.bbeUrl))
                except:
                    pass

    def resizeWidget(self):
        self.viewHeight=self.view.size().height()
        self.viewWidth=self.view.size().width()
        #print "RESIZEWIDGET",self.viewWidth,self.viewHeight
        if self.viewWidth >300:
            self.view.SV.resize(self.viewWidth,self.viewHeight)
            self.view.BE.resize(self.viewWidth,self.viewHeight)
            self.view.switch2BE.move(self.viewWidth-152,2)
            self.view.switch2BE.resize(150,25)
            self.view.switch2SV.move(self.viewWidth-152,2)
            self.view.switch2SV.resize(150,25)
            self.view.openInBrowserBE.move(self.viewWidth-152,28)
            self.view.openInBrowserBE.resize(150,25)
            self.view.takeSnapshotSV.move(self.viewWidth-152,54)
            self.view.takeSnapshotSV.resize(150,25)
            self.view.openInBrowserSV.move(self.viewWidth-152,28)
            self.view.openInBrowserSV.resize(150,25)
        else:
            self.view.SV.resize(self.viewWidth,self.viewHeight-75)
            self.view.BE.resize(self.viewWidth,self.viewHeight-75)
            self.view.SV.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff);
            self.view.SV.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff);
            self.view.BE.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff);
            self.view.BE.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff);
            self.view.switch2BE.move(0,self.viewHeight-75)
            self.view.switch2BE.resize(self.viewWidth,25)
            self.view.switch2SV.move(0,self.viewHeight-75)
            self.view.switch2SV.resize(self.viewWidth,25)
            self.view.openInBrowserBE.move(0,self.viewHeight-50)
            self.view.openInBrowserBE.resize(self.viewWidth,25)
            self.view.takeSnapshotSV.move(0,self.viewHeight-50)
            self.view.takeSnapshotSV.resize(self.viewWidth,25)
            self.view.openInBrowserSV.move(0,self.viewHeight-25)
            self.view.openInBrowserSV.resize(self.viewWidth,25)

    def switch2BE(self):
        # Procedure to operate switch to bing dialog set
        self.view.BE.show()
        self.view.SV.hide()
        self.view.switch2BE.hide()
        self.view.switch2SV.show()
        self.view.openInBrowserSV.hide()
        self.view.takeSnapshotSV.hide()
        self.view.openInBrowserBE.show()
        self.view.setWindowTitle("Bing Bird's Eye")

    def switch2SV(self):
        # Procedure to operate switch to streetview dialog set
        self.view.BE.hide()
        self.view.SV.show()
        self.view.switch2BE.show()
        self.view.switch2SV.hide()
        self.view.openInBrowserSV.show()
        self.view.takeSnapshotSV.show()
        self.view.openInBrowserBE.hide()
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
        self.actualPOV={}
        self.resizeWidget()
        self.heading = math.trunc(self.heading)
        self.gswDialogUrl = "qrc:///plugins/go2streetview/g2sv.html?lat="+str(self.pointWgs84.y())+"&long="+str(self.pointWgs84.x())+"&width="+str(self.viewWidth)+"&height="+str(self.viewHeight)+"&heading="+str(self.heading)
        #self.gswDialogUrl = "file:///D:/documenti/dev/go2streetview/g2sv.html?lat="+str(self.pointWgs84.y())+"&long="+str(self.pointWgs84.x())+"&width=600&height=360&heading="+str(heading)
        self.headingBing = math.trunc(round (self.heading/90)*90)
        self.bbeUrl = "http://dev.virtualearth.net/embeddedMap/v1/ajax/Birdseye?zoomLevel=17&center="+str(self.pointWgs84.y())+"_"+str(self.pointWgs84.x())+"&heading="+str(self.headingBing)
        gswTitle = "Google Street View"
        #print self.gswDialogUrl
        #print self.gswBrowserUrl
        #print self.bbeUrl
        self.view.switch2BE.show()
        self.view.switch2SV.hide()
        self.view.openInBrowserSV.show()
        self.view.takeSnapshotSV.show()
        self.view.openInBrowserBE.hide()
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
        #set event repeat to get current position
        

    def StreetviewRun(self):
        # called by click on toolbar icon
        self.view.resized.connect(self.resizeStreetview)
        gsvMessage="Pick a point to display Google Street View in browser window"
        iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.dumLayer.setCrs(iface.mapCanvas().mapRenderer().destinationCrs())
        self.canvas.setMapTool(self)
