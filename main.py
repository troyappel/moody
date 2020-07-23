from apscheduler.schedulers.blocking import BlockingScheduler
from interface.SpotifyInterface import SpotifyInterface
import configparser

INTERVAL = 30

config = configparser.ConfigParser()
config.read('config.txt')
scheduler = BlockingScheduler()


interfaces = [
    SpotifyInterface(config, INTERVAL)
]

# LOOP
iterations = 0
def loop_event():
    global iterations
    iterations += 1

    for interface in interfaces:
        print(interface.get_observation())
        interface.action_callback(([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 255, 100], 1))



job = scheduler.add_job(loop_event, 'interval', seconds=INTERVAL)
