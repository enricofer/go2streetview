# -*- coding: utf-8 -*-
"""
/***************************************************************************
 go2streetview
                                 A QGIS plugin
 click to open Google Street View
                             -------------------
        begin                : 2014-02-17
        copyright            : (C) 2014 by Enrico Ferreguti
        email                : enricofer@me.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))


def classFactory(iface):
    # load go2streetview class from file go2streetview
    from go2streetview import go2streetview
    return go2streetview(iface)
