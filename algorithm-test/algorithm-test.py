import algorithmutils
import argparse
            

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

parser.add_argument('--geohash',
                    action = "store_true",
                    default = False,
                    help='use geohash based matching, rather than GPS points distance')                   

parser.add_argument('--chars',
                    default = 8,
                    help='number of chars to use in a geoash.  8 seems sensible')                   

parser.add_argument('--samples',
                    default = 6,
                    help='number of intersection samples to assess for a notification. 6 = 30 mins is normal')                   

parser.add_argument('--percent',
                    default = 66,
                    help='percentage of samples that must hit an intersection to generate a notification.')                   

parser.add_argument('--exposure',
                    default = 300,
                    help='seconds duration within which we calculate an intersection.  Was 14400 - now 300.')                   

parser.add_argument('--test',
                    default = "",
                    help='run one specific test - use the name of a file in the tests folder')

parser.add_argument('--all',
                    action = "store_true",
                    default = False,
                    help='Run all tests in tests folder.  If "all" or "test" parameter not specified, supply distance & duration')  

parser.add_argument('--distance',
                    default = 150,
                    help='Use with duration parameter - run a single test with two static uses at a set distance for a specified duration.')                   

parser.add_argument('--duration',
                    default = 3600,
                    help='Use with distance parameter - run a single test with two static uses at a set distance for a specified duration.')                   

parser.add_argument('--iterations',
                    default = 0,
                    help='override number of iterations')

parser.add_argument('--radius',
                    default = 20,
                    help='Radius to use in proximity detection algorithm')    

args = parser.parse_args()

algorithmutils.run_tests(args.gps,
                         args.times,
                         args.verbose,
                         args.test,
                         args.iterations,
                         args.geohash,
                         args.chars,
                         args.percent,
                         args.samples,
                         args.exposure,
                         args.all,
                         args.distance,
                         args.duration,
                         args.radius)
