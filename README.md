# Indoor Wheelchair Navigation Project
### This code builds off of a previous project, found here: https://github.com/hechtej/indoor-nav

Class: CSCI 497T, Winter 2023\
Group Members (Group 1): Ethan Blight, Brady McCoy, Maxwell Dodd, Andrew Luna

## Individual Contributions

### Ethan Blight
## R1
Improved logic for existing backend, including the nested for loop logic in `get_reference()` for setting pixel brightness, and the logic in `analyze_frame()` for subtraction underflow prevention, both in `indoor_nav_gui.py`. Also worked on adding sections and details to the README describing what was added for R1.

## R2
Changed danger calculation to be purely based on distance, and be much more accurate, (later changed to be depth-based by Max). Cleaned up UI by consolidating everything to one window, adding danger to the warning area, and added the `blobconverter` package for neural network object detection and outlining in the camera view. Also was responsible for creating the final presentation for the project, and adding sections and details to the README describing what was added for R1.

### Brady McCoy
## R1
Created a Figma prototype for our UI design, including the controls and views for all of our needed features. Also handled the UI guidelines and documentation.

## R2
Added finishing touches to our final presentation, and recorded a video of it. Also helped facilitate our usability evaluation session.

### Maxwell Dodd
## R1
Worked on a Pyqt5 GUI that implements our Figma prototype, testing and implementing the needed features.

## R2
Implemented a depth system to detect objects at a given distance away from the camera, ranging from 0 to 255, and issuing warnings at a value less than or equal to the minimum depth. This replaced the old danger system which computed a value ranging from 0 to 10 from a given frame of camera output. Also recorded a final demo of our software.

### Andrew Luna
## R1
Also worked on the same Pyqt5 GUI that implements our Figma prototype, and created the initial UI framework in order to make this possible.

## R2
Added a minimum depth slider for this value to be adjusted by the user, and added the ability to customize the sound for collision warnings in the program via a button.

## Explanation of Implemented Features

### UI
Our implemented features for our UI include a large view for the camera, which shows a warning symbol below it for danger depth values greater than the minimum depth, as determined by the depth slider, and potential obstacles outlined using neural network technology. A warning sound is optionally played when the danger value is great enough, as shown near the warning symbol. Next to this is an area that includes logs altering users if they are about to collide with an obstacle, such as a door, wall, or trash can. Lastly, at the bottom right there are settings that allows the user to adjust various preferences with the program, including muting the collision warnings, changing the sound, and adjusting the minimum depth.

An early mockup and final implementation of our UI are given in the UI documentation section below.

### Backend Improvements
Most of the previous camera logic was replaced with new logic centering around a depth calculation and neural network object detection. Instead of a danger value ranging from 0 to 10 by comparing the current frame to a reference frame, our program calculates a depth value ranging from 0 to 255 that can be adjusted by the user. When the camera depth exceeds this threshold, a warning is issued. Many of the methods for the black and white colors shown by the camera were also replaced by us with more efficient solutions.

## Instructions for Installation
In order to run the camera program, we first need to clone the code repository by running `git clone https://github.com/BradenMccoy/indoor-nav-gui`.

After the repository has been cloned, we can run `sudo apt install python3` in order to install Python in the current environment if it is not yet installed. Then, just use `cd` to navigate into the repository, use `pip3 install -r requirements.txt` to install the necessary packages for the program to run, and run `python3 indoor_nav_gui.py` to start the program with the depth camera connected via USB.

If done correctly, a window will pop up showing our program UI with the depth camera stream.

## Our UI Documentation

### #1 - Main Page

Our solution is based around assisting the user by supplying additional helpful information about their surroundings, and to this end, we decided that only one page would be necessary. We found that everything users would need could fit into a single screen with room to spare for additions if they are needed. Future work may add additional screens as more features are added.

The main page includes a camera display, a collision indicator with a danger value, a text based log box, and a settings panel with buttons for adjusting the auditory warnings, and a slider for adjusting the minimum depth. All of these are clearly displayed and have their own dedicated spaces. **Visibility** was a key guideline considered for these features, with how much space the camera display takes up to allow for users to clearly see what the camera is seeing. Additionally on the settings menu, we’ve used a large icon to represent "mute", which is **consistent** with other applications and more visible than the other settings because we anticipate it to be the most used.

We will use **feedback** by using both visual and audio indicators for collision warnings, which will make it clear and easy to understand when a collision is imminent. The collision indicator is to further aid in determining the cause of a potential collision, and this simple graphic is used to display a direction and location as an effective visual representation. This ultimately represents high **affordance**, as users will visually recognize this symbol and be aware of its purpose from other places they have witnessed it.

Here is an early mockup of our main page UI:
![image](https://user-images.githubusercontent.com/13970556/219263404-354d13b7-30e5-42de-9ccc-30ce7ede7acd.png)

And here is our final implementation of it working with a connected depth camera:
![python_dyZNHcloZg](https://user-images.githubusercontent.com/55826558/222355730-b4e398e5-d61b-45ad-94bb-dcf2625958ca.png)

No simulated backend was used for this, as a functioning backend was already implemented by the previous team, and was only marginally improved by our work.
