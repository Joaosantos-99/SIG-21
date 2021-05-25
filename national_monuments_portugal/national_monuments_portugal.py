# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NationalMonumentsPortugal
                                 A QGIS plugin
 This plugin displays Portuguese Monuments' coordinates in the Map
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-05-04
        git sha              : $Format:%H$
        copyright            : (C) 2021 by André Pereira, João Santos
        email                : joao-santos-26@outlook.com
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
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *
import sys
from SPARQLWrapper import *
import pandas as pd
import json 
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .national_monuments_portugal_dialog import NationalMonumentsPortugalDialog
import os.path

endpoint_url = "https://query.wikidata.org/sparql"

query = """#Humans born in New York City
    # that has the property of 'administrative area of' New York City or New York City itself.
    SELECT DISTINCT  ?nome ?coordenadas ?localiza__oLabel ?imagem ?DGPC_ID  WHERE {
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,nl". }
      ?Portugal wdt:P17 wd:Q45.
      OPTIONAL { ?Portugal wdt:P131 ?localiza__o. }
      ?Portugal wdt:P1435 wd:Q908411.
      { ?Portugal wdt:P18 ?imagem. }
      { ?Portugal wdt:P373 ?nome. }
      { ?Portugal wdt:P625 ?coordenadas. }
     OPTIONAL{ ?Portugal wdt:P1702 ?DGPC_ID.}
    }
    ORDER BY DESC (?nome)"""

endpoint_url1 = "https://query.wikidata.org/sparql"

