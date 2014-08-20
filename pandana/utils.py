from shapely.geometry import Point
from fiona import crs
import geopandas as gpd
import pandas as pd
import numpy as np


def bbox_convert(bbox, from_epsg, to_epsg):
    bbox = gpd.GeoSeries([Point(bbox[0], bbox[1]),
                          Point(bbox[2], bbox[3])],
                         crs=crs.from_epsg(from_epsg))
    bbox = bbox.to_crs(epsg=to_epsg)
    bbox = [bbox[0].x, bbox[0].y, bbox[1].x, bbox[1].y]
    return bbox


def get_nodes_from_osm(bbox, query, to_epsg=3740):
    gdf = gpd.io.osm.query_osm('node',
                               bbox=bbox,
                               tags=query)
    gdf = gdf[gdf.type == 'Point'].to_crs(epsg=to_epsg)
    print "Found %d nodes" % len(gdf)
    x, y = zip(*[(p.x, p.y) for (i, p)
               in gdf.geometry.iteritems()])
    x = pd.Series(x)
    y = pd.Series(y)
    return x, y


def anything_score(net, config, max_distance, decay, bbox):
    score = pd.Series(np.zeros(len(net.node_ids)), index=net.node_ids)
    for query, weights in config.iteritems():
        print "Computing for query: %s" % query
        print "Fetching nodes from OSM"
        x, y = get_nodes_from_osm(bbox, query)
        print "Done"
        net.set_pois(query, x, y)
        print "Computing nearest"
        df = net.nearest_pois(max_distance, query, num_pois=len(weights))
        print "Done"

        for idx, weight in enumerate(weights):
            # want the 1st not the 0th
            idx += 1
            print "Adding contribution %f for number %d nearest" % \
                  (weight, idx)
            score += decay(df[idx])*weight
            # print score.describe()

    assert score.min() > 0
    return score/score.max()*100
