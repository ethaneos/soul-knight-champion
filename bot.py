import subprocess
import time

# Button coordinates
JOYSTICK = (300, 400)
ATTACK = (300, 2025)
SKILL = (300, 1675)
WEAPON_SPECIAL = (575, 1800)
SWITCH_WEAPON = (645, 2050)

# Soul Knight package name
SOUL_KNIGHT_PACKAGE = "com.ChillyRoom.DungeonShooter"

def get_active_app():
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "window", "windows"],
        capture_output=True, text=True
    )
    for line in result.stdout.split("\n"):
        if "mSurface" in line:
            return line
    return ""

def is_soul_knight_active():
    active = get_active_app()
    return SOUL_KNIGHT_PACKAGE in active

def tap(x, y):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

def swipe(x1, y1, x2, y2, duration=500):
    subprocess.run(["adb", "shell", "input", "swipe",
                    str(x1), str(y1), str(x2), str(y2), str(duration)])

def move(direction, distance=100):
    jx, jy = JOYSTICK
    if direction == "right":
        swipe(jx, jy, jx + distance, jy)
    elif direction == "left":
        swipe(jx, jy, jx - distance, jy)
    elif direction == "up":
        swipe(jx, jy, jx, jy - distance)
    elif direction == "down":
        swipe(jx, jy, jx, jy + distance)

def attack():
    tap(*ATTACK)

def use_skill():
    tap(*SKILL)

# Bot loop
print("Bot started! Switch to Soul Knight to begin.")

was_active = False

while True:
    if is_soul_knight_active():
        print("on")
        if not was_active:
            print("Soul Knight detected — bot running!")
            was_active = True

        # Move in a pattern
        move("right")
        attack()
        time.sleep(0.3)

        move("up")
        attack()
        time.sleep(0.3)

        move("left")
        attack()
        time.sleep(0.3)

        move("down")
        attack()
        time.sleep(0.3)

        use_skill()
        time.sleep(0.5)

    else:
        if was_active:
            print("Soul Knight not active — bot paused.")
            was_active = False
        print("not on " + str(time.time()))
        time.sleep(1)  # Check every second when paused