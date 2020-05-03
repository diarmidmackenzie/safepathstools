import random
import math
import json
import os
import argparse

def gps_data_from_movement_set(movement_set):
    
    gps_data = []
    
    # pick a time for the first offset.
    # Note this is a different algorithm from picking the next offset.
    # Important due to the very uneven distribution of time offsets.
    gps_time = movement_set[0]['time'] + get_first_time_offset()
 
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


            lat_position = point_a['latitude'] + time_interval_portion * latitude_delta
            long_position = point_a['longitude'] + time_interval_portion * longitude_delta
             
            # Now add noise to the point, reflecting inaccuracy of GPS measurement
            (noisy_lat_position, noisy_long_position) = add_location_noise(lat_position, long_position)

            # And add the GPS point ot the list
            gps_point = {'latitude': noisy_lat_position,
                         'longitude': noisy_long_position,
                         'time': gps_time}

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


# Returns list of intersections between two data sets
# But at most one intersectin in set a.
def check_gps_data_for_intersection(gps_set_a,
                                    gps_set_b):
    
    # Default assumption: no intersection
    intersections = []

    for gps_data_a in gps_set_a:
        for gps_data_b in gps_set_b:
            distance = distance_between_two_points(gps_data_a['latitude'],
                                                   gps_data_a['latitude'],
                                                   gps_data_b['longitude'],
                                                   gps_data_b['longitude'])
            if (distance < 20):
                # Two points within 20m
                # Check whether they fall within fours hours.
                if abs(gps_data_a['time'] - gps_data_b['time']) < (3600 * 4):
                    intersections.append([gps_data_a, gps_data_b])

                    # Only count one intersection for each point in the set.
                    break

    return intersections


def distance_between_two_points(lat_a,
                                long_a,
                                lat_b,
                                long_b):
     
     # Length of a degree.  These are for UK - we should be smmarter
     # Units are metres

     p1 = (lat_a * math.pi) / 180;
     p2 = (lat_b * math.pi) / 180;
     deltaLambda = ((long_b - long_a) * math.pi) / 180;
     R = 6371e3; ### gives d in metres
     d = math.acos(math.sin(p1) * math.sin(p2) +
                   math.cos(p1) * math.cos(p2) * math.cos(deltaLambda)) * R;
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
                 iterations,
                 verbose):

    ok_count = 0
    too_few_count = 0
    too_many_count = 0
    none_count = 0

    percent_modifier = iterations/100
    print("\n=======================")
    print("\nTEST RESULTS FOR:" + test_name)
    
    for counter in range(iterations):   
        # Generate a random set of GPS data to match teh movement set
        gps_data_a = gps_data_from_movement_set(movement_set_a)
        gps_data_b = gps_data_from_movement_set(movement_set_b)

        intersections = check_gps_data_for_intersection(gps_data_a, gps_data_b)
        
        if len(intersections) < min_intersections:

            if verbose and too_few_count == 0:
                print("EXAMPLE WITH TOO FEW INTERSECTIONS")
                print_verbose_diags(gps_data_a,
                                    gps_data_b,
                                    intersections)

            too_few_count += 1
             
            # Extra counter in case of no intersections 
            if len(intersections) == 0:
                none_count += 1
            
        elif len(intersections) > max_intersections:
            if verbose and too_many_count == 0:
                print("EXAMPLE WITH TOO MANY INTERSECTIONS")
                print_verbose_diags(gps_data_a,
                                    gps_data_b,
                                    intersections)

            too_many_count += 1
                
        else:
            ok_count += 1

    if verbose: 
        print("\nOVERALL RESULTS FOR:" + test_name)    
    print("Expected intersections: %d to %d" % (min_intersections, max_intersections))
    print("OK:                       " + str(round(ok_count/percent_modifier)) + "%")
    print("None (False Negative):    " + str(round(none_count/percent_modifier)) + "%")
    print("Too Few (False Negative): " + str(round(too_few_count/percent_modifier)) + "%")
    print("Too Many (False Positive):" + str(round(too_many_count/percent_modifier)) + "%")


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
              iterations_input):
    
    global GPS_OFFSETS
    global TIME_INTERVALS 

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
                             iterations,
                             verbose)
            

# Configure the argument parser
parser = argparse.ArgumentParser(description='Test the accuracy of the intersection algorithm.',
                                 epilog='For verbose mode, recommend piping output to a file')

parser.add_argument('--gps',
                    default = "./test_data/gps/gps-offsets.json",
                    help='file to use to reflect noise in GPS data')

parser.add_argument('--times',
                    default = "./test_data/times/time-intervals.json",
                    help='file to use to reflect variations in time intervals')

parser.add_argument('--verbose',
                    action = "store_true",
                    default = False,
                    help='generate detailed data on GPS calculations')                   

parser.add_argument('--test',
                    default = "",
                    help='run one specific test')

parser.add_argument('--iterations',
                    default = 0,
                    help='override number of iterations')

args = parser.parse_args()

run_tests(args.gps,
          args.times,
          args.verbose,
          args.test,
          args.iterations)