query1 = """SELECT ?nome ?localizado_na_unidade_administrativaLabel ?coordenadas ?data_de_cria__o_ou_funda__o ?p_gina_inicial_oficial ?imagem  WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?museu wdt:P31 wd:Q33506;
    wdt:P17 wd:Q45.
  { ?museu wdt:P373 ?nome. }
  { ?museu wdt:P18 ?imagem. }
  { ?museu wdt:P625 ?coordenadas. }
  OPTIONAL { ?museu wdt:P856 ?p_gina_inicial_oficial. }
  { ?museu wdt:P131 ?localizado_na_unidade_administrativa. }
  OPTIONAL { ?museu wdt:P571 ?data_de_cria__o_ou_funda__o. }
}"""
class NationalMonumentsPortugal:
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
            'NationalMonumentsPortugal_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&National Monuments Portugal')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

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
        return QCoreApplication.translate('NationalMonumentsPortugal', message)


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
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/national_monuments_portugal/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Displays Monuments'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&National Monuments Portugal'),
                action)
            self.iface.removeToolBarIcon(action)

    


    def get_results(self,endpoint_url, query):
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()


    def trat_data(self,results):
      
      content = results["results"]["bindings"]
      #for result in results["results"]["bindings"]:
      #print(content)
      for monumento in content :
        del monumento['nome']['type']
        nome = monumento['nome']['value']
        monumento['nome'] = nome
        del monumento['coordenadas']['datatype']
        del monumento['coordenadas']['type']
        coord =monumento['coordenadas']['value']
        monumento['coordenadas'] = coord
        del monumento['localiza__oLabel']['type']
        del monumento['localiza__oLabel']['xml:lang']
        local =monumento['localiza__oLabel']['value']
        monumento['localiza__oLabel'] = local
        del monumento['imagem']['type']
        img =monumento['imagem']['value']
        monumento['imagem'] = img
        #del monumento['DGPC_ID']['type']
        #monumento['DGPC_ID'] = monumento['DGPC_ID']['value']
        #print(monumento)
        
        if 'DGPC_ID' not in list(monumento.keys()):
          monumento['informação'] = 'http://www.google.com/search?q='+monumento['nome'].replace(" ","%20")
        else:
          del monumento['DGPC_ID']['type']
          monumento['DGPC_ID'] = monumento['DGPC_ID']['value']
          monumento['informação']='http://www.patrimoniocultural.gov.pt/pt/patrimonio/patrimonio-imovel/pesquisa-do-patrimonio/classificado-ou-em-vias-de-classificacao/geral/view/'+monumento['DGPC_ID']
        #del monumento['nome']['value']
        #print(monumento)
      json_data = json.dumps(content)

      with open('https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/monumento.json', 'w') as f:

        f.write(json_data)

      json_file = 'https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/monumento.json'

      df = pd.read_json(json_file)

      df.to_csv('https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/monumento.csv')

    def add_open_street_map(self):

        sources = [layer.source() for layer in QgsProject.instance().mapLayers().values()]
        print(sources)
        source_found = False
        for source in sources:
            if 'xyz&url' in source:
                source_found = True
                print('found')
        if not source_found:
            print('adding')
            urlWithParams = 'type=xyz&url=http://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
            rlayer = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')
            if rlayer.isValid():
                QgsProject.instance().addMapLayer(rlayer)
            else:
                print('invalid layer')
    # adicionar camada a partir dos dados do csv
    def add_layer(self):

          uri = "https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/monumento.csv?encoding={}&delimiter={}&crs=epsg:4723&wktField={}".format("UTF-8",",", "coordenadas")

          vlayer = QgsVectorLayer(uri, "monumentos_nacionais", "delimitedtext")
          #QgsProject.instance().addMapLayer(vlayer)
          path = "https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/pointer.svg"

          symbol = QgsSvgMarkerSymbolLayer(path)
          symbol.setSize(6)
          vlayer.renderer().symbol().changeSymbolLayer(0, symbol )

          # initialize the default symbol for this geometry type
          #symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
          #path = "file:///C:/Users/joao-/OneDrive/Desktop/4ano/2semestre/sig/pratico_mons/pointer.svg"

          #new_symbol = QgsSvgMarkerSymbolLayer(path)
          #new_symbol.setSize(6)
          #vlayer.renderer().symbol().changeSymbolLayer(0, new_symbol)

          # replace default symbol layer with the configured one
          
          QgsProject.instance().addMapLayer(vlayer)

    def get_results1(self,endpoint_url1, query1):
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        # TODO adjust user agent; see https://w.wiki/CX6
        sparql = SPARQLWrapper(endpoint_url1, agent=user_agent)
        sparql.setQuery(query1)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    def trat_data1(self,results):
      
      content = results["results"]["bindings"]
      #for result in results["results"]["bindings"]:
      #print(content)
      for museu in content :
        del museu['nome']['type']
        nome = museu['nome']['value']
        museu['nome'] = nome
        del museu['coordenadas']['datatype']
        del museu['coordenadas']['type']
        coord =museu['coordenadas']['value']
        museu['coordenadas'] = coord
        del museu['localizado_na_unidade_administrativaLabel']['type']
        del museu['localizado_na_unidade_administrativaLabel']['xml:lang']
        local =museu['localizado_na_unidade_administrativaLabel']['value']
        museu['localidade'] = local
        del museu['localizado_na_unidade_administrativaLabel']
        del museu['imagem']['type']
        img =museu['imagem']['value']
        museu['imagem'] = img

        #del monumento['DGPC_ID']['type']
        #monumento['DGPC_ID'] = monumento['DGPC_ID']['value']
        #print(monumento)
        
        if 'p_gina_inicial_oficial' not in list(museu.keys()):
          museu['informação'] =  'http://www.google.com/search?q='+museu['nome'].replace(" ","%20")
        else:
          del museu['p_gina_inicial_oficial']['type']
          museu['p_gina_inicial_oficial'] = museu['p_gina_inicial_oficial']['value']
          museu['informação']=museu['p_gina_inicial_oficial']
          del museu['p_gina_inicial_oficial']


        if 'data_de_cria__o_ou_funda__o' not in list(museu.keys()):
          museu['data_criacao'] =  "Desconhecida"
        else:
          del museu['data_de_cria__o_ou_funda__o']['type']
          museu['data_de_cria__o_ou_funda__o'] = museu['data_de_cria__o_ou_funda__o']['value']
          museu['data_criacao']=museu['data_de_cria__o_ou_funda__o']
          del museu['data_de_cria__o_ou_funda__o']
        #del monumento['nome']['value'
        #print(museu)
      json_data = json.dumps(content)

      with open('https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/museu.json', 'w') as f:

        f.write(json_data)

      json_file = 'https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/museu.json'

      df = pd.read_json(json_file)

      df.to_csv('https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/museu.csv')

    
    # adicionar camada a partir dos dados do csv
    def add_layer1(self):

          uri = "https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/museu.csv?encoding={}&delimiter={}&crs=epsg:4326&wktField={}".format("UTF-8",",", "coordenadas")

          vlayer = QgsVectorLayer(uri, "museus", "delimitedtext")
          #QgsProject.instance().addMapLayer(vlayer)
          path = "https://gitlab.com/andresp99/sig/-/blob/master/NationalMonumentsPortugal/museum.svg"

          symbol = QgsSvgMarkerSymbolLayer(path)
          symbol.setSize(6)
          vlayer.renderer().symbol().changeSymbolLayer(0, symbol )

          # initialize the default symbol for this geometry type
          #symbol = QgsSymbol.defaultSymbol(vlayer.geometryType())
          #path = "file:///C:/Users/joao-/OneDrive/Desktop/4ano/2semestre/sig/pratico_mons/pointer.svg"

          #new_symbol = QgsSvgMarkerSymbolLayer(path)
          #new_symbol.setSize(6)
          #vlayer.renderer().symbol().changeSymbolLayer(0, new_symbol)

          # replace default symbol layer with the configured one
          
          QgsProject.instance().addMapLayer(vlayer)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = NationalMonumentsPortugalDialog()

        # Clear the contents of the comboBox from previous runs
        self.dlg.comboBox.clear()

        # Populate the comboBox with names of all the loaded layers
        self.dlg.comboBox.addItems(['National Monuments', 'Museums','Both'])

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            text = self.dlg.comboBox.currentText()
            if text =='National Monuments' :
                self.add_open_street_map()
                results =self.get_results(endpoint_url,query)
                self.trat_data(results)
                self.add_layer()
            elif text == 'Museums':
                self.add_open_street_map()
                results =self.get_results1(endpoint_url1,query1)
                self.trat_data1(results)
                self.add_layer1()
            else:
                self.add_open_street_map()
                results =self.get_results(endpoint_url,query)
                self.trat_data(results)
                self.add_layer()
                results =self.get_results1(endpoint_url1,query1)
                self.trat_data1(results)
                self.add_layer1()
        print('plugin done')
        