# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TopoNum
                                 A QGIS plugin
 Calcuate SOI toposheet numbers from the features
                              -------------------
        begin                : 2016-07-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Shailesh Chaure
        email                : sk_chaure@rediffmail.com
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
#from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtCore import *
#from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import *
from qgis.utils import iface
from qgis.core import QgsVectorLayer, QgsFeature, QgsPoint, QgsField, QgsMapLayerRegistry,QgsGeometry,QgsGraduatedSymbolRendererV2,QgsSymbolV2,QgsRendererRangeV2
from qgis.gui import QgsMessageBar
from qgis import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from Topo_num_dialog import TopoNumDialog
import os.path

start_index=[32,37,42,51,60,69,75,80,89,98]
WGSAlpha=['C','D','E','F','G','H','I','J','K','L']
global scaleID
global sheetw
global sheeth
    
def degDec2dms(dec):
        deg=int(dec)
        temp=dec-deg
        temp=temp*60
        minute=int(temp)
        sec=temp-minute
        sec=int(round((sec*60),0))	
        return deg,minute,sec
        
def DMS2DD(d,m,s):
        dd=d+(float(m)/60)+(float(s)/3600)
        return dd
               
def dmstosec(d,m,s):
        seconds=(d*3600)+(m*60)+round(s,0)
        return seconds

def sectodeg(t):
        decimal=float(t)/3600
        a,b,c=degDec2dms(decimal)
        return a,b,c


def CalculateExtentInTermsOfSheet(minlongs,maxlongs,minlats,maxlats):
        #sheetw,sheeth=setFactor1(scaleID) 
        if minlongs % sheetw<>0:
            while (minlongs % sheetw)!=0:
                minlongs=minlongs-1
        else:
            minlongs=minlongs-sheetw
       
        if maxlongs%sheetw<>0:
            while (maxlongs % sheetw)!=0:
                maxlongs=maxlongs+1
        else:
            maxlongs=maxlongs+sheetw
       
        if minlats%sheeth<>0:
            while (minlats% sheeth)!=0:
                minlats=minlats-1
        else: 
            minlats=minlats-sheeth

        if maxlats % sheeth<>0: 
            while (maxlats % sheeth)!=0:
                maxlats=maxlats+1
        else:
            maxlats=maxlats+sheeth
        return minlongs,maxlongs,minlats,maxlats
      
def validSheet(lt_deg,ln_deg):
        valid=True
        if lt_deg<20:
            if ln_deg<72:
                valid=False
            if (ln_deg>=88)and(ln_deg<92):
                valid=False
        if lt_deg<16:
            if (ln_deg>=84)and(ln_deg<92):
                valid=False;
        if (ln_deg<64)or(ln_deg>=100):
                valid=False
        if (lt_deg<4)or(lt_deg>=40):
                valid=False
        if ((ln_deg>=88)and(ln_deg<92))and(lt.deg<21):
                valid=False
        return valid
     
    
def CalculateOldSheetNum(lat_deg,lat_min,lat_sec,long_deg,long_min,long_sec):
        n=0
        s=" "
        sn=" "
        
        #lat_deg,lat_min,lat_sec=sectodeg(lats)
        #long_deg,long_min,long_sec=sectodeg(longs)
        def Indexno1():
	      n=(long_deg / 4)-16
	      n=start_index[n]+((39-lat_deg)/ 4)
	      s=str(n)
	      return s
          
        def Indexno2():
	      n=(long_deg-(long_deg / 4)*4)*4+((lat_deg / 4)*4)+4-lat_deg-1
	      s1=chr(65+n)
	      return (Indexno1()+s1)	
          
        def Indexno3():
	      if lat_min>=30:
                s1='N'
	      else:
                s1='S'
	      if long_min>=30:
                s1=s1+'E'
	      else:
                s1=s1+'W'
	      return(Indexno2()+'/'+s1)
          
        def Indexno4():
          n=(long_min/15)*4+(59-lat_min) /15+1
          s1=str(n)
          return(Indexno2()+'/'+s1)	
          
        def Indexno5():
	      n=(lat_min*60)+lat_sec  	
	      while (n>=900): 
                n=n-900
	      if( n>=450):
                s1='N' 
	      else:
	         s1='S'
	      n=(long_min*60)+long_sec  
 	      while (n>=900): 
                n=n-900
	      if (n>=450):
                s1=s1+'E' 
	      else: 
                s1=s1+'W'
	      return(Indexno4()+'/'+s1)
        
        if validSheet(lat_deg,long_deg):        
            if(scaleID==1):
                sn=Indexno1() 
            if(scaleID==2):
                sn=Indexno2() 
            if(scaleID==3):
                sn=Indexno3()
            if(scaleID==4):
                sn=Indexno4() 
            if(scaleID==5):
                sn=Indexno5() 
        else:
			sn='#'
        return sn
        
