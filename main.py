import sys
import json
import math
import mysql.connector as connector
from mysql.connector import errorcode
from sql_config import connection

logfileNames = sys.argv[1:]

# For evaluating the result of prediction
DISTANCE_THRESHOLD = 10

try:
    # Connect to database
    cnx = connector.connect(**connection)
except connector.Error as err:
    # Code obtain from https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
    exit()

cursor = cnx.cursor()

# Hardcode form name to prevent sql injection
query = "SELECT data FROM object_annotation WHERE image=%s"


for logfileName in logfileNames:
    logfile = open(logfileName)
    right = 0
    totalDist = 0
    logCount = 0
    falsePos = 0
    falseNeg = 0
    notFound = 0

    for line in logfile:
        logCount += 1
        # Line structure: FrameName X-coordinate Y-coordinate
        frameName, x, y = line.split()
        x = eval(x)
        y = eval(y)
        cursor.execute(query, (frameName,))
        try:
            data = cursor.fetchone()[0]
        except TypeError:
            # Not found? Skip to next image
            print("Not found on database:", frameName)
            notFound += 1
            continue
        labels = json.loads(data)
        dist = float("inf")
        for label in labels:
            shapeAttr = label['shape_attributes']
            xlabel = shapeAttr['x'] + shapeAttr['width'] / 2
            ylabel = shapeAttr['y'] + shapeAttr['height'] / 2
            xdist = abs(xlabel - x)
            ydist = abs(ylabel - y)
            # In case of multiple labels in one frame
            # Select the one closest to prediction for evaluation
            dist = min(dist, math.sqrt(xdist**2 + ydist**2))
        if dist == float("inf"):
            # No label, false positive
            print("False positive:", frameName)
            falsePos += 1
            continue
        if dist < DISTANCE_THRESHOLD:
            right += 1
        totalDist += dist

    print("Prediction Result for %s: %f | falsePos (found armor when there is none): %f | Average Distance: %f | Not found: %d | Total frame count: %d" % (logfileName, right / logCount, falsePos / logCount, totalDist / logCount, notFound, logCount))

    logfile.close()
cursor.close()
cnx.close()