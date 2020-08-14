import json
import time

f = open("Location History.json", "r")
data = json.loads(f.read())

points = data["locations"]

TWO_WEEKS_IN_MSECS = 14 * 24 * 60 * 60 * 1000

new_data = []
prev_timestamp = 0
new_file = True
file_index = 0

for ii in range(len(points)):

    timestamp = int(points[ii]["timestampMs"])

    if (new_file):
        file_start_timestamp = timestamp
        file_index += 1
        new_file = False

        # We normalize the data so the last point is right now.
        time_now = int(time.time() * 1000)
        time_2weeks_ago = time_now - TWO_WEEKS_IN_MSECS
        time_offset = time_2weeks_ago - file_start_timestamp
        print("Time offset:" + str(time_offset))

    if (timestamp - file_start_timestamp) > (TWO_WEEKS_IN_MSECS):
        # got 4 weeks of data.
        filename = "location_data" + str(file_index) + ".json"
        write_file = open(filename, "w")

        text = json.dumps(new_data, indent=0)

        write_file.write(text)
        write_file.close()
        new_data = []
        new_file = True

    # Only record points 5 mins apart
    if timestamp - prev_timestamp > 300000:
        offset_timestamp = int(points[ii]["timestampMs"]) + time_offset
        latitude = int(points[ii]["latitudeE7"]) * 10e-08
        longitude = int(points[ii]["longitudeE7"]) * 10e-08

	    new_data.append({'time': offset_timestamp,
	                     'latitude': latitude,
                         'longitude': longitude})

	    prev_timestamp = timestamp


