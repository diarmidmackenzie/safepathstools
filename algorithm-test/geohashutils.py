import math
import geohash
import hashlib

def geohashes_from_gps(latitude, longitude):

    lat_offset = [7e-06, 1e-05, 7e-06,
                  0, 0, 0,
                  -7e-06, -1e-05, -7e-06]

    long_offset = [-7e-06, 0, 7e-06,
                   -1e-05, 0, 1e-05,
                   -7e-06, 0, 7e-06]  

    radius = 10
    geohash_chars = 8
    near_geohashes = []

    for ii in (range(9)):
        near_geohashes.append(geohash.encode(latitude +
                                             radius * lat_offset[ii],
                                             longitude +
                                             radius * long_offset[ii])[0:geohash_chars])

    return set(near_geohashes)

# Take a timestampe (in msecs) and create 2 x timestamps rounded to nearest 300 seconds
def timestamps_from_timestamp(timestamp):


    timestamp1 = round(timestamp/300000) * 300000

    if timestamp - timestamp1 > 150000:
        timestamp2 = timestamp1 + 300000
    else:
        timestamp2 = timestamp1
        timestamp1 -= 300000
    
    timestamps = [str(timestamp1), str(timestamp2)]

    return timestamps



def scrypt_hashes(latitude, longitude, timestamp, hash_cost = 12):
    
    near_geohashes = geohashes_from_gps(latitude, longitude)
    timestamps = timestamps_from_timestamp(timestamp)

    for t in timestamps:
        for g in near_geohashes:
            geo_string = g + t
            hash_output = hashlib.scrypt(bytes(geo_string, 'utf-8'),
                                         salt=bytes("salt",'utf-8'),
                                         n=(2 ** hash_cost),
                                         r=8,
                                         p=1,
                                         maxmem=(((2 ** hash_cost) * 8 * 128) + 3072),
                                         dklen=8)


            print (t, g, geo_string, hash_output.hex())







