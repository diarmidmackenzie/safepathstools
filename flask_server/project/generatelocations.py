import json
import time
import random
import geohashutils
import scrypthash

def write_location_data(num_points,
                        start_latitude,
                        start_longitude,
                        walk_step):
               

    gps_dps = 12
    time_multiplier = 1000

    data_rows = []
    time_now = time.time()
    base_time = time_now - (num_points * 300)
    latitude = start_latitude
    longitude = start_longitude
    next_timestamp = int(base_time) * time_multiplier

    for point in range(num_points):     
        lat_delta = (random.random() - 0.5) * (walk_step * 2)
        long_delta = (random.random() - 0.5) * (walk_step * 2)

        latitude += lat_delta
        longitude += long_delta

        if num_points < 288:
            # For < 1 day of data we use real hashes.
            # For >= 1 day we use fake hashes (which mean that Exposure Notifications won't work)
            # Default is 1 day (288 points) and uses fake hashes, so we don't spend the CPU cycles
            # by default.
            hashes = real_hashes(latitude, longitude, next_timestamp)
        else:
            hashes = fake_hashes()

        data_rows.append({'time': next_timestamp,
                         'latitude': round(latitude, gps_dps),
                         'longitude':round(longitude,gps_dps),
                         'hashes': hashes})
                  
        next_timestamp += 300 * time_multiplier

    text = json.dumps(data_rows, indent=0)

    return text


def fake_hashes():
    # Generating hashes is time consuming.  This function generates a random set of 4-6 fake (random) hashes.
    # These will mean that testing of Exposure Notifications performance will be realistic, even though the ENs themselves won't trigger.

    # Average number of hashes is 4.6
    # Will typically be 4 or 6 (2 or 3 geohashes x 2 timestamps)
    if random.random() > 0.7:
        num_hashes = 6
    else:
        num_hashes = 4

    hashes = []
    for ii in range(num_hashes):
        hashes.append(random_hash())

    return(hashes)


def random_hash():
    # Returns a random 16 character hashes

    hash_value = int(random.random() * (2 ** 64))
    hash_string = hex(hash_value)
    return hash_string


def real_hashes(latitude, longitude, timestamp):
    # This code is similar to code in geohashutils - would be nice to communalize but I'm in a hurry.
    # This code is not cheap to run due to hash cost, so use sparingly.
    near_geohashes = geohashutils.geohashes_from_gps(latitude, longitude, 8)
    timestamps = geohashutils.timestamps_from_timestamp(timestamp)
    hash_cost = 12

    hashes = []
    
    for t in timestamps:
        for g in near_geohashes:
            encode_string = g + t
            try:
                hash_output = hashlib.scrypt(bytes(encode_string, 'utf-8'),
                                             salt=bytes("salt",'utf-8'),
                                             n=(2 ** hash_cost),
                                             r=8,
                                             p=1,
                                             maxmem=(((2 ** hash_cost) * 8 * 128) + 3072),
                                             dklen=8)
            except:
                # If the platform doesn't have OpenSSL 1.1 (e.g. Python Anywhere) we can't use hashlib
                # Instead we use a custom python module that calls through to a scrypt linux binary
                # This one: https://github.com/jkalbhenn/scrypt
                # This version just takes strings, not byte arrays, and has no maxmem parameter
                hash_output = scrypthash.scrypt_hash(encode_string,
                                                     "salt",
                                                     n=(2 ** hash_cost),
                                                     r=8,
                                                     p=1,
                                                     dklen=8)
            hashes.append(hash_output.hex()) 

    return hashes
