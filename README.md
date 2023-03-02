# Indoor Wheelchair Navigation Project
### This code builds off of a previous project, found here: https://github.com/hechtej/indoor-nav

Class: CSCI 497T, Winter 2023\
Group Members (Group 1): Ethan Blight, Brady McCoy, Maxwell Dodd, Andrew Luna

## Individual Contributions

### Ethan Blight
## R1
Improved logic for existing backend, including the nested for loop logic in `get_reference()` for setting pixel brightness, and the logic in `analyze_frame()` for subtraction underflow prevention, both in `indoor_nav_gui.py`. Also worked on adding sections and details to the README describing what was added for R1.

## R2
Changed danger calculation to be purely based on distance, and be much more accurate. Cleaned up UI by consolidating everything to one window, adding danger to the warning area, and added the `blobconverter` package for neural network object detection and outlining in the camera view. Also was responsible for the final presentation for the project.
### Brady McCoy
## R1
Created a Figma prototype for our UI design, including the controls for and views for all of our needed features. Also handled the UI guidelines and documentation.

## R2
TODO
### Maxwell Dodd
## R1
Worked on a Pyqt5 GUI that implements our Figma prototype, testing and implementing the needed features.

## R2
TODO
### Andrew Luna
## R1
Also worked on the same Pyqt5 GUI that implements our Figma prototype, and created the initial UI framework in order to make this possible.

## R2
TODO
## Explanation of Implemented Features

### UI
Our implemented features for our UI include a large view for the camera, which shows a warning stop sign for danger values greater than 5, and potential obstacles in black and white, where black objects are expected, and white objects are unexpected. Below this is an indicator of the collision radius, delineating in what range objects will be detected with the current camera angle. Next to this is an area that includes logs about the current location data, such as if a door is detected, and at what time with what distance. Lastly, at the bottom right there is a settings panel that allows the user to adjust various preferences with the program.

An early mockup and final implementation of our UI are given in the UI documentation section below.

### Backend Improvements
The for loop logic for setting each pixel's initial brightness was improved to not use any loops, and instead utilize `numpy` functions including `linspace()` and `tile()` in order to perform this more efficiently. This saves us from iterating through the entire camera height and width in order to set each brightness manually, saving on computation time.

Additionally, the logic for preventing underflow when subtracting `frame` and `referenceFrame` was greatly improved, with a boolean mask being used to know whether to subtract `frame` from `referenceFrame`, or `referenceFrame` from `frame`, and then clipping to 255, requiring no conversion to `int16` types.

## Instructions for Installation
In order to run the camera program, we first need to clone the code repository by running `git clone https://github.com/BradenMccoy/indoor-nav-gui`.

After the repository has been cloned, we can run `sudo apt install python3` in order to install Python in the current environment if it is not yet installed. Use `pip3 install -r requirements.txt` to install the necessary packages for the program to run. Then, just use `cd` to navigate into the repository, and run `python3 indoor_nav_gui.py` to start the program with the depth camera connected via USB.

If done correctly, a window will pop up showing our program UI with the depth camera stream.

## Our UI Documentation

### #1 - Main Page

Our solution is based around assisting the user by supplying additional helpful information about their surroundings, and to this end, we decided that only one page would be necessary. We found that everything users would need could fit into a single screen with room to spare for additions if they are needed. Future work may add additional screens as more features are added.

The main page includes a camera display, a collision indicator, a text based log box, and a settings panel. All of these are clearly displayed and have their own dedicated spaces. **Visibility** was a key guideline considered for these features, notice how much space the camera display takes up to allow for users to clearly see what the camera is seeing. Additionally on the settings menu, we’ve used a large icon to represent "mute", which is **consistent** with other applications and more visible than the other settings because we anticipate it to be the most used.

We will use **feedback** by using both visual and audio indicators on collision warnings, which will make it clear and easy to understand when a collision is imminent. The collision indicator is to further aid in determining the cause of a potential collision, and this simple graphic is used to display a direction and location as an effective visual representation. This exists on top of a stop sign that will appear on screen when a problem is detected, representing high **affordance**, as users will visually recognize this stop sign and be aware of its purpose from other places they have witnessed it. The audio warning will also become higher frequency as the object gets closer, which will serve as the audio counterpart to the collision indicator.

Here is an early mockup of our main page UI:
![image](https://user-images.githubusercontent.com/13970556/219263404-354d13b7-30e5-42de-9ccc-30ce7ede7acd.png)

And here is our final implementation of it working with a connected depth camera:
![python_dyZNHcloZg](https://user-images.githubusercontent.com/55826558/222355730-b4e398e5-d61b-45ad-94bb-dcf2625958ca.png)

No simulated backend was used for this, as a functioning backend was already implemented by the previous team, and was only marginally improved by our work.
