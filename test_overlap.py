import subprocess
import time
import threading

def swipe(x, y, duration):
    subprocess.run([
        "adb", "shell", "input", "touchscreen", "swipe",
        str(x), str(y), str(x), str(y), str(duration)
    ])

print("Switch to Soul Knight in 5 seconds...")
time.sleep(5)

# Start first direction in a thread
t1 = threading.Thread(target=swipe, args=(421, 531, 3000))  # up
t1.start()

# Wait 1 second then start second direction in another thread
time.sleep(1)
t2 = threading.Thread(target=swipe, args=(571, 781, 3000))  # right
t2.start()

t1.join()
t2.join()
print("Done!")