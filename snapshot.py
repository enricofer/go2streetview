"""
/***************************************************************************
 snapshot class write sv image and geolocate snapshot
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
from string import digits
from .go2streetviewDialog import snapshotNotesDialog
from osgeo import ogr
#from .reversegeocoder import ReverseGeocoder
from urllib.error import URLError

import resources_rc
import webbrowser
from urllib.request import urlopen
import string
import os
import datetime
import osgeo.ogr, osgeo.osr
import os.path

class snapShot():

    def __init__(self,parentInstance):
       # Save reference to the QGIS interface
       # Save reference to QWebView with Streetview application
        self.parent = parentInstance
        self.webview = parentInstance.view.SV
        self.iface = parentInstance.iface
        self.canvas = self.iface.mapCanvas()
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        self.annotationsDialog = snapshotNotesDialog()
        self.annotationsDialog.setWindowTitle("Custom snapshot notes")
        self.annotationsDialog.hide()
        self.annotationsDialog.pushButton.clicked.connect(self.returnAnnotationsValue)
        self.GeocodingServerUp = True
        self.cb = QtWidgets.QApplication.clipboard()
        #self.featureIndex = 0

    #method to define session directory and create if not present
    def sessionDirectory(self):
        path = os.path.dirname( os.path.abspath( __file__ ) )
        #datetime.datetime.now().strftime("%Y-%m-%d")
        sDir = os.path.join(self.path,'snapshots')
        if not os.path.isdir(sDir):
            os.makedirs(sDir)
        return sDir

    #method to extract actual position from Streetview html application
    def setCurrentPOV(self):
        actualLoc = self.webview.page().currentFrame().findFirstElement("div#position_cell")
        actualLoc = actualLoc.toPlainText()
        actualLat = actualLoc[1:actualLoc.find(", ")]
        actualLon = actualLoc[actualLoc.find(", ")+2:len(actualLoc)-1]
        actualHeading = self.webview.page().currentFrame().findFirstElement("div#heading_cell")
        actualHeading = actualHeading.toPlainText()
        actualZoom = self.webview.page().currentFrame().findFirstElement("div#zoom_cell")
        actualZoom = actualZoom.toPlainText()
        if actualHeading.find(".") != -1:
            actualHeading = actualHeading[:actualHeading.find(".")+2]
        actualPitch = self.webview.page().currentFrame().findFirstElement("div#pitch_cell")
        actualPitch = actualPitch.toPlainText()
        if actualPitch.find(".") != -1:
            actualPitch = actualPitch[:actualPitch.find(".")]
        actualAddress = self.webview.page().currentFrame().findFirstElement("div#pano_address")
        actualAddress = actualAddress.toPlainText()
        actualAddress = actualAddress.replace("'","")
        actualAddress = actualAddress.replace('"',"")
        self.pov = dict([('lat',actualLat[:actualLat.find(".")+8]),('lon',actualLon[:actualLon.find(".")+8]),('heading',actualHeading),('pitch',actualPitch),('zoom',actualZoom),('address',actualAddress)])
        return self.pov

    # setup dialog for custom annotation
    def getAnnotations(self):
        self.annotationsDialog.label.setText("Snapshot:"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" "+self.pov['lon']+"E "+self.pov['lat']+"N")
        self.annotationsDialog.textEdit.clear()
        self.annotationsDialog.show()
        self.annotationsDialog.raise_()
        self.annotationsDialog.textEdit.setFocus()

    # landing method from ok click of annotation dialog
    def returnAnnotationsValue(self):
        self.snapshotNotes = self.annotationsDialog.textEdit.toPlainText ()
        self.snapshotNotes = self.snapshotNotes.replace("'","")
        self.snapshotNotes = self.snapshotNotes.replace('"',"")
        self.annotationsDialog.hide()
        self.saveShapeFile()
        if self.annotationsDialog.textEdit.toPlainText ()[0:1] == '#':
            self.saveImg(path = os.path.join(self.sessionDirectory(),self.annotationsDialog.textEdit.toPlainText()[1:]+'.jpg'))

    # landing method from take snapshot button"
    def saveSnapShot(self):
        self.pov = self.setCurrentPOV()
        self.getAnnotations()

    # method to save google image to local file
    def saveImg(self,path = None):
        urlimg="http://maps.googleapis.com/maps/api/streetview?size=640x400&location="+self.pov['lat']+","+self.pov['lon']+"&heading="+self.pov['heading']+"&pitch="+self.pov['pitch']+"&sensor=false&key="+self.parent.APIkey
        #print urlimg
        if path:
            self.file_name = path
        else:
            self.file_name = os.path.join(self.sessionDirectory(),'streetview-'+self.pov['lat'].replace(".","_")+'-'+self.pov['lon'].replace(".","_")+"-"+self.pov['heading'].replace(".","_")+'-'+self.pov['pitch'].replace(".","_")+'.jpg')
        core.QgsMessageLog.logMessage(self.file_name, tag="go2streetview", level=core.Qgis.Info)
        u = urlopen(urlimg)
        f = open(self.file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
        f.close()

    def getGeolocationInfo(self):
        self.setCurrentPOV()
        return self.pov

    # procedure to create shapefile log
    def createShapefile(self,path):
        fields = core.QgsFields()
        fields.append(core.QgsField("date", QtCore.QVariant.String))
        fields.append(core.QgsField("lon", QtCore.QVariant.String))
        fields.append(core.QgsField("lat", QtCore.QVariant.String))
        fields.append(core.QgsField("heading", QtCore.QVariant.String))
        fields.append(core.QgsField("pitch", QtCore.QVariant.String))
        fields.append(core.QgsField("address", QtCore.QVariant.String))
        fields.append(core.QgsField("notes", QtCore.QVariant.String))
        fields.append(core.QgsField("url", QtCore.QVariant.String, len=250))
        srs = core.QgsCoordinateReferenceSystem ()
        srs.createFromProj4 ("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
        writer = core.QgsVectorFileWriter(path, "ISO 8859-1", fields,  core.QgsWkbTypes.WKBPoint, srs, "ESRI Shapefile")
        del writer 

    # procedure to store image and write log
    def saveShapeFile(self):
        #The line below is commented to disable saving of static images in local directory to not violate point 10.1.3.b) of https://developers.google.com/maps/terms
        #self.saveImg()
        #fov = str(int(90/max(1,float(self.pov['zoom']))))
        zoom = float(self.pov['zoom'])
        fov = 3.9018*pow(zoom,2) - 42.432*zoom + 123
        urlimg="http://maps.googleapis.com/maps/api/streetview?size=640x400&location="+self.pov['lat']+","+self.pov['lon']+"&heading="+self.pov['heading']+"&pitch="+self.pov['pitch']+"&sensor=false"+"&fov="+str(fov)+"&key="+self.parent.APIkey
        self.cb.setText(urlimg)
        sfPath=os.path.join(self.sessionDirectory(),"Streetview_snapshots_log.shp")
        if not os.path.isfile(sfPath):
            self.createShapefile(sfPath)
        vlayer = core.QgsVectorLayer(sfPath, "Streetview_snapshots_log", "ogr")
        testIfLayPresent = None
        for lay in self.canvas.layers():
            if lay.name() == "Streetview_snapshots_log":
                testIfLayPresent = True
        if not testIfLayPresent:
            vlayer.loadNamedStyle(os.path.join(self.path,"snapshotStyle.qml"))
            #self.iface.actionFeatureAction().trigger()
            core.QgsProject.instance().addMapLayer(vlayer)
            set=QtCore.QSettings()
            set.setValue("/qgis/showTips", True)
        feat = core.QgsFeature()
        feat.initAttributes(8)
        feat.setAttribute(0,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        feat.setAttribute(1,self.pov['lon'])
        feat.setAttribute(2,self.pov['lat'])
        feat.setAttribute(3,self.pov['heading'])
        feat.setAttribute(4,self.pov['pitch'])
        feat.setAttribute(5,self.pov['address'])#self.getAddress())
        feat.setAttribute(6,self.snapshotNotes)
        #feat.setAttribute(7,self.file_name)
        feat.setAttribute(7,QtCore.QUrl(urlimg).toString())
        feat.setGeometry(core.QgsGeometry.fromPointXY(core.QgsPointXY(float(self.pov['lon']), float(self.pov['lat']))))
        vlayer.dataProvider().addFeatures([feat])
        vlayer.triggerRepaint()
