import os
import processing
from qgis.core import *
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsRasterLayer
import csv
import random
#Variables
filepath = "/Users/alexhogan/Desktop/Uni (Geospatial Science/4th Year/Geo Programming/Project/Data/"
inf = 'lga_data2.csv'
vector = 'lgaarea.shp'
lga = 'lgastats.shp'
joined = 'joined.shp'

#import files
vectorLyr = QgsVectorLayer((filepath + vector), vector[:-4], "ogr")
csv_file = QgsVectorLayer(filepath+inf, 'table', 'ogr')

#join files
joindict ={'INPUT':vectorLyr,'FIELD':'ABSLGACODE','INPUT_2':csv_file,'FIELD_2':'LGAcode','METHOD':0,'DISCARD_NONMATCHING':True,'PREFIX':'JOINED','OUTPUT':(filepath+lga)}
processing.run('qgis:joinattributestable',joindict)
lgastats = iface.addVectorLayer((filepath + lga), lga[:-4], "ogr")

#add new field
lgastats.dataProvider().addAttributes([QgsField('65+',QVariant.String)])

lgastats.updateFields()
lgastats.commitChanges()

#fill new field based upon over 65%
features = lgastats.getFeatures()

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
    lgastats.updateFeature(feature)
    lgastats.commitChanges()

#get unique values
fni = lgastats.fields().indexFromName('65+')
unique_ids = lgastats.dataProvider().uniqueValues(fni)
QgsMessageLog.logMessage("sstyle for run layer..." + str(unique_ids))

#assign the colour scheme for unique values
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

#confirms the colour scheme
renderer = QgsCategorizedSymbolRenderer('65+', categories)
# assign the created renderer to the layer
if renderer is not None:
    lgastats.setRenderer(renderer)
lgastats.triggerRepaint()


    
    
    







