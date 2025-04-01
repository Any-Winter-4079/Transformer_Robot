For the creation of the robot, it is first suggested to collect all hardware components (Arduino Uno, L298N, INMP441, SG-90, MAX89357A, KY-037, breadboards, batteries, etc.), and plan their distribution on a potential chassis. This planning should consider ease of access for battery charging, code flashing to the Arduino Uno and ESP32 modules, etc., to determine the number of levels—and size per level—needed for the robot chassis.

In this case, two levels (or floors) are created using wooden board or particleboard of approximately 24x13x0.3cm for each level. A robot car template (see Figure 1) is used to draw the chassis shape to be cut, leaving space for the 2 wheels to connect to motors and with 6 protrusions for joining the levels using hexagonal spacers. Figures 2, 3, and 4 show the processes of sanding (after cutting), drilling, and motor anchoring, respectively.
<img width="531" alt="Screenshot 2025-04-01 at 19 20 58" src="https://github.com/user-attachments/assets/b6813e53-c767-4744-9b71-3a8c905d3670" />

<div align="center"><img width="500" alt="sand" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/dc2a5f76-a026-4f6a-ab81-25aafd2552d3">
  <p>Figure 1. Template followed for cutting each level of the chassis, from ELEGOO Smart Robot Car Kit V4.0, on the left, and view of 2 chassis levels joined by hexagonal spacers, noting the position of the wheels - where the 2 DC motors would fit, which are in turn screwed to the lower chassis - in the spaces specifically left for them, on the right.</p>
</div>

The chassis therefore has two complete levels, with components attached to the bottom of the first level, to the top of the first level, and to the top of the second level. Later, a third level is partially created, only at the back of the robot (similar to a spoiler), due to space limitations after expanding the robot for audio and speech capabilities compared to the initial design. It is recommended to increase the chassis size if a third level is to be avoided.

It's important to note that the motors are attached to the bottom of the first floor in this case, so they are level with the caster wheel that's similarly installed below the first floor. Depending on the size of the caster wheel, however, it may be necessary to install the motors on the top of the first floor, as the wheels attached to the motors are usually significantly larger than the caster wheel, and it's important to keep the lower chassis level.

The result of this first phase of construction can be seen in Figure 4.
<div align="center"><img width="500" alt="sand" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/dc2a5f76-a026-4f6a-ab81-25aafd2552d3">
  <p>Figure 2. Sanding of the robot's chassis after the cutting phase.</p>
</div>
<div align="center"><img width="500" alt="drill" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/b24a6268-7095-434d-ac06-69c8f85bd6d6">
  <p>Figure 3. Drilling in both chassis levels for joining with hexagonal spacers.</p>
</div>
<div align="center"><img width="500" alt="motor" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/a28444a3-977f-4c02-9657-413754f5de1b">
  <p>Figure 4. Installation of motors on the lower part of the first chassis level.</p>
</div>
<div align="center"><img width="500" alt="first_level" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/b55729d7-3c2b-4a74-b6a4-3feb76642fd3">
<p>Figure 5. First level of the chassis with two wheels connected to motors and a third caster wheel.</p>
</div>

Regarding the motor pack purchase, note that either they are acquired with pre-soldered +/- cables, or soldering will be required. For attaching motors to the chassis, it's recommended to acquire 2 motor mounts (metal pieces shown in Figure 3) to screw with 2 horizontal screws (holding the motor to the mount) and 2 vertical screws (securing the mount to the chassis) if they're not included in the pack.

After this first phase, it's recommended to test the Arduino Uno by connecting it to the computer—using a USB A to USB B cable—and uploading a test program such as Blink.ino. If functional, it should be screwed to the top of the second chassis level—using the default M3 holes that come with the Arduino—as shown in Figure 5.

<div align="center"><img width="500" alt="attach" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/18a8485e-dd92-484f-84cb-da1406c7e1e5">
  <p>Figure 6. Mounting the Arduino Uno Rev3 and L298N to the top of the second chassis level using M3 screws, with the Arduino connected to the computer for running the Blink.ino sketch.</p>
</div>

After testing the Arduino (powered from the computer at this point), proceed to install a rechargeable battery and a breadboard to the top of the lower chassis level. In this case, Blue Tack is used for adhesion, allowing easy disassembly if needed. It's important to ensure that the battery's charging connector (in this case, micro-USB) and the breadboard pins are easily accessible to facilitate battery charging and connecting other components to the breadboard's power columns (+ and -).

Next, join both chassis levels with hexagonal spacers and M3 cap screws. Once both chassis parts are joined, connect the positive (+) and negative (-) cables from the motors to the L298N (also screwed to the chassis), specifically to OUT1 and OUT2 (for the right motor) and OUT3 and OUT4 (for the left motor, from the robot's perspective).

Then connect the +/- cables from the 7.4V battery to one of the power column pairs on the breadboard (positive battery terminal to positive breadboard column, and likewise for the negative terminal) to power the Arduino and L298N (but not the motors directly, as they are powered through the L298N controller). For the L298N, use the +12V input (not 5V) for the positive pole (and GND for the negative), and use the DC barrel jack for the Arduino, as using the 5V or 3.3V input would damage the component. Note that unless specified otherwise, all connections use Dupont cables.

At this point, if desired, the operation of the motors can be tested (see the [move_motors](https://github.com/Any-Winter-4079/Transformer_Robot/blob/main/arduino_uno_code/test_sketches/move_motors.ino) sketch) by connecting pins 8 and 7 of the Arduino Uno to IN1 and IN2 of the L298N (to control the direction of rotation, forward, backward or stop, of the right wheel) and pins 5 and 4 to IN3 and IN4 (to control the direction of rotation of the left wheel). Additionally, by connecting pins 6 and 3 (for pulse width modulation) of the Arduino Uno to ENA and ENB of the L298N, values from 0 to 255 can be written (on these pins 6 and 3 of the Arduino Uno), which the L298N will interpret in ENA and ENB as indicators of the speed at which the right and left motors should move, respectively, according to the duration of the pulses sent. This idea of PWM (pulse-width modulation), where information is not only sent by modifying the voltage (usually, 5V or 0V) but also the duration of the pulses sent (which ultimately modifies the average voltage received), can be observed in Figure 6.

<div align="center"><img width="400" alt="pulse-width-modulation" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/cc500e90-97dc-48b4-82a9-f4e15632581b">
  <p>Figure 6. Pulse-width modulation. By Thewrightstuff - Own work, CC BY-SA 4.0, https://commons.wikimedia.org/w/index.php?curid=72876123</p>
</div>

The result of the joining of both levels can be observed in Figure 7. Note that there is an additional connection to GND and 5V of the L298N (initially intended to power a camera) that can be ignored. Moreover, it is recommended to lubricate the free wheel if it does not spin easily, and ensure that it aligns with the direction of movement of the robot.
<div align="center">
  <img width="500" alt="robot 2 levels" src="https://github.com/Any-Winter-4079/Transformer_Robot/assets/50542132/f4a89014-68a4-4f08-a55c-9e027524565c">
  <p>Figure 7. 2-level robot with Arduino Uno Rev3 and L298N on the upper level and 7.4V battery, 400-pin breadboard, wheels, and motors on the lower level.</p>
</div>
