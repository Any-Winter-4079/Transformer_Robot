import requests

#################
# Description   #
#################
# This is a test program to move the servo from the computer.
# Computer and ESP32 are connected to the same WiFi network (or hotspot).
# Computer sends a request to the ESP32 to move the servo to the specified angle.
# The ESP32 receives the request and forwards the angle to the Uno.
# The Uno receives the request and moves the servo to the specified angle.

#################
# venv          #
#################
# Remember to create a virtual environment, install the packages, and activate it.
# In my case: source ./tensorflow-metal-test/bin/activate (from v2 folder)

#################
# Note          #
#################
# Make sure there is a sketch loaded to the Uno that can receive the angle
# and move the servo accordingly (for example, production.ino).

#################
# Configuration #
#################
USE_HOTSPOT = False

ip = "*.*.*.*" if USE_HOTSPOT else "*.*.*.*" # e.g. "192.168.1.182".                     ** Replace **
esp32_command_url = f"http://{ip}/command"

def move_servo(angle):
    """Send a request to move the servo to the specified angle."""
    data = {'angle': angle}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(esp32_command_url, data=data, headers=headers)
        print(f"Response from ESP32: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending request: {e}")

def main():
    while True:
        user_input = input("Enter servo angle (0-180) or 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break

        try:
            angle = int(user_input)
            if 0 <= angle <= 180:
                move_servo(angle)
            else:
                print("Please enter a number between 0 and 180.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

if __name__ == "__main__":
    main()
