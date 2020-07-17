from apscheduler.schedulers.blocking import BlockingScheduler
import spotify_hooks as sp_hooks

INTERVAL=30

scheduler = BlockingScheduler()

# SETUP
sp.init()



# LOOP

iterations = 0

def loop_event():
    global iterations

    if(sp_hooks)

    iterations += 1

job = scheduler.add_job(loop_event, 'interval', seconds=INTERVAL)
