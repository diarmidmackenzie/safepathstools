import random
import math
import json
import os
import geohash

def rotate_movement_set(movement_set, rotation):
    
    # Movement set is rotated in place.  This modifies the supplied bject

    # Rotation is about the poitn (0,0)
    # (x,0) -> (x cos, x sin)
    # (0,y) -> (- y sin, y cos)
    # so x-coord = x cos - y sin
    # y co-ord = x sin + y cos
    
    for ii in range(len(movement_set)):
        x = movement_set[ii]['longitude']
        y = movement_set[ii]['latitude']
        movement_set[ii]['longitude'] = (math.cos(rotation) * x - 
                                         math.sin(rotation) * y)
        movement_set[ii]['latitude'] = (math.sin(rotation) * x + 
                                        math.cos(rotation) * y) 
    #print ("ROTATION BY: " + str(rotation / math.pi))
    #print ("x = " + str(x))
    #print ("y = " + str(y))
    #print ("xcos = " + str(math.cos(rotation) * x))
    #print ("ycos = " + str(math.cos(rotation) * y))
    #print ("xsin = " + str(math.sin(rotation) * x))
    #print ("ysin = " + str(math.sin(rotation) * y))


    #print (movement_set)
    
    return


def gps_data_from_movement_set(base_lat, base_long, movement_set, geohash_chars, radius, rotation):
    
    gps_data = []
    
    # First we rotate the movement set by "rotation"
    rotate_movement_set(movement_set, rotation)

    # pick a time for the first offset.
    # Note this is a different algorithm from picking the next offset.
    # Important due to the very uneven distribution of time offsets.
    gps_time = movement_set[0]['time'] + get_first_time_offset()

    #~Offsets used t compute geohashes
    # NOTE: these are not accurate except near the equator...
    # And at high latitudes, geohashes get so narrow that you may need more than 9 to cover a 20m circle.
    # FOr now we ignore all that.
    # 20m circle  has points at 14m, 20m, 14m (14 = sqrt(2) x 20).
    # 1m = 1e-05
    # So 14m = 1.4e-04
    lat_offset = [7e-06, 1e-05, 7e-06,
                  0, 0, 0,
                  -7e-06, -1e-05, -7e-06]
    long_offset = [-7e-06, 0, 7e-06,
                  -1e-05, 0, 1e-05,
                  -7e-06, 0, 7e-06]   

    # Iterate through each step in the movement set
    for ii in range(len(movement_set) - 1):
        point_a = movement_set[ii]  
        point_b = movement_set[ii + 1]


        # In this step of the movement step, there may be 0, 1 or many GPS points logged

        while (gps_time < point_b['time']):
            # time falls between points A & B.
            # Pick a linear point between
            a_b_time_gap = point_b['time'] - point_a['time']
            gps_time_delta = gps_time - point_a['time']

            latitude_delta = point_b['latitude'] - point_a['latitude']
            longitude_delta = point_b['longitude'] - point_a['longitude']

            time_interval_portion = gps_time_delta / a_b_time_gap

            lat_position = base_lat + point_a['latitude'] + time_interval_portion * latitude_delta
            long_position = base_long + point_a['longitude'] + time_interval_portion * longitude_delta
             
            # Now add noise to the point, reflecting inaccuracy of GPS measurement
            (noisy_lat_position, noisy_long_position) = add_location_noise(lat_position, long_position)

            near_geohashes = []
            #print(noisy_lat_position, noisy_long_position)
            #print ("9 points...")

            for ii in (range(9)):
                near_geohashes.append(geohash.encode(noisy_lat_position +
                                                     radius * lat_offset[ii],
                                                    noisy_long_position +
                                                     radius * long_offset[ii])[0:geohash_chars])
                # print(noisy_lat_position + 100 * lat_offset[ii])
                # print(noisy_long_position + 100 * long_offset[ii])

            # And add the GPS point ot the list
            gps_point = {'latitude': noisy_lat_position,
                         'longitude': noisy_long_position,
                         'geohash_centre': near_geohashes[4],
                         'near_geohashes': near_geohashes,
                         'time': gps_time}
            # print(gps_point)

            gps_data.append(gps_point)

            # Pick the next time at which the user generates a GPS data point.
            gps_time += get_next_time_offset()
     
    # gps_data is now a list of (lat, long, time) triples
    # representing noised points along the movement set.

    return (gps_data)


