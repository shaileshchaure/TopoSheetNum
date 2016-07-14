# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TopoNum
                                 A QGIS plugin
 Calcuate SOI toposheet numbers from the features
                             -------------------
        begin                : 2016-07-11
        copyright            : (C) 2016 by Shailesh Chaure
        email                : sk_chaure@rediffmail.com
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
    """Load TopoNum class from file TopoNum.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Topo_num import TopoNum
    return TopoNum(iface)
