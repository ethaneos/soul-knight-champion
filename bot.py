import subprocess
import time
import cv2
import numpy as np
import os

# Button coordinates
JOYSTICK = (400, int(1080-300))
ATTACK = (2025, int(1080-300))
SKILL = (1675, int(1080-300))
WEAPON_SPECIAL = (1800, int(1080-575))
SWITCH_WEAPON = (2050, int(1080-645))

# Soul Knight package name
SOUL_KNIGHT_PACKAGE = "com.ChillyRoom.DungeonShooter"

def get_active_app():
    result = subprocess.run(
        ["adb", "shell", "dumpsys", "window", "windows"],
        capture_output=True, text=True
    )
    lines = []
    for line in result.stdout.split("\n"):
        if "mSurface" in line:
            lines.append(line)
    return ";;;".join(lines)

SCREEN_CENTER_X = 2340 // 2  # 1170
SCREEN_CENTER_Y = 1080 // 2  # 540

def move_toward(target_x, target_y, threshold=100):
    dx = target_x - SCREEN_CENTER_X
    dy = target_y - SCREEN_CENTER_Y

    # Move horizontally
    if dx > threshold:
        move("right")
    elif dx < -threshold:
        move("left")

    # Move vertically
    if dy > threshold:
        move("down")
    elif dy < -threshold:
        move("up")

def is_soul_knight_active():
    active = get_active_app()
    return SOUL_KNIGHT_PACKAGE in active

def find_item(screen, item):
    template_dir = f"/storage/emulated/0/SoulKnightBot/templates/{item}/"
    
    for filename in os.listdir(template_dir):
        if not filename.startswith("chest_"):
            continue
            
        template = cv2.imread(os.path.join(template_dir, filename))
        if template is None:
            continue
            
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, confidence, _, location = cv2.minMaxLoc(result)
        print("checked")
        if confidence > 0.8:
            print(f"Chest found using template {filename} with confidence {confidence:.2f}")
            return location
    
    return None

def screenshot():
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        capture_output=True
    )
    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

def tap(x, y):
    subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

def swipe(x1, y1, x2, y2, duration=500):
    subprocess.run(["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

def move(direction, distance=100):
    jx, jy = JOYSTICK
    if direction == "up":
        swipe(jx, jy, jx + distance, jy)
    elif direction == "down":
        swipe(jx, jy, jx - distance, jy)
    elif direction == "left":
        swipe(jx, jy, jx, jy - distance)
    elif direction == "right":
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
        if not was_active:
            print("Soul Knight detected — bot running!")
            was_active = True
        
        screen = screenshot()
        chest = find_item(screen, "chest")
        if chest is not None:
            chest_x, chest_y = chest
            print(f"Chest detected at {chest_x}, {chest_y}!")
            
            # Check if we are close enough to interact
            dx = abs(chest_x - SCREEN_CENTER_X)
            dy = abs(chest_y - SCREEN_CENTER_Y)
            
            if dx < 100 and dy < 100:
                # Close enough, interact
                print("Close enough, interacting!")
                tap(*ATTACK)
                time.sleep(0.5)
                tap(*ATTACK)
            else:
                # Move toward chest
                print("Moving toward chest...")
                move_toward(chest_x, chest_y)

    else:
        if was_active:
            print("Soul Knight not active — bot paused.")
            was_active = False
        time.sleep(1)  # Check every second when paused