def add_location_noise(latitude, longitude):
    
    num_choices = len(GPS_OFFSETS)
    noise_choice = int(random.random() * num_choices)
    
    lat_offset = GPS_OFFSETS[noise_choice]['latitude']
    long_offset = GPS_OFFSETS[noise_choice]['latitude']
    
    return (latitude + lat_offset, longitude + long_offset)

def get_first_time_offset():

    # Different logic for 1st time offet
    # We are proportionately more likely to start in a longer offset.
    total_time = 0
    for interval in TIME_INTERVALS:
       total_time += int(interval['time'])

    time_picked = random.random() * total_time

    # Now step through time intervals again until we get beyond the time we picked
    # The difference will be our interval.
    next_log_time = 0
    for interval in TIME_INTERVALS:
        next_log_time += int(interval['time'])
        if next_log_time > time_picked:
            time_offset = next_log_time - time_picked
            break
        
    return (time_offset)


def get_next_time_offset():

    num_choices = len(TIME_INTERVALS)
    time_choice = int(random.random() * num_choices)
    
    interval = TIME_INTERVALS[time_choice]['time']

    return (interval)


def check_gps_data_for_geohash_intersection(gps_set_a,
                                            gps_set_b,
                                            exposure_time):
    
    # Default assumption: no intersection
    intersections = []

    # Assuming all GPS points in roughly the same area, we can set up distance without 
    # For now just assume we are at the equator and 1 degree long or lat = 100km.
    # (most of the test data makes this assumption!)
                  
    for gps_data_a in gps_set_a:
        for gps_data_b in gps_set_b:
            
            # Assume no match
            matching = False
            for ii in (range(len(gps_data_a['near_geohashes']))):
                if gps_data_b['geohash_centre'] == gps_data_a['near_geohashes'][ii]:
                    matching = True
                    break

            if (matching):
                # Two points match at the geohash level.
                # Check whether they fall within 5 mins of each other
                if abs(gps_data_a['time'] - gps_data_b['time']) < exposure_time:
                    intersections.append([gps_data_a, gps_data_b])

                    # Only count one intersection for each point in the set.
                    break
    
    return intersections

def notifications_from_intersections(intersections,
                                     percent_required,
                                     num_samples):
    # Count how many notifications we generate from an intersection
    
    if len(intersections) < 1:
        return 0
    start_time = intersections[0][0]['time']
    end_time = intersections[-1][0]['time']

    # create list of time gaps.
    time_gaps = []
    last_time = 0
    for intersection in intersections:
        this_time = intersection[0]['time']
        if last_time != 0:
            time_gaps.append(this_time - last_time)

        last_time = this_time

    # Now count number of times we get N time gaps in less than M minutes
    # When M = 5 x num_samples 
    # N = (percent_required x num_samples.) - 1
    required = int((percent_required * num_samples)/100)
    time_window = 300 * num_samples
    notification_count = 0

    
    if len(time_gaps) >= required:
        for ii in range(len(time_gaps) - required):
            elapsed_time = 0
            for jj in range(required):
                elapsed_time += time_gaps[jj]

            if elapsed_time < time_window:
                notification_count +=1


    return notification_count  

# Returns list of intersections between two data sets
# But at most one intersectin in set a.
def check_gps_data_for_intersection(gps_set_a,
                                    gps_set_b,
                                    exposure_time,
                                    radius):
    
    # Default assumption: no intersection
    intersections = []

    for gps_data_a in gps_set_a:
        for gps_data_b in gps_set_b:
            distance = distance_between_two_points(gps_data_a['latitude'],
                                                   gps_data_a['longitude'],
                                                   gps_data_b['latitude'],
                                                   gps_data_b['longitude'])
            if (distance < radius):
                # Two points within 20m
                # Check whether they fall within fours hours.
                if abs(gps_data_a['time'] - gps_data_b['time']) < exposure_time:
                    intersections.append([gps_data_a, gps_data_b])

                    # Only count one intersection for each point in the set.
                    break

    return intersections


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
        #print(p1, p2, deltaLambda, cos_d)
        cos_d = 1.0

    d = math.acos(cos_d) * R;
    #print(lat_a)
    #print(long_a)
    #print(lat_b)
    #print(long_b)
    #print(d)

    return(d)

