from pynput import mouse
import threading, time
import math



#### Global trackers ####

SMOOTHING = 0.1
movement_avg = 0
click_avg = 0
scroll_avg = 0
keystroke_avg = 0

def rolling_avg(prev_val, new_val):
    return new_val * SMOOTHING + (1 - SMOOTHING) * prev_val


#### Inner housekeeping ####

prev_x_y = None
new_movement_avg = 0
new_click_avg = 0
new_scroll_avg = 0
new_keystroke_avg = 0

# Mouse handlers

def on_move(x, y):
    global prev_x_y, new_movement_avg
    if not prev_x_y:
        prev_x_y = (x, y)

    dx = prev_x_y[0]-x
    dy = prev_x_y[1] - y

    dist = math.sqrt(dx**2 + dy**2)

    new_movement_avg += dist


def on_click(x, y, button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    if not pressed:
        # Stop listener
        return False

def on_scroll(x, y, dx, dy):
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))

# # Collect events until released
# with mouse.Listener(
#         on_move=on_move,
#         on_click=on_click,
#         on_scroll=on_scroll) as listener:
#     listener.join()

# ...or, in a non-blocking fashion:
listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll)
listener.start()

# 10s average timer

print("hya!")

WAIT_SECONDS = 3

def check_averages():
    global movement_avg, new_movement_avg

    movement_avg = rolling_avg(movement_avg, new_movement_avg)
    new_movement_avg = 0

    print(movement_avg)

    threading.Timer(WAIT_SECONDS, check_averages).start()

check_averages()