# -*- coding: utf-8 -*-
"""
/***************************************************************************
 globespotterTest
                                 A QGIS plugin
 desc
                             -------------------
        begin                : 2015-01-30
        copyright            : (C) 2015 by ef
        email                : enricofer@gmail.com
        git sha              : $Format:%H$
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load globespotterTest class from file globespotterTest.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .globespotterTest import globespotterTest
    return globespotterTest(iface)