def execute_test(test_name,
                 movement_set_a,
                 movement_set_b,
                 min_intersections,
                 max_intersections,
                 min_notifications,
                 max_notifications,
                 iterations,
                 verbose,
                 geohash,
                 geohash_chars,
                 notify_percent,
                 notify_samples,
                 exposure_time,
                 radius,
                 expected_results):

    ok_count = 0
    too_few_count = 0
    too_many_count = 0
    none_count = 0

    gps_start_points_count = 0
    gps_start_points_near_geohash_count = 0

    notifications_ok_count = 0
    notifications_too_few_count = 0
    notifications_too_many_count = 0
    notifications_none_count = 0
    
    percent_modifier = iterations/100
    print("\n=======================")
    print("\nTEST RESULTS FOR:" + test_name)
    
    for counter in range(iterations):   
        # Generate a random set of GPS data to match the movement set
        # To ensure random position vs geohash positions, we pick a random
        # Base lat & long offset for both A & B 
        # Don't go more than 30 degrees north, because we are using equatorial measurements
        # For our circle of geohashes below - needs improving to go to higher latitudes.
        base_lat = (random.random() - 0.5) * 30
        base_long = (random.random() - 0.5) * 360
        
        rotation = random.random() * math.pi * 2

        gps_data_a = gps_data_from_movement_set(base_lat, base_long, movement_set_a, geohash_chars, radius, rotation)
        gps_data_b = gps_data_from_movement_set(base_lat, base_long, movement_set_b, geohash_chars, radius, rotation)

        gps_start_points_count += 2
        if len(gps_data_a) > 0:
            gps_start_points_near_geohash_count += len(set(gps_data_a[0]['near_geohashes']))
        if len(gps_data_b) > 0:
            gps_start_points_near_geohash_count += len(set(gps_data_b[0]['near_geohashes']))

        if geohash:
            intersections = check_gps_data_for_geohash_intersection(gps_data_a,
                                                                    gps_data_b,
                                                                    exposure_time)
            
        else:
            intersections = check_gps_data_for_intersection(gps_data_a,
                                                            gps_data_b,
                                                            exposure_time,
                                                            radius)
            
        notifications = notifications_from_intersections(intersections,
                                                         notify_percent,
                                                         notify_samples)
        
        if notifications < min_notifications:
            notifications_too_few_count +=1
            
        elif notifications > max_notifications:
            notifications_too_many_count +=1

        else:
            notifications_ok_count +=1
        
        if notifications == 0:
                notifications_none_count +=1


        if len(intersections) < min_intersections:

            if verbose and too_few_count == 0:
                print("EXAMPLE WITH TOO FEW INTERSECTIONS")
                print_verbose_diags(gps_data_a,
                                    gps_data_b,
                                    intersections)

            too_few_count += 1
             
            
        elif len(intersections) > max_intersections:
            if verbose and too_many_count == 0:
                print("EXAMPLE WITH TOO MANY INTERSECTIONS")
                print_verbose_diags(gps_data_a,
                                    gps_data_b,
                                    intersections)

            too_many_count += 1
                
        else:
            ok_count += 1


        # Extra counter in case of no intersections 
        if len(intersections) == 0:
            none_count += 1
            
    if verbose: 
        print("\nOVERALL RESULTS FOR:" + test_name)   

    if (expected_results):
        print("Expected intersections: %d to %d" % (min_intersections, max_intersections))
        print("OK:                       " + str(round(ok_count/percent_modifier)) + "%")
        print("None (False Negative):    " + str(round(none_count/percent_modifier)) + "%")
        print("Too Few (False Negative): " + str(round(too_few_count/percent_modifier)) + "%")
        print("Too Many (False Positive):" + str(round(too_many_count/percent_modifier)) + "%")
        print("NOTIFICATIONS ON " + str(notify_percent) + "%" + " OF ANY " + str(notify_samples) + " CONSECUTIVE RECORDS.")
        print("Expected notifications: %d to %d" % (min_notifications, max_notifications))
        print("OK:                       " + str(round(notifications_ok_count/percent_modifier)) + "%")
        print("None (False Negative):    " + str(round(notifications_none_count/percent_modifier)) + "%")
        print("Too Few (False Negative): " + str(round(notifications_too_few_count/percent_modifier)) + "%")
        print("Too Many (False Positive):" + str(round(notifications_too_many_count/percent_modifier)) + "%")
    else:
        # No specific results expected - just output what happened
        print("Intersections:       " + str(round((iterations - none_count)/percent_modifier)) + "%")
        print("No Intersections:    " + str(round(none_count/percent_modifier)) + "%")
        print("---------------------")
        print("Notifications:       " + str(round((iterations - notifications_none_count)/percent_modifier)) + "%")
        print("No Notifications:    " + str(round(notifications_none_count/percent_modifier)) + "%")
        
    print("Average geohashes:" + str(gps_start_points_near_geohash_count / gps_start_points_count))
            

