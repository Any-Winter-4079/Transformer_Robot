// Right motor (from the robot's perspective)
int INA = 6; // Control movement speed with pulse-width modulation: [0-255]
int IN1 = 8; // Control direction of movement: [0,1]
int IN2 = 7; // Control direction of movement: [0,1]

// Left motor
int ENB = 3; // Control movement speed with pulse-width modulation: [0-255]
int IN3 = 5; // Control direction of movement: [0,1]
int IN4 = 4; // Control direction of movement: [0,1]

// To control direction:
// 10 (right motor) 10 (left motor) -> Forward
// 01 (right motor) 01 (left motor) -> Backward
// 00 (right motor) 00 (left motor) -> Stop
// 01 (right motor) 10 (left motor) -> Rotate right
// 10 (right motor) 01 (left motor) -> Rotate left

// To control speed:
// Any value from 0 to 255. Due to friction and the weight of the robot,
// the min speed is set here to 135. Low speeds may not generate enough
// force to move the robot when it gets resistance from the ground.

// Make sure the caster wheel freely spins and aligns itself with
// the direction of motion when driving forward (or backward).
// If not, some lubrication may help.

int SHORT_WAIT_TIME = 500; // 0.5 seconds
int MEDIUM_WAIT_TIME = 1000; // 1 second
int LONG_WAIT_TIME = 3000; // 3 seconds

int TOP_SPEED = 255; // 100% duty cycle
int INTERMEDIATE_SPEED = 180; // 71% duty cycle
int LOW_SPEED = 135; // 53% duty cycle
int NO_SPEED = 0; // 0% duty cycle

void setup() {
    // Sets pins as output pins (meaning we'll write to them)
    pinMode(INA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(ENB, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);

    // Move forward (10 10)
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(INA, LOW_SPEED);

    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, LOW_SPEED);

    delay(LONG_WAIT_TIME); // Wait (robot keeps moving)

    // Move backward (01 01)
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(INA, LOW_SPEED);

    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, LOW_SPEED);

    delay(LONG_WAIT_TIME); // Wait (robot keeps moving)

    // Turn left (10 01)
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(INA, TOP_SPEED);

    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, TOP_SPEED);

    delay(LONG_WAIT_TIME); // Wait (robot keeps moving)

    // Stop the motors
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);

    delay(MEDIUM_WAIT_TIME); // Wait (robot stays still)

    // Turn right (01 10)
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(INA, TOP_SPEED);

    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, TOP_SPEED);

    delay(LONG_WAIT_TIME); // Wait (robot keeps moving)

    // Stop the motors
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
}

void loop() {
    // Do nothing
}
