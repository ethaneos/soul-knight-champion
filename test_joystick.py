from joystick import VirtualJoystick
import time
import subprocess

joystick = VirtualJoystick(
    center_x=421,
    center_y=781,
    radius=150
)

try:
    print("Switch to Soul Knight in 5 seconds...")
    time.sleep(5)

    print("Moving up... (angle 180)")
    joystick.set_direction(180)
    time.sleep(2)

    print("Moving down... (angle 0)")
    joystick.set_direction(0)
    time.sleep(2)

    print("Moving left... (angle 270)")
    joystick.set_direction(270)
    time.sleep(2)

    print("Moving right... (angle 90)")
    joystick.set_direction(90)
    time.sleep(2)

    print("Diagonal up-right... (angle 135)")
    joystick.set_direction(135)
    time.sleep(2)

    print("Smooth rotation...")
    for angle in range(0, 360, 10):
        joystick.set_direction(angle)
        time.sleep(0.15)

finally:
    print("Cleaning up...")
    joystick.cleanup()
    print("Done!")