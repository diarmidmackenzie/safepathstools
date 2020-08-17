There are various tools in this repo.

Most of the tools are web-based, running in a Python Flask Server.  They have been deployed at [pathcheck.pythonanywhere.com](), and instructions for setting up a similar deployment are available in this repo.

As well as the web tools, we also have some python scripts, intended to be run in a python 3.X environment.



### Web Tools

The key web tools are as follows:

* infection-data
  * Generates a set of infection data at a particular longitude and latitude
  * Can generate data in plain text or hashed (hashes are needed for correct interop with PathCheck GPS solution)
  * Can generate a single page of data, or a "cursor" file that refers to a set of sub-pages
  * In latest versions of the GPS App, this URL cannot be used directly in the App, but this URL can be used by the higher-level yaml URL - see below.
* location-data
  * Generates a set of location data points that can be imported into the GPS Mobile App
  * This URL can be used directly in the Mobile App (under the "Import Location Data" Feature Flag)
* yaml
  * Generates a YAML file containing a number of mock Health Departments, all centered around a particular latitude and longitude
  * This generates a YAML page, which also encodes appropriate infection-data URLs to provide mock data for these HDs
* upload
  * A tool to analyze a JSON location file exported from the GPS Mobile App (using the "Download Locally" Feature Flag)
  * Upload any JSON file locally from your PC for some quick analysis of the contents
  * Particularly useful for assessing data reliability.  Not so useful for assessing accuracy.

In each case, entering the URL with no parameters should provide a brief help page, explaining each of the parameters.

You should see this same page if you enter an illegal value with a parameter, together with an error message intended to help explain what parameter you got wrong.

We also have a 30 minute video explaining these tools in more detail, and how to use them with the PathCheck GPS solution in the PathCheck GPS Confluence pages here: https://pathcheck.atlassian.net/wiki/spaces/TEST/pages/200638489/PathCheck+GPS+Safe+Places+Feature+Flags+Test+Tools+Video


### Python Scripts

##### algorithm-test.py

This runs a stochastic process to estimate the outcomes of a given match algorithm for a GPS-based exposure notification algorithm.

The inputs include:

- A set of movements of two individuals in space / time  - or simply a static distance & duration
- Data files showing representative inaccuracies in collection of GPS data, and in the variations in the time intervals at which GPS data is logged
- Algorithm to use: GPS distance based, or Geohash, with 8 or 9 characters.  Plus sensitivity in terms of accuracy of time match, and how many samples need to be considered to "match" to generate an EN.

Usage details below.

```
usage: algorithm-test.py [-h] [--gps GPS] [--times TIMES] [--verbose] [--geohash] [--chars CHARS] [--samples SAMPLES]
                         [--percent PERCENT] [--exposure EXPOSURE] [--test TEST] [--all] [--distance DISTANCE]
                         [--duration DURATION] [--iterations ITERATIONS] [--radius RADIUS]

Test the accuracy of the intersection algorithm.

optional arguments:
  -h, --help            show this help message and exit
  --gps GPS             file to use to reflect noise in GPS data
  --times TIMES         file to use to reflect variations in time intervals
  --verbose             generate detailed data on GPS calculations
  --geohash             use geohash based matching, rather than GPS points distance
  --chars CHARS         number of chars to use in a geoash. 8 seems sensible
  --samples SAMPLES     number of intersection samples to assess for a notification. 6 = 30 mins is normal
  --percent PERCENT     percentage of samples that must hit an intersection to generate a notification.
  --exposure EXPOSURE   seconds duration within which we calculate an intersection. Was 14400 - now 300.
  --test TEST           run one specific test - use the name of a file in the tests folder
  --all                 Run all tests in tests folder. If "all" or "test" parameter not specified, supply distance &
                        duration
  --distance DISTANCE   Use with duration parameter - run a single test with two static users at a set distance for a
                        specified duration.
  --duration DURATION   Use with distance parameter - run a single test with two static users at a set distance for a
                        specified duration.
  --iterations ITERATIONS
                        override number of iterations
  --radius RADIUS       Radius to use in proximity detection algorithm
```



To run this you will need Python 3.x, and also:

`pip install python-geohash`

On Windows this required me to first install Visual C++ 14.0



Some of the testing results generated using this tool are documented in PathCheck Confluence pages: https://pathcheck.atlassian.net/wiki/spaces/TEST/pages/50823761/Exposure+Detection

The code was initially developed to assess a distance-based GPS match algorithm, looking at a range of different possible movements.  It was then extended to cover a range of geohash-based algorithms.  To test these without bias required some significant changes to the code, including randomizing of position to avoid geohash boundaries (integer lat/long tend to land on geohash boundaries which are non-representative) and to rotate paths in space (purely vertical/horizontal movements are unrealistic when assessing geohash-based algorithms).

Since then, PathCheck focus has moved away from GPS DCT towards GAEN, so I have not invested further in this.

Overall the code is not in a great state.  There is some very basic test code, but anyone wanting to use this code would be well advised to extend the test code to ensure that the code operates correctly in their desired use cases.



##### gpx2json.py

Very simple python script.

Takes a GPX file (e.g. a Google Location takeout) and converts it into a set of PathCheck GPS-format JSON location data files:

- In PathCheck GPS JSON format
- Data points no less than 5 mins apart (denser points are discarded)
- Files of up to 2 weeks duration.
- All times rebased to be over the last 2 weeks at the time of running.

Functional, but immature.  Basic details like input & output filenames are hardcoded.  No test code, but it's been used with real GPX data and seems to work OK.



### A Note on Code Structure

This repo began as a set of 3 independent tools:

- algorithm-test
- flask_server
- json_analysis

(gpx2json came later)

As the set of function I wanted to offer as web tools grew, I ended up making use of code developed for json_analysis & algorithm-test inside the web tools.

Hence the fact that the Flask Server code has to be pulled in from various different directories.

Some refactoring to clearly separate out and package up the common code elements would be nice, but not attempted yet.

