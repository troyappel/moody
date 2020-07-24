import geocoder

import sounddevice as sd
import numpy as np
duration = 90.5  # seconds
fs = 48000

sound_count = 0
sound_sum = 0


def inc_sound(indata, outdata, frames, time, status):
    global sound_count, sound_sum
    volume_norm = np.linalg.norm(indata)*10
    sound_sum += volume_norm
    sound_count += 1


def get_avg():
    global sound_count, sound_sum
    if sound_count == 0:
        return 0
    toret = sound_sum / sound_count
    sound_sum = 0
    sound_count = 0
    return toret


f = sd.Stream(callback=inc_sound)

f.start()

g = geocoder.ip('me')
print(g.latlng)


while(True):
    sd.sleep(1000)
    print(get_avg())