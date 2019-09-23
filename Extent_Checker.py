# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ExtentChecker
                                 A QGIS plugin
 To convert cad plan to shapfile
                              -------------------
        begin                : 2019-09-15
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Prabhath W.J.K.A.N. Survey Dept. of Sri Lanka
        email                : npjasinghe@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
# Import the code for the dialog
from Extent_Checker_dialog import ExtentCheckerDialog
import os.path
from qgis.core import*
from qgis.gui import*
from PyQt4.QtGui import*
from PyQt4.QtCore import*
import processing
from qgis.utils import *
from PyQt4 import QtGui
import os, sys, datetime,time
import qgis
from qgis.utils import iface
import resources


class ExtentChecker:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
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
            'ExtentChecker_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
        self.dlg = ExtentCheckerDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&2 Extent Checker')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ExtentChecker')
        self.toolbar.setObjectName(u'ExtentChecker')
        self.dlg.lineEdit.clear()
        self.dlg.pushButton.clicked.connect(self.select_TL)

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
        return QCoreApplication.translate('ExtentChecker', message)


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

        # Create the dialog (after translation) and keep reference
        #self.dlg = ExtentCheckerDialog()

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

        icon_path = ':/plugins/ExtentChecker/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Check the Extent V0.1'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&2 Extent Checker'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
    def select_TL(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Select TL","",'*.xlsx')      
        self.dlg.lineEdit.setText(filename)


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            TL = self.dlg.lineEdit.text()                      
            cLayer = self.iface.mapCanvas().currentLayer()
            cLayer.removeSelection()
            outputs_QGISDISSOLVE_1=processing.runalg('qgis:dissolve', cLayer,False,'Text',None)

            outputs_QGISFIELDCALCULATOR_1=processing.runalg('qgis:fieldcalculator',outputs_QGISDISSOLVE_1['OUTPUT'] ,'farea',0,10.0,3.0,True,'$area',None)
            outputs_QGISJOINATTRIBUTESTABLE_1=processing.runalg('qgis:joinattributestable', outputs_QGISFIELDCALCULATOR_1['OUTPUT_LAYER'],TL,'Text','LotNo',None)
            outputs_QGISADDFIELDTOATTRIBUTESTABLE_1=processing.runalg('qgis:addfieldtoattributestable', outputs_QGISJOINATTRIBUTESTABLE_1['OUTPUT_LAYER'],'ex',0,10.0,0.0,None)
            outputs_QGISFIELDCALCULATOR_1=processing.runandload('qgis:fieldcalculator', outputs_QGISADDFIELDTOATTRIBUTESTABLE_1['OUTPUT_LAYER'],'ex',1,10.0,0.0,True,'abs("Extent"  *10000-"farea")',None)

            cLayer = iface.mapCanvas().currentLayer()
            layer = self.iface.activeLayer()
            myfilepath= iface.activeLayer().dataProvider().dataSourceUri()
            QgsMapLayerRegistry.instance().removeMapLayer( cLayer)
            layer = QgsVectorLayer(myfilepath,"ExError", 'ogr')
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            b= r""+TL[:-5]+"Report02.txt" 
            file = open(b, 'w')
            cLayer = iface.mapCanvas().currentLayer()
            file.write('----------Report of Extent Matching result--------"\n')
            file.write('\nLot No  Ex.Error(sq.m) \n')
            expr = QgsExpression("ex>-2 AND ex<2 ")
            it = cLayer.getFeatures( QgsFeatureRequest( expr ) )
            ids = [i.id() for i in it]
            cLayer.setSelectedFeatures( ids )
            cLayer.startEditing()
            for fid in ids:
                cLayer.deleteFeature(fid)
            cLayer.commitChanges()
            count=cLayer.featureCount()
            if count==0:
                window = iface.mainWindow()
                QMessageBox.information(window,"Info", "Correct..! There is no extent errors...")
                file.write('\nThere is no extent errors\n ')
            else:
                feats = []
                cLayer = iface.mapCanvas().currentLayer()
                for feat in cLayer.getFeatures():
                    msgout = '%s,%s,%s\n' % (feat["Text"],"    ", feat["ex"])
                    unicode_message = msgout.encode('utf-8')
                    feats.append(unicode_message)     
                feats.sort()
                for item in feats:
                    file.write(item)
            now = datetime.datetime.now()
            date= str (now)
            a1= str (now.strftime("%Y-%m-%d"))
            file.write ("\nDate : "+ a1+"\n")
            file.write ('\n------------------------- R&D @ SGO ------------------------')
            file.close()

            window = iface.mainWindow()
            QMessageBox.information(window,"Info", "Process complete....! \n  \n             ~~~  R&D - SGO ~~~")

            pass

