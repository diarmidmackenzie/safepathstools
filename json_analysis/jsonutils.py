#!/usr/bin/python3
import json
from datetime import datetime, timedelta
import traceback

def analyze_json_file(f):

    try: 
        data = json.loads(f.read())
        text = stats_from_json_data(data)

    except:
        text = "<p>This does not seem to be a valid JSON location data file.\n</p><p>"
        text += "<p>If you think this is a valid JSON location file (as exported from PathCheck GPS), "
        text += "please contact Diarmid Mackenzie on PathCheck Slack with details of the file and this error message:</p><p>"
        text += traceback.format_exc() 
        text += "</p>"

    return text


def stats_from_json_data(data):

    # This code assumes we have JSON data of the following format.
    # Exceptions handled at top-level.
    # [{"latitude":40,"longitude":13,"time":1593553918000},{"latitude":40,"longitude":13,"time":1593554212000}]
    # We also assume the points are in time order.

    start_time = int(data[0]['time'])
    end_time = int(data[-1]['time'])

    start_long = data[0]['longitude']
    start_lat = data[0]['latitude']
    end_long = data[-1]['longitude']
    end_lat = data[-1]['latitude']

    text = "<html><head><script type=\"text/javascript\"  src=\"static\dygraph.js\"></script><link rel=\"stylesheet\" src=\"dygraph.css\" />"
    text += "</head><body>"

    text += overview(data)

    text += data_gap_analysis(data)

    text += visual_graph(data)

    text += "</body></html>"

    return text



def overview(data):

    start_time = int(data[0]['time'] / 1000)
    start_dt = str(datetime.fromtimestamp(start_time))

    end_time = int(data[-1]['time'] / 1000)
    end_dt = str(datetime.fromtimestamp(end_time))

    start_long = str(round(data[0]['longitude'], 3))
    start_lat = str(round(data[0]['latitude'], 3))
    end_long = str(round(data[-1]['longitude'], 3))
    end_lat = str(round(data[-1]['latitude'], 3))

    duration_secs = int(end_time - start_time)
    duration_string = str(timedelta(seconds=duration_secs))

    text = "<p>Trace starts at " + start_dt + " UTC, GPS position: lat: " + start_lat + ", long: " + start_long + "</p>"
    text += "<p>and ends at " + end_dt + " UTC, GPS position: lat: " + end_lat + ", long: " + end_long + "</p>"

    text += "<p>Total duration " + duration_string + "</p>" 

    return(text)


def data_gap_analysis(data):

    # Step through the data calculating time gaps.
    # Metrics we want to compute:
    # % of expeceted number of data points
    # Number of gaps > 6 mins
    # Number of gaps > 9 mins
    # Number of gaps > 14 mins
    # Number of gaps > 29 mins
    # Time, duration and location of longest gap.
    # All output as a nice table.
    # We compute everything in seconds, even though data is in msecs.

    start_time = int(data[0]['time'] / 1000)
    end_time = int(data[-1]['time'] / 1000)
    
    duration = end_time - start_time

    expected_points = int((duration + 300) / 300)
    total_points = len(data)
    percent_of_expected = round(total_points/expected_points, 3) * 100
   
    over_6_mins = 0
    over_9_mins = 0
    over_14_mins = 0
    over_29_mins = 0
    longest_gap = 0
    longest_gap_time = 0

    last_timestamp = 0
    for point in data:
        this_time = int(point['time'] / 1000)
        if (last_timestamp > 0):
            gap = this_time - last_timestamp

            if gap > 360:
                over_6_mins +=1 

            if gap > 540:
                over_9_mins +=1 

            if gap > 840:
                over_14_mins +=1 

            if gap > 1740:
                over_29_mins +=1 
            
            if gap > longest_gap:
                longest_gap = gap
                longest_gap_time = this_time

        last_timestamp = this_time

    text = "<table>"
    text += add_table_row("Number of Points Expected", expected_points, "")
    text += add_table_row("Points Observed", percent_of_expected, " %")
    text += add_table_row("Gaps > 6 mins", over_6_mins, "")
    text += add_table_row("Gaps > 9 mins", over_9_mins, "")
    text += add_table_row("Gaps > 14 mins", over_14_mins, "")
    text += add_table_row("Gaps > 29 mins", over_29_mins, "")
    text += add_table_row("Longest Gap", timedelta(seconds=round(longest_gap,0)), " (HH:MM:SS)")
    text += add_table_row("Longest Gap ended at", str(datetime.fromtimestamp(longest_gap_time)), " UTC")
    
    text += "</table>"

    return(text)


def add_table_row(row_name, value, units):
    text = "<tr><td>" + row_name + "</td><td>" + str(value) + units + "</td></tr>"
    return(text)

def visual_graph(data):
    csv_text = ""
    last_timestamp = 0
    consecutive_points = 0
    for point in data:
        this_time = int(point['time'] / 1000)
        
        if (last_timestamp > 0):
            gap = this_time - last_timestamp
            # If gap is > 6 mins, we insert a gap 5 mins previously, which breaks the line in Dygraph
            if gap > 360:
               #time_text = str(datetime.fromtimestamp(this_time - 300))
               #csv_text += time_text + ",\\n"
               consecutive_points = 0
            else:
                consecutive_points += 1 

        time_text = str(datetime.fromtimestamp(this_time))
        csv_text += time_text + "," + str(consecutive_points) + "\\n"

        last_timestamp = this_time

        # Yes, I know this is ghastly and we should use some templating - but I'm short of time just now.
        # So hacking this in.
        text = "<p>This chart shows where we had consistent points in a row, and where we had gaps.</p>"
        text += "<div id=\"graphdiv\"></div><script type=\"text/javascript\">  g = new Dygraph("
        text += "document.getElementById(\"graphdiv\"),"
        text += "\"Time, Consecutive points\\n"
        text += csv_text
        text += "\",{drawPoints: true, pointSize: 4});"
        text += "</script>"

    return text

        
