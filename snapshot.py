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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from PyQt4.QtNetwork import *
from string import digits
from go2streetviewDialog import snapshotNotesDialog
from osgeo import ogr

import resources
import webbrowser
import urllib2
import string 
import os
import datetime
import osgeo.ogr, osgeo.osr
import os.path

class snapShot():

    def __init__(self,iface,w):
       # Save reference to the QGIS interface
       # Save reference to QWebView with Streetview application
        self.webview = w
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        self.annotationsDialog = snapshotNotesDialog()
        self.annotationsDialog.setWindowTitle("Custom snapshot notes")
        self.annotationsDialog.hide()
        self.annotationsDialog.pushButton.clicked.connect(self.returnAnnotationsValue)
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
        actualLat = actualLoc[1:actualLoc.find(", ")-1]
        actualLon = actualLoc[actualLoc.find(", ")+2:len(actualLoc)-1]
        actualHeading = self.webview.page().currentFrame().findFirstElement("div#heading_cell")
        actualHeading = actualHeading.toPlainText()
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
        self.pov = dict([('lat',actualLat[:actualLat.find(".")+6]),('lon',actualLon[:actualLon.find(".")+6]),('heading',actualHeading),('pitch',actualPitch),('address',actualAddress)])
        print self.pov
        return self.pov

    # setup dialog for custom annotation
    def getAnnotations(self):
        self.annotationsDialog.label.setText("Snapshot:"+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" "+self.pov['lon']+"E "+self.pov['lon']+"N")
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

    # landing method from take snapshot button"
    def saveSnapShot(self):
        self.pov = self.setCurrentPOV()
        #print self.pov
        self.getAnnotations()

    # method to save google image to local file
    def saveImg(self):
        urlimg="http://maps.googleapis.com/maps/api/streetview?size=640x400&location="+self.pov['lat']+","+self.pov['lon']+"&heading="+self.pov['heading']+"&pitch="+self.pov['pitch']+"&sensor=false"
        #print urlimg
        self.file_name = os.path.join(self.sessionDirectory(),'streetview-'+self.pov['lat'].replace(".","_")+'-'+self.pov['lon'].replace(".","_")+"-"+self.pov['heading'].replace(".","_")+'-'+self.pov['pitch'].replace(".","_")+'.jpg')
        #print self.file_name
        u = urllib2.urlopen(urlimg)
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

    # procedure to create shapefile log
    def createShapefile(self,path):
        fields = QgsFields()
        fields.append(QgsField("date", QVariant.String))
        fields.append(QgsField("lon", QVariant.String))
        fields.append(QgsField("lat", QVariant.String))
        fields.append(QgsField("heading", QVariant.String))
        fields.append(QgsField("pitch", QVariant.String))
        fields.append(QgsField("address", QVariant.String))
        fields.append(QgsField("notes", QVariant.String))
        fields.append(QgsField("url", QVariant.String))
        srs = QgsCoordinateReferenceSystem ()
        srs.createFromProj4 ("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
        writer = QgsVectorFileWriter(path, "ISO 8859-1", fields,  QGis.WKBPoint, srs, "ESRI Shapefile")
        del writer
    
    # procedure to store image and write log
    def saveShapeFile(self):
        #The line below is commented to disable saving of static images in local directory to not violate point 10.1.3.b) of https://developers.google.com/maps/terms
        #self.saveImg()
        urlimg="http://maps.googleapis.com/maps/api/streetview?size=640x400&location="+self.pov['lat']+","+self.pov['lon']+"&heading="+self.pov['heading']+"&pitch="+self.pov['pitch']+"&sensor=false"
        sfPath=os.path.join(self.sessionDirectory(),"Streetview_snapshots_log.shp")
        #print sfPath
        if not os.path.isfile(sfPath):
            self.createShapefile(sfPath)
        vlayer = QgsVectorLayer(sfPath, "Streetview_snapshots_log", "ogr")
        #print ', '.join(self.canvas.layers())
        testIfLayPresent = None
        for lay in self.canvas.layers():
            #print lay.name()
            if lay.name() == "Streetview_snapshots_log":
                testIfLayPresent = True
        if not testIfLayPresent:
            vlayer.loadNamedStyle(os.path.join(self.path,"snapshotStyle.qml"))
            self.iface.actionFeatureAction().trigger()
            print "trigger"
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            set=QSettings()
            set.setValue("/qgis/showTips", True)
        feat = QgsFeature()
        feat.initAttributes(8)
        feat.setAttribute(0,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        feat.setAttribute(1,self.pov['lon'])
        feat.setAttribute(2,self.pov['lat'])
        feat.setAttribute(3,self.pov['heading'])
        feat.setAttribute(4,self.pov['pitch'])
        feat.setAttribute(5,self.pov['address'])
        feat.setAttribute(6,self.snapshotNotes)
        #feat.setAttribute(7,self.file_name)
        feat.setAttribute(7,urlimg)
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(self.pov['lon']), float(self.pov['lat']))))
        (res, outFeats) = vlayer.dataProvider().addFeatures([feat])
        QgsVectorFileWriter.writeAsVectorFormat(vlayer,sfPath, "ISO 8859-1", None, "ESRI Shapefile")
        del vlayer
        self.canvas.refresh() 
        
    