from pynput import mouse
import gym
import math

from . import GenericInterface

class KeyMouseInterface(GenericInterface):


    def __init__(self, config, callback_interval):
        listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        listener.start()

        self.SMOOTHING = 0.1
        self.movement_avg = 0
        self.click_avg = 0
        self.scroll_avg = 0
        self.keystroke_avg = 0

        self.prev_x_y = None
        self.new_movement_avg = 0
        self.new_click_avg = 0
        self.new_scroll_avg = 0
        self.new_keystroke_avg = 0

    def input_space(self) -> gym.spaces.space:
        attrs = gym.spaces.Box(low=[0, 0, 0, 0], high=[10000, 10000, 10000, 10000])
        return attrs

    def output_space(self) -> gym.spaces.space:
        return None

    def get_observation(self):
        self.movement_avg = self.rolling_avg(self.movement_avg, self.new_movement_avg)
        self.new_movement_avg = None

        self.click_avg = self.rolling_avg(self.click_avg, self.new_click_avg)
        self.new_click_avg = None

        self.scroll_avg = self.rolling_avg(self.scroll_avg, self.new_scroll_avg)
        self.new_scroll_avg = None

        pass

    def action_callback(self):
        return None


    def rolling_avg(self, prev_val, new_val):
        return new_val * self.SMOOTHING + (1 - self.SMOOTHING) * prev_val


    #### Inner housekeeping ####


    # Mouse handlers

    def on_move(self, x, y):
        if not self.prev_x_y:
            self.prev_x_y = (x, y)

        dx = self.prev_x_y[0]-x
        dy = self.prev_x_y[1] - y

        dist = math.sqrt(dx**2 + dy**2)

        self.new_movement_avg += dist


    def on_click(self, x, y, button, pressed):
        self.new_click_avg += 1

    def on_scroll(self, x, y, dx, dy):
        self.new_scroll_avg += 1