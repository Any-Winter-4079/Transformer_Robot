In terms of components, the following electronic devices are selected, prioritizing low cost and simplicity:

- **1x 7.4V rechargeable battery** - in this case, an ELEGOO micro-USB rechargeable battery - for motors, motor controller, Arduino, servos, ESP32-WROVER, sound detector, microphone, amplifier, speaker, and OLED display.
- **4x 1.2V rechargeable AA batteries** (with series holder and switch) - to provide 4.8V to the ESP32-CAMs, one for each robot eye.
- **2x Voltage reducers** (buck converters) adjustable by potentiometer - to reduce to 5V and 3.3V for components that don't accept 7.4V directly.
- **1x 2-pin switch** - to easily turn the robot on and off, noting that another switch would be needed if one isn't available in the battery holder (since ESP32-CAMs have separate power to avoid voltage spikes during motor and servo use).
- **1x 400-pin breadboard** - for creating 2 power lines, 7.4V (directly from battery) and 5V (from a voltage reducer).
- **2x 170-pin breadboards** - one for sound input (KY-037, INMP441) at the front of the robot, and another for output (MAX98357A) at the rear.
- **Dupont male-to-male, male-to-female, and female-to-female cables** for the robot's wiring.
- **1x Arduino Uno Rev3** - to send commands received from the ESP32-WROVER to the motor controller (for wheel movement) and/or servos (for eye movement).
- **1x DC barrel jack** (DC power jack) - to power the Arduino with 7.4V, internally regulated by the Arduino to 5V.
- **1x L298N motor controller** - to receive direction commands (forward rotation, backward rotation, or stop) and intensity (rotation speed) from the Arduino to send to the motors.
- **2x SG-90 Servos** - to move the eyes horizontally and vertically according to angles received from the Arduino Uno.
- **2x ESP32-CAM** - in this case, Ai-Thinker and M5Stack Wide, although both could be the same model - to establish a web server responsible for sending frames on demand to the computer (where the robot's brain runs).
- **1x ESP32-WROVER** (or ESP32-CAM without using the camera) - in this case, 1x Freenove ESP32-WROVER CAM Board - to manage receiving movement commands (to send to Arduino Uno) and sending (to computer) and receiving (from computer) audio.
- **2x OV2640** - one per ESP32-CAM - with 160-degree fisheye lens, with a 75mm cable (longer than the original 21mm cable) to allow eye movement (with embedded camera).
- **1x 128x64 OLED SSD1306 I2C display** - to show information such as the WiFi network from which IP address is acquired, useful in case of multiple possibilities, or internal robot status ('Listening...', 'Thinking...').
- **1x KY-037 sound detection microphone** - to start sending audio to the computer when a certain sound threshold is exceeded.
- **1x INMP441 I2S microphone** - to capture that sound, to be sent by the ESP32-WROVER to the computer to determine, using Speech-to-Text, if it's noise or a natural language phrase, and if so, send it to the language model.
- **1x MAX98357A I2S amplifier** - to receive audio sent to the ESP32-WROVER from the computer, relating to the language model's response converted to audio using Text-to-Speech and forwarded to the amplifier.
- **1x 3W and 8Ω speaker** - for playing audio received by the amplifier.
- **2x 3-6V DC motors with gearbox** - in this case, with Dupont termination - to attach to each of the front wheels to direct the robot's movement.

Additionally, the following materials are used for chassis construction, component mounting, and eye manufacturing:

- **2x Wheels** - one for each gearbox motor.
- **2x Metal motor mounts** - to screw each motor to the chassis with 2 horizontal and 2 vertical screws.
- **1x Caster wheel of ~3cm diameter** - to place at the central rear of the robot.
- **1x Wooden or particleboard of ~40x40x0.3cm** - for chassis.
- **1x Wooden board of ~11x4x0.8cm** - for support pieces in the vertical and horizontal movement of eyes.
- **M3 hexagonal spacers of ~4cm length** - to separate the different chassis levels.
- **M3 screws of ~1.5cm length** - both with heads and double threaded (without heads).
- **M3 washers**.
- **Normal and self-locking M3 nuts**.
- **2x M2 screws** - to attach the OLED SSD1306 I2C display to the chassis.
- **2x M2 nuts** - to secure the display to the chassis.
- **4x Ping pong balls** - to serve as molds for pouring resin to manufacture the eyes.
- **1x Epoxy Resin Kit**.
- **Paints and brushes** - for painting the resin.
- **Red thread** - for veins on the eyes.
- **Blue Tack** - for non-permanent attachments.
- **Colored adhesive tape** - to label cables by type (e.g., power, motors, servos, audio, etc.).
- **Super Glue-3** to attach the SG-90 servo horn (attached to it by pressure) to the vertical rotation cylinder - noting that with this design the servo is replaceable, being detachable from the horn by pressure.

Similarly, although not part of the robot, the following tools and accessories are used for manufacturing and/or testing:

- **1x Digital multimeter** - to verify voltages.
- **1x Steel saw** - 24 TPI - for the chassis.
- **Sandpapers** - for the chassis.
- **1x Drill Kit** - with M3 size.
- **1x Soldering Kit** - to solder pins to the INMP441 and MAX98357A.
- **Pliers and wire strippers**.
- **Screwdrivers**.
- **1x Clamp** - for holding during cutting.
- **1x Measuring tape**.
- **1x Scissors**.
- **1x Printer and paper** - to print the iris of the eyes and the calibration pattern for the ESP32-CAMs.

And finally, for the operation of the robot, the following are required:

- **1x Computer** - with adequate specifications for the LLM.
- **1x Router** for internet access and/or phone with hotspot, to connect 2x ESP32-CAMs, ESP32-WROVER, and computer to the same network, as well as to access the internet (necessary according to functions invokable by the LLM).
- **1x USB-A to Serial converter** (to upload code to some ESP32-CAM models, such as Ai-Thinker) or USB-A to USB-C cable (for other models, such as M5Stack Wide).
- **1x USB A to USB B cable** - to flash code to the Arduino Uno.
- **1x USB A to micro-USB cable** - to recharge the 7.4V battery.
- **1x AA battery charger**.
