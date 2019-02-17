# Classifier Evaluator
Used for evaluating classifier prediction from log file with labeled data in database

## How to run
1. Install package requirements 

        pip install -r requirements.txt
        
1. Create a file named `sql_config.py` in the following format

        connection = {
            "user": "USERNAME",
            "password": "PASSWORD",
            "host": "HOST",
            "database": "DATABASE"
        }
        
1. Run the python script  

        $python evalutor.py -h

        usage: evaluator.py [-h] [--threshold [THRESHOLD]] [--loglevel [LOGLEVEL]]
                    [LOGFILE]

        positional arguments:
        LOGFILE               Multiple log files directories separated by space

        optional arguments:
        -h, --help            show this help message and exit
        --threshold [THRESHOLD]
                                Set the distance threshold for evalution (default to
                                be 10, meaning that predictions within 10 px is
                                counted as correct prediction)
        --loglevel [LOGLEVEL]
                                Specify logging level (DEBUG|INFO|WARNING|CRITICAL),
                                default to be INFO

## Configuration
1. Change `DISTANCE_THRESHOLD` for different prediction tolerance (Default to be 10 pixels)

## Log file format

    // VideoFrameName X-coordinate-of-Center Y-coordinate-of-Center
    // Sample
    robot_red_3m_480p_frame513.jpg 460 150