def CalcWGS84_Sheetno(lt_deg,lt_min,lt_sec,ln_deg,ln_min,ln_sec):
    def Indexno1():
      n=((lt_deg-8) / 4)
      n1=((ln_deg-66) / 6)+42
      return WGSAlpha[n]+str(n1)

    def Indexno2():
      n=(ln_deg-(ln_deg / 6)*6)
      n1=3-(lt_deg-(lt_deg / 4)*4)
      s1=chr(65+n+(n1*6))
      return Indexno1()+s1 

    def Indexno4():
      n=(ln_min / 15)*4+(59-lt_min) / 15+1
      s1=str(n)
      if len(s1)==1:
       	s1='0'+s1
      return Indexno2()+s1 

    def Indexno5():
		n=lt_min*60+lt_sec
		while n>=900:
			n=n-900
		if n>=450: 
			s1='N' 
		else:
			s1='S'
		n=ln_min*60+ln_sec
		while n>=900:
			n=n-900
		if n>=450:
			s1=s1+'E' 
		else:
			s1=s1+'W'
		return Indexno4()+'/'+s1 
  
    def Indexno6():
      x=ln_min / 15
      y=lt_min / 15
      n=((ln_min-(x*15)) / 3)
      n1=4-((lt_min-(y*15)) / 3)
      s1=chr(65+n+(n1*5))
      return Indexno4()+s1
 
    def Indexno7():
      ltmin=lt_min % 3
      n=((ltmin*60)+lt_sec) / 36
      n=5-n
      lnmin=ln_min % 3
      n1=((lnmin*60)+ln_sec) / 36
      n=n+(n1*5)
      s1=str(n)
      if len(s1)==1: 
        s1='0'+s1
      return Indexno6()+s1  

    if validSheet(lt_deg,ln_deg):
        if(scaleID==1):
            sn=Indexno1() 
        if(scaleID==2):
            sn=Indexno2() 
        if(scaleID==3):
            sn=Indexno4()
        if(scaleID==4):
            sn=Indexno5()
        if(scaleID==5):
            sn=Indexno6()
        if(scaleID==6):
            sn=Indexno7()
    else:
        sn='#'
    return sn


def CalculateSheet(sheetTypeID,s_lats,s_longs,Xg,Yg):
        laty=s_lats
        lcount=0
        id=0
        for i in range(0,Yg):
            longx=s_longs
            bx1=0
            s=" "
            for j in range(0,Xg):		
                Blt_deg,Blt_min,Blt_sec=sectodeg(laty) # Bottom latitude
                Lln_deg,Lln_min,Lln_sec=sectodeg(longx) # Left longitude
                tlaty=laty+sheeth
                Tlt_deg,Tlt_min,Tlt_sec=sectodeg(tlaty) # Top latitude
                rlongx=longx+sheetw
                Rln_deg,Rln_min,Rln_sec=sectodeg(rlongx) # Right longitude
                xmin=DMS2DD(Lln_deg,Lln_min,Lln_sec)
                ymin=DMS2DD(Blt_deg,Blt_min,Blt_sec)
                xmax=DMS2DD(Rln_deg,Rln_min,Rln_sec)
                ymax=DMS2DD(Tlt_deg,Tlt_min,Tlt_sec)
                if sheetTypeID==1:
					Sheetnum=CalculateOldSheetNum(Blt_deg,Blt_min,Blt_sec,Lln_deg,Lln_min,Lln_sec)
                else:
					Sheetnum=CalcWGS84_Sheetno(Blt_deg,Blt_min,Blt_sec,Lln_deg,Lln_min,Lln_sec)
                points = [QgsPoint(xmin,ymin),QgsPoint(xmin,ymax),QgsPoint(xmax,ymax),QgsPoint(xmax,ymin),QgsPoint(xmin,ymin)]
                poly.setGeometry(QgsGeometry.fromPolygon([points]))
                poly.setAttributes([id,Sheetnum,False])
                id=id+1
                pr.addFeatures([poly])
                longx=longx+sheetw	
            laty=laty+sheeth
               
        
def setFactor1(sclid):
    if sclid==1:
        fx=14400
    if sclid==2:
        fx=3600
    if sclid==3:
        fx=1800
    if sclid==4:
        fx=900        
    if sclid==5:
        fx=450
    fy=fx
    return fx,fy
    
def setFactor2(sclid):
    if sclid==1:
        fx=21600
        fy=14400
    if sclid==2:
        fx=3600
    if sclid==3:
        fx=900
    if sclid==4:
        fx=450        
    if sclid==5:
        fx=180
    if sclid==6:
        fx=36
    if sclid>1:
        fy=fx
    return fx,fy

