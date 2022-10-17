# Frame Manipulation

## Ways of running the program

### 1. python main.py
#### main.py get the configuration from the config file and do this:
#### first, run over every item_dilution frame and create panorama of all the frames
#### then, if delete_frames is true, delete all the frames pictures and save only the panorama
#### second, save the average point the drone was at the time of the scan at average_point.csv

### 2. python main.py [number of frame: int]
#### Gets number of frame and return his picture(if the picture doesn't exist for this frame, write accordingally)

### 3. python main.py [x: float] [y: float] [z: float]
#### Gets point and return this:
#### first, plot all the points as cloud points and mark in red the point we got as input and in green the closest
#### point in the cloud points of the scan.
#### second, create panorama of all the frames that contains the closest point and show it to the user
