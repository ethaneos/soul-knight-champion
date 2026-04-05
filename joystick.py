import subprocess
import math
import time
import threading

class VirtualJoystick:
    def __init__(self, center_x, center_y, radius=150):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius

        self.angle = 0
        self.magnitude = 0
        self.is_held = False

        self._current_process = None
        self._process_lock = threading.Lock()
        self._state_lock = threading.Lock()

        # Keep persistent ADB shell connection open
        self._shell = subprocess.Popen(
            ["adb", "shell"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True
        )

        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def _angle_to_xy(self, angle_deg, magnitude):
        angle_rad = math.radians(angle_deg)
        offset_x = magnitude * self.radius * math.sin(angle_rad)
        offset_y = magnitude * self.radius * math.cos(angle_rad)
        target_x = int(self.center_x + offset_x)
        target_y = int(self.center_y + offset_y)
        return target_x, target_y

    def _send_command(self, cmd):
        # Send command through persistent shell — much faster than new process
        try:
            self._shell.stdin.write(cmd + "\n")
            self._shell.stdin.flush()
        except:
            # Reconnect if shell died
            self._shell = subprocess.Popen(
                ["adb", "shell"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                text=True
            )
            self._shell.stdin.write(cmd + "\n")
            self._shell.stdin.flush()

    def _kill_current(self):
        with self._process_lock:
            if self._current_process is not None:
                try:
                    self._current_process.kill()
                    self._current_process.wait()
                except:
                    pass
                self._current_process = None

    def _start_press(self, x, y, duration_ms):
        self._kill_current()
        with self._process_lock:
            self._current_process = subprocess.Popen(
                ["adb", "shell", "input", "touchscreen", "swipe",
                 str(x), str(y), str(x), str(y), str(duration_ms)],
            )

    def _update_loop(self):
        while True:
            with self._state_lock:
                angle = self.angle
                magnitude = self.magnitude
                held = self.is_held

            if held and magnitude > 0:
                target_x, target_y = self._angle_to_xy(angle, magnitude)
                self._start_press(target_x, target_y, 200)
                time.sleep(0.1)
            else:
                self._kill_current()
                time.sleep(0.01)

    def set_direction(self, angle_deg, magnitude=1.0):
        with self._state_lock:
            self.angle = angle_deg
            self.magnitude = max(0.0, min(1.0, magnitude))
            self.is_held = magnitude > 0
        self._kill_current()

    def move_toward(self, target_x, target_y, screen_center_x=1170, screen_center_y=540):
        dx = target_x - screen_center_x
        dy = target_y - screen_center_y
        angle = math.degrees(math.atan2(dx, -dy)) % 360
        magnitude = min(1.0, math.sqrt(dx**2 + dy**2) / 500)
        self.set_direction(angle, magnitude)

    def stop(self):
        with self._state_lock:
            self.is_held = False
            self.magnitude = 0
        self._kill_current()

    def cleanup(self):
        self.stop()
        try:
            self._shell.kill()
        except:
            pass