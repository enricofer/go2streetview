from qgis.core import QgsPoint, QgsGeometry
from PyQt5.QtWidgets import QMessageBox
import math
import re

class transformGeometry:
    # Rotates a geometry.
    # (c) Stefan Ziegler
    def rotate(self,geom,  point,  angle):
        
        if angle == 0 or angle == 2 * math.pi or angle == -2 * math.pi:
            return geom
        
        type = geom.wkbType()
        
        if type == 1:
            p0 = geom.asPoint()
            p1 = QgsPoint(p0.x() - point.x(),  p0.y() - point.y())
            p2 = rotatePoint(p1,  angle)
            p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
            return QgsGeometry().fromPoint(p3)
            
        elif type == 2:
            coords = []
            for i in geom.asPolyline():
                p1 = QgsPoint(i.x() - point.x(),  i.y() - point.y())
                p2 = self.rotatePoint(p1,  angle)
                p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
                coords.append(p3)
            return QgsGeometry().fromPolyline(coords)
    
        elif type == 3:
            coords = []
            ring = []
            for i in geom.asPolygon():
                for k in i: 
                    p1 = QgsPoint(k.x() - point.x(),  k.y() - point.y())
                    p2 = self.rotatePoint(p1,  angle)
                    p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
                    ring.append(p3)
                coords .append(ring)
                ring = []
            return QgsGeometry().fromPolygon(coords)
                
        elif type == 4:
            coords = []
            for i in geom.asMultiPoint():
                p1 = QgsPoint(i.x() - point.x(),  i.y() - point.y())
                p2 = self.rotatePoint(p1,  angle)
                p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
                coords.append(p3)
            return QgsGeometry().fromMultiPoint(coords)
            
        elif type == 5:
            coords = []
            singleline = [] 
            for i in geom.asMultiPolyline():
                for j in i:
                    p1 = QgsPoint(j.x() - point.x(),  j.y() - point.y())
                    p2 = self.rotatePoint(p1,  angle)
                    p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
                    singleline.append(p3)
                coords.append(singleline)
                singleline = []
            return QgsGeometry().fromMultiPolyline(coords)
            
        elif type == 6:
            coords = []
            ring = []
            for i in geom.asMultiPolygon():
                for j in i:
                    for k in j:
                        p1 = QgsPoint(k.x() - point.x(),  k.y() - point.y())
                        p2 = self.rotatePoint(p1,  angle)
                        p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
                        ring.append(p3)                    
                    coords.append(ring)
                    ring = []
            return QgsGeometry().fromMultiPolygon([coords])
            
        else:
            QMessageBox.information(None, 'Information', str(self.tr("Vector type is not supported.")))   
            return None


    # Rotates a single point (centre 0/0).
    # (c) Stefan Ziegler
    def rotatePoint(self,point,  angle):
        x = math.cos(angle)*point.x() - math.sin(angle)*point.y()
        y = math.sin(angle)*point.x() + math.cos(angle)*point.y()
        return QgsPoint(x,  y)