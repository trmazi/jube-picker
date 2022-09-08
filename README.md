# JubePicker
 <img src="https://github.com/trmazi/jube-picker/blob/main/assets/tex/title.png" alt="logo" width="500"/>
 
 A program written with PyGame to use a 4x4 panel over usb HID to start software.

## How to use
 You can either run by getting the latest release from the releases tab, or install `requirements.txt` and run `picker.py`. The app's requirements are very small, only needing pygame.
 
 To add the paths to your executibles, set them in games.json for the game you'd like to start. You can add up to 15 buttons. For best results, use 1-2 words with a newline (\n) in between the two words.
 
 Once in the software, you just push the button for the program you want to start, and press "Start!"
 
## How to interface with app
 If you have an HID controller plugged in with at least 16 buttons, you will be brought to the binding screen when you start the software for the first time.
 If you don't have a controller, however, The app will just take you to the main screen and you can use the mouse cursor to select the game.
 
 You can rebind your controller by pressing the Enter key on your keyboard.
 
## Future development
 The current V1 code is insanely gross. I'd like to sit down and refactor it a lot in the future.
 
 Currently, the app will only run properly in Jubeat's native resolution, this can be fixed in the future by scaling everything to the set resolution.
 
 I'd like to interface the jbio hook for P4IO support in the future, but I'll probably do the refactor and scaling before.
 
## Known issues
* App cannot scale properly (will be looked at)
* After adding controller support, touch input became wildly slower, for some reason. I'll look more into this soon.
