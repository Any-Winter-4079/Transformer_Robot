For the creation of the robot, it is first suggested to collect the hardware components (Arduino Uno, L298N, INMP441, SG-90, MAX89357A, KY-037, breadboards, batteries, etc.), and propose a distribution on a potential chassis (considering aspects such as access to them for battery charging, flashing code to the Arduino Uno and ESP32-CAM, etc.), to determine the number of levels -and the size of each level- necessary.

In this case, 2 levels (or floors) are created, using a wooden board or particle board of approximately 24x13x0.3cm for each level, and making use of a robot car template to draw the shape of the chassis to be cut (to leave space for the 2 or 4 wheels to connect to the motors -in this case, 2- and with 6 protrusions for the joining of the levels by hexagonal spacers). In Figures 1, 2, and 3, you can see the processes of sanding -after cutting-, drilling, and anchoring the motors.

The chassis, therefore, has two complete levels, joining components to the bottom of the first level, to the top of the first level, and to the top of the second level. Later, a third level is created partially, only at the back of the robot (similar to a spoiler), due to lack of space after the expansion (for audio and speech capabilities) compared to the initial idea of the robot, so it is suggested to increase the size of the chassis if a third level is to be avoided.

It is relevant to highlight that the motors are attached in this case to the bottom of the first floor, so that they are leveled with the free wheel (caster wheel) that is installed similarly below the first floor. Depending on the size of the free wheel, however, it may be necessary to install the motors on the top of the first floor, as the wheels attached to the motors are usually significantly larger than the free wheel, and it is important to keep the lower chassis leveled.

The result of this first phase of construction can be seen in Figure 4.
<div align="center"><img width="500" alt="sand" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/dc2a5f76-a026-4f6a-ab81-25aafd2552d3">
  <p>Figure 1. Sanding of the robot's chassis after the cutting phase.</p>
</div>
<div align="center"><img width="500" alt="drill" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/b24a6268-7095-434d-ac06-69c8f85bd6d6">
  <p>Figure 2. Drilling in both levels of the chassis for joining with hexagonal spacers.</p>
</div>
<div align="center"><img width="500" alt="motor" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/a28444a3-977f-4c02-9657-413754f5de1b">
  <p>Figure 3. Installation of motors on the lower part of the first level of the chassis.</p>
</div>
<div align="center"><img width="500" alt="first_level" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/b55729d7-3c2b-4a74-b6a4-3feb76642fd3">
<p>Figure 4. The first level of the chassis with two wheels connected to motors and a third free wheel.</p>
</div>

Regarding the purchase of the motor pack, note that either they are acquired with the +, - cables pre-soldered, or soldering will be required, as well as for their attachment to the chassis, it is recommended to acquire 2 motor mounts, to screw 2 screws horizontally - holding the motor to the mount - and 2 vertically - securing the mount to the chassis - in case they are not included in the pack.

After this first phase, it is recommended to test the hardware components (for example, connecting the Arduino Uno to the computer - by means of a USB A to USB B cable -, and uploading a basic program, such as Blink.ino), as well as their attachment to the top of the second level of the chassis - using the default M3 holes. A snapshot of this process can be seen in Figure 5.

<div align="center"><img width="500" alt="attach" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/18a8485e-dd92-484f-84cb-da1406c7e1e5">
  <p>Figure 5. Joining of Arduino Uno Rev3 and L298N to the top part of the second level of the chassis by M3 screws and connection of Uno to computer for uploading of the Blink.ino sketch.</p>
</div>

After testing the first components, it is suggested to install a battery - preferably rechargeable - and a breadboard to the top of the lower level of the chassis. In this case, Blue Tack is used for joining, to allow easy disassembly if necessary. It is important here that the battery charging connector (such as micro-USB B), and the breadboard pins are easily accessible, to facilitate charging tasks and connection of components to the power columns (+, -).

After this, both levels of the chassis can be joined with hexagonal spacers and M3 cap screws - although, if a third level is needed, headless M3 screws would be required for joining to the second level, so that both ends can be screwed into a hexagonal spacer.

Once both parts of the chassis are joined, it is suggested to connect the + and - cables of the motors to OUT1, OUT2 (right motor, from the robot's perspective) and OUT3, OUT4 (left motor) of the L298N, and power all components, connecting +, - of the 7.4V battery to one of the breadboard's power columns (+, -), where we connect our L298N and Arduino Uno. In the case of the L298N, note that, since the battery provides 7.4V, the +12V and GND input are used, while in the case of the Uno Rev3, the DC barrel jack is used, as using the 5V or 3.3V input would damage our component. For all connections, Dupont cables are used.

At this point, if desired, the operation of the motors can be tested (see the [move_motors](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/arduino_uno_code/test_sketches/move_motors.ino) sketch) by connecting pins 8 and 7 of the Arduino Uno to IN1 and IN2 of the L298N (to control the direction of rotation, forward, backward or stop, of the right wheel) and pins 5 and 4 to IN3 and IN4 (to control the direction of rotation of the left wheel). Additionally, by connecting pins 6 and 3 (for pulse width modulation) of the Arduino Uno to ENA and ENB of the L298N, values from 0 to 255 can be written (on these pins 6 and 3 of the Arduino Uno), which the L298N will interpret in ENA and ENB as indicators of the speed at which the right and left motors should move, respectively, according to the duration of the pulses sent. This idea of PWM (pulse-width modulation), where information is not only sent by modifying the voltage (usually, 5V or 0V) but also the duration of the pulses sent (which ultimately modifies the average voltage received), can be observed in Figure 6.

<div align="center"><img width="400" alt="pulse-width-modulation" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/cc500e90-97dc-48b4-82a9-f4e15632581b">
  <p>Figure 6. Pulse-width modulation. By Thewrightstuff - Own work, CC BY-SA 4.0, https://commons.wikimedia.org/w/index.php?curid=72876123</p>
</div>

The result of the joining of both levels can be observed in Figure 7. Note that there is an additional connection to GND and 5V of the L298N (initially intended to power a camera) that can be ignored. Moreover, it is recommended to lubricate the free wheel if it does not spin easily, and ensure that it aligns with the direction of movement of the robot.
<div align="center">
  <img width="500" alt="robot 2 levels" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/f4a89014-68a4-4f08-a55c-9e027524565c">
  <p>Figure 7. 2-level robot with Arduino Uno Rev3 and L298N on the upper level and 7.4V battery, 400-pin breadboard, wheels, and motors on the lower level.</p>
</div>
