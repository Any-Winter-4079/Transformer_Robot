#include <Servo.h>

#define UP_DOWN_SERVO_PIN 9
#define LEFT_RIGHT_SERVO_PIN A0 // Use A0 as a digital pin

// Vertically, because of the ESP32-CAMs being connected to the eyes,
// the SG-90 servos are constrained to a range of motion of [55, 130].
// Noticeably, because both ESP32-CAMs are different (and have different heights),
// we have more range of motion to look up than to look down. Going  <50 degrees
// collides with an ESP32-CAM, but restricting to [50, 90] seems to be an
// unnecessary constraint. Make sure to test the range of motion of your eyes
// as your robot will probably have different constraints.
#define DOWN_ANGLE 50                   // ** Replace **
#define UP_ANGLE 105                    // ** Replace **
#define VERT_CENTER_ANGLE 70            // ** Replace **

// Horizontally, the SG-90 servos are constrained to a range of motion of [70, 130],
// with 100 being the center. Make sure to test the range of motion of your eyes
// as your robot will probably have different constraints.
#define LEFT_ANGLE 130                  // ** Replace **
#define RIGHT_ANGLE 70                  // ** Replace **
#define HORIZ_CENTER_ANGLE 100          // ** Replace **

#define DELAY_TIME 400 // 0.4 seconds
#define NUM_ITERATIONS 3

Servo up_down_servo;
Servo left_right_servo;

void setup() {
    // Attach the servos to their respective pins
    up_down_servo.attach(UP_DOWN_SERVO_PIN);
    left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);

    // Start the servos at their center positions
    up_down_servo.write(VERT_CENTER_ANGLE);
    left_right_servo.write(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);

    // Centered vertically, move left and right
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        up_down_servo.write(VERT_CENTER_ANGLE);
        left_right_servo.write(LEFT_ANGLE);
        delay(DELAY_TIME);

        up_down_servo.write(VERT_CENTER_ANGLE);
        left_right_servo.write(RIGHT_ANGLE);
        delay(DELAY_TIME);
    }

    // Return both servos to their center positions
    up_down_servo.write(VERT_CENTER_ANGLE);
    left_right_servo.write(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);

    // Centered horizontally, move up and down
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        up_down_servo.write(UP_ANGLE);
        left_right_servo.write(HORIZ_CENTER_ANGLE);
        delay(DELAY_TIME);

        up_down_servo.write(DOWN_ANGLE);
        left_right_servo.write(HORIZ_CENTER_ANGLE);
        delay(DELAY_TIME);
    }

    // Return both servos to their center positions
    up_down_servo.write(VERT_CENTER_ANGLE);
    left_right_servo.write(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);

    // Move in a diagonal pattern from the top left to the bottom right
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        up_down_servo.write(UP_ANGLE);
        left_right_servo.write(LEFT_ANGLE);
        delay(DELAY_TIME);

        up_down_servo.write(DOWN_ANGLE);
        left_right_servo.write(RIGHT_ANGLE);
        delay(DELAY_TIME);
    }

    // Return both servos to their center positions
    up_down_servo.write(VERT_CENTER_ANGLE);
    left_right_servo.write(HORIZ_CENTER_ANGLE);
    delay(DELAY_TIME);

    // Move in a diagonal pattern from the top right to the bottom left
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        up_down_servo.write(UP_ANGLE);
        left_right_servo.write(RIGHT_ANGLE);
        delay(DELAY_TIME);

        up_down_servo.write(DOWN_ANGLE);
        left_right_servo.write(LEFT_ANGLE);
        delay(DELAY_TIME);
    }

    // Return both servos to their center positions
    up_down_servo.write(VERT_CENTER_ANGLE);
    left_right_servo.write(HORIZ_CENTER_ANGLE);
}

void loop() {
    // Do nothing
}
