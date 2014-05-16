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
from go2streetviewDialog import go2streetviewDialog
from snapshot import snapShot

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

    def initGui(self):
        # Create actions that will start plugin configuration
        self.StreetviewAction = QAction(QIcon(":/plugins/go2streetview/icoStreetview.png"), \
            "Click to open Google Street View", self.iface.mainWindow())
        QObject.connect(self.StreetviewAction, SIGNAL("triggered()"), self.StreetviewRun)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.StreetviewAction)
        self.iface.addPluginToMenu("&go2streetview", self.StreetviewAction)
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        #self.view = uic.loadUi( os.path.join( self.path, "go2streetview.ui" ) )
        self.view = go2streetviewDialog()
        self.view.switch2BE.clicked.connect(self.switch2BE)
        self.view.switch2SV.clicked.connect(self.switch2SV)
        self.view.openInBrowserBE.clicked.connect(self.openInBrowserBE)      
        self.view.takeSnapshotSV.clicked.connect(self.takeSnapshotSV)
        self.view.openInBrowserSV.clicked.connect(self.openInBrowserSV)
        self.view.SV.loadFinished.connect(self.catchCoord)
        self.pressed=None
        self.snapshotOutput = snapShot(self.iface,self.view.SV)
        # procedure to set proxy if needed
        s = QSettings() #getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled", "")
        proxyType = s.value("proxy/proxyType", "" )
        proxyHost = s.value("proxy/proxyHost", "" )
        proxyPort = s.value("proxy/proxyPort", "" )
        proxyUser = s.value("proxy/proxyUser", "" )
        proxyPassword = s.value("proxy/proxyPassword", "" )
        print proxyEnabled+"; "+proxyType+"; "+proxyHost+"; " + proxyPort+"; " + proxyUser+"; " +"*********; "
        
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
        self.iface.removePluginMenu("&go2streetview",self.StreetviewAction)
        self.iface.removeToolBarIcon(self.StreetviewAction)

    def catchCoord(self):
        print "Catch!"

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

    def takeSnapshotSV(self,):
        self.snapshotOutput.saveSnapShot()
        
    def transformToWGS84(self, pPoint):
        # transformation from the current SRS to WGS84
        crcMappaCorrente = iface.mapCanvas().mapRenderer().destinationCrs() # get current crs
        crsSrc = crcMappaCorrente
        crsDest = QgsCoordinateReferenceSystem(4326)  # WGS 84
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
        print "x:",self.pressx," y:",self.pressy
        self.PressedPoint = self.canvas.getCoordinateTransform().toMapCoordinates(self.pressx, self.pressy)
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
        self.pressed=None
        self.highlight.reset()
        self.releasedx = event.pos().x()
        self.releasedy = event.pos().y()
        #print "x:",self.releasedx," y:",self.releasedy
        if (self.releasedx==self.pressx)&(self.releasedy==self.pressy):
            heading=0
            result=0
        else:
            result = math.atan2((self.releasedx - self.pressx),(self.releasedy - self.pressy))
            result = math.degrees(result)
            if result > 0:
                heading =  180 - result
            else:
                heading = 360 - (180 + result)      
        self.openSVDialog(heading)
        
    def openSVDialog(self,heading):
        # procedure for compiling streetview and bing url with the given location and heading
        heading = math.trunc(heading)
        #self.gswDialogUrl = "qrc:///plugins/go2streetview/g2sv.html?lat="+str(self.pointWgs84.y())+"&long="+str(self.pointWgs84.x())+"&width=600&height=360&heading="+str(heading) 
        self.gswDialogUrl = "file:///D:/documenti/dev/go2streetview/g2sv.html?lat="+str(self.pointWgs84.y())+"&long="+str(self.pointWgs84.x())+"&width=600&height=360&heading="+str(heading) 
        self.gswBrowserUrl ="https://maps.google.com/maps?q=&layer=c&cbll="+str(self.pointWgs84.y())+","+str(self.pointWgs84.x())+"&cbp=12,"+str(heading)+",0,0,0&z=18"
        heading = math.trunc(round (heading/90)*90)
        self.bbeUrl = "http://dev.virtualearth.net/embeddedMap/v1/ajax/Birdseye?zoomLevel=17&center="+str(self.pointWgs84.y())+"_"+str(self.pointWgs84.x())+"&heading="+str(heading) 
        gswTitle = "Google Street View"
        #print self.gswDialogUrl
        print self.gswBrowserUrl
        #print self.bbeUrl   
        self.view.switch2BE.show()
        self.view.switch2SV.hide()
        self.view.openInBrowserSV.show()
        self.view.takeSnapshotSV.show()
        self.view.openInBrowserBE.hide()
        self.view.setWindowTitle("Google Street View")
        self.view.show()
        self.view.raise_()
        self.view.activateWindow()
        self.view.BE.hide()
        self.view.SV.hide()
        self.view.SV.load(QUrl(self.gswDialogUrl))
        self.view.BE.load(QUrl(self.bbeUrl))
        self.view.SV.show()        
        


    def StreetviewRun(self):
        # called by click on toolbar icon
        gsvMessage="Pick a point to display Google Street View in browser window"
        iface.mainWindow().statusBar().showMessage(gsvMessage)
        self.canvas.setMapTool(self)
