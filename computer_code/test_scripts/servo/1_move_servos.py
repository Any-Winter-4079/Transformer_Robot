import requests

#################
# Description   #
#################
# This is a test program to move the servos from the computer.
# Computer and ESP32 are connected to the same WiFi network (or hotspot).
# Computer sends a request to the ESP32 to move the servos to the specified angles.
# The ESP32 receives the request and forwards the angles to the Uno.
# The Uno receives the request and moves the servos to the specified angles.

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

def move_servo(angleV, angleH):
    """Send a request to move the servos to the specified angles."""
    data = {'angleV': angleV, 'angleH': angleH}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(esp32_command_url, data=data, headers=headers)
        print(f"Response from ESP32: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending request: {e}")

def main():
    while True:
        user_input = input("Enter vertical and horizontal servo angles separated by a space (0-180 for each) or 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break

        try:
            angleV, angleH = map(int, user_input.split())
            if 0 <= angleV <= 180 and 0 <= angleH <= 180:
                move_servo(angleV, angleH)
            else:
                print("Please enter numbers between 0 and 180 for both angles.")
        except ValueError:
            print("Invalid input. Please enter two valid integers separated by a space.")

if __name__ == "__main__":
    main()
