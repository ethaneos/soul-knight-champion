import subprocess
import cv2
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import time

class SoulKnightEnv(gym.Env):
    def __init__(self):
        super().__init__()

        # Screen dimensions (landscape)
        self.SCREEN_W = 2340
        self.SCREEN_H = 1080

        # Resize to smaller resolution for faster training
        self.OBS_W = 480
        self.OBS_H = 270

        # Button coordinates
        self.JOYSTICK = (421, int(1080-299))
        self.ATTACK = (2025, int(1080-300))
        self.SKILL = (1675, int(1080-300))
        self.WEAPON_SPECIAL = (1800, int(1080-575))
        self.SWITCH_WEAPON = (2050, int(1080-645))

        # Define all possible actions the model can take
        self.ACTIONS = [
            "move_up",
            "move_down",
            "move_left",
            "move_right",
            "attack",
            "use_skill",
            "weapon_special",
            "switch_weapon",
            "idle"
        ]

        # Replace discrete actions with continuous joystick control
        self.action_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0]),    
            high=np.array([360.0, 1.0, 1.0, 1.0]),  
            dtype=np.float32
        )
        # Actions are now:
        # [joystick_angle, joystick_magnitude, attack (0 or 1), skill (0 or 1)]

        # Tell gymnasium what a screenshot observation looks like
        # Shape is (height, width, RGB channels)
        self.observation_space = spaces.Box(
            low=0, high=255,
            shape=(self.OBS_H, self.OBS_W, 3),
            dtype=np.uint8
        )

        # Track game state
        self.prev_health = 100
        self.current_health = 100
        self.steps = 0
        self.max_steps = 1000

    def screenshot(self):
        result = subprocess.run(
            ["adb", "exec-out", "screencap", "-p"],
            capture_output=True
        )
        img_array = np.frombuffer(result.stdout, dtype=np.uint8)
        screen = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        # Resize for faster processing
        screen = cv2.resize(screen, (self.OBS_W, self.OBS_H))
        return screen

    def tap(self, x, y):
        subprocess.run(["adb", "shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1, y1, x2, y2, duration=200):
        subprocess.run(["adb", "shell", "input", "swipe",
                        str(x1), str(y1), str(x2), str(y2), str(duration)])

    def perform_action(self, action):
        angle, magnitude, should_attack, should_skill = action
        
        # Move joystick smoothly
        self.joystick.set_direction(angle, magnitude)
        
        # Attack if model decides to
        if should_attack > 0.5:
            self.tap(*self.ATTACK)
        
        # Use skill if model decides to
        if should_skill > 0.5:
            self.tap(*self.SKILL)

    def get_health(self, screen):
        # Sample the health bar region
        # These coordinates are approximate - may need tuning
        health_bar = screen[10:20, 50:200]

        # Count red pixels (health bar is red in Soul Knight)
        red_pixels = np.sum(
            (health_bar[:,:,2] > 150) &  # high red
            (health_bar[:,:,1] < 100) &  # low green
            (health_bar[:,:,0] < 100)    # low blue
        )

        # Normalize to 0-100
        max_pixels = health_bar.shape[0] * health_bar.shape[1]
        return (red_pixels / max_pixels) * 100

    def calculate_reward(self, screen):
        reward = 0

        self.current_health = self.get_health(screen)

        # Penalty for taking damage
        if self.current_health < self.prev_health:
            damage = self.prev_health - self.current_health
            reward -= damage * 2

        # Penalty for dying
        if self.current_health <= 0:
            reward -= 100

        # Small penalty each step to encourage efficiency
        reward -= 0.1

        self.prev_health = self.current_health
        return reward

    def is_dead(self, screen):
        return self.current_health <= 0

    def reset(self, seed=None):
        super().reset(seed=seed)
        print("Resetting environment...")

        # Restart the game - tap through death screen if needed
        time.sleep(2)
        # Tap center of screen to dismiss any menus
        self.tap(self.SCREEN_W // 2, self.SCREEN_H // 2)
        time.sleep(1)

        self.prev_health = 100
        self.current_health = 100
        self.steps = 0

        obs = self.screenshot()
        return obs, {}

    def step(self, action):
        self.steps += 1

        # Perform the chosen action
        action_name = self.ACTIONS[action]
        self.perform_action(action_name)

        # Get new screenshot
        obs = self.screenshot()

        # Calculate reward
        reward = self.calculate_reward(obs)

        # Check if episode is over
        terminated = self.is_dead(obs)
        truncated = self.steps >= self.max_steps

        info = {
            "health": self.current_health,
            "steps": self.steps,
            "action": action_name
        }

        return obs, reward, terminated, truncated, info