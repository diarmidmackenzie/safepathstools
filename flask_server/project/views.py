from . import app
from flask import Flask, render_template, request
import json
import time
import random
import geohash
import hashlib
import scrypthash
import urllib
import jsonutils
import generatelocations

@app.route('/upload')
def upload_json():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def json_uploader():
   if request.method == 'POST':
      f = request.files['file']
      text = jsonutils.analyze_json_file(f)
      return text

@app.route('/')
def index():
    text = "<h1>Test tools for PathCheck GPS Digital Contact Tracing Solution</h1><p></p>"
    text += "For more details see <a href=\"https://github.com/diarmidmackenzie/safepathstools/blob/master/Documentation.md\">"
    text += "this page</a>."
    return text

@app.route('/location-data')
def locations():
    # Start assuming data valid& set defaults.
    data_valid = True

    longitude = request.args.get('longitude')
    if longitude == None:
      longitude = "error"

    latitude = request.args.get('latitude')
    if latitude == None:
        latitude = "error"

    points = request.args.get('points')
    if points == None:
        points = "10"

    step = request.args.get('step')
    if step == None:
        step = "1e-10"

    try:
        latitude_float = float(latitude)
        longitude_float = float(longitude)
    except:
        data_valid = False
        error_text = "Latitude and Longitude must be decimal numbers, e.g. longitude=-73.9878584&latitude=40.7484445"

    try:
        walk_step_float = float(step)
    except:
        data_valid = False
        error_text = "Step should be a decimal number, indicating the random step size on each data point."

    try:
        points_int = int(points)
        assert(points_int >= 1)
        assert(points_int <= 8000)
    except:
        data_valid = False
        error_text = "points must be an integer from 1 to 8000"

    if (data_valid):
        text = generatelocations.write_location_data(points_int,
                                                     latitude_float,
                                                     longitude_float,
                                                     walk_step_float)
    else:
      # Invalid data - show usage statement
        text = "<center><b><p>PRIVACY WARNING</p><p>IF YOU USE A URL CENTRED ON YOUR CURRENT LOCATION</p>"
        text += "<p>THINK CAREFULLY BEFORE POSTING THAT URL IN PUBLIC (E.G. ON A GITHUB ISSUE)</p>"
        text += "<p>IT MAY BE UNWISE TO PUBLISH YOUR LOCATION ON A PUBLIC FORUM</p></b></center>"
        text += "<p><b>" + error_text + "</b></p>"
        text += "<p>This tool generates a set of N location points, on a random walk from a specified latitude and longitude.<p>"
        text += "<p>Points are generated every 5 mins, starting in the past, and finishing at this moment.<p>"
        text += "<p>URL should be of the form: http://[base URL]/location-data?longitude=-73.9878584&latitude=40.7484445&points=4000</p>"
        text += "<p>step is an optional parameter that leads to a random walk.  If not specified all points are very close together, but not identical (step=1e-10)</p>"
        text += "<p>step is a number of degrees that the position may move with each successive point.  Try 1e-5 for example for a bit more movement</p>"
        text += "<p>if you want no movement at all, explicitly specify step=0</p>"
        text += "<p>Note that lat/long are only output to 12dp, if you use smaller steps than 1e-10, you'll end up with many exactly matching points</p>"


    return (text)


