import math
import time
import geohash
import hashlib
import json

def geohashes_from_gps(latitude, longitude, num_chars):

    # This data is used for the 8 char geohashes case
    # Approximates 1m = 1e-05 degrees.
    # This is a ~1m radius circle - we multiple later by the required radius
    lat_offset = [7e-06, 1e-05, 7e-06,
                  0, 0, 0,
                  -7e-06, -1e-05, -7e-06]
    long_offset = [-7e-06, 0, 7e-06,
                   -1e-05, 0, 1e-05,
                   -7e-06, 0, 7e-06]  
    
    start_time = time.time()
    near_geohashes = []
    # Default to MVP1 behaviour: 8 char geohashes
    if num_chars == 9:
        # For 9 char geohashes (5m x 5m, we have to pick up a lot of points to cover a 20m radius)
        geohash_chars = 9
        radius = 18

        # trawl a square 1.2 x radius, at 1m intervals (approximating 1m = 1e-05 degrees)
        # Only include points where distance is < radius (using law of cosines)
        if abs(latitude) < 25:
           h_1m_in_degs = 1e-05
        elif abs(latitude) < 45:
           h_1m_in_degs = 1.3e-05
        elif abs(latitude) < 60:
           h_1m_in_degs = 1.8e-05
        elif abs(latitude) < 70:
           h_1m_in_degs = 2.6e-05
        elif abs(latitude) < 80:
           h_1m_in_degs = 5.2e-05
        elif abs(latitude) < 85:
           h_1m_in_degs = 1e-04
        else:
           # We won't cope perfectly all the way to 90 degrees north but this is good enough.
           h_1m_in_degs = 1e-03

        v_1m_in_degs = 1e-05

        # Geohash square size in degrees will be at least 5*h_1m_in_degs by 5*v_1m_in_degs.
        # Let's ensure we scan at least that frequently.
        h_scan_unit_in_m = 1 * v_1m_in_degs/h_1m_in_degs
        v_scan_unit_in_m = 1
 
        print(h_scan_unit_in_m, v_scan_unit_in_m)
        h_scan_width = int(1.5 * radius / h_scan_unit_in_m)
        v_scan_width = int(1.5 * radius / v_scan_unit_in_m)

        print(h_scan_width, v_scan_width)
        
        # Scale factor converts scan units back to degrees.
        h_scale_factor = h_scan_unit_in_m * h_1m_in_degs
        v_scale_factor = v_scan_unit_in_m * v_1m_in_degs
        
        counter = 0

        for lat_offset in range(- v_scan_width, v_scan_width):
            for long_offset in range(- h_scan_width, h_scan_width):
                # Calculate distance of this point from the central point.
                test_lat = latitude + (lat_offset * v_scale_factor)
                test_long = longitude + (long_offset * h_scale_factor)
                                 
                distance = distance_between_two_points(latitude,
                                                       longitude,
                                                       test_lat,
                                                       test_long)

                if distance < radius:
                    near_geohashes.append(geohash.encode(test_lat,
                                                         test_long)[0:geohash_chars])                

    else:
        geohash_chars = 8
        radius = 10

        for ii in (range(9)):
            near_geohashes.append(geohash.encode(latitude +
                                                 radius * lat_offset[ii],
                                                 longitude +
                                                 radius * long_offset[ii])[0:geohash_chars])

    end_time = time.time()
    print("%s msecs" % int((end_time - start_time) * 1000))
    print("%d hashes" % len(set(near_geohashes)))

    return set(near_geohashes)


def distance_between_two_points(lat_a,
                                long_a,
                                lat_b,
                                long_b):
     
    deltaLong = long_b - long_a;

    p1 = (lat_a * math.pi) / 180;
    p2 = (lat_b * math.pi) / 180;
    deltaLambda = ((long_b - long_a) * math.pi) / 180;
    R = 6371e3; ### gives d in metres
    
    cos_d = (math.sin(p1) * math.sin(p2)) + (math.cos(p1) * math.cos(p2) * math.cos(deltaLambda))
    # Weird bug (Python-only?) sometimes this is > 1.
    # Specifically with 
    # p1 = 0.0017454475853176147
    # p2 = 0.0017454475853176147
    # deltaLambda = 1
    if cos_d > 1:
        cos_d = 1.0

    d = math.acos(cos_d) * R;
    return(d)


# Take a timestampe (in msecs) and create 2 x timestamps rounded to nearest 300 second  s
def timestamps_from_timestamp(timestamp):


    timestamp1 = round(timestamp/300000) * 300000

    if timestamp - timestamp1 > 150000:
        timestamp2 = timestamp1 + 300000
    else:
        timestamp2 = timestamp1
        timestamp1 -= 300000
    
    timestamps = [str(timestamp1), str(timestamp2)]

    return timestamps



def scrypt_hashes(latitude, longitude, timestamp, hash_cost = 12, geohash_chars = 8):
    
    near_geohashes = geohashes_from_gps(latitude, longitude, geohash_chars)
    timestamps = timestamps_from_timestamp(timestamp)

    json_dictionary = {"latitude": latitude,
                       "longitude": longitude,
                       "time": int(timestamp)}
    hashes = []
    
    print("Total number of geohashes:")
    print(len(near_geohashes))
    print("Total number of timestamps:")
    print(len(timestamps))
    print("Total number of hashes to calculate:")
    print(len(timestamps) * len(near_geohashes))

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
            hashes.append(hash_output.hex()) 

            print (t, g, geo_string, hash_output.hex())

    json_dictionary["hashes"] = hashes

    text = json.dumps(json_dictionary, indent=0)
    print(text)






