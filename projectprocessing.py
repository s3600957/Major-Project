# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProject,
                       QgsField,
                       QgsFields,
                       QgsMessageLog,
                       QgsSymbol,
                       QgsSimpleFillSymbolLayer,
                       QgsRendererCategory,
                       QgsCategorizedSymbolRenderer)
from qgis.utils import iface
import processing
import csv
import random
import os



class CreateThematicMap(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_SHP = 'INPUT SHAPEFILE'
    INPUT_CSV = 'INPUT CSV'
    OUTPUT = 'OUTPUT'
    

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return CreateThematicMap()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'createthematicmap'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('creates a thematic map of over 65 % in Victoria')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_SHP,
                self.tr('Input Shapefile'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_CSV,
                self.tr('Input CSV'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT_SHP,
            context
        )
        
        sourcecsv = self.parameterAsSource(
            parameters,
            self.INPUT_CSV,
            context
        )

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Send some information to the user
       # feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))
       # chosenFile = self.parameterDefinition('OUTPUT').valueAsPythonString(parameters['OUTPUT'], context)
        #outfilepath = os.path.dirname
        #feedback.pushInfo(outfilepath)
        chosenFile = self.parameterDefinition('OUTPUT').valueAsPythonString(parameters['OUTPUT'], context)
        filepath = os.path.dirname(chosenFile[1:]) + '/'
        feedback.pushInfo(filepath)
        
        


        
        
        joindict ={'INPUT':parameters[self.INPUT_SHP],'FIELD':'ABSLGACODE','INPUT_2':parameters[self.INPUT_CSV],'FIELD_2':'LGAcode','METHOD':0,'DISCARD_NONMATCHING':True,'PREFIX':'JOINED','OUTPUT':'memory'}
        join_layer = processing.run('qgis:joinattributestable',joindict)
        
        layers = self.QgsMapLayerRegistry.instance().mapLayers().values()
        allFeatures = []
        for l in layers:
            for f in l.getFeatures():
                allFeatures.append(f.geometry())
        
        features = join_layer.getFeatures()
        for feature in features:
            new_feature =  QgsFeature()
            # Set geometry to dissolved geometry
            new_feature.setGeometry(f.geometry())
            # Set attributes from sum_unique_values dictionary that we had computed
            new_feature.setAttributes([f[ABSLGACODE], sum_unique_values[f[ABSLGACODE]]])
            sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

        self.OUTPUT.dataProvider().addAttributes([QgsField('65+',QVariant.String)])

        self.OUTPUT.updateFields()
        self.OUTPUT.commitChanges()

        features = self.OUTPUT.getFeatures()

        for feature in features:
            lgastats.startEditing()
            elderly = feature['JOINED65+%']
            old = feature['65+']
            if float(elderly) > 35:
                old= 'VERY HIGH'
            elif float(elderly) > 25:
                old= 'HIGH'
            elif float(elderly) > 20:
                old= 'MEDIUM'
            elif float(elderly) > 15:
                old= 'LOW'
            else: old = 'VERY LOW'
        feature['65+'] = old
        self.OUTPUT.updateFeature(feature)
        self.OUTPUT.commitChanges()

        fni = self.OUTPUT.fields().indexFromName('65+')
        unique_ids = self.OUTPUT.dataProvider().uniqueValues(fni)
        QgsMessageLog.logMessage("sstyle for run layer..." + str(unique_ids))

        categories = []
        for unique_id in unique_ids:
        # initialize the default symbol for this geometry type
            symbol = QgsSymbol.defaultSymbol(lgastats.geometryType())
            symbol.setOpacity(0.5)

            layer_style = {}
            layer_style['color'] = '%d, %d, %d' % (random.randrange(0, 256), random.randrange(0, 256), random.randrange(0, 256))
            layer_style['outline'] = '#000000'
            symbolLayer = QgsSimpleFillSymbolLayer.create(layer_style)

            if symbolLayer is not None:
                symbol.changeSymbolLayer(0, symbolLayer)
            category = QgsRendererCategory(unique_id, symbol, str(unique_id))
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer('65+', categories)
        # assign the created renderer to the layer
        if renderer is not None:
            self.OUTPUT.setRenderer(renderer)
            self.OUTPUT.triggerRepaint()
            
        return {self.OUTPUT: dest_id}