@app.route('/infection-data')
def infections():
    longitude = request.args.get('longitude')
    if longitude == None:
    	longitude = "error"

    latitude = request.args.get('latitude')
    if latitude == None:
        latitude = "error"

    cases = request.args.get('cases')
    if cases == None:
        cases = "1"

    hash_cost = request.args.get('hash')
    if hash_cost == None:
        hash_cost = "0"

    pages = request.args.get('pages')
    if pages == None:
        pages = "0"

    days = request.args.get('days')
    if days == None:
        days = "1"

    radius = request.args.get('radius')
    if radius == None:
        radius = "0.00001"

    notification_threshold_percent = request.args.get('notification_threshold_percent')
    if notification_threshold_percent == None:
        notification_threshold_percent = "66"

    notification_threshold_timeframe = request.args.get('notification_threshold_timeframe')
    if notification_threshold_timeframe == None:
        notification_threshold_timeframe = "30"

    # Start assuming data valid.& set dedaults.
    data_valid = True

    try:
    	latitude_float = float(latitude)
    	longitude_float = float(longitude)
    except:
    	data_valid = False
    	error_text = "Latitude and Longitude must be decimal numbers, e.g. longitude=-73.9878584&latitude=40.7484445"

    try:
    	radius_float = float(radius)
    except:
    	data_valid = False
    	error_text = "Radius must be a decimal number, e.g. radius=0.0001"

    try:
        cases_int = int(cases)
        days_int = int(days)
        hash_int = int(hash_cost)
        pages_int = int(pages)
        notification_threshold_percent_int = int(notification_threshold_percent)
        notification_threshold_timeframe_int = int(notification_threshold_timeframe)

        assert(cases_int >= 1)
        assert(days_int >= 1)

        if cases_int > 10000:
            data_valid = False
            error_text = "For scalability reasons, we don't support more than 10,000 cases yet"

        if days_int > 28:
            data_valid = False
            error_text = "We don't support more than 28 days of data"

        if hash_int > 17:
            data_valid = False
            error_text = "We don't support a Hash Cost over 17 (even with lower hash costs, only 10 seconds of hashes are generated"

        if pages_int > 28:
            data_valid = False
            error_text = "We don't support more than 28 pages."
    except:
    	data_valid = False
    	print("validation error: cases:" + cases + " days:" + days)
    	error_text = "Days & Cases must be integers > 0,  e.g. cases=3&days=10.  Hash, Pages & Notification params must be integers."

    if (data_valid):
      if (pages_int == 0):
  	    text = write_data(cases_int,
  	    	                days_int,
    	    	              latitude_float,
    	    	              longitude_float,
    	    	              "TestAuthority",
    	    	              False,
    	    	              radius_float,
                          hash_int,
                          notification_threshold_percent_int,
                          notification_threshold_timeframe_int)
      else:
        text = write_cursor_file(cases_int,
                                 days_int,
                                 latitude_float,
                                 longitude_float,
                                 "TestAuthority",
                                 radius_float,
                                 hash_int,
                                 pages_int,
                                 notification_threshold_percent_int,
                                 notification_threshold_timeframe_int)
    else:
	 	# Invalid data - show usage statement
        text = "<center><b><p>PRIVACY WARNING</p><p>IF YOU USE A URL CENTRED ON YOUR CURRENT LOCATION</p>"
        text += "<p>THINK CAREFULLY BEFORE POSTING THAT URL IN PUBLIC (E.G. ON A GITHUB ISSUE)</p>"
        text += "<p>IT MAY BE UNWISE TO PUBLISH YOUR LOCATION ON A PUBLIC FORUM</p></b></center>"
        text += "<p><b>" + error_text + "</b></p>"
        text += "<p>This tool generates a sample data set for a Health Authority, within a certain distance of a specified location<p>"
        text += "<p>URL should be of the form: http://[base URL]/infection-data?longitude=-73.9878584&latitude=40.7484445&cases=2&days=10&radius=0.0001</p>"
        text += "<p>All parameters except longitude & latitude are optional</p>"
        text += "<p>Other possible parameters: hash, pages, notification_threshold_percent, notification_threshold_timeframe</p>"
        text += "Default values are:"
        text += "<li>Cases: 1</li>"
        text += "<li>Days: 1</li>"
        text += "<li>Radius: 0.0001</li>"
        text += "<li>Hash: 0</li></ul>"
        text += "<li>Pages: 0</li></ul>"
        text += "<li>:Notification Threshold Percent: 66</li></ul>"
        text += "<li>:Notification Threshold Time: 30</li></ul>"

        text += "<p>Radius represents the number of degrees away from the specified latitude and longitude that data points may be generated.</p>"
        text += "<p>Use radius=0 if you want every data point to be recorded at the exact latitude & longitude specified.</p>"
        text += "<p>Note: it is not a true <i>radius</i>.  In fact the area in which data points are placed is square.</p>"
        text += "<p>Hash represents the cost of the Scrypt hash used to encoded hashes of data.</p>"
        text += "<p>Use hash=0 for no hashes.</p>"
        text += "<p>For an app that needs hashes the hash cost must match the hash cost used in the app.</p>"
        text += "<p>Note that the true cost of hashing is 2^N where N is the hash cost.  For N = 16 each hash takes about a second to compute</p>"
        text += "<p>To save CPU on the server, we only output at most 10 seconds worth of hashes, not matter what the overall data size.</p>"
        text += "<p>Pages > 0 will result in the initial page being served as a cursor file, with URL references to sub-pages.</p>"
        text += "<p>Every pages is populated as per the initial parameters, so pages=10 will generate 10x as much data in total.</p>"
        text += "<p></p>"
        text += "<p><b>Some Examples</b></p>"
        text += "<table><tr><td>(original version of app) Single data file, plain text</td><td>?longitude=1&latitude=2</td></tr>"
        text += "<tr><td>Single data file with hashes at cost = 12</td><td>?longitude=1&latitude=2&hash=12</td></tr>"
        text += "<tr><td>(standard for MVP1) Multiple datas file with hashes at cost = 12</td><td>?longitude=1&latitude=2&hash=12&pages=3</td></tr></table>"

    return (text)


