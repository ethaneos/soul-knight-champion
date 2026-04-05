import subprocess
import cv2
import numpy as np
import time

def screenshot():
    result = subprocess.run(
        ["adb", "exec-out", "screencap", "-p"],
        capture_output=True
    )
    img_array = np.frombuffer(result.stdout, dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

print("Find a chest in game, switch back in 5 seconds...")
time.sleep(5)

# Take 10 screenshots 0.2 seconds apart to capture all animation frames
for i in range(10):
    screen = screenshot()
    cv2.imwrite(f"/storage/emulated/0/SoulKnightBot/chest_{i}.png", screen)
    print(f"Captured frame {i}")
    time.sleep(0.2)

print("Done! All frames captured.")