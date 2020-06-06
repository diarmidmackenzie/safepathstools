from . import app
from flask import request
import json
import time
import random
import geohash
import hashlib
import scrypthash

@app.route('/')
def index():
    return "Hello World!"

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
    
    days = request.args.get('days')
    if days == None:
        days = "1"

    radius = request.args.get('radius')
    if radius == None:	
        radius = "0.00001"
    
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
        
        assert(cases_int >= 1)
        assert(days_int >= 1)

        if cases_int > 10000:
            data_valid = False
            error_text = "For scalability reasons, we don't support more than 10,000 cases yet"

        if days_int > 28:
            data_valid = False
            error_text = "We don't support more than 28 days of data"

        if hash_int > 27:
            data_valid = False
            error_text = "We don't support a Hash Cost over 17 (even with lower hash costs, only 10 seconds of hashes are generated"

    except:
    	data_valid = False
    	print("validation error: cases:" + cases + " days:" + days)
    	error_text = "Days & Cases must be integers > 0,  e.g. cases=3&days=10"


    if (data_valid):
	    text = write_data(cases_int,
	    	              days_int,
	    	              latitude_float,
	    	              longitude_float,
	    	              "Test Authority",
	    	              False,
	    	              radius_float,
                      hash_int)
    else:
	 	# Invalid data - show usage statement
        text = "<center><b><p>PRIVACY WARNING</p><p>IF YOU USE A URL CENTRED ON YOUR CURRENT LOCATION</p>"
        text += "<p>THINK CAREFULLY BEFORE POSTING THAT URL IN PUBLIC (E.G. ON A GITHUB ISSUE)</p>"
        text += "<p>IT MAY BE UNWISE TO PUBLISH YOUR LOCATION ON A PUBLIC FORUM</p></b></center>"
        text += "<p><b>" + error_text + "</b></p>"
        text += "<p>This tool generates a sample data set for a Health Authority, within a certain distance of a specified location<p>"
        text += "<p>URL should be of the form: http://[base URL]/infection-data?longitude=-73.9878584&latitude=40.7484445&cases=2&days=10&radius=0.0001</p>"
        text += "<p>All parameters except longitude & latitude are optional</p>"
        text += "Default values are:"
        text += "<li>Cases: 1</li>"
        text += "<li>Days: 1</li>"
        text += "<li>Radius: 0.0001</li>"
        text += "<li>Hash: 0</li></ul>"
        text += "<p>Radius represents the number of degrees away from the specified latitude and longitude that data points may be generated.</p>"
        text += "<p>Use radius=0 if you want every data point to be recorded at the exact latitude & longitude specified.</p>"
        text += "<p>Note: it is not a true <i>radius</i>.  In fact the area in which data points are placed is square.</p>"
        text += "<p>Hash represents the cost of the Scrypt hash used to encoded hashes of data.</p>"
        text += "<p>Use hash=0 for no hashes.</p>"
        text += "<p>For an app that needs hashes the hash cost must match the hash cost used in the app.</p>"
        text += "<p>Note that the true cost of hashing is 2^N where N is the hash cost.  For N = 16 each hash takes about a second to compute</p>"
        text += "<p>To save CPU on the server, we only output at most 10 seconds worth of hashes, not matter what the overall data size.</p>"
        
        
        
    return (text)


def write_data(cases,
               days,
               latitude,
               longitude,
               authority,
               compress,
               radius,
               hash_cost):

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
     
                  # We only generate hashes for at most 10 seconds' CPU time.
                  # We work backwards, so the most recent data points will be hashed.
                  if (hash_cost > 0) and (hash_timer < time_now + 10):
                      geohash_string = geohash.encode(latitude + lat_delta,longitude + long_delta)[0:8]
                      rounded_time = round(next_timestamp/300) * 300

                      try:
                          hash_output = hashlib.scrypt(bytes(geohash_string + str(rounded_time), 'utf-8'),
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
                          hash_output = scrypthash.scrypt_hash(geohash_string + str(rounded_time),
                                                               "salt",
                                                               n=(2 ** hash_cost),
                                                               r=8,
                                                               p=1,
                                                               dklen=8)

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
                  # SInce we expect that will be most useful.
                  next_timestamp -= 300 * time_multiplier
     json_dictionary = {'authority_name':authority,
                        'publish_date_utc': int(time_now),
                        'info_website': "https://raw.githack.com/tripleblindmarket/safe-places/develop/examples/portal.html",
                        'concern_points':data_rows}
                        
     if hash_cost > 0:
         json_dictionary['concern_point_hashes'] = hash_data_rows

     text = json.dumps(json_dictionary, indent=0)

     return text
