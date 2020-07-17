import usb.core
import usb.util
import sys

class find_class(object):
    def __init__(self, class_):
        self._class = class_
    def __call__(self, device):
        # first, let's check the device
        if device.bDeviceClass == self._class:
            return True
        # ok, transverse all devices to find an
        # interface that matches our class
        for cfg in device:
            # find_descriptor: what's it?
            intf = usb.util.find_descriptor(
                                        cfg,
                                        bInterfaceClass=self._class
                                )
            if intf is not None:
                return True

        return False

devices = usb.core.find(find_all=True)


def wrapper(gen):
  while True:
    try:
      yield next(gen)
    except StopIteration:
      break
    except Exception as e:
      print(e) # or whatever kind of logging you want

for x in (devices):
    print (x)