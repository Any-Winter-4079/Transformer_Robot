#include <Servo.h>

#define UP_DOWN_SERVO_PIN 9
#define LEFT_RIGHT_SERVO_PIN A0

// Your range of motion may differ, so you may need to replace these values
// Up and down
#define DOWN_ANGLE 50                   // ** Replace **
#define UP_ANGLE 110                    // ** Replace **
#define VERT_CENTER_ANGLE 80            // ** Replace **

// Left and right
#define LEFT_ANGLE 120                  // ** Replace **
#define RIGHT_ANGLE 60                  // ** Replace **
#define HORIZ_CENTER_ANGLE 90           // ** Replace **

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
