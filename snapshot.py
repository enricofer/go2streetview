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
from reversegeocoder import ReverseGeocoder
from urllib2 import URLError

import resources_rc
import webbrowser
import urllib2
import string
import os
import datetime
import osgeo.ogr, osgeo.osr
import os.path

class snapShot():

    def __init__(self,parent):
       # Save reference to the QGIS interface
       # Save reference to QWebView with Streetview application
        self.parent = parent
        self.webview = parent.view.SV
        self.iface = parent.iface
        self.canvas = iface.mapCanvas()
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        self.annotationsDialog = snapshotNotesDialog()
        self.annotationsDialog.setWindowTitle("Custom snapshot notes")
        self.annotationsDialog.hide()
        self.annotationsDialog.pushButton.clicked.connect(self.returnAnnotationsValue)
        self.GeocodingServerUp = True
        self.cb = QApplication.clipboard()
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
        #print self.pov
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
        #print self.pov
        self.getAnnotations()

    # method to save google image to local file
    def saveImg(self,path = None):
        urlimg="http://maps.googleapis.com/maps/api/streetview?size=640x400&location="+self.pov['lat']+","+self.pov['lon']+"&heading="+self.pov['heading']+"&pitch="+self.pov['pitch']+"&sensor=false&key="+self.parent.APIkey
        #print urlimg
        if path:
            self.file_name = path
        else:
            self.file_name = os.path.join(self.sessionDirectory(),'streetview-'+self.pov['lat'].replace(".","_")+'-'+self.pov['lon'].replace(".","_")+"-"+self.pov['heading'].replace(".","_")+'-'+self.pov['pitch'].replace(".","_")+'.jpg')
        QgsMessageLog.logMessage(self.file_name, tag="go2streetview", level=QgsMessageLog.INFO)
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

    def getAddress(self):
        #Reverse geocode support if geocode plugin is loaded
        if self.GeocodingServerUp:
            try:
                geocoder = ReverseGeocoder()
                address = geocoder.geocode(self.pov['lat'],self.pov['lon'])
                QgsMessageLog.logMessage(address, tag="go2streetview", level=QgsMessageLog.INFO)
                if address != "":
                    return address
                else:
                    return self.pov['address']
            except URLError, e:
                #QMessageBox.information(self.iface.mainWindow(), QCoreApplication.translate('GeoCoding', "Reverse GeoCoding error"), unicode(QCoreApplication.translate('GeoCoding', "<strong>Nominatim server is unreachable</strong>.<br>Disabling Remote geocoding,\nplease check network connection.")))
                QgsMessageLog.logMessage("Nominatim server is unreachable. Disabling Remote geocoding, please check network connection.", tag="go2streetview", level=QgsMessageLog.CRITICAL)
                self.GeocodingServerUp = None
                return self.pov['address']
        else:
            return self.pov['address']

    def getGeolocationInfo(self):
        self.setCurrentPOV()
        self.pov['address'] = self.getAddress()
        return self.pov

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
        fields.append(QgsField("url", QVariant.String, len=250))
        srs = QgsCoordinateReferenceSystem ()
        srs.createFromProj4 ("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
        writer = QgsVectorFileWriter(path, "ISO 8859-1", fields,  QGis.WKBPoint, srs, "ESRI Shapefile")
        del writer

    # procedure to store image and write log
    def saveShapeFile(self):
        #The line below is commented to disable saving of static images in local directory to not violate point 10.1.3.b) of https://developers.google.com/maps/terms
        #self.saveImg()
        #fov = str(int(90/max(1,float(self.pov['zoom']))))
        zoom = float(self.pov['zoom'])
        fov = 3.9018*pow(zoom,2) - 42.432*zoom + 123
        #print self.pov['zoom'],fov
        urlimg="http://maps.googleapis.com/maps/api/streetview?size=640x400&location="+self.pov['lat']+","+self.pov['lon']+"&heading="+self.pov['heading']+"&pitch="+self.pov['pitch']+"&sensor=false"+"&fov="+str(fov)+"&key="+self.parent.APIkey
        self.cb.setText(urlimg)
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
            #print "trigger"
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
        feat.setAttribute(5,self.getAddress())

        #if 'GeoCoding' in plugins:
            #gc = plugins['GeoCoding']
            #geocoder = gc.get_geocoder_instance()
            #address = geocoder.reverse((self.pov['lat'],self.pov['lon']), exactly_one=True)
            #print address
            #feat.setAttribute(5,address[0])
        #else:
            #feat.setAttribute(5,self.pov['address'])
        feat.setAttribute(6,self.snapshotNotes)
        #feat.setAttribute(7,self.file_name)
        print "urlimg",urlimg
        feat.setAttribute(7,QUrl(urlimg).toString())
        feat.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(self.pov['lon']), float(self.pov['lat']))))
        (res, outFeats) = vlayer.dataProvider().addFeatures([feat])
        QgsVectorFileWriter.writeAsVectorFormat(vlayer,sfPath, "ISO 8859-1", None, "ESRI Shapefile")
        del vlayer
        self.canvas.refresh()
