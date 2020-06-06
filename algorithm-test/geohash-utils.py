import math
import geohash

def geohashes_from_gps(latitude, longitude):

	lat_offset = [7e-06, 1e-05, 7e-06,
                  0, 0, 0,
                  -7e-06, -1e-05, -7e-06]
    long_offset = [-7e-06, 0, 7e-06,
                  -1e-05, 0, 1e-05,
                  -7e-06, 0, 7e-06]   

    radius = 10
    near_geohashes = []
            #print(noisy_lat_position, noisy_long_position)
            #print ("9 points...")

            for ii in (range(9)):
                near_geohashes.append(geohash.encode(latitude +
                                                     radius * lat_offset[ii],
                                                    longitude +
                                                     radius * long_offset[ii])[0:geohash_chars])

    return (near_geohashes)
    
