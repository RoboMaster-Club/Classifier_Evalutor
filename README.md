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

        python main.py LOGFILE1 LOGFILE2 LOGFILE3

## Configuration
1. Change `DISTANCE_THRESHOLD` for different prediction tolerance (Default to be 10 pixels)

## Log file format

    // VideoFrameName X-coordinate-of-Center Y-coordinate-of-Center
    // Sample
    robot_red_3m_480p_frame513.jpg 460 150

