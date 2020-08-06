# Stada App

This is a program built for one of the prototype design of Stada's project on food waste reduction using Raspberry Pi Module. It mainly consists of two parts : *Sensor Integration* and *User Interface*. The code in general must be ran on a **Raspberry Pi Module** since some of it's library can't be performed elsewhere. It should also be noted that the code can only run if both all of hardware and software setup process has completely finished.

## Prototype Guides

After running the code, it will firstly direct the user to the login page. For now insert for the username "rafif" and for the password "Wortel" (changable by class `User`). Succeeding authentication, you will be directed to the dashbord frame and  it will wait for the loadcell to be loaded with something weighing at least 15g (changable by`minmass`). After being loaded for more or less 5 seconds (changable), the camera will be triggered to capture the object. The image captured can be then previewed in the preview frame. Press the confirm button to continue. In the background, the image will be sent to a server and a response should be received. But, for now because there is no data available yet, the code will send the image to a dummy server and the device will receive nothing in return. The last page of the UI would be the confirmation page. For the sake of the presentation, an image would be shown as if it were the response from the server. In this page the user has to confirm wether the image detection is correct. Finally, press the 'yes' button if it is and 'no' button if it isn't. At it's current state, the motor will be triggered eitherway and the user will be brought again to the dashboard page.


## Sensor Integration Codes Explanation

The sensors and actuators used for the prototype are listed as follows:
1. Load Cell
2. HX711
3. Servo
4. Pi Camera
5. Touch Screen LCD Display

Part of codes that is responsible for controlling how the hardware interacts are located inside of the `Controller()` class. Inside the class, there will be several methods that can be accesed from the main program. 
- `initialize()` is used to initialize the load cell and tare it so that readings from the load cell will always be 0 when there is no object placed.
- `measure_weight()` is used to measure the weight of the object loaded on the load cell. This method will call `handle_start()`.
- `handle_start()` is used to call `captureImage()` and make sure that there is no problem while capturing.
- `captureImage()` is used for as the name suggests, capture image.
- `handle_send()` is used to call sendImage() and make sure that there is no problem while connecting.
- `sendImage()` is used for as the name suggests, sending image to the server. Note that for now it is empty.
- `dump_waste(0` is used to call `moveServo()` and make sure that there is no problem while moving the servo.
- `moveServo()` is used to move servo from the initial position `startpos` to the final position `finalpos` and back.



## Graphical User Interface Codes Explanation
The user interface is divided into several classes as follows:
1. Root
2. Login Frame
3. Dashboard Frame
4. Preview Frame
5. Confirmation Frame


- The `StadaAPP()` class is responsible as the root of the entire UI. It determines the styling being used,as well as how the UI frames are being stacked on top of each other. `self.frames = {}` is used to make an empty dictionaries that will consist of frames so that the frame that must be shown can be placed on top.

These lines of code will instantiate classes of frames.
```python
login_frame = LoginFrame(container, self, self.controller)
dashboard_frame = DashboardFrame(container, self,self.controller)
preview_frame = PreviewFrame(container, self, self.controller)
confirmation_frame = ConfirmationFrame(container,self, self.controller)
```
These lines of code will input frames into the empty dictionaries explained earlier:
```python
self.frames[DashboardFrame] = dashboard_frame
self.frames[LoginFrame] = login_frame
self.frames[PreviewFrame] = preview_frame
self.frames[ConfirmationFrame] = confirmation_frame
```
The method `show_frame()` will then raise the frame on top so that the user will only be able to see one frame at a moment.

The method `refresh_frame()` has the function to call `measure_weight()` every 500ms so that the program will loop and wait for an event as the loadcell detects an object.

- The `LoginFrame()` class is used to be showing an authentication page.
- The `DashboardFrame()` class is used to be showing the dashboard page.
- The `PreviewFrame()` class is used to be showing the preview page.
- The `ConfimationFrame()` class is used to be showing the confirmation page.


## What the code should be able to do next
1. Data visualization for the dashboard page.
2. Send and receive data from the server. 