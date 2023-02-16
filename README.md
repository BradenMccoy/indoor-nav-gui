## Overview
Link to source code repo: https://github.com/hechtej/indoor-nav

Shows an estimated depth stream from the OAK-D camera.  Based on how much this deviates from a pre-determined average depth, a danger value is calculated which, if it exceeds a certain threshold, may warrant an emergency stop.

Can simply be run with `python3 indoor_nav.py`.  If no camera is connected, the program will crash.

## Setup
```
$ sudo apt install python3
$ sudo apt install virtualenv
 # In a separate folder from the repo #
$ python3 -m virtualenv env
$ source env/bin/activate
 # cd into your repo #
$ pip3 install -r requirements.txt
$ python3 main.py
 # to deactivate virtualenv #
$ deactivate 
```

## Implemented Features
- [X] Installation & Testing of Sensors
- [X] Obstacle Detection
- [X] Danger Bar

## Programming
Look into the depthai and opencv APIs for programming info.

Other, more complicated sample programs with more fancy features are available.  We can look to those for inspiration if we wish.  https://github.com/luxonis/depthai-experiments
