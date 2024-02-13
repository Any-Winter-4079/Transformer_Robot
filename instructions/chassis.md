For the creation of the robot, it is first suggested to collect the hardware components (Arduino Uno, L298N, INMP441, SG-90, MAX89357A, KY-037, breadboards, batteries, etc.), and propose a distribution on a potential chassis (considering aspects such as access to them for battery charging, flashing code to the Arduino Uno and ESP32-CAM, etc.), to determine the number of levels -and the size of each level- necessary.

In this case, 2 levels (or floors) are created, using a wooden board or particle board of approximately 40x40x0.3cm for each level, and making use of a robot car template to draw the shape of the chassis to be cut (to leave space for the 2 or 4 wheels to connect to the motors -in this case, 2- and with 6 protrusions for the joining of the levels by hexagonal spacers). In Figures 1, 2, and 3, you can see the processes of sanding -after cutting-, drilling, and anchoring the motors.

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