class TopoNum:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TopoNum_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = TopoNumDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&TopoSheet Nubers Calculator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'TopoNum')
        self.toolbar.setObjectName(u'TopoNum')
        self.items = {1:['1:1M','1:250,000','1:125,000','1:50,000','1:25,000'],2:['1:1M','1:250,000','1:50,000','1:25,000']}
        self.dlg.sheetTypeComboBox.activated[str].connect(self.on_combo_activated)
        
    def on_combo_activated(self, text):
        self.dlg.scaleComboBox.clear()
        #maptype= self.dlg.sheetTypeComboBox.currentIndex()+1
        self.dlg.scaleComboBox.addItems(self.items[self.dlg.sheetTypeComboBox.currentIndex()+1])
        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TopoNum', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TopoNum/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'TopoSheet Number Calculator'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&TopoSheet Nubers Calculator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    

    def run(self):
        """Run method that performs all the real work"""
        self.dlg.layerComboBox.clear()
        self.dlg.sheetTypeComboBox.clear()
        self.dlg.scaleComboBox.clear()  
        #self.dlg.label_2.setText('')        
        Alllayers = self.iface.legendInterface().layers()
        #layer_list = []
        lcount=0
        for layer in Alllayers:
            xyCrs = layer.crs()
            if xyCrs.projectionAcronym()=='longlat':
                lcount=lcount+1
                self.dlg.layerComboBox.addItem(layer.name(),layer)
                
        self.dlg.sheetTypeComboBox.addItem('Indian and Adjoining Countries Series Maps')    
        self.dlg.sheetTypeComboBox.addItem('Open Series Maps')    
        
        scale_list=['1:1M','1:250,000','1:125,000','1:50,000','1:25,000']
        self.dlg.scaleComboBox.addItems(scale_list)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            global scaleID
            global sheetw
            global sheeth
            if lcount>0:
                scaleID=self.dlg.scaleComboBox.currentIndex()+1
                maptype= self.dlg.sheetTypeComboBox.currentIndex()+1
                if maptype==1:                
                    sheetw,sheeth=setFactor1(scaleID)
                if maptype==2:
                    sheetw,sheeth=setFactor2(scaleID)               
                index = self.dlg.layerComboBox.currentIndex()
                clayer = self.dlg.layerComboBox.itemData(index)
                e=clayer.extent()
                a,b,c=degDec2dms(e.xMinimum())
                slongs=dmstosec(a,b,c)
                a,b,c=degDec2dms(e.xMaximum())
                elongs=dmstosec(a,b,c)
                a,b,c=degDec2dms(e.yMinimum())
                slats=dmstosec(a,b,c)
                a,b,c=degDec2dms(e.yMaximum())
                elats=dmstosec(a,b,c)
                slongs,elongs,slats,elats=CalculateExtentInTermsOfSheet(slongs,elongs,slats,elats)
                Xgrids=int(elongs-slongs)//sheetw # // is used for modular division
                Ygrids=int(elats-slats)//sheeth
                layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "TopoSheets", "memory")
                global poly
                global pr
                pr = layer.dataProvider() 
                pr.addAttributes([QgsField("id",QVariant.Int),QgsField("SheetNo",QVariant.String),QgsField("Inside",QVariant.String)])
                layer.updateFields()
               
                poly = QgsFeature()
                CalculateSheet(maptype,slats,slongs,Xgrids,Ygrids)
                n=0
                # check intersection of selected layer feature with sheets
                fieldIdx = pr.fields().indexFromName('Inside' )
                updateMap = {}
                for f in clayer.getFeatures():
                    for a in layer.getFeatures():
                        if a.geometry().intersects(f.geometry()):
                            n=n+1
                            updateMap[a.id()] = { fieldIdx:True }
                pr.changeAttributeValues(updateMap)
                
                # set the layer symbology
                values = (
                ('In', True,True,QColor.fromRgb(95,254,99)),
                ('Out', False,False,'yellow'),
                )
                # create a category for each item in values
                ranges=[]
                for label, lower, upper, color in values:
                    symbol = QgsSymbolV2.defaultSymbol(layer.geometryType())
                    symbol.setColor(QColor(color))
                    rng = QgsRendererRangeV2(lower, upper, symbol, label)
                    ranges.append(rng)
                expression = 'Inside' # field name
                renderer = QgsGraduatedSymbolRendererV2(expression, ranges)
                layer.setRendererV2(renderer)
                
                # set layer transparence and dolabelling
                layer.setLayerTransparency(65)              
                layer.updateExtents()
                QgsMapLayerRegistry.instance().addMapLayers([layer])
                layer.setCustomProperty("labeling", "pal")
                layer.setCustomProperty("labeling/enabled", "true")
                layer.setCustomProperty("labeling/fontFamily", "Arial")
                layer.setCustomProperty("labeling/fontSize", "10")
                layer.setCustomProperty("labeling/fieldName", "SheetNo")
                layer.setCustomProperty("labeling/placement", "1")
                iface.mapCanvas().refresh()
            else:
                iface.messageBar().pushMessage("Error", "No layers loaded, Load layer with Geographic Corrdinates", level=QgsMessageBar.CRITICAL)
            pass
