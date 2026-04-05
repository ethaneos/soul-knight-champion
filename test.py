import subprocess
import cv2
import numpy as np

result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
img_array = np.frombuffer(result.stdout, dtype=np.uint8)
screen = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
cv2.imwrite("test.png", screen)
print(f"Screenshot size: {screen.shape[1]}x{screen.shape[0]}")