def print_verbose_diags(gps_data_a,
                        gps_data_b,
                        intersections):
    print("A DATA")
    print(gps_data_a)
    print("B DATA")
    print(gps_data_b)
    print("INTERSECTIONS")
    print(intersections)



def run_tests(gps,
              times,
              verbose,
              test,
              iterations_input,
              geohash,
              chars,
              percent,
              samples,
              exposure,
              all_tests,
              distance,
              duration,
              radius):
    
    global GPS_OFFSETS
    global TIME_INTERVALS 

    if gps == "PERFECT":
        gps = "./test_data/gps/gps-offsets-perfect.json"

    if times == "PERFECT":
        times = "./test_data/times/time-intervals-perfect.json"

    with open(gps, 'r') as gps_file:
       GPS_OFFSETS = json.load(gps_file)
       if (verbose):
           print("Loaded %d GPS offsets" % len(GPS_OFFSETS))
           print(GPS_OFFSETS)

    with open(times, 'r') as times_file:
       TIME_INTERVALS = json.load(times_file)
       if (verbose):
           print("Loaded %d time intervals" % len(TIME_INTERVALS))
           print(TIME_INTERVALS)

    # Movement set is series of trips of lat, long & time (seconds)
    if all_tests or test != "":
        # Run one or more tests from test folder
        TEST_DIR = "./tests"
        for filename in os.listdir(TEST_DIR):
            with open(TEST_DIR + "/" + filename, 'r') as test_file:

                if (test == "") or (test == filename):
                    test_data = json.load(test_file)

                    # Take number of iterations from test data unless explicitly specificed.
                    iterations = int(iterations_input)
                    if iterations == 0:
                        iterations = int(test_data["iterations"])

                    execute_test(test_data["test_name"],
                                 test_data["movement_set_a"],
                                 test_data["movement_set_b"],
                                 test_data["min_intersections"],
                                 test_data["max_intersections"],
                                 test_data["min_notifications"],
                                 test_data["max_notifications"],
                                 iterations,
                                 verbose,
                                 geohash,
                                 int(chars),
                                 int(percent),
                                 int(samples),
                                 int(exposure),
                                 float(radius),
                                 True)
    else:
        # Run a static test with a specified duration and distance
        # pick a random direction
        direction = random.random() * 2 * math.pi
         
        # Assume 1 degree = 100km.  Not quite right, but we haven't picked a position yet!
        # Needs some rework...!
        # Also, this has a huge impact on the outcome, depending on the latitude component
        # need to feed one level lower.
        x_offset = math.sin(direction) * float(distance) / 100000
        y_offset = math.cos(direction) * float(distance) / 100000
        print (x_offset * 100000, y_offset * 100000)

        iterations = int(iterations_input)
        if iterations == 0:
            iterations = 100

        movement_set_a = [{
                        "latitude": 0,
                        "longitude": 0,
                        "time": 0
                },
                {
                        "latitude": 0,
                        "longitude": 0,
                        "time": int(duration)
                }]

        movement_set_b = [{
                        "latitude": x_offset,
                        "longitude": y_offset,
                        "time": 0
                },
                {
                        "latitude": x_offset,
                        "longitude": y_offset,
                        "time": int(duration)
                }]

        test_name = "Static test.  Duration: " + str(duration) + " seconds.  Distance: " + str(distance) + " metres."
        execute_test(test_name,
                     movement_set_a,
                     movement_set_b,
                     0, 0, 0, 0,
                     iterations,
                     verbose,
                     geohash,
                     int(chars),
                     int(percent),
                     int(samples),
                     int(exposure),
                     float(radius),
                     False)
