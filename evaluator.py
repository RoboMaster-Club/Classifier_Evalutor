import sys
import json
import math
import logging
import argparse
import mysql.connector as connector
from mysql.connector import errorcode
from sql_config import connection

# Parsing commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument("--threshold", help="Set the distance threshold for \
    evalution (default to be 10, meaning that predictions within 10 px is counted)",
    type=float, nargs="?", default=10)
parser.add_argument("--loglevel", nargs="?", help="Specify logging level (DEBUG|INFO|WARNING|CRITICAL), default to be INFO", default="INFO")
parser.add_argument("LOGFILE", help="Multiple log files directories separated by space", nargs="+")
parser.add_argument("--output", nargs="?", help="Store logging output into this file")
args = parser.parse_args()


logfileNames = args.LOGFILE
# For evaluating the result of prediction
DISTANCE_THRESHOLD = args.threshold

numeric_level = getattr(logging, args.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % args.loglevel)
if args.output:
    logging.basicConfig(level=numeric_level, filename=args.output, filemode='w')
else:
    logging.basicConfig(level=numeric_level)

try:
    # Connect to database
    cnx = connector.connect(**connection)
except connector.Error as err:
    # Code obtain from https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        logging.error("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        logging.error("Database does not exist")
    else:
        logging.error(err)
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
            logging.debug("Not found on database:", frameName)
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
            logging.debug("False positive:", frameName)
            falsePos += 1
            continue
        if dist < DISTANCE_THRESHOLD:
            right += 1
        totalDist += dist

    logging.info("Prediction Result for %10s: %f | falsePos (found armor when there is none): %.4f | Average Distance: %.4f | Not found: %d | Correct frame count: %d | Total frame count: %d" 
          % (logfileName, right / logCount, falsePos / logCount, totalDist / logCount, notFound, right, logCount))
    logfile.close()
cursor.close()
cnx.close()