@app.route('/yaml')
def hds():

    # Start assuming data valid.& set defaults.
    data_valid = True

    longitude = request.args.get('longitude')
    if longitude == None:
      longitude = "error"

    latitude = request.args.get('latitude')
    if latitude == None:
        latitude = "error"

    hds = request.args.get('hds')
    if hds == None:
        hds = "error"

    try:
      latitude_float = float(latitude)
      longitude_float = float(longitude)
    except:
      data_valid = False
      error_text = "Latitude and Longitude must be decimal numbers, e.g. longitude=-73.9878584&latitude=40.7484445"

    try:
        hds_int = int(hds)
        assert(hds_int >= 1)
    except:
        data_valid = False
        error_text = "Health Departments (hds) must be an integer > 0\n"

    if (data_valid):
        text = "authorities:\n"
        for ii in range(hds_int):
            # Probably want some more sophistictaed pattern here...
            # This gives n^3 data, i.e. 1x, 8x, 27x, 64x etc.
            pages = ii + 1
            cases = ii + 1
            days = ii + 1
            org_id = "Org" + str(ii)
            text += write_hd(org_id, pages, cases, days, latitude_float, longitude_float, 0, 66, 1)
    else:
        text = "<center><b><p>PRIVACY WARNING</p><p>IF YOU USE A URL CENTRED ON YOUR CURRENT LOCATION</p>"
        text += "<p>THINK CAREFULLY BEFORE POSTING THAT URL IN PUBLIC (E.G. ON A GITHUB ISSUE)</p>"
        text += "<p>IT MAY BE UNWISE TO PUBLISH YOUR LOCATION ON A PUBLIC FORUM</p></b></center>"
        text += "<p><b>" + error_text + "</b></p>"
        text += "<p>This tool generates a set of Health Departments in your location<p>"
        text += "<p>URL should be of the form: http://[base URL]/yaml?longitude=-73.9878584&latitude=40.7484445&hds=2</p>"
        text += "<p>The hds parameter defines the number of Health Departments to be created.</p>"
        text += "<p>The 1st HD will be created to server 1 page, with 1 day of data for 1 case.</p>"
        text += "<p>The 2nd HD will be created to server 2 pages, with 2 day of data for 2 cases.</p>"
        text += "<p>And so on...</p>"
        text += "<p>If you create 10 HDs, the 10th HD will server 10 pages of data, each with 10 cases for 10 days.</p>"
        text += "<p>With 288 data points per day, that's 288 x 10 x 10 x 10 = 288k data points.</p>"
        text += "<p>So this can be useful for scale testing!</p>"
        text += "<p>If you want to test a very large number of HDs, e.g. 100 or more, that's fine...</p>"
        text += "<p>... but if you subscribe to the HA, the App will try to download 288M data points...</p>"
        text += "<p>... so maybe don't actually subscribe to those, unless you specifically want to test extreme load.</p>"

    return text


def write_hd(org_id,
             pages,
             cases,
             days,
             latitude,
             longitude,
             radius,
             notification_threshold_percent,
             notification_threshold_timeframe):

    cursor_url = "diarmidmackenzie.pythonanywhere.com/infection-data?"
    cursor_url += "latitude=" + str(latitude)
    cursor_url += "&longitude=" + str(longitude)
    cursor_url += "&hash=12"
    cursor_url += "&pages=" + str(pages)
    cursor_url += "&cases=" + str(cases)
    cursor_url += "&days=" + str(days)
    cursor_url += "&radius=" + str(radius)
    cursor_url += "&notification_threshold_percent=" + str(notification_threshold_percent)
    cursor_url += "&notification_threshold_timeframe=" + str(notification_threshold_timeframe)

    authority = "Custom Test HD"
    authority += " P" + str(pages)
    authority += " C" + str(cases)
    authority += " D" + str(days)

    text = "- name: " + authority + "\n"
    text += "  bounds:\n"
    text += "    ne:\n"
    text += "      latitude: " + str(latitude + 1) + "\n"
    text += "      longitude: " + str(longitude + 1)  + "\n"
    text += "    sw:\n"
    text += "      latitude: " + str(latitude - 1)  + "\n"
    text += "      longitude: " + str(longitude - 1)  + "\n"
    text += "  org_id: " + org_id + "\n"
    text += "  public_api: https://doesnotexist\n"
    text += "  cursor_url: \"https://" + cursor_url + "\"\n"

    return text

def write_data(cases,
               days,
               latitude,
               longitude,
               authority,
               compress,
               radius,
               hash_cost,
               notification_threshold_percent,
               notification_threshold_timeframe):

     if (compress):
         gps_dps = 5
         time_multiplier = 1
     else:
         gps_dps = 8
         time_multiplier = 1000

     data_rows = []
     hash_data_rows = []
     time_now = time.time()
     base_time = time_now

     for case in range(cases):
          next_timestamp = int(base_time) * time_multiplier
          for day in range(days):
              for time_delta in range(288): # 12 logs / hour, 24 hours/day
                  lat_delta = (random.random() - 0.5) * (radius * 2)
                  long_delta = (random.random() - 0.5) * (radius * 2)

                  hash_timer = time.time()

                  # We only generate hashes for at most 20 seconds' CPU time.
                  # We work backwards, so the most recent data points will be hashed.
                  if (hash_cost > 0) and (hash_timer < time_now + 20):
                      geohash_string = geohash.encode(latitude + lat_delta,longitude + long_delta)[0:8]
                      rounded_time = round(next_timestamp/300000) * 300000

                      encode_string = geohash_string + str(rounded_time)
                      print("Encoding string: %s" % encode_string)

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

                      print("Resulting hash: %s" % hash_output.hex())
                      hash_data_rows.append(hash_output.hex())

                  if (compress):
                      data_rows.append({'y': round(latitude + lat_delta, gps_dps),
                                        'x': round(longitude + long_delta,gps_dps),
                                        't':next_timestamp})
                  else:
                      data_rows.append({'time':next_timestamp,
                                        'longitude':round(longitude + long_delta,gps_dps),
                                        'latitude': round(latitude + lat_delta, gps_dps)})

                  # Note, data is generated backwards, so that the data points for which we produce hashes will be the most recent
                  # Since we expect that will be most useful.
                  next_timestamp -= 300 * time_multiplier

     json_dictionary = {'version': '1.0',
                       'authority_name':authority,
                       'publish_date_utc': int(time_now),
                       'info_website_url': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                       'api_endpoint_url': "https://diarmidmackenzie.pythonanywhere.com",
                       'privacy_policy_url': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                       'reference_website_url': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                       'notification_threshold_percent': notification_threshold_percent,
                       'notification_threshold_timeframe': notification_threshold_timeframe,
                       'authority_name':authority}

     if hash_cost > 0:
         json_dictionary['concern_point_hashes'] = hash_data_rows
     else:
         json_dictionary['concern_points'] = data_rows

     text = json.dumps(json_dictionary, indent=0)

     return text

def write_cursor_file(cases,
                      days,
                      latitude,
                      longitude,
                      authority,
                      radius,
                      hash_cost,
                      pages,
                      notification_threshold_percent,
                      notification_threshold_timeframe):

    pages_data = []
    time_now = int(time.time()) * 1000
    base_time = time_now - (pages * 1000)

    url_string = "https://diarmidmackenzie.pythonanywhere.com/infection-data?"
    url_string += "latitude=" + str(latitude)
    url_string += "&longitude=" + str(longitude)
    url_string += "&authority=" + authority
    url_string += "&radius=" + str(radius)
    url_string += "&hash=" + str(hash_cost)
    url_string += "&cases=" + str(cases)
    url_string += "&days=" + str(days)
    url_string += "&notification_threshold_percent=" + str(notification_threshold_percent)
    url_string += "&notification_threshold_timeframe=" + str(notification_threshold_timeframe)

    for ii in range(pages):
      start_time = base_time + (ii * 1000)
      end_time = start_time + 999
      pages_data.append({'id': str(start_time) + "_" + str(end_time),
                         'startTimestamp': start_time,
                         'endTimestamp': end_time,
                         'filename': url_string})

    json_dictionary = {'version': '1.0',
                       'authority_name':authority,
                       'publish_date_utc': int(time_now),
                       'info_website_url': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                       'api_endpoint_url': "https://diarmidmackenzie.pythonanywhere.com",
                       'privacy_policy_url': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                       'reference_website_url': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                       'notification_threshold_percent': notification_threshold_percent,
                       'notification_threshold_timeframe': notification_threshold_timeframe,
                       'pages': pages_data}

    text = json.dumps(json_dictionary, indent=0)

    return text
