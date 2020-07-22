from apscheduler.schedulers.blocking import BlockingScheduler
from interface import SpotifyInterface
import configparser

INTERVAL=30


config = configparser.ConfigParser()
config.read()
scheduler = BlockingScheduler()


# Interfaces

# LOOP
iterations = 0
def loop_event():
    global iterations
    iterations += 1



job = scheduler.add_job(loop_event, 'interval', seconds=INTERVAL)
