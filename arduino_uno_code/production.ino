#include <Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// Software serial (e.g. with pins 10, 11) is an alternative to get
// the angle data from the ESP32-CAM. It is not used, as it
// caused noise on nearby pins (e.g. on pin 9, close to 10, 11),
// interfering with the servo and causing it to randomly jitter (?).
// Using Rx on the Uno on the other hand, worked fine without noise.

// The Rx connection must be removed when uploading code to the Uno.

#define UP_DOWN_SERVO_PIN 9
#define LEFT_RIGHT_SERVO_PIN A0

// Usually, the servo can rotate from 0 to 180 degrees (and some, 360º)
// In this case, the servo is further constrained by the OV2640 cable
// which goes through the eyeball and into the ESP32-CAM.
// Your range of motion may differ, so you may need to replace these values.

// Up and down
#define DOWN_ANGLE 50                   // ** Replace **
#define UP_ANGLE 110                    // ** Replace **
#define VERT_CENTER_ANGLE 80            // ** Replace **

// Left and right
#define LEFT_ANGLE 120                  // ** Replace **
#define RIGHT_ANGLE 60                  // ** Replace **
#define HORIZ_CENTER_ANGLE 90           // ** Replace **

#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT  64
#define OLED_RESET     -1 // Reset pin # (-1 if sharing Arduino reset pin)

Servo up_down_servo;
Servo left_right_servo;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Update the display with the specified message
void updateDisplay(const String& message) {
  display.clearDisplay();
  display.setCursor(0,0);
  display.print(message);
  display.display();
}

// Move left_right_servo to the specified angle and update the display
void moveLeftRightServo(int angle) {
  angle = constrain(angle, RIGHT_ANGLE, LEFT_ANGLE);
  left_right_servo.write(angle);
  updateDisplay("Angle: " + String(angle));
}

// Move up_down_servo to the specified angle and update the display
void moveUpDownServo(int angle) {
  angle = constrain(angle, DOWN_ANGLE, UP_ANGLE);
  up_down_servo.write(angle);
  updateDisplay("Angle: " + String(angle));
}

void setup() {
  // The baud rate must match the baud rate of the ESP32-CAM
  // that sends the angle data.
  Serial.begin(9600);
  up_down_servo.attach(UP_DOWN_SERVO_PIN);  // Attach servo that moves the eyes up and down
  left_right_servo.attach(LEFT_RIGHT_SERVO_PIN);  // Attach servo that moves the eyes left and right

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3C for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  display.display();
  delay(2000); // Pause for 2 seconds

  // Clear the buffer
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0,0);              // Start at top-left corner
  display.cp437(true);                 // Use full 256 char 'Code Page 437' font

  // Center the eyes
  moveLeftRightServo(HORIZ_CENTER_ANGLE); // Move to the center
  moveUpDownServo(UP_ANGLE); // Move to the center
}

void loop() {
  // Read data from the ESP32-CAM sent to RX pin
  if (Serial.available()) {
    String received_data = Serial.readStringUntil('\n');
    // Serial.print("Raw Data: ");
    // Serial.println(received_data);

    // received_data.trim(); // Remove whitespace or newline characters
    // Serial.print("Trimmed Data: ");
    // Serial.println(received_data);

    int up_down_angle, left_right_angle;
    if (received_data.startsWith("SSID:")) {
      String ssid = received_data.substring(5);
      updateDisplay(ssid);
    }
    else if (received_data.startsWith("angleV:") && received_data.indexOf(",angleH:") > 0) {
      int up_down_index = received_data.indexOf("angleV:") + 7;
      int left_right_index = received_data.indexOf(",angleH:") + 8;
      String up_down_angle_str = received_data.substring(up_down_index, received_data.indexOf(",", up_down_index));
      String left_right_angle_str = received_data.substring(left_right_index);
    
      up_down_angle = up_down_angle_str.toInt();
      left_right_angle = left_right_angle_str.toInt();
    
      moveUpDownServo(up_down_angle);
      moveLeftRightServo(left_right_angle);
    } else if (received_data.startsWith("Listening") || received_data.startsWith("Thinking")) {
      // Update the display with the listening or thinking status
      updateDisplay(received_data);
    }
  }
